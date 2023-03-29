
import pytest

from scripts.libs.yt_transcript_client import YtClient, YtRawTranscriptStruct, RTTMTranscriptstruct, YtChapterStruct, GetChapterByTimestampStrategy, GetChapterByTokenSizeStrategy
from youtube_transcript_api import YouTubeTranscriptApi

@pytest.fixture
def rttm_transcripts():
    return [
        RTTMTranscriptstruct(speaker="Speaker1", start=0, duration=10, text="Hello world"),
        RTTMTranscriptstruct(speaker="Speaker1", start=11, duration=10, text="How are you?"),
        RTTMTranscriptstruct(speaker="Speaker1", start=22, duration=10, text="I'm fine, thank you and you are very pretty"),
    ]

def test_GetChapterByTimestampStrategy(rttm_transcripts):
    strategy = GetChapterByTimestampStrategy()
    chapters = strategy.get_chapters(time_segment_by_sec=30, end_timestamp=60,)

    assert len(chapters) == 3
    assert chapters[0] == YtChapterStruct(title="PLACEHOLDER_CHAPTER_0", time=0)
    assert chapters[1] == YtChapterStruct(title="PLACEHOLDER_CHAPTER_1", time=30)
    assert chapters[2] == YtChapterStruct(title="PLACEHOLDER_CHAPTER_2", time=60)

def test_GetChapterByTokenSizeStrategy(rttm_transcripts):
    strategy = GetChapterByTokenSizeStrategy()
    chapters = strategy.get_chapters(rttm_transcripts=rttm_transcripts, token_size=20)
    assert len(chapters) == 1
    assert chapters[0] == YtChapterStruct(title="PLACEHOLDER_CHAPTER_0", time=0)
    
    chapters = strategy.get_chapters(rttm_transcripts=rttm_transcripts, token_size=10)
    assert len(chapters) == 2
    assert chapters[0] == YtChapterStruct(title="PLACEHOLDER_CHAPTER_0", time=0)
    assert chapters[1] == YtChapterStruct(title="PLACEHOLDER_CHAPTER_1", time=22)
