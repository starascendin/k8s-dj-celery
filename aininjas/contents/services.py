from aininjas.contents.models import ContentSource, ContentCreator, ContentProcessed,ContentYtChunk, PromptCompletion, Prompt, UserPromptRunVersion, PromptCompletionExecutionHistory, UserDefaultPrompt
from aininjas.sbusers.models import SbPublicUser, SbUserProfile
from aininjas.sbusers.services import UsersService
from scripts.libs.yt_transcript_client import YtClient, RTTMTranscriptstruct, YtChapterStruct
from typing import List, Optional, Tuple
from pydantic import BaseModel
import textwrap
import hashlib
from libs.supabase_client import SupabaseClient
import logging
from aininjas.contents.tasks import task_queue_and_extract_yt_audio
import snoop
import os
from libs.chatgpt_wrapper import RevChatGPTWrapper
from typing import Union

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

logger = logging.getLogger(__name__)


class ChunkSegmentsStruct(BaseModel):
    type: str
    chapter_segments: list

    class Config:
        extra = 'forbid'


class RawTranscriptStruct(BaseModel):
    chapters: list[dict]
    transcripts: list[dict]

    class Config:
        extra = 'forbid'

PromptExecTupleStruct = Tuple[str, Union[Prompt, None], ContentYtChunk]

# ==== PART Content Service



# Depends on Prompt Service
class ContentService():
    def __init__(self, yt_client: YtClient, sb_client: SupabaseClient):
        self.yt_client = yt_client
        self.sb = sb_client

    def _get_or_create_content_creator(self, channel_id,
            source_channel=ContentCreator.SourceChoice.NONE,
            ) -> Tuple[ContentCreator, bool]:
            meta = self.yt_client.get_channel_meta(channel_id)
            snippet = meta.get('snippet')
            result = ContentCreator.objects.get_or_create(
                creator_id=meta.get('id'),
                defaults={
                    'creator_name': snippet.get('customUrl'),
                    'creator_url': '',
                    'source_channel': source_channel,
                    'profile_json_blob': meta,
                }
            )
            return result

    def _get_or_create_content(self, video_id, creator: ContentCreator, raw_content_json_blob: Optional[RawTranscriptStruct]=None, podcast_type="MONO") -> ContentSource:
        url = self.yt_client._get_yt_url_from_video_id(video_id)
        video_snippet = self.yt_client._get_video_snippet_by_id(video_id)
        content = ContentSource.objects.filter(url=url).first()
        if content:
            print("content already exists, retrieving....")
            return content


        content = ContentSource.objects.create(
            url=url,
            content_creator=creator,
            content_title=video_snippet.get('title'),
            content_description=video_snippet.get('description'),
            raw_content_json_blob=raw_content_json_blob.dict(),
            param_json_blob=dict({
                'podcast_type': podcast_type,
            }),
            # number_of_speaker=number_of_speaker
        )
        content.save()
        return content

    # @snoop # type: ignore
    def _create_processed(self, content: ContentSource, process_mode=ContentProcessed.ProcessAlgoTypeChoice.NORMAL_YT_TRANSCRIBE, processed_content_json_blob=None, number_of_speaker=1) -> ContentProcessed:

        if process_mode == ContentProcessed.ProcessAlgoTypeChoice.NORMAL_YT_TRANSCRIBE:
            # normal speaker, add SPEAKER_1 to transcript shape
            (processed, created) = ContentProcessed.objects.get_or_create(
                content=content,
                processing_algo_type=ContentProcessed.ProcessAlgoTypeChoice.NORMAL_YT_TRANSCRIBE,
                defaults={
                    'processed_content_json_blob': {"data": processed_content_json_blob},
                    'state': ContentProcessed.ProcessStateChoice.READY_TO_CHUNK,
                    'number_of_speaker': number_of_speaker
                }
            )
            processed.save()

        else:

            (processed, created) = ContentProcessed.objects.get_or_create(
                content=content,
                processing_algo_type=ContentProcessed.ProcessAlgoTypeChoice.SPEAKER_TRANSCRIBE,
                defaults={
                    'processed_content_json_blob': {"data": processed_content_json_blob},
                    'state': ContentProcessed.ProcessStateChoice.WAV_JOB_STARTED,
                    'number_of_speaker': number_of_speaker
                }
            )
            logger.info(f"#DEBUG processed, created {processed, created}" )
            if created:
                task = task_queue_and_extract_yt_audio.delay(processed.id, content.url)
        print("#DEBUG ContentProcessed created ", created)
        return processed

    @staticmethod
    def update_processed_transcribe_state(processed: ContentProcessed, processed_content_json_blob_struct=None):
        if processed.state != ContentProcessed.ProcessStateChoice.TRANSCRIPT_STORED:
            raise Exception('Content processed state is not TRANSCRIPT_STORED, cannot update state')
        # Update proceseed transcribe state and store transcript
        # this needs to be a {'data': []}
        processed.processed_content_json_blob = {'data': processed_content_json_blob_struct}
        processed.state = ContentProcessed.ProcessStateChoice.READY_TO_CHUNK
        processed.save()
        return processed


    # === Chunking

    @staticmethod
    def chunk_yt_processed(content_processed: ContentProcessed) -> List[ContentYtChunk]:
        """
        This takes ContentProcessed.processed_content_json_blob and chunks it.

        """

        # TODO: here we should add in chunking strategy (processed -> chunk_strategy -> chunkeds)
        # If exist, retrieve
        if content_processed.is_chunked or content_processed.state == ContentProcessed.ProcessStateChoice.COMPLETED:
            return ContentYtChunk.objects.filter(content_processed=content_processed)

        if content_processed.state != ContentProcessed.ProcessStateChoice.READY_TO_CHUNK:
            logger.info(f"Content processing not READY yet, state is: {content_processed.state} skipping chunking")
            return []

        chapter_transcripts = content_processed.processed_content_json_blob['data']
        chunks = []

        # TOODO: need to account for transcripts too long


        for chapter_transcript in chapter_transcripts:
            txt = ''

            segments = ChunkSegmentsStruct(
                type='rttm',
                chapter_segments=chapter_transcript['chapter_segments'] # # TODO this should be a RTTMTranscriptstruct
            ).dict()
            chunks.append(ContentYtChunk(
                content_processed=content_processed,
                transcript_start_time=chapter_transcript['chapter_start'],
                content_chunk_title=chapter_transcript['chapter_title'],
                content_chunk_text=txt,
                content_segments_json=segments
            ))


        # This will result in bad returned IDs
        content_chunks = ContentYtChunk.objects.bulk_create(chunks, ignore_conflicts=True)
        content_processed.is_chunked = True
        content_processed.state = ContentProcessed.ProcessStateChoice.COMPLETED
        content_processed.save()

        return content_chunks

    @staticmethod
    def get_all_unprompted_chunks() -> List[ContentYtChunk]:
        return ContentYtChunk.objects.filter(promptcompletion__isnull=True)

    def run_yt_url_to_chunks(self, url, podcast_type='MONO') -> dict:
        video_id = YtClient._parse_yt_video_id_from_url(url)
        video_snippet = self.yt_client._get_video_snippet_by_id(video_id)
        channel_id = video_snippet.get('channelId')
        process_type = None
        number_of_speaker = 0
        if podcast_type == "MONO":
            process_type = ContentProcessed.ProcessAlgoTypeChoice.NORMAL_YT_TRANSCRIBE
            number_of_speaker = 1
        elif podcast_type == "DUO":
            process_type = ContentProcessed.ProcessAlgoTypeChoice.SPEAKER_TRANSCRIBE
            number_of_speaker = 2
        elif podcast_type == "MULTI":
            process_type = ContentProcessed.ProcessAlgoTypeChoice.SPEAKER_TRANSCRIBE
            number_of_speaker = 3
        else:
            raise Exception('Podcast type not supported')

        (content_creator, created) = self._get_or_create_content_creator(
            channel_id,
            source_channel=ContentCreator.SourceChoice.YOUTUBE
            )
        (chapters, rttm_transcript, raw_transcript) = self.yt_client._get_chapters_and_raw_transcript(video_id)

        raw_content_json_blob: RawTranscriptStruct = RawTranscriptStruct(**{
                'chapters': chapters,
                'transcripts': rttm_transcript
            })


        # BL: Strategy for NO chapters.
        if len(chapters) == 0:
            # by timestamp
            chapters_timestamp: List[YtChapterStruct] = self.yt_client._generate_chapters_strategy("NAIVE_BY_FIXED_TIME", transcripts=rttm_transcript)
            print("#DEBUG chapters by timestamp", chapters_timestamp)
            # by token size
            chapters_tokens: List[YtChapterStruct] = self.yt_client._generate_chapters_strategy("NAIVE_BY_TOKEN_SIZE", transcripts=rttm_transcript)

            print("#DEBUG chapters by tokens", chapters_tokens)
            chapters = chapters_tokens

        chapter_with_transcripts = self.yt_client._format_rttm_transcript_into_chapters(
            chapters,
            rttm_transcript,
            video_id=video_id,
            podcast_type=podcast_type,
            )

        content: ContentSource = self._get_or_create_content(video_id, content_creator,
            raw_content_json_blob=raw_content_json_blob,
            podcast_type=podcast_type,
            )


        processed = self._create_processed(
            content=content,
            process_mode=process_type,
            processed_content_json_blob=chapter_with_transcripts, #list[TranscriptChapterStruct]
            number_of_speaker=number_of_speaker
            )


        chunks = ContentService.chunk_yt_processed(processed)
        print("#DEBUG run_yt_url_to_chunks done. Artifacts: ", content, processed, chunks)
        return {
            'content': content,
            'processed': processed,
            'chunks': chunks,
        }





from libs.openai_sdk import OpenaiSdk

from scripts.libs.yt_transcript_client import YtClient
from typing import List
import re
import openai
from pydantic import BaseModel
import textwrap


# ==== PART Prompt Service


from dataclasses import dataclass
@dataclass
class PromptExecResult:
    histories: List[PromptCompletionExecutionHistory]
    run_version: UserPromptRunVersion

import sys
class PromptService():
    def __init__(self, api_key):
        if not api_key:
            raise Exception("No OpenAI api key provided")

        self.openai_sdk = OpenaiSdk(api_key)


    def run_chatgpt_prompt(self, input_prompt):
        results = self.openai_sdk.run([input_prompt])
        return results[0]

    def user_run_prompt(self, sb_user: SbUserProfile, processed: ContentProcessed,  prompts_execs: List[PromptExecTupleStruct], run_strategy_type=None) -> PromptExecResult:
        """
        user should run a prompt, saves version, saves execution history
        """
        logger.info(f"Executing user_run_prompt for {run_strategy_type}")
        # step 1 -- create run version
        run_version = UserPromptRunVersion.objects.create(
            sb_user=sb_user,
            processed=processed,
            run_type=run_strategy_type,
        )
        run_version.save()
        logger.debug(f"#Created run version: {str(run_version)}")


        tuple_list: List[Tuple[PromptCompletion, PromptExecTupleStruct]] = self._execute_prompt_and_save(sb_user, prompts_execs)

        histories: List[PromptCompletionExecutionHistory] = []
        for tuple_pc_exec in tuple_list:
            (pc, execs) = tuple_pc_exec
            history = PromptCompletionExecutionHistory(
                user_processed_prompt_version=run_version,
                source_content_processed=processed,
                source_content_chunk=execs[2],
                prompt_completion=pc
            )
            # history.save()
            histories.append(history)
        # print("#DEBUG histories", histories)
        PromptCompletionExecutionHistory.objects.bulk_create(histories)
        result: PromptExecResult = PromptExecResult(
            histories=histories,
            run_version=run_version
        )
        return result


    def _execute_prompt_and_save(self, sb_user: SbUserProfile, prompts_execs: List[PromptExecTupleStruct]) -> List[Tuple[PromptCompletion, PromptExecTupleStruct]]:
        prompt_completions_created = []
        return_tuples = []
        print("#DEBUG ", prompts_execs[0][0])
        results = self.openai_sdk.run([prompt_exec[0] for prompt_exec in prompts_execs])
        for i, result in enumerate(results):
            try:
                completion = result
                completion = completion.strip()
                completion_state = PromptCompletion.CompletionStateChoice.COMPLETED
            except Exception as e:
                logger.error(f"Error running prompt: {e}")
                completion = f"FAILED: {e}"
                completion_state = PromptCompletion.CompletionStateChoice.FAILED
            prompt_exec = prompts_execs[i]
            prompt_txt = prompt_exec[0]
            prompt = prompt_exec[1]
            # content_chunk = prompt_exec[2]

            prompt_completion = PromptCompletion(
                prompt_text=prompt_txt,
                prompt=prompt,
                output_completion=completion,
                completion_state=completion_state,
                sb_user=sb_user
            )
            # TODO: this can be optimized
            # prompt_completion.save()
            prompt_completions_created.append(prompt_completion)
            return_tuples.append((prompt_completion, prompt_exec))
        results_bulk_create = PromptCompletion.objects.bulk_create(prompt_completions_created)
        return return_tuples



# ==== PART Orchestrator Service

class ContentPromptOrchestrator():
    def __init__(self, prompt_service: PromptService=None, content_service: ContentService=None):
        self.prompt_service: PromptService = prompt_service
        self.content_servic: ContentService = content_service


    def hash_prompt(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def _prep_chunk_segments_to_context_txt(self, content_chunk: ContentYtChunk):
        content_chunk_title = content_chunk.content_chunk_title
        chunk_struct: ChunkSegmentsStruct = ChunkSegmentsStruct(**content_chunk.content_segments_json)

        chunk_segments_txt_blob = ""

        for segment in chunk_struct.chapter_segments:
            segment = RTTMTranscriptstruct(**segment)
            chunk_segments_txt_blob += f"{segment.speaker}: {segment.text} \n"

        context_txt = textwrap.dedent(f"""
                TITLE: {content_chunk_title}
                Transcripts:
        {chunk_segments_txt_blob}
        """).strip()
        final_text = '\n'.join(line.lstrip() for line in context_txt.splitlines())
        return final_text

    @staticmethod
    def _prepend_context_to_prompt(context_txt, prompt):
        txt = textwrap.dedent(f"""
                {context_txt}
                -----
                {prompt}
                """).strip()

        return txt


    def apply_prompts_to_processed_and_chunks(self, sb_user: SbUserProfile, processed: ContentProcessed, use_custom_prompt=False, custom_prompt='') -> Union[PromptExecResult, None]:
        logger.debug("#DEBUG: apply_prompts_to_processed_and_chunks... 1")
        content_chunks = processed.content_chunks.all()
        if len(content_chunks) == 0:
            return None
        try:
            user_default_prompt_chunk: UserDefaultPrompt = UserDefaultPrompt.objects.get(sb_user=sb_user, exec_type=Prompt.ExecTypeChoice.DEFAULT_CHUNK_SUMMARIZE)
        except Exception as e:
            logger.info("#DEBUG: creating default prompt for user...")
            user_service = UsersService()
            user_default_prompt_chunk = user_service.add_default_prompts_for_user(sb_user, Prompt.ExecTypeChoice.DEFAULT_CHUNK_SUMMARIZE)
            logger.info('Created default chunk prompt for user')

        prompt: Prompt = user_default_prompt_chunk.prompt
        prompts_execs: List[PromptExecTupleStruct] = []
        existing_prompt_completions = []
        results: List[Tuple[PromptCompletion, PromptExecTupleStruct]] = []
        for content_chunk in content_chunks:
            context_txt = self._prep_chunk_segments_to_context_txt(content_chunk)

            if use_custom_prompt is True:
                prompt_txt = ContentPromptOrchestrator._prepend_context_to_prompt(context_txt, custom_prompt)
                prompt_exec: PromptExecTupleStruct = (prompt_txt, None, content_chunk)
            else:
                chunk_already_prompted = PromptCompletion.objects.filter(prompt=prompt, content_chunk=content_chunk)
                if chunk_already_prompted.exists():
                    logger.info("prompt completion already exists, skipping")
                    prompt_exec: PromptExecTupleStruct = ("N/A", None, content_chunk)
                    results.append((chunk_already_prompted.first(), prompt_exec))
                    continue
                prompt_txt = ContentPromptOrchestrator._prepend_context_to_prompt(context_txt, prompt.prompt)
                prompt_exec: PromptExecTupleStruct = (prompt_txt, prompt, content_chunk)

            prompts_execs.append(prompt_exec)

        if len(results) > 0:
            return None

        # TODO: This should call prompt service run version
        # results: List[Tuple[PromptCompletion, PromptExecTupleStruct]] = self.prompt_service._execute_prompt_and_save(prompts_execs)
        result: PromptExecResult = self.prompt_service.user_run_prompt(
            sb_user,
            processed,
            prompts_execs,
            run_strategy_type=UserPromptRunVersion.PromptRunTypeChoice.YT_CHUNK_SUMMARIZE
            )
        return result




    def finalize_summary_for_processed(self, sb_user: SbUserProfile, processed: ContentProcessed, run_version: UserPromptRunVersion , use_custom_prompt=False, custom_prompt='') -> Union[PromptExecResult, None]:
        logger.info(f'Executing finalize_summary_for_processed for user {sb_user.email}')
        # final_summarize_prompt: (Prompt | None) = Prompt.objects.filter(exec_type=Prompt.ExecTypeChoice.DEFAULT_YT_FINAL_SUMMARIZE).first()

        # if final_summarize_prompt is None:
        #     raise Exception("No final summarize prompt found")
        # BL: Get user's selected default prompt
        try:
            user_default_prompt_chunk: UserDefaultPrompt = UserDefaultPrompt.objects.get(sb_user=sb_user, exec_type=Prompt.ExecTypeChoice.DEFAULT_YT_FINAL_SUMMARIZE)
        except:
        #     user_default_prompt_chunk = None
        # if user_default_prompt_chunk is None:
            # TODO: should add migration to seed default prompt for user.
            # This is assuming user as already seeded prompt
            user_service = UsersService()
            user_default_prompt_chunk = user_service.add_default_prompts_for_user(sb_user, Prompt.ExecTypeChoice.DEFAULT_YT_FINAL_SUMMARIZE)
            logger.info('Created default final prompt for user')

        final_summarize_prompt: (Prompt | None)  = user_default_prompt_chunk.prompt

        prompts_execs = []
        # Get the latest run version for YT_CHUNK_SUMMARIZE
        # run_version = processed.userpromptrunversion_set.filter(run_type="YT_CHUNK_SUMMARIZE").latest('created')
        # print("#DEBUG run_version", run_version)
        exec_history_set = run_version.promptcompletionexecutionhistory_set.all()
        # print("#exec_history_set", exec_history_set)
        context_text = ""
        # for prompt_completion in prompt_completions:
        for exec_history in exec_history_set:
            prompt_completion = exec_history.prompt_completion
            output_completion = prompt_completion.output_completion
            chunk = exec_history.source_content_chunk
            chunk_title = chunk.content_chunk_title
            context_text += f"Chapter: {chunk_title} \n"
            context_text += f"{output_completion} \n"


        # Prepping for the Final summary
        if use_custom_prompt is True:
            prompt_formatted = f"{context_text} \n {custom_prompt}"
            prompt_exec: PromptExecTupleStruct = (prompt_formatted, None, None)
            prompts_execs.append(prompt_exec)
        else:
            prompt_formatted = textwrap.dedent(f"""{context_text}
            ----
            {final_summarize_prompt.prompt}
            """).strip()
            prompt_exec: PromptExecTupleStruct = (prompt_formatted, None, None)
            prompts_execs.append(prompt_exec)

        # print("#prompt_formatted", prompt_formatted)
        # results: List[Tuple[PromptCompletion, PromptExecTupleStruct]] = self.prompt_service._execute_prompt_and_save(prompts_execs)
        if len(prompts_execs) == 0:
            return None
        result: PromptExecResult = self.prompt_service.user_run_prompt(
            sb_user,
            processed,
            prompts_execs,
            run_strategy_type=UserPromptRunVersion.PromptRunTypeChoice.YT_FINAL_SUMMARIZE
        )
        return result

    def run_user_processed_prompt_version(self, sb_user: SbUserProfile, processed: ContentProcessed, run_strategy_type: UserPromptRunVersion.PromptRunTypeChoice , run_version=None, use_custom_prompt=False, custom_prompt='') -> PromptExecResult:
        """
        Strategy A.
            1. Take a processed, create a Prompt Run Version entry with run_type=YT_CHUNK_SUMMARIZE.
            2. THen take its chunks and apply prompts to each chunk. Save entries in PromptCompletionExecutionHistory
        Strategy B. Finalize Summary
            1. Take a processed, create a Prompt Run Version entry with run_type=YT_FINAL_SUMMARIZE.
            2. Then get its chunks and their related PromptCompletion, concat output_completion into 1 text blob, then feed into finalize_summary_for_processed. Then save entry PromptCompletionExecutionHistory.
        """
        # step 2 -- take proceed and apply to the right path
        # path 1 -- chunk summarize
        try:
            if run_strategy_type == UserPromptRunVersion.PromptRunTypeChoice.YT_CHUNK_SUMMARIZE:
                # FOR CHUNKS
                print("#DEBUG executing chunk summarize")
                result: PromptExecResult = self.apply_prompts_to_processed_and_chunks(
                    sb_user,
                    processed,
                    use_custom_prompt=use_custom_prompt,
                    custom_prompt=custom_prompt,
                    )
                logger.info(f'Finished applying prompts to chunks')
                return result
            elif run_strategy_type == UserPromptRunVersion.PromptRunTypeChoice.YT_FINAL_SUMMARIZE:
                if run_version is None:
                    raise Exception("run_version is required for YT_FINAL_SUMMARIZE")
                print("#DEBUG executing Final summarize")
                result: PromptExecResult  = self.finalize_summary_for_processed(
                    sb_user,
                    processed,
                    run_version,
                    use_custom_prompt=use_custom_prompt,
                    custom_prompt=custom_prompt
                    )
                logger.info(f'Finished applying prompts to finalize summary')
                return result
            else:
                raise Exception("Invalid run strategy type")
        except Exception as e:
            logger.error(f'Error executing prompts for processed {processed.id}')
            logger.error(e)
            raise e




