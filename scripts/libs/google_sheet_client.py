

import gspread
from typing import List
# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1bacmSb83gxHW9M8F7755eofNtZFYlp9QDWrNKXatrOo'
SAMPLE_RANGE_NAME = 'YT_Transcripts!A2:E'


# my gsheet colums 5: video_title	chapter_idx	startTime	ChunkTitle	ChunkContent

def pipe_content_to_gsheet(rows_data: List[str]):

    # This automatically scopes for Drive + sheets
    client = gspread.oauth(
        credentials_filename='./.credentials.json',
        authorized_user_filename='./.authorized_user.json'
    )

    # Open the Google Sheet
    sheet = client.open_by_key(SAMPLE_SPREADSHEET_ID).worksheet("YT_Transcripts")


    # print(sheet.get('A:E'))

    # Append the data to the sheet
    # data = ["string1", "string2", "string3"]
    # print("#row_data", rows_data)
    sheet.append_rows(rows_data)



if __name__ == '__main__':
    pipe_content_to_gsheet([''])
