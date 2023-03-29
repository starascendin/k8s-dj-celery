
# import pytest
from libs.supabase_client import SupabaseClient
import pytest
import io
from unittest.mock import MagicMock, patch
from supabase.client import create_client, Client, ClientOptions
from supabase.lib.storage_client import SyncBucketProxy

def test_download_transcript_from_bucket(monkeypatch):
    # create mock object for storage
    storage_mock = MagicMock()
    # bucket_mock = MagicMock()
    # storage_mock.from_.return_value = bucket_mock
    # create mock object for client
    client_mock = MagicMock(spec=Client)
    client_mock.storage.return_value = storage_mock

    # replace create_client with a mock
    monkeypatch.setattr('supabase.client.create_client', MagicMock(return_value=client_mock))

    # create mock response for storage.from_.download
    file = io.BytesIO(b'some binary data')
    response_mock = MagicMock(content=file.getvalue(), status_code=200)

    # setup storage_mock
    storage_mock.from_.return_value.download.return_value = response_mock

    # create an instance of SupabaseClient
    supabase_client = SupabaseClient('https://test.com', 'test_key')

    # call the download_transcript_from_bucket method
    result = supabase_client.download_transcript_from_bucket('test_file')

    # # assert that storage.from_().download was called with correct parameters
    # storage_mock.from_.return_value.download.assert_called_once_with('yt_wavs/test_file')

    # assert that the result is what we expect
    assert result[0] == '/tmp/test_file'
    assert result[1] == response_mock


def test_download_transcript_from_bucket_exception(monkeypatch):
    # create mock object for storage
    storage_mock = MagicMock()

    # create mock object for client
    client_mock = MagicMock(spec=Client)
    client_mock.storage.return_value = storage_mock

    # replace create_client with a mock
    monkeypatch.setattr('supabase.client.create_client', MagicMock(return_value=client_mock))

    # setup storage_mock to raise an exception
    storage_mock.from_.return_value.download.side_effect = Exception('test exception')

    # create an instance of SupabaseClient
    supabase_client = SupabaseClient('https://test.com', 'test_key')

    # call the download_transcript_from_bucket method
    result = supabase_client.download_transcript_from_bucket('test_file')

    # assert that the result is what we expect
    assert result[0] == '/tmp/test_file'
    assert str(result[1]) == 'test exception'
