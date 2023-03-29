
# write tests for yt_transcript_client here


import pytest

from scripts.libs.yt_transcript_client import YtClient, YtRawTranscriptStruct, RTTMTranscriptstruct, YtChapterStruct
from youtube_transcript_api import YouTubeTranscriptApi

test_video_id = 't_vTe8pFL3M'


def test_get_yt_url_from_video_id():
    client = YtClient(api_key='AIzaSyDLTKG_yxJypSuv5KvM4yq0rOfuP0DCkPY')
    url = client._get_yt_url_from_video_id(test_video_id)
    assert url == f'https://www.youtube.com/watch?v={test_video_id}'

# def test_get_video_profile_by_id():
#     client = YtClient(api_key='AIzaSyDLTKG_yxJypSuv5KvM4yq0rOfuP0DCkPY')
#     video_profile = client._get_video_profile_by_id(test_video_id)
#     # print('#video_profile ', video_profile)
#     assert video_profile['kind'] == 'youtube#video'


def test__parse_yt_video_id_from_url():
    video_id = YtClient._parse_yt_video_id_from_url(f'https://www.youtube.com/watch?v={test_video_id}')
    assert video_id == test_video_id


import pytest

def test_get_yt_transcript(mocker):
    client = YtClient(api_key='AIzaSyDLTKG_yxJypSuv5KvM4yq0rOfuP0DCkPY')

    mock_get_transcript = mocker.patch.object(YouTubeTranscriptApi, 'get_transcript')
    mock_get_transcript.return_value = [{'start': 0, 'duration': 1, 'text': 'Hello'},
                                        {'start': 1, 'duration': 2, 'text': 'world'}]

    # call the function to be tested
    t = client._get_yt_transcript("video_id")

    # assertions
    assert len(t) == 2
    assert isinstance(t[0], YtRawTranscriptStruct)
    assert t[0].start == 0
    assert t[0].duration == 1
    assert t[0].text == 'Hello'
    assert t[1].start == 1
    assert t[1].duration == 2
    assert t[1].text == 'world'
    mock_get_transcript.assert_called_with("video_id")

def test_convert_yt_transcripts_to_rttm_mono():
    client = YtClient(api_key='testss')

    list_transcripts = [
        YtRawTranscriptStruct(start=0, duration=1, text='Hello'),
        YtRawTranscriptStruct(start=1, duration=1, text='World'),
    ]
    converted = client._convert_yt_transcripts_to_rttm_mono(list_transcripts)

    assert len(converted) == 2
    assert converted[0].speaker == 'SPEAKER_1'
    assert converted[0].start == 0
    assert converted[0].duration == 1
    assert converted[0].text == 'Hello'
    assert converted[1].speaker == 'SPEAKER_1'
    assert converted[1].start == 1
    assert converted[1].duration == 1
    assert converted[1].text == 'World'



def test_format_transcript_into_chapters_1_speaker():
    api_key = 'test_api_key'
    client = YtClient(api_key)
    client.cache_video_ids_meta = {
        'test_video_id': {
            'contentDetails': {
                'duration': 'PT1M31S'
            }
        }
    }

    video_end = client.convert_duration_to_seconds(client.cache_video_ids_meta['test_video_id']['contentDetails']['duration'])
    assert video_end == 91
    chapters = [
        YtChapterStruct(title='Chapter 1', time=0),
        YtChapterStruct(title='Chapter 2', time=10)
    ]

    json_formatted_transcript = [
        YtRawTranscriptStruct(start=0, duration=2, text='text 1'),
        YtRawTranscriptStruct(start=2, duration=2, text='text 2'),
        YtRawTranscriptStruct(start=4, duration=2, text='text 3'),
        YtRawTranscriptStruct(start=10, duration=2, text='text 4'),
        YtRawTranscriptStruct(start=12, duration=(video_end - 4 * 2), text='text 5')
    ]
    rttm_transcripts = client._convert_yt_transcripts_to_rttm_mono(json_formatted_transcript)
    result = client._format_rttm_transcript_into_chapters(
        chapters=chapters,
        rttm_transcripts=rttm_transcripts,
        video_id='test_video_id',
        # numb_of_speaker=1
    )

    expected_result = [
        {
            'chapter_start': 0,
            'chapter_title': 'Chapter 1',
            'chapter_segments': [
                RTTMTranscriptstruct(**{
                    'speaker':'SPEAKER_1',
                    'start':0,
                    'duration':10,
                    'text':'text 1text 2text 3'
                }).dict()
            ]
        },
        {
            'chapter_start': 10,
            'chapter_title': 'Chapter 2',
            'chapter_segments': [
                RTTMTranscriptstruct(**{
                    'speaker': 'SPEAKER_1',
                    'start': 10,
                    'duration': 81,
                    'text': 'text 4text 5'
                }).dict()
            ]
        }
    ]

    assert result == expected_result
import pandas as pd
from datetime import datetime, timedelta


def test_format_rttm_transcript_into_chapters_multi_speaker():
    """
    This should load from a csv
    Start,End,Speaker,Text
    0:00:00,0:01:21,SPEAKER 1," Hi, I'm Dr. John D. Martini. I've been involved in the study of human behavior and personal development  for 47 years. I have the opportunity to travel all over the world, educating all different types of  people in all different walks of life. And very common that I get asked by people around the world  on what exactly is fear and how do we deal with it and is it a good thing? Is it a bad thing?  And the whole spectrum of responses are out there by different teachers. And it could be confusing.  Some say it's the very path of your destiny. If you conquer your fear, you'll be fulfilling your  soul's mission. Others say, no, you want to avoid all forms of fear. It's a sign to avoid things  and go off on the easy path. I've seen a whole spectrum of ideas about fear. So I'd like to clarify  it and put it into context. Because in some contexts, all of them are accurate and other contexts  they can be misleading. So first of all, I'm going to describe fear as an assumption that you're about  to experience through your senses or imagination, more loss and gain, more negative than positive,  more pain and pleasure, more disadvantage and advantage, more risk than reward from somebody  or yourself in the future. And so it's an assumption you're about to get some negative experience, "
    0:01:21,0:01:28,SPEAKER 2, you might say. Now fear has its opposite. So I'm going to describe that. Now fear has another name

    """
    yt_client = YtClient(api_key='fake-api-key')
    yt_client.cache_video_ids_meta = {
        'test_video_id': {
            'contentDetails': {
                'duration': 'PT1M31S'
            }
        }
    }
    df = pd.read_csv('scripts/libs/tests/data/multi_speaker_dialog.txt')
    # in lex-hubmerman clip, pretend theres 2 chapters
    chapters = [
        YtChapterStruct(title='intro', time=0),
        YtChapterStruct(title='chapter 1', time=55), # 0:03:58 to sec
        YtChapterStruct(title='chapter 2', time=80), #  06:27 to sec
    ]
    rttm_transcripts = []
    for index, row in df.iterrows():
        rttm = RTTMTranscriptstruct(
            speaker=row['Speaker'],
            start=convert_time_to_seconds(row['Start']),
            duration=convert_time_to_seconds(row['End']) - convert_time_to_seconds(row['Start']), # here just use END
            text=row['Text']
        )
        rttm_transcripts.append(rttm)
    result = yt_client._format_rttm_transcript_into_chapters(
        chapters=chapters,
        rttm_transcripts=rttm_transcripts,
        video_id='test_video_id',
        # numb_of_speaker=2
    )
    expected_result = [
        {
            'chapter_start': 0,
            'chapter_title': 'intro',
            'chapter_segments': [
                {
                    'speaker': 'SPEAKER 2',
                    'start': 0,
                    'duration': 30,
                    'text': 'INTRO --  speaker 2'
                },
                {
                    'speaker': 'SPEAKER 1',
                    'start': 30,
                    'duration': 10,
                    'text': 'speaker 1'
                },
                {
                    'speaker': 'SPEAKER 2',
                    'start': 40,
                    'duration': 10,
                    'text': 'speaker 2'
                },
                {
                    'speaker': 'SPEAKER 1',
                    'start': 50,
                    'duration': 5,
                    'text': 'speaker 1'
                }
            ]
        },
        {
            'chapter_start': 55,
            'chapter_title': 'chapter 1',
            'chapter_segments': [
                {
                    'speaker': 'SPEAKER 1',
                    'start': 55,
                    'duration': 15,
                    'text': 'Chapter 1 -- speaker 1'
                },
                {
                    'speaker': 'SPEAKER 2',
                    'start': 70,
                    'duration': 10,
                    'text': 'speaker 2'
                },
            ]
        },
        {
            'chapter_start': 80,
            'chapter_title': 'chapter 2',
            'chapter_segments': [
                {
                    'speaker': 'SPEAKER 2',
                    'start': 80,
                    'duration': 10,
                    'text': 'Chapter 2 --  speaker 2'
                },
                {
                    'speaker': 'SPEAKER 1',
                    'start': 90,
                    'duration': 10,
                    'text': 'speaker 1'
                },
            ]
        },
    ]
    assert result == expected_result
