# write tests for services here

import pytest
from unittest.mock import MagicMock
from aininjas.contents.services import ContentService, RawTranscriptStruct
from aininjas.contents.models import ContentSource, ContentProcessed, ContentCreator
import uuid

from scripts.libs.yt_transcript_client import YtClient
from libs.supabase_client import SupabaseClient
from pydantic.error_wrappers import ValidationError
pytestmark = pytest.mark.django_db

yt_client = MagicMock()
content = MagicMock()

def test_yt_processed_struct():
    yt_processed_struct = RawTranscriptStruct(**{
        'chapters': [
            { 'title': 'chapter1', 'time': 0 },
            {'title': 'chapter2', 'time': 3}
            ],
        'transcripts': [{'text': 'text1', 'start': 0, 'duration': 2}, {'text': 'text2', 'start': 4, 'duration': 5}]
    })
    assert 1 == 1
    assert yt_processed_struct.chapters == [
            { 'title': 'chapter1', 'time': 0 },
            {'title': 'chapter2', 'time': 3}
            ]
    assert yt_processed_struct.transcripts == [{'text': 'text1', 'start': 0, 'duration': 2}, {'text': 'text2', 'start': 4, 'duration': 5}]
    # correct struct will not raise error and fail this pytest
    # extra or missing will throw error
    with pytest.raises(ValidationError):
        RawTranscriptStruct(**{
        'chapters': [
            { 'title': 'chapter1', 'time': 0 },
            {'title': 'chapter2', 'time': 3}
            ],
        'transcripts': [{'text': 'text1', 'start': 0, 'duration': 2}, {'text': 'text2', 'start': 4, 'duration': 5}],
        'extra': 'extra'
    })



def test_create_processed():
    sb = SupabaseClient("http://localhost:54321", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU")
    content_service = ContentService(yt_client, sb)
    creator = ContentCreator.objects.create(id=uuid.uuid4())
    content = ContentSource.objects.create(id=uuid.uuid4(), content_creator=creator)
    content_service._create_processed(
        content=content,
        process_mode=ContentProcessed.ProcessAlgoTypeChoice.NORMAL_YT_TRANSCRIBE,
        # process_mode=ContentProcessed.ProcessAlgoTypeChoice.SPEAKER_TRANSCRIBE
    )
    assert 1 == 1


from unittest.mock import Mock
from typing import List
from aininjas.contents.models import ContentYtChunk, PromptCompletion, Prompt, OpenaiSdk
from ..services import PromptExecTupleStruct


def test_apply_prompts_to_chunks():
    # Set up test data
    content_chunks = [
        ContentYtChunk(
            content_chunk_title="Test chunk",
            content_segments_json={
                "type": "test",
                "chapter_segments": [
                    {"speaker": "Alice", "text": "Hello world."},
                    {"speaker": "Bob", "text": "Goodbye world."},
                ],
            },
        ),
    ]

    default_prompt = Mock()
    default_prompt.prompt = "Test prompt <%_INSERT_CONTEXT_%>"
    default_prompt.exec_type = "DEFAULT_CHUNK_SUMMARIZE"

    Prompt.objects.filter.return_value = [default_prompt]

    prompt_completion = Mock()
    prompt_completion.exists.return_value = False
    PromptCompletion.objects.filter.return_value = prompt_completion

    openai_sdk = Mock()
    openai_sdk.estimate_tokens.return_value = 10
    openai_sdk.target_prompt_tokens = 5
    openai_sdk.run.return_value = ["Test completion"]

    # Run the method being tested
    prompt_completions_created = PromptExecTupleStruct(prompt_service=Mock(openai_sdk=openai_sdk))._apply_prompts_to_chunks(content_chunks)

    # Check that the prompt completions were created
    assert len(prompt_completions_created) == 1
    assert prompt_completions_created[0].prompt_text == "Test prompt TITLE: Test chunk\nTranscripts: Alice: Hello world. \nBob: Goodbye world. \n"
    assert prompt_completions_created[0].output_completion == "Test completion"
