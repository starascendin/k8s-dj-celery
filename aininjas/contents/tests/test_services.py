# test_content_service.py

import pytest
from unittest.mock import MagicMock
from scripts.libs.yt_transcript_client import YtClient
from aininjas.contents.services import ContentService, RawTranscriptStruct, PromptExecTupleStruct, PromptExecResult
from aininjas.contents.models import ContentSource, ContentCreator, ContentProcessed, ContentYtChunk, SbUserProfile, PromptCompletion, UserPromptRunVersion
from unittest import mock
from scripts.libs.yt_transcript_client import YtClient
from libs.supabase_client import SupabaseClient
from aininjas.sbusers.tests.factory import SbUserProfileFactory

pytestmark = pytest.mark.django_db

@pytest.fixture
def mock_yt_client():
    return mock.MagicMock(spec=YtClient)


@pytest.fixture
def mock_sb_client():
    return mock.MagicMock(spec=SupabaseClient)




@pytest.fixture
def mock_raw_transcript():
    return RawTranscriptStruct(
        chapters=[{'start_time': 0, 'end_time': 10, 'title': 'Chapter 1'}],
        transcripts=[{'start_time': 0, 'end_time': 10, 'text': 'Chapter 1 text'}]
    )


@pytest.fixture
def mock_content_service(mock_yt_client, mock_sb_client):
    return ContentService(mock_yt_client, mock_sb_client)

@pytest.fixture
def mock_content_creator():
    return ContentCreator.objects.create(
        creator_id='test_creator_id',
        creator_name='test_creator_name',
        creator_url='https://test_creator_url.com',
        source_channel=ContentCreator.SourceChoice.NONE,
        profile_json_blob={'test': 'data'}
    )

@pytest.fixture
def mock_content_source(mock_content_creator):
    return ContentSource.objects.create(
        url='https://www.youtube.com/watch?v=test_video_id',
        content_creator=mock_content_creator,
        content_title='Test Video',
        content_description='This is a test video.',
        raw_content_json_blob={},
        param_json_blob={},
    )

@pytest.fixture
def mock_content_processed(mock_content_source):
    return ContentProcessed.objects.create(
        content=mock_content_source,
        processing_algo_type=ContentProcessed.ProcessAlgoTypeChoice.NORMAL_YT_TRANSCRIBE,
        processed_content_json_blob={
            'data': [
                {
                    'chapter_start': 0,
                    'chapter_title': 'Test Chapter 1',
                    'chapter_segments': [
                        {'start_time': 0, 'end_time': 10, 'speaker': 'SPEAKER_1', 'text': 'Hello world!'}
                    ]
                }
            ]
        },
        number_of_speaker=1,
        state=ContentProcessed.ProcessStateChoice.READY_TO_CHUNK
    )

@pytest.fixture
def mock_content_yt_chunk(mock_content_processed):
    return ContentYtChunk.objects.create(
        content_processed=mock_content_processed,
        transcript_start_time=0,
        content_chunk_title="Test Chapter 1",
        content_chunk_text="",
        content_segments_json={
        'type': 'rttm',
        'chapter_segments':[
            {'start_time': 0, 'end_time': 10, 'speaker': 'SPEAKER_1', 'text': 'Hello world!'}
        ]},
    )


def test__get_or_create_content_creator(mock_yt_client, mock_sb_client, mock_content_creator, mock_content_service):
    # Test creating new content creator
    mock_yt_client.get_channel_meta.return_value = {'id': 'new_creator_id', 'snippet': {'customUrl': 'new_creator_name'}}
    (creator, created) = mock_content_service._get_or_create_content_creator('new_creator_id')
    assert creator.creator_id == 'new_creator_id'
    assert creator.creator_name == 'new_creator_name'
    assert created == True

    # Test retrieving existing content creator
    mock_yt_client.get_channel_meta.return_value = {'id': 'test_creator_id', 'snippet': {'customUrl': 'test_creator_name'}}
    (creator, created) = mock_content_service._get_or_create_content_creator('test_creator_id')
    assert creator.creator_name == mock_content_creator.creator_name
    assert created == False

def test__get_or_create_content(mock_yt_client, mock_sb_client, mock_raw_transcript, mock_content_creator, mock_content_service):
    mock_video_id = 'ABC123'
    # mock_raw_transcript = RawTranscriptStruct(chapters=[], transcripts=[])

    # mock_yt_client = MagicMock()
    mock_yt_client._get_yt_url_from_video_id.return_value = f'https://www.youtube.com/watch?v={mock_video_id}'
    mock_yt_client._get_video_snippet_by_id.return_value = {
        'title': 'sample video title',
        'description': 'sample video description'
    }

    # mock_sb_client = MagicMock()

    creator = ContentCreator.objects.create(creator_id='XYZ', creator_name='test creator')

    service = ContentService(mock_yt_client, mock_sb_client)

    # create new content
    content = service._get_or_create_content(mock_video_id, creator, raw_content_json_blob=mock_raw_transcript)
    assert isinstance(content, ContentSource)
    assert content.url == f'https://www.youtube.com/watch?v={mock_video_id}'
    assert content.content_creator == creator
    assert content.content_title == 'sample video title'
    assert content.content_description == 'sample video description'
    assert content.raw_content_json_blob == mock_raw_transcript.dict()

    # retrieve existing content
    content2 = service._get_or_create_content(mock_video_id, creator, raw_content_json_blob=mock_raw_transcript)
    assert isinstance(content2, ContentSource)
    assert content2.id == content.id


def test__create_processed(mock_yt_client, mock_sb_client, mock_content_source, mock_content_processed):
    content_service = ContentService(mock_yt_client, mock_sb_client)

    # Test ContentProcessed creation with NORMAL_YT_TRANSCRIBE algorithm
    content_processed = content_service._create_processed(
        mock_content_source,
        process_mode=ContentProcessed.ProcessAlgoTypeChoice.NORMAL_YT_TRANSCRIBE,
        processed_content_json_blob=mock_content_processed.processed_content_json_blob['data'],
        number_of_speaker=1
    )

    assert isinstance(content_processed, ContentProcessed)
    assert content_processed.processing_algo_type == ContentProcessed.ProcessAlgoTypeChoice.NORMAL_YT_TRANSCRIBE
    assert content_processed.number_of_speaker == 1
    assert content_processed.state == ContentProcessed.ProcessStateChoice.READY_TO_CHUNK

    # Test ContentProcessed creation with SPEAKER_TRANSCRIBE algorithm
    content_processed = content_service._create_processed(
        mock_content_source,
        process_mode=ContentProcessed.ProcessAlgoTypeChoice.SPEAKER_TRANSCRIBE,
        processed_content_json_blob=mock_content_processed.processed_content_json_blob['data'],
        number_of_speaker=2
    )

    assert isinstance(content_processed, ContentProcessed)
    assert content_processed.processing_algo_type == ContentProcessed.ProcessAlgoTypeChoice.SPEAKER_TRANSCRIBE
    assert content_processed.number_of_speaker == 2
    assert content_processed.state == ContentProcessed.ProcessStateChoice.WAV_JOB_STARTED


def test_chunk_yt_processed(mock_content_processed, mock_content_yt_chunk):
    assert not mock_content_processed.is_chunked
    assert mock_content_processed.state == ContentProcessed.ProcessStateChoice.READY_TO_CHUNK

    chunks = ContentService.chunk_yt_processed(mock_content_processed)

    assert mock_content_processed.is_chunked
    assert mock_content_processed.state == ContentProcessed.ProcessStateChoice.COMPLETED
    assert len(chunks) == 1
    assert isinstance(chunks[0], ContentYtChunk)
    assert chunks[0].content_processed == mock_content_processed
    assert chunks[0].transcript_start_time == 0
    assert chunks[0].content_chunk_title == "Test Chapter 1"
    assert chunks[0].content_chunk_text == ""
    assert chunks[0].content_segments_json == {
        'type': 'rttm',
        'chapter_segments':[
            {'start_time': 0, 'end_time': 10, 'speaker': 'SPEAKER_1', 'text': 'Hello world!'}
        ]}

from unittest.mock import MagicMock, patch

@patch('aininjas.contents.tasks.task_queue_and_extract_yt_audio')
def test_run_yt_url_to_chunks(
    mock_task_queue_and_extract_yt_audio, mock_content_service,
    mock_content_creator, mock_content_source, mock_content_processed,
    mock_content_yt_chunk
    ):
    mock_task_queue_and_extract_yt_audio = MagicMock()
    url = 'https://www.youtube.com/watch?v=abcdefghijk'
    podcast_type = 'MONO'
    mock_content_service.yt_client._parse_yt_video_id_from_url.return_value = 'abcdefghijk'
    mock_content_service.yt_client._get_video_snippet_by_id.return_value = {
        'channelId': 'lmnopqrstuvwxyz',
        'title': 'Test Video',
        'description': 'This is a test video.',
    }
    mock_content_service.yt_client._get_chapters_and_raw_transcript.return_value = (
        [{'id': 'chapter1', 'start': '0.0', 'title': 'Chapter 1'}, {'id': 'chapter2', 'start': '600.0', 'title': 'Chapter 2'}],
        [{'start': 0, 'end': 10, 'speaker': 'SPEAKER_1', 'text': 'This is the transcript for chapter 1.'},
         {'start': 600, 'end': 610, 'speaker': 'SPEAKER_1', 'text': 'This is the transcript for chapter 2.'}],
        "raw_transcript"
    )
    mock_content_service.yt_client._format_rttm_transcript_into_chapters.return_value = [
        {
            'chapter_start': 0.0,
            'chapter_title': 'Chapter 1',
            'chapter_segments': [
                {
                    'speaker': 'SPEAKER_1',
                    'start': 0,
                    'end': 10,
                    'text': 'This is the transcript for chapter 1.'
                }
            ]
        },
        {
            'chapter_start': 600.0,
            'chapter_title': 'Chapter 2',
            'chapter_segments': [
                {
                    'speaker': 'SPEAKER_1',
                    'start': 600,
                    'end': 610,
                    'text': 'This is the transcript for chapter 2.'
                }
            ]
        }
    ]
    mock_content_service._get_or_create_content_creator = MagicMock(return_value=(mock_content_creator, True))
    mock_content_service._get_or_create_content = MagicMock(return_value=mock_content_source)
    mock_content_service._create_processed = MagicMock(return_value=mock_content_processed)
    mock_content_service.chunk_yt_processed =  MagicMock(return_value=[mock_content_yt_chunk])

    result = mock_content_service.run_yt_url_to_chunks(url, podcast_type)

    assert isinstance(result, dict)
    assert 'content' in result
    assert 'processed' in result
    assert 'chunks' in result
    assert mock_task_queue_and_extract_yt_audio.called_once_with(result['processed'].id, result['content'].url)



## ========================
## === PROMPT SERVICE TEST
from aininjas.contents.models import SbUserProfile, PromptCompletionExecutionHistory, UserPromptRunVersion, Prompt, ContentYtChunk
from aininjas.contents.services import PromptService, PromptExecTupleStruct
from libs.openai_sdk import OpenaiSdk
from typing import List
from aininjas.sbusers.tests.factory import SbUserProfileFactory
from aininjas.contents.tests.factory import (ContentCreatorFactory, ContentSourceFactory, ContentProcessedFactory,
                                            ContentYtChunkFactory, PromptFactory, PromptCompletionFactory,
                                            UserPromptRunVersionFactory, PromptCompletionExecutionHistoryFactory,
                                            UserDefaultPromptFactory)

class MockOpenaiResponse:
    def __init__(self, text):
        self.choices = [MagicMock(text=text)]


@pytest.fixture
def prompt_service():
    return PromptService("api_key")


def test_init_no_key():
    with pytest.raises(Exception):
        PromptService(None)




def test_run_chatgpt_prompt(prompt_service):
    with patch.object(OpenaiSdk, "run", return_value=["Hello world!"]):
        result = prompt_service.run_chatgpt_prompt("Hello?")
        assert result == "Hello world!"


# def test_user_run_prompt(prompt_service):

#     p1 = Prompt(prompt="Prompt 1")
#     prompts_execs: List[PromptExecTupleStruct] = [
#         ("Prompt 1", Prompt.objects.create(
#             prompt="Prompt 1"
#             ), ContentYtChunk.objects.create(chunk_title="Test Chapter 1", chunk_text="")),
#         ("Prompt 2", Prompt.objects.create(
#             prompt="Prompt 2"
#             ), ContentYtChunk.objects.create(chunk_title="Test Chapter 1", chunk_text="")),
#     ]

#     with patch.object(prompt_service, "_execute_prompt_and_save", return_value=[("Completion 1", prompts_execs[0]), ("Completion 2", prompts_execs[1])]), \
#          patch.object(PromptCompletionExecutionHistory.objects, "bulk_create"), \
#          patch.object(UserPromptRunVersion.objects, "create") as mock_create:
#         mock_run_version = MagicMock()
#         mock_create.return_value = mock_run_version
#         result = prompt_service.user_run_prompt(SbUserProfile(), ContentProcessed(), prompts_execs)
#         assert len(result) == 2
#         assert mock_create.call_count == 1
#         assert PromptCompletionExecutionHistory.objects.bulk_create.call_count == 1
#         assert mock_run_version.save.call_count == 1


# def test_execute_prompt_and_save(prompt_service):
#     # class SbUserProfile:
#     #     pass

#     # class PromptExecTupleStruct(BaseModel):
#     #     prompt_text: str
#     #     prompt: str
#     #     content_chunk: str

#     prompts_execs: List[PromptExecTupleStruct] = [
#         ("Prompt 1", Prompt(
#             prompt="Prompt 1"
#             ), ContentYtChunk(content_chunk_title="Test Chapter 1", content_chunk_text="")),
#         ("Prompt 2", Prompt(
#             prompt="Prompt 2"
#             ), ContentYtChunk(content_chunk_title="Test Chapter 1", content_chunk_text="")),
#     ]

#     with patch.object(OpenaiSdk, "run", return_value=["Completion 1", "Completion 2"]):
#         result = prompt_service._execute_prompt_and_save(SbUserProfile(), prompts_execs)
#         assert len(result) == 2
#         assert result[0][0].output_completion == "Completion 1"
#         assert result[1][0].output_completion == "Completion 2"


import pytest
from unittest.mock import MagicMock
# from your_module import PromptService, SbUserProfile, PromptExecTupleStruct, PromptCompletion

# @pytest.fixture
# def mock_openai_sdk_run(monkeypatch):
#     def mock_run(prompts):
#         return ["result1"]

#     monkeypatch.setattr("libs.openai_sdk.OpenaiSdk.run", mock_run)


@pytest.fixture
def prompt_service():
    api_key = "your_api_key"
    prompt_service = PromptService(api_key)
    return prompt_service

# @pytest.fixture
# def sb_user():
#     return SbUserProfile()
@pytest.fixture
def sb_user():
    sb_user = SbUserProfileFactory.build()
    sb_user.save()
    return sb_user

@pytest.fixture
def prompts_execs(mock_content_processed):
    prompts_execs: List[PromptExecTupleStruct] = [
        ("Prompt 1", Prompt.objects.create(
            prompt="Prompt 1"
            ), ContentYtChunk.objects.create(
                content_processed=mock_content_processed,
                transcript_start_time=0,
                content_chunk_title="Test Chapter 1",
                content_chunk_text="")),
        ("Prompt 2", Prompt.objects.create(
            prompt="Prompt 2"
            ), ContentYtChunk.objects.create(
                content_processed=mock_content_processed,
                transcript_start_time=10,
                content_chunk_title="Test Chapter 2",
                content_chunk_text="")),
    ]

    return prompts_execs


def test_execute_prompt_and_save(prompt_service, sb_user, prompts_execs):
    with patch.object(OpenaiSdk, "run", return_value=["Prompt0 result", "Prompt1 result"]):
        results = prompt_service._execute_prompt_and_save(sb_user, prompts_execs)

        assert len(results) == len(prompts_execs)

        for i, result in enumerate(results):
            prompt_completion, prompt_exec = result
            assert prompt_completion.prompt_text == prompt_exec[0]
            assert prompt_completion.prompt == prompt_exec[1]
            assert prompt_completion.output_completion.strip() == f"Prompt{i} result"
            assert prompt_completion.completion_state == PromptCompletion.CompletionStateChoice.COMPLETED
            assert prompt_completion.sb_user == sb_user



# import pytest
from django.test import TestCase
from typing import Tuple
# from django.contrib.auth.models import User
# from unittest.mock import MagicMock

# from .models import SbUserProfile, ContentProcessed, PromptExecTupleStruct, UserPromptRunVersion, PromptCompletionExecutionHistory
# from .libs.openai_sdk import OpenaiSdk
# from .scripts.libs.yt_transcript_client import YtClient
# from .prompt_service import PromptService

class TestPromptService(TestCase):

    def setUp(self):
        # self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.sb_user = SbUserProfileFactory.create()
        self.creator = ContentCreatorFactory.create()
        self.source = ContentSourceFactory.create(content_creator=self.creator)
        self.processed = ContentProcessedFactory.create(content=self.source)
        # ContentProcessed.objects.create(
        #     sb_user=self.sb_user,
        #     original_content="Test content",
        #     content_type="text"
        # )
        self.prompt_execs: List[PromptExecTupleStruct] = [
        ("Prompt 1", PromptFactory.create(
            prompt="Prompt 1"
            ), ContentYtChunkFactory.create(
                content_processed=self.processed,
                transcript_start_time=0,
                content_chunk_title="Test Chapter 1",
                content_chunk_text="")),
        ("Prompt 2", PromptFactory.create(
            prompt="Prompt 2"
            ), ContentYtChunkFactory.create(
                content_processed=self.processed,
                transcript_start_time=10,
                content_chunk_title="Test Chapter 2",
                content_chunk_text="")),
    ]

        self.api_key = "your_openai_api_key"
        self.prompt_service = PromptService(self.api_key)

    @patch("aininjas.contents.services.PromptService._execute_prompt_and_save")
    def test_user_run_prompt(self, _execute_prompt_and_save_mock):
        # Mock OpenaiSdk run method
        # self.prompt_service.openai_sdk.run = MagicMock(return_value=[
        #     {'id': 'test_result_1', 'choices': [{'text': 'Test result text 1'}]},
        #     {'id': 'test_result_2', 'choices': [{'text': 'Test result text 2'}]}
        # ])
        # List[Tuple[PromptCompletion, PromptExecTupleStruct]]
        result_list: List[Tuple[PromptCompletion, PromptExecTupleStruct]] = []
        for i, exec_tuple in enumerate(self.prompt_execs):
            prompt_completion = PromptCompletionFactory.create(
                prompt_text=exec_tuple[0],
                prompt=exec_tuple[1],
                output_completion=f"Test result text {i}"
            )
            result_list.append((prompt_completion, exec_tuple))

        _execute_prompt_and_save_mock.return_value = result_list
        result = self.prompt_service.user_run_prompt(
            self.sb_user,
            self.processed,
            self.prompt_execs,
            run_strategy_type=UserPromptRunVersion.PromptRunTypeChoice.YT_CHUNK_SUMMARIZE
            )
        _execute_prompt_and_save_mock.assert_called_once_with(
            self.sb_user,
            self.prompt_execs,
        )
        assert isinstance(result, PromptExecResult)
        assert isinstance(result.run_version, UserPromptRunVersion)
        assert len(result.histories) == 2

        for history in result.histories:
            assert isinstance(history, PromptCompletionExecutionHistory)
            assert history.user_processed_prompt_version == result.run_version
            assert history.source_content_processed == self.processed

        # Check if the run method was called with the correct arguments
        # self.prompt_service.openai_sdk.run.assert_called_with([exec_tuple.prompt_text for exec_tuple in self.prompt_execs])
