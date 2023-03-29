import unittest

from scripts.libs.custom_yt_api import YouTubeAPI


class TestYouTubeAPI(unittest.TestCase):
    API_KEY = "your_api_key_here"
    VIDEO_ID = "NpK-Fg0TG_4"

    def setUp(self):
        self.api = YouTubeAPI(api_key=self.API_KEY)

    def test_get_video_data(self):
        video_data = self.api.get_video_chapters_data(video_id=self.VIDEO_ID)
        self.assertEqual(video_data.kind, "youtube#videoListResponse")
        self.assertIsNotNone(video_data.etag)
        self.assertIsInstance(video_data.items, list)
        self.assertGreater(len(video_data.items), 0)
        video = video_data.items[0]
        self.assertEqual(video.kind, "youtube#video")
        self.assertIsNotNone(video.etag)
        self.assertEqual(video.id, self.VIDEO_ID)
        self.assertIsInstance(video.contentDetails, dict)
        self.assertIsInstance(video.chapters, dict)


if __name__ == "__main__":
    unittest.main()
