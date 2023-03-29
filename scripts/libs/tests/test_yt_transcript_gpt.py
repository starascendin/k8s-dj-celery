import unittest
from typing import List
from scripts.libs.yt_transcript_client import YtClient, YtChapterStruct
import asyncio

class TestYtClient(unittest.TestCase):
    def setUp(self):
        self.client = YtClient(api_key='AIzaSyDLTKG_yxJypSuv5KvM4yq0rOfuP0DCkPY')

        # Lex Hub: https://www.youtube.com/watch?v=NpK-Fg0TG_4
        # 6 chapters
        self.yt_id = "NpK-Fg0TG_4"

    def test_get_channel_meta(self):
        meta = self.client.get_channel_meta('UCJIfeSCssxSC_Dhc5s7woww')
        self.assertEqual(meta['snippet']['title'], 'Lex Clips')

    def test_convert_duration_to_seconds(self):
        duration = 'PT1H23M16S'
        seconds = self.client.convert_duration_to_seconds(duration)
        self.assertEqual(seconds, 4996)

    def test_format_rttm_transcript_into_chapters(self):
        video_id = self.yt_id
        chapters, rttm_transcripts = self.client._get_chapters_and_raw_transcript(video_id)
        formatted_transcript = self.client._format_rttm_transcript_into_chapters(chapters, rttm_transcripts, video_id=video_id)
        self.assertEqual(len(formatted_transcript), len(chapters))


    def test_get_chapters_for_video_url(self):
        url = f'https://www.youtube.com/watch?v={self.yt_id}'
        chapters: List[YtChapterStruct] = self.client._get_chapters_for_video_url(url)
        self.assertEqual(len(chapters), 6)
        self.assertEqual(chapters[0].title, 'Intro')
        self.assertEqual(chapters[0].time, 0)
        self.assertEqual(chapters[1].title, 'Priority')
        self.assertEqual(chapters[1].time, 20)
        self.assertEqual(chapters[2].title, 'Decision')
        self.assertEqual(chapters[2].time, 40)

if __name__ == '__main__':
    unittest.main()
