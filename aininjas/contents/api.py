

from ninja_extra import NinjaExtraAPI, api_controller, http_get
from ninja import Router
from .models import ContentSource, ContentProcessed, UserPromptRunVersion
from aininjas.sbusers.models import SbPublicUser, SbUserProfile

from .services import ContentService, ContentPromptOrchestrator, PromptService, PromptExecTupleStruct, PromptExecResult
from ninja import Schema
from scripts.libs.yt_transcript_client import YtClient
from libs.supabase_client import SupabaseClient
from scripts.libs.yt_transcript_client import YtClient, RTTMTranscriptstruct, TranscriptChapterStruct, convert_time_to_seconds, YtChapterStruct
from config.settings.base import YT_API_KEY, SUPABASE_KEY, SUPABASE_URL, ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import snoop
from .tasks import task_transcribe_yt_content_to_prompt_completion
from ninja.errors import HttpError
router = Router()

@router.get('/')
def get_all_contents(request):
    
    # print("#DEBUG request", request)
    print("#DEBUG request.auth", request.auth)
    
    return [
        {"id": e.id , "url": e.url}
        for e in ContentSource.objects.all()
    ]

class ContentProcessedIn(Schema):
    # id: str
    state: str


class ContentProcessedOut(Schema):
    # id: str
    state: str


@router.put('/content-processed/{processed_id}', response=ContentProcessedOut)
def update_content_processed_by_id(request, processed_id, content_processed_in: ContentProcessedIn):
    print("#DEBUG", request.body)

    content_processed = ContentProcessed.objects.get(id=processed_id)    # update state

    content_processed.save()
    return content_processed


class ContentYtTranscribeIn(Schema):
    # id: str
    yt_url: str
    podcast_type: str
    number_of_speakers: int

@router.post('/yt-transcribe', )
def content_yt_transcribe(request, content_yt_transcribe_in: ContentYtTranscribeIn):
    if content_yt_transcribe_in.podcast_type not in ['MONO', 'DUO', 'MULI']:
        raise Exception('podcast_type must be one of MONO, DUO, MULI')
    user_profile: SbUserProfile = request.auth
    if user_profile.openai_key is None:
        raise HttpError(400, 'User does not have openai_key')
    task_id = task_transcribe_yt_content_to_prompt_completion.delay(
        yt_url=content_yt_transcribe_in.yt_url,
        podcast_type=content_yt_transcribe_in.podcast_type,
        user_id=user_profile.id,
    )
    return 'API call done. Starting Task: task_transcribe_yt_content_to_prompt_completion' + str(task_id)

from aininjas.contents.models import ContentSource, ContentCreator, ContentProcessed,ContentYtChunk, PromptCompletion, Prompt, UserPromptRunVersion, PromptCompletionExecutionHistory
from typing import List, Tuple, Optional
from ninja.orm import create_schema


class PromptChaptersIn(Schema):
    custom_prompt: str
    content_processed_id: str
    summarize_type: str
    chunks_run_version_id: Optional[str]


yt_client = YtClient(YT_API_KEY)
sb = SupabaseClient(SUPABASE_URL, SUPABASE_KEY, 
                            endpoint_url=ENDPOINT_URL, 
                            s3_key=AWS_ACCESS_KEY_ID, 
                            s3_secret=AWS_SECRET_ACCESS_KEY
                            )    
content_service = ContentService(yt_client, sb)


HistorySchema = create_schema(PromptCompletionExecutionHistory, depth=1, fields=['user_processed_prompt_version', 'prompt_completion'])

@router.post('/custom-prompt', auth=None, response=List[HistorySchema] )
def custom_prompt(request, prompt_chapters_in: PromptChaptersIn):
    """
    Takes in a custom prompt and apply it to transcripts of a content_processed_id
    - Take a prompt, create a task, call apply prompt ot chunks
    """
    if prompt_chapters_in.summarize_type not in ['SUMMARIZE_CHUNKS', 'SUMMARIZE_FINAL']:
        raise Exception('podcast_type must be one of MONO, DUO, MULI')    

    user_profile: SbUserProfile = SbUserProfile.objects.get(id="19a1e545-58df-4d2f-a0be-7e30748c1eee")
    prompt_service = PromptService(user_profile.openai_key)
    orchestrator = ContentPromptOrchestrator(prompt_service=prompt_service, content_service=content_service)
    
    processed = ContentProcessed.objects.get(id=prompt_chapters_in.content_processed_id)

    if prompt_chapters_in.summarize_type == 'SUMMARIZE_CHUNKS':
        result: PromptExecResult = orchestrator.run_user_processed_prompt_version(
            user_profile,
            processed,
            UserPromptRunVersion.PromptRunTypeChoice.YT_CHUNK_SUMMARIZE,
            use_custom_prompt=True,
            custom_prompt=prompt_chapters_in.custom_prompt
            )
        return result.histories
        # pcs = [e.prompt_completion for e in results]
        # return pcs
    elif prompt_chapters_in.summarize_type == 'SUMMARIZE_FINAL':
        # TODO: This needs to take in selected "chunks + PCs"
        run_version: UserPromptRunVersion = UserPromptRunVersion.objects.get(id=prompt_chapters_in.chunks_run_version_id)
        result: PromptExecResult = orchestrator.run_user_processed_prompt_version(
            user_profile,
            processed,
            UserPromptRunVersion.PromptRunTypeChoice.YT_FINAL_SUMMARIZE,
            custom_prompt=prompt_chapters_in.custom_prompt,
            run_version=run_version
            )
        return result.histories
    
    else:
        raise Exception('summarize_type must be one of SUMMARIZE_CHUNKS, SUMMARIZE_FINAL')
    
