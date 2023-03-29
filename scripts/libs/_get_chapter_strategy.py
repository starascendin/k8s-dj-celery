# from abc import ABC, abstractmethod
# from typing import List
# from .yt_transcript_client import YtChapterStruct, RTTMTranscriptstruct

# from langchain.text_splitter import TextSplitter, RecursiveCharacterTextSplitter

# class GetChapterStrategy(ABC):
#     @abstractmethod
#     def get_chapters(self)  -> List[YtChapterStruct]:
#         pass



# class GetChapterByTimestampStrategy(GetChapterStrategy):
#     def get_chapters(self, time_segment_by_sec, end_timestamp) -> List[YtChapterStruct]:
#         ctr_seconds: int = 0
#         ctr = 0
#         chapters = []
#         while True:
#             if ctr_seconds > end_timestamp:
#                 break
#             chapters.append(YtChapterStruct(
#                 title=f'PLACEHOLDER_CHAPTER_{ctr}',
#                 time=ctr_seconds
#             ))
#             ctr_seconds+=time_segment_by_sec
#             ctr += 1
#         return chapters

# import tiktoken
# # use langchain token helpers
# class GetChapterByTokenSizeStrategy(GetChapterStrategy):
#     def _get_token_length(self, text: str) -> int:
#         enc = tiktoken.get_encoding("gpt2")
#         token_length = len(enc.encode(
#             text,
#             allowed_special=set(),
#             disallowed_special="all",
#         ))
#         return token_length
    
#     def get_chapters(self, rttm_transcripts: List[RTTMTranscriptstruct], token_size=2000 ) -> List[YtChapterStruct]:
#         chapters = []
#         i, j = 0, 0  # Initialize two pointers
#         current_chapter = {'start_time': None, 'text': ''}
#         curr_chapter = YtChapterStruct(time=0, title="")
#         accu_token = 0
#         raw_transcripts = rttm_transcripts
#         chapter_ctr = 0
#         while i < len(raw_transcripts):
#             # Update current chapter with new transcript
#             text_i = raw_transcripts[i].text.strip()
#             text_i_tokens = self._get_token_length(text_i)
#             if accu_token + text_i_tokens <= token_size:
#                 # current_chapter['text'] += ' ' + text_i if current_chapter['text'] else text_i
#                 accu_token += text_i_tokens
#             else:
#                 # Chapter is complete, add to output
#                 current_chapter['start_time'] = raw_transcripts[j].start
                
#                 chapters.append(YtChapterStruct(
#                     title=f"PLACEHOLDER_CHAPTER_{chapter_ctr}",
#                     time=raw_transcripts[j].start
#                 ))
#                 # Move j pointer to next starting point
#                 j = i
#                 chapter_ctr += 1
#                 # current_chapter = {'start_time': None, 'text': ''}
#             i += 1
        
#         # adding in last chapter
#         chapters.append(YtChapterStruct(
#             title=f"PLACEHOLDER_CHAPTER_{chapter_ctr}",
#             time=raw_transcripts[j].start
#         ))
            
        
#         return chapters
            


# # class SubtractStrategy(Strategy):
# #     def do_operation(self, num1, num2):
# #         return num1 - num2