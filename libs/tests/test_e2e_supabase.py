import unittest
import os
from libs.supabase_client import SupabaseClient

class TestSupabaseClient(unittest.TestCase):

    def setUp(self):
        # Set up the Supabase client with your Supabase URL and API key
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        self.supabase_client = SupabaseClient(url, key)

    def test_download_transcript_from_bucket(self):
        # Download an audio file from your Supabase storage bucket and check that the file exists
        filename = "example_audio.mp3"
        file_dir = "/tmp"
        bucket_name = "yt-extracts"
        folder_name = "yt_wavs"
        filepath, response = self.supabase_client.download_transcript_from_bucket(filename, file_dir, bucket_name, folder_name)
        self.assertTrue(os.path.isfile(filepath))

    def test_upload_audio_to_bucket(self):
        # Upload an audio file to your Supabase storage bucket and check that the file exists in the bucket
        file_dir = "/tmp"
        filename = "example_audio.mp3"
        folder_name = "yt_wavs"
        bucket_name = "yt-extracts"
        filepath = f"{file_dir}/{filename}"
        with open(filepath, "wb") as f:
            f.write(b"example audio file content")
        response = self.supabase_client.upload_audio_to_bucket(file_dir, filename, folder_name, bucket_name)
        self.assertEqual(response[1].status_code, 200)

    def tearDown(self):
        # Clean up the test files and remove them from the bucket
        filename = "example_audio.mp3"
        file_dir = "/tmp"
        bucket_name = "yt-extracts"
        folder_name = "yt_wavs"
        filepath = f"{file_dir}/{filename}"
        os.remove(filepath)
        storage = self.supabase_client.client.storage()
        storage.from_(bucket_name).remove(f"{folder_name}/{filename}")
