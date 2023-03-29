# import asyncio
import asyncio
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
# from scripts.libs.get_chapter_strategy import GetChapterByTimestampStrategy
from collections import OrderedDict
from pyyoutube import Api
from typing import List, Union
from pydantic import BaseModel
import re
from collections import defaultdict
from pydantic import BaseModel
from scripts.libs.custom_yt_api import YouTubeAPI, VideoListResponse
import httpx
import json
import logging
import os
from abc import ABC, abstractmethod


LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

logger = logging.getLogger(__name__)

class YtChapterStruct(BaseModel):
    title: str
    time: int

    class Config:
        extra = 'forbid'

class YtRawTranscriptStruct(BaseModel):
    start: int
    duration: int
    text: str

    class Config:
        extra = 'forbid'


# this is stored in Processed.processed_content_json under Chapter_segments
class RTTMTranscriptstruct(BaseModel):
    speaker: str
    start: int
    duration: int
    text: str

    class Config:
        extra = 'forbid'


# This is Processed.processed_content_json['data']
class TranscriptChapterStruct(BaseModel):
    chapter_start: int
    chapter_title: str
    # chapter_segments: list  # TODO: should be list[RTTMTranscriptstruct]
    chapter_segments: list[RTTMTranscriptstruct]

    class Config:
        extra = 'forbid'



class GetChapterStrategy(ABC):
    @abstractmethod
    def get_chapters(self)  -> List[YtChapterStruct]:
        pass



class GetChapterByTimestampStrategy(GetChapterStrategy):
    def get_chapters(self, time_segment_by_sec, end_timestamp) -> List[YtChapterStruct]:
        ctr_seconds: int = 0
        ctr = 0
        chapters = []
        while True:
            if ctr_seconds > end_timestamp:
                break
            chapters.append(YtChapterStruct(
                title=f'PLACEHOLDER_CHAPTER_{ctr}',
                time=ctr_seconds
            ))
            ctr_seconds+=time_segment_by_sec
            ctr += 1
        return chapters

import tiktoken
import snoop
# use langchain token helpers
class GetChapterByTokenSizeStrategy(GetChapterStrategy):
    def _get_token_length(self, text: str) -> int:
        enc = tiktoken.get_encoding("gpt2")
        token_length = len(enc.encode(
            text,
            allowed_special=set(),
            disallowed_special="all",
        ))
        return token_length
    
    def get_chapters(self, rttm_transcripts: List[RTTMTranscriptstruct], token_size=2000 ) -> List[YtChapterStruct]:
        chapters = []
        i, j = 0, 0  # Initialize two pointers
        current_chapter = {'start_time': None, 'text': ''}
        curr_chapter = YtChapterStruct(time=0, title="")
        accu_token = 0
        raw_transcripts = rttm_transcripts
        chapter_ctr = 0
        while i < len(raw_transcripts):
            # Update current chapter with new transcript
            text_i = raw_transcripts[i].text.strip()
            text_i_tokens = self._get_token_length(text_i)
            if accu_token + text_i_tokens <= token_size:
                # current_chapter['text'] += ' ' + text_i if current_chapter['text'] else text_i
                accu_token += text_i_tokens
                # print("#accu_token + text_i_tokens <= token_size. accu_token, text_i_tokens", accu_token, text_i_tokens)
            else:
                # Chapter is complete, add to output
                # current_chapter['start_time'] = raw_transcripts[j].start
                print("#Appending accu_token, text_i_tokens", accu_token, text_i_tokens)
                chapters.append(YtChapterStruct(
                    title=f"PLACEHOLDER_CHAPTER_{chapter_ctr}",
                    time=raw_transcripts[j].start
                ))
                
                # Move j pointer to next starting point
                j = i
                chapter_ctr += 1
                accu_token = text_i_tokens
                # current_chapter = {'start_time': None, 'text': ''}
            i += 1
        
        # adding in last chapter
        chapters.append(YtChapterStruct(
            title=f"PLACEHOLDER_CHAPTER_{chapter_ctr}",
            time=raw_transcripts[j].start
        ))
        
        return chapters
            

class YtClient():
    def __init__(self, api_key):
        self.chapters = []
        self.json_transcript = []

        self.YtApi = Api(api_key=api_key)
        self.yt_api = YouTubeAPI(api_key=api_key)
        self.cache_video_ids_meta = {}

    @staticmethod
    def _get_yt_url_from_video_id(video_id):
        return f"https://www.youtube.com/watch?v={video_id}"

    @staticmethod
    def _parse_yt_video_id_from_url(url):
        return url.split('=')[1]

    def get_channel_meta(self, channel_id):
        response = self.YtApi.get_channel_info(channel_id=channel_id)
        # print(response.items)
        resp = response.items[0].to_dict()  # type: ignore
        meta = resp
        return meta


    def _get_video_id(self, video_id):
        return self.YtApi.get_video_by_id(video_id=video_id)


    # TODO: BL: need to account for NO-CHAPTERS
    def _get_video_snippet_by_id(self, video_id):
        rsp = self._get_video_id(video_id).items[0].to_dict() # type: ignore
        return rsp.get('snippet')

    def _get_video_content_details_by_id(self, video_id):
        rsp = self._get_video_id(video_id).items[0].to_dict() # type: ignore
        return rsp.get('contentDetails')

    def _get_chapters_and_raw_transcript(self, video_id):
        """
        This takes a YT url, get its chapters (if any) and raw transcript
        """
        url = self._get_yt_url_from_video_id(video_id)
        chapters: List[YtChapterStruct] = self._get_chapters_for_video_url(url)
        
        raw_transcript = self._get_yt_transcript(video_id)
        rttm_transcript: List[RTTMTranscriptstruct] = self._convert_yt_transcripts_to_rttm_mono(raw_transcript)
        return (chapters, rttm_transcript, raw_transcript)


    def _get_chapters_for_video_url(self, video_url) -> List[YtChapterStruct]:
        # can use this https://yt.lemnoslife.com/videos?part=chapters&id=vmt1Li1Rnes
        # better_yt_api = "https://yt.lemnoslife.com/videos?id=YT_ID&part=contentDetails,chapters"
        yt_id = self._parse_yt_video_id_from_url(video_url)
        # url = better_yt_api.replace('YT_ID', yt_id)
        yt_api = YouTubeAPI(yt_id)
        # if no chapters, should create 1 chapter for the whole video
        results: VideoListResponse = yt_api.get_video_chapters_data(yt_id)
        self.cache_video_ids_meta[yt_id] = results
        
        chapters = []
        
        for video in results.items:
            # should just have 1 video
            #video.contentDetails.duration

            for chapter in video.chapters.chapters:
                chapters.append(YtChapterStruct(**{
                    'title': chapter.title,
                    'time': chapter.time,
                }))
            if len(chapters) == 0:
                # chapters.insert(0, YtChapterStruct(**{
                #     'title': 'NO_CHAPTERS',
                #     'time': 0,
                # }))
                return []
        # print("#DEBUG chapters", chapters)
        if chapters[0].dict()['time'] != 0:
            chapters.insert(0, YtChapterStruct(**{
                'title': 'INTRO',
                'time': 0,
            }))
        return chapters


    def _get_yt_transcript(self, video_id) -> List[YtRawTranscriptStruct]:
        ts = YouTubeTranscriptApi.get_transcript(video_id)
        return [YtRawTranscriptStruct(**t) for t in ts]

    def _convert_yt_transcripts_to_rttm_mono(self, list_transcripts: List[YtRawTranscriptStruct]):
        """
        For mono speaker
        columns are the fields:
        (Speaker) (Start Time) (Duration) (text)
        """
        converted = [RTTMTranscriptstruct(**{
            **t.dict(),
            'speaker': 'SPEAKER_1',
            }) for t in list_transcripts]
        return converted        

    def _generate_chapters_strategy(self, strategy, transcripts: List[RTTMTranscriptstruct]=None) -> List[YtChapterStruct]:
        if strategy == 'NO_CHAPTERS':
            return []
        elif strategy == "NAIVE_BY_FIXED_TIME":
            last_chapter = transcripts[-1]
            end_timestamp = last_chapter.start + last_chapter.duration
            return GetChapterByTimestampStrategy().get_chapters(120, end_timestamp) # 60 x 2 min
        elif strategy == "NAIVE_BY_TOKEN_SIZE":
            return GetChapterByTokenSizeStrategy().get_chapters(transcripts)
        return  
        

    def _format_rttm_transcript_into_chapters(self, chapters: List[YtChapterStruct], rttm_transcripts: List[RTTMTranscriptstruct], video_id=None, podcast_type="MONO", vid_duration=None) -> list:
        """
        This takes a list of chapters and a list of rttm transcripts and merge them into chapters
        This should be a strategy pattern.

        NO CHAPTERS + MONO -> chunk it by token size
        """

        ### take json_formatted and transform into an ordereddict with time as key and chapter as value
        od = OrderedDict()
        video_duration = vid_duration or self._get_video_content_details_by_id(video_id)['duration'] # type: ignore
        # PT1H23M16S
        video_duration = self.convert_duration_to_seconds(video_duration)
        len_chapters = len(chapters)
        # for chapter in chapters:
        for i in range(len_chapters):
            chapter = chapters[i].dict()
            j = i + 1 # seek ahead
            if i == len(chapters) - 1:
                chapters.append(YtChapterStruct(**{
                    'title': 'end',
                    'time': video_duration # this should be the end of the video, which is the entire duration
                }))
            next_chapter = chapters[j].dict()
            chapter_range = [chapter['time'], next_chapter['time']]
            chatpter_txt = ''
            chapter_segments = []
            
            if podcast_type == "MONO":
                # This assumes for 1 speaker and concat all transcript into 1 within a Chapter's ts range.
                for i in range(len(rttm_transcripts)):
                    rttm_transcript: RTTMTranscriptstruct = rttm_transcripts[i]

                    if rttm_transcript.start >= chapter_range[0] and rttm_transcript.start < chapter_range[1]:
                        
                        txt = re.sub(r"\[.*?\]", "", rttm_transcript.text)
                        chatpter_txt += f'({rttm_transcript.start}s)-{txt} '
                # Combine all mono speaker fragments into 1
                segment_struct: RTTMTranscriptstruct = RTTMTranscriptstruct(
                        speaker='SPEAKER_1',
                        start=chapter['time'],
                        duration=next_chapter['time'] - chapter['time'],
                        text=chatpter_txt
                    )

                chapter_segments.append(segment_struct.dict())
            else:
                for i in range(len(rttm_transcripts)):
                    rttm_transcript: RTTMTranscriptstruct = rttm_transcripts[i]
                    # if theres a continuous speaker
                    if rttm_transcript.start >= chapter_range[0] and rttm_transcript.start < chapter_range[1]:
                        chapter_segments.append(rttm_transcript.dict())


            od[chapter['time']] = TranscriptChapterStruct(**{
                'chapter_start': int(chapter['time']),
                'chapter_title': chapter['title'],
                'chapter_segments': chapter_segments
                })

        chapters.pop()

        # list_transcripts = list(od.items())
        list_transcripts = [item.dict() for item in od.values()]
        return list_transcripts


    def convert_duration_to_seconds(self, duration):
        parts = re.findall(r'(\d+)([MHS])', duration)
        total_seconds = 0
        for part, unit in parts:
            part = int(part)
            if unit == 'H':
                total_seconds += part * 3600
            elif unit == 'M':
                total_seconds += part * 60
            else:
                total_seconds += part
        return total_seconds

def convert_time_to_seconds(time_str):
    d = datetime.strptime(time_str, "%H:%M:%S")
    return int((d - datetime(1900, 1, 1)).total_seconds())



# TODO: save raw transcript, full text transcripot, and chaptered transcript

if __name__ == '__main__':
    client = YtClient(api_key='AIzaSyDLTKG_yxJypSuv5KvM4yq0rOfuP0DCkPY')
    video_id = "v0bMOgojSus"
    video_snippet = client._get_video_snippet_by_id(video_id)
    channel_id = video_snippet.get('channelId')
    channel_meta =client.get_channel_meta(channel_id)
    (chapters, transcripts, raw_transcripts) = client._get_chapters_and_raw_transcript(video_id)
    processed_transcript = client._format_rttm_transcript_into_chapters(chapters, transcripts, video_id=video_id)

    # print("#chapters, transcripts", chapters, transcripts)
    # print("#processed_transcript", processed_transcript)

    # print(channel_meta)
    # duration = "PT1H11M1S"
    # seconds = client.convert_duration_to_seconds(duration)
    # print(seconds)

