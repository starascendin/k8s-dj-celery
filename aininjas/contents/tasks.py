from config import celery_app
from aininjas.contents.models import  ContentSource, ContentProcessed, UserPromptRunVersion
from libs.extract_yt_audio_file import extract_vid_audio, rm_vid_audio, dl_yt_vid
from libs.supabase_client import SupabaseClient
from scripts.libs.yt_transcript_client import YtClient, RTTMTranscriptstruct, TranscriptChapterStruct, convert_time_to_seconds, YtChapterStruct
from config.settings.base import YT_API_KEY, SUPABASE_KEY, SUPABASE_URL, ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
# from aininjas.SbContentsUsers.models import SbContentsUser

import logging
logger = logging.getLogger(__name__)
import snoop

@celery_app.task(name="content_process.task_queue_and_extract_yt_audio")
def task_queue_and_extract_yt_audio(
    process_id,
    url
    ):
    """
    Changes ContentProcessed State machine
    extract mp4 from yt, upload to supabase and let GPU instance convert to wav and transcribe + speaker label.
    """
    try:
        processed: ContentProcessed | None = ContentProcessed.objects.filter(pk=process_id).first()
        if processed is None:
            logger.info(f"task_queue_and_extract_yt_audio: No ContentProcessed found for id {process_id}")
            return "No ContentProcessed found"
        sb_client = SupabaseClient(SUPABASE_URL, SUPABASE_KEY,
                               endpoint_url=ENDPOINT_URL,
                               s3_key=AWS_ACCESS_KEY_ID,
                               s3_secret=AWS_SECRET_ACCESS_KEY
                               )
        output_mp4_name = str(processed.id) + ".mp4"
        output_artifact_name = output_mp4_name
        output_dir = '/tmp/'
        audio_file = dl_yt_vid(url, filename=output_mp4_name, filepath=output_dir)
        print("#DEBUG audio_file extracted....", audio_file)
        output, resp,  = sb_client.upload_audio_to_bucket(
            output_dir,
            output_artifact_name,
            )
        # print("#DEBUG audio_file uploaded.... resp:", resp)

        if resp != None:
            # error, pass
            # print("#ERROR in upload_audio_to_bucket", resp)
            processed.state = ContentProcessed.ProcessStateChoice.ERROR
            artifact_blob: dict = processed.state_artifact_blob
            artifact_blob.setdefault('error_msg', str(resp))
            processed.save()
            raise resp
        processed.state = ContentProcessed.ProcessStateChoice.WAV_STORED
        artifact_blob: dict = processed.state_artifact_blob
        artifact_blob.setdefault('wav_url', output)
        processed.save()
        files_to_rm = [output_dir + output_mp4_name, output_dir + output_artifact_name]
        # rm_vid_audio(files_to_rm)
        return f'Done uploading {output_artifact_name} to {output}'
    except Exception as e:
        error_str = f'Error in task_queue_and_extract_yt_audio: {str(e)}'
        logger.warn(error_str)
        raise e


# import pandas as pd
# @celery_app.task(name="content_process.task_dl_transcripts_and_format")
# def task_dl_transcripts_and_format():
#     from aininjas.contents.services import ContentService, ContentPromptOrchestrator, PromptService
#     """
#     1. look thru processed table, get all Transcript_stored objects
#     2. pull transcripts from SB storage
#     3. format transcripts into RTTM
#     4. store into PROCESSED and update state
#     5. chunk
#     """
#     try:
#         yt_client = YtClient(YT_API_KEY)
#         sb = SupabaseClient(SUPABASE_URL, SUPABASE_KEY,
#                                 endpoint_url=ENDPOINT_URL,
#                                 s3_key=AWS_ACCESS_KEY_ID,
#                                 s3_secret=AWS_SECRET_ACCESS_KEY
#                                 )
#         content_service = ContentService(yt_client, sb)
#         prompt_service = PromptService("")
#         orchestrator = ContentPromptOrchestrator(prompt_service=prompt_service, content_service=content_service)


#         # content_service = ContentService(yt, sb)
#         processeds = ContentProcessed.objects.select_related('content').filter(state="TRANSCRIPT_STORED")
#         # print("#DEBUG processeds....", processeds)
#         dfs = []
#         for processed in processeds:
#             if processed.output_artifacts_url is None:
#                 continue
#             file_folder, filename = processed.output_artifacts_url.split('/')
#             transcript = sb.download_transcript_from_bucket(filename, folder_name=file_folder)
#             df = pd.read_csv(transcript[0])
#             dfs.append(df)

#             chapters = processed.content.raw_content_json_blob.get('chapters')
#             # print("#chapters", chapters)
#             chapters = [YtChapterStruct(**chapter) for chapter in chapters]
#             # format df into rttm
#             rttm_transcripts = []
#             for index, row in df.iterrows():
#                 rttm = RTTMTranscriptstruct(
#                     speaker=row['Speaker'],
#                     start=convert_time_to_seconds(row['Start']),
#                     duration=convert_time_to_seconds(row['End']) - convert_time_to_seconds(row['Start']), # here just use END
#                     text=row['Text']
#                 )

#                 rttm_transcripts.append(rttm)

#             chapters_with_transcripts = yt_client._format_rttm_transcript_into_chapters(
#                 chapters,
#                 rttm_transcripts,
#                 vid_duration='PT10M1S',
#                 podcast_type="DUO" # assuming DUO for podcast for now, since this task is for podcast
#                 # numb_of_speaker=processed.number_of_speaker
#                 )

#             processed = ContentService.update_processed_transcribe_state(processed, chapters_with_transcripts)

#         processeds = ContentProcessed.objects.select_related('content').filter(state="READY_TO_CHUNK")
#         for processed in processeds:
#             # print("#processed", processed)
#             chunks = ContentService.chunk_yt_processed(processed)

#             if len(chunks) == 0:
#                 return "DONE task_transcribe_yt_content_to_prompt_completion, no chunks created"

#             # TODO: Here take the proceed, create prompt run version, apply prompt to its chunks
#             # promptcompletions = orchestrator.apply_prompts_to_chunks(chunks)
#             promptcompletions = orchestrator.apply_prompts_to_processed_and_chunks(processed)
#             # Summarize final summary for a processed content
#             final_pc = orchestrator.finalize_summary_for_processed(processed, promptcompletions)

#         return 'Completed task_dl_transcripts_and_format '
#     except Exception as e:
#         raise Exception('Error in task_dl_transcripts_and_format: ' + str(e))


from aininjas.sbusers.models import SbPublicUser, SbUserProfile
from typing import Union
@celery_app.task(name="content_process.task_transcribe_yt_content_to_prompt_completion")
def task_transcribe_yt_content_to_prompt_completion(**kwargs):
    """
    This takes a yt_url and goes thru the entire steps to prompt completion.
    If YT is mono, then PC will be generated
    If YT is DUO, then mp4 will be uploaded to s3 and then awaits for other tasks to process it.
    - duo should not go thru chunking/prompting
    """
    from .services import ContentService, ContentPromptOrchestrator, PromptService, PromptExecResult

    try:
        yt_url = kwargs['yt_url']
        podcast_type = kwargs['podcast_type']
        user_id = kwargs['user_id']
        sb_user: SbUserProfile = SbUserProfile.objects.get(id=user_id)
        print("#DEBUG sb_user sb_user.openai_key", sb_user.openai_key)

        yt_client = YtClient(YT_API_KEY)
        sb_client = SupabaseClient(SUPABASE_URL, SUPABASE_KEY,
                                endpoint_url=ENDPOINT_URL,
                                s3_key=AWS_ACCESS_KEY_ID,
                                s3_secret=AWS_SECRET_ACCESS_KEY
                                )
        content_service = ContentService(yt_client, sb_client)
        prompt_service = PromptService(sb_user.openai_key)
        orchestrator = ContentPromptOrchestrator(prompt_service=prompt_service, content_service=content_service)

        result = content_service.run_yt_url_to_chunks(
            yt_url,
            podcast_type=podcast_type,
            )
        if len(result['chunks']) == 0:
            return "DONE task_transcribe_yt_content_to_prompt_completion, no chunks created"

        processed = result['processed']

        # TODO: Need to refactor this to be DRY
        # Summarize, go thru summarizing chunks then final
        # sb_user = SbContentsUser.objects.get(id=user_id)
        chunk_result: Union[PromptExecResult, None] = orchestrator.run_user_processed_prompt_version(
                sb_user,
                processed,
                UserPromptRunVersion.PromptRunTypeChoice.YT_CHUNK_SUMMARIZE
                )
        # TODO: shoudl take in a chunk run version
        fina_result: Union[PromptExecResult, None] = orchestrator.run_user_processed_prompt_version(
            sb_user, 
            processed,
            UserPromptRunVersion.PromptRunTypeChoice.YT_FINAL_SUMMARIZE,
            run_version=chunk_result.run_version
            )

        return "DONE task_transcribe_yt_content_to_prompt_completion. finalize_summary_for_processed executed"
        
    except Exception as e:
        raise Exception('Error in task_transcribe_yt_content_to_prompt_completion: ' + str(e))


