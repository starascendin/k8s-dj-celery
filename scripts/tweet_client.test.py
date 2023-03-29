import unittest
from unittest.mock import MagicMock, patch
# from tweet_client import TwitterThread

class TestTwitterClient(unittest.TestCase):
    def setUp(self):
        self.consumer_key = 'your_consumer_key'
        self.consumer_secret = 'your_consumer_secret'
        self.access_token = 'your_access_token'
        self.access_token_secret = 'your_access_token_secret'
        self.thread_content = [{'content': 'This is the first tweet in my thread.'},
                               {'content': 'This is the second tweet in my thread.'},
                               {'content': 'This is the third tweet in my thread.'}]
        self.video_file = 'path/to/myvideo.mp4'

    @patch('tweepy.API')
    def test_create_thread(self, mock_api):
        # Create a mock API object
        mock_api_instance = mock_api.return_value

        # Create an instance of the TwitterThread class
        thread = TwitterThread(self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret)

        # Call the create_thread method and check that the expected API calls are made
        thread.create_thread(self.thread_content,self.video_file)
        mock_api_instance.update_status.assert_called()
        mock_api_instance.media_upload.assert_called_with(self.video_file)

    @patch('tweepy.API')
    def test_create_thread_without_video(self, mock_api):
        # Create a mock API object
        mock_api_instance = mock_api.return_value

        # Create an instance of the TwitterThread class
        thread = TwitterThread(self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret)

        # Call the create_thread method and check that the expected API calls are made
        thread.create_thread(self.thread_content)
        mock_api_instance.update_status.assert_called()
        mock_api_instance.media_upload.assert_not_
