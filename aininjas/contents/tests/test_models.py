import pytest
from django.db import IntegrityError
from aininjas.contents.models import ContentCreator, ContentSource, ContentProcessed, ContentYtChunk, Prompt, PromptCompletion, UserPromptRunVersion

pytestmark = pytest.mark.django_db

@pytest.fixture
def content_creator_data():
    return {
        "creator_name": "test",
        "creator_id": "test123",
        "creator_url": "https://test.com",
        "profile_json_blob": {"test_key": "test_value"},
        "source_channel": "TWITTER",
    }

@pytest.fixture
def content_source_data(content_creator_data):
    return {
        "url": "https://test.com/video",
        "content_creator": ContentCreator.objects.create(**content_creator_data),
        "content_title": "Test Video",
        "content_description": "This is a test video",
        "content_categories": "GPT",
        "raw_content_json_blob": {"test_key": "test_value"},
        "param_json_blob": {"test_key": "test_value"},
        "speaker_type": "MONO",
        "number_of_speaker": 1,
        "speakers_blob": {"test_key": "test_value"}
    }
@pytest.fixture
def user_processed_prompt_version_data():
    return {
        "run_type": "YT_CHUNK_SUMMARIZE",
    }
@pytest.fixture
def content_processed_data(content_source_data):
    return {
        "content": ContentSource.objects.create(**content_source_data),
        "number_of_speaker": 1,
        "processing_algo_type": "NORMAL_YT_TRANSCRIBE",
        "processed_content_json_blob": {"test_key": "test_value"},
        "state": "COMPLETED",
        "state_artifact_blob": {"test_key": "test_value"},
        "is_chunked": False,
        "output_artifacts_url": "https://test.com/output",
        "time_to_process": {"test_key": "test_value"},
    }

@pytest.fixture
def content_yt_chunk_data(content_processed_data):
    return {
        "content_processed": ContentProcessed.objects.create(**content_processed_data),
        "transcript_start_time": 0,
        "content_chunk_title": "Test Chunk",
        "content_chunk_text": "This is a test chunk",
        "content_segments_json": {"test_key": "test_value"},
        "raw_data_json_blob": {"test_key": "test_value"},
    }

@pytest.fixture
def prompt_data():
    return {
        "name": "Test Prompt",
        "meta_json_blob": {"test_key": "test_value"},
        "prompt": "This is a test prompt",
        "categories": "SUMMARIZATION",
        "exec_type": "DEFAULT_CHUNK_SUMMARIZE"
    }

@pytest.fixture
def prompt_completion_data(content_yt_chunk_data, content_processed_data, prompt_data):
    return {
        "content_chunk": ContentYtChunk.objects.create(**content_yt_chunk_data),
        "content_processed": ContentProcessed.objects.create(**content_processed_data),
        "prompt": Prompt.objects.create(**prompt_data),
        "prompt_text": "This is a test prompt",
        "prompt_hashed": "abcd1234",
        "completion_state": "COMPLETED",
        "output_completion": "This is a test output",
    }

# @pytest.mark.django_db
@pytest.mark.django_db(databases=['default', 'auth_db'])
def test_create_content_source(content_source_data):
    source = ContentSource.objects.create(**content_source_data)
    assert source.url == content_source_data["url"]

@pytest.mark.django_db(databases=['default', 'auth_db'])
def test_create_duplicate_content_source(content_source_data):
    with pytest.raises(IntegrityError):
        ContentSource.objects.create(**content_source_data)
        ContentSource.objects.create(**content_source_data)

@pytest.mark.django_db(databases=['default', 'auth_db'])
def test_create_content_processed(content_processed_data):
    processed = ContentProcessed.objects.create(**content_processed_data)
    assert processed.state == content_processed_data["state"]

@pytest.mark.django_db(databases=['default', 'auth_db'])
def test_create_content_yt_chunk(content_yt_chunk_data):
    chunk = ContentYtChunk.objects.create(**content_yt_chunk_data)
    assert chunk.transcript_start_time == content_yt_chunk_data["transcript_start_time"]

@pytest.mark.django_db(databases=['default', 'auth_db'])
def test_create_prompt(prompt_data):
    prompt = Prompt.objects.create(**prompt_data)
    assert prompt.name == prompt_data["name"]

@pytest.mark.django_db(databases=['default', 'auth_db'])
def test_create_prompt_completion(prompt_completion_data):
    completion = PromptCompletion.objects.create(**prompt_completion_data)
    assert completion.completion_state == prompt_completion_data["completion_state"]

@pytest.mark.django_db
def test_create_user_processed_prompt_version(user_processed_prompt_version_data):
    version = UserPromptRunVersion.objects.create(**user_processed_prompt_version_data)
    assert version.run_type == user_processed_prompt_version_data["run_type"]
