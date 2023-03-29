from pytube import YouTube
from pytube.cli import on_progress
import os
import snoop
import logging
import datetime

logger = logging.getLogger(__name__)

def dl_yt_vid(video_url, filename=None, filepath="/tmp/"):
    yt = YouTube(video_url, on_progress_callback=on_progress)
    itag = 18
    duration_seconds = yt.length
    print(f'duration: {duration_seconds} seconds')
    size_bytes = yt.streams.get_by_itag(itag).filesize
    print(f'File size: {size_bytes} bytes')

    # shoud rename
    output_dir = filepath

    # check if file exists in directory
    abs_video_path = f'{output_dir}/{filename}'
    if not os.path.isfile(abs_video_path):

        # This creates mp4 audio file
        print("Downloading video...")
        time_before = datetime.datetime.utcnow()

        # t=yt.streams.filter(only_audio=True, file_extension='mp4')
        # abs_video_path = t.first().download(
        #     output_path=output_dir, filename=filename
        #     )

        stream = yt.streams.get_by_itag(itag)
        abs_video_path = stream.download(output_path=output_dir, filename=filename)

        download_time = datetime.datetime.utcnow() - time_before
        print(f'Downloading time: {download_time.total_seconds()} seconds')
        print(f'Average speed:    {size_bytes/download_time.total_seconds()/1024} kB/s ')
    return abs_video_path

def extract_vid_audio(abs_video_path):
    """
    This module should DL a YT video locally and extract audio to /tmp
    /tmp should be cleaned up by end of Day.

    """


    _, file_ending = os.path.splitext(f'{abs_video_path}')
    print(f'file_ending is {file_ending}')
    audio_file = abs_video_path.replace(file_ending, ".wav")
    if not os.path.isfile(audio_file):
        print("AUDIO file does not exist. Creating...")
        os.system(f'ffmpeg -i "{abs_video_path}" -ar 16000 -ac 1 -c:a pcm_s16le "{audio_file}"')


    if os.path.isfile(audio_file):
        logger.debug(f"Audio file {audio_file} exists")

    return audio_file

def rm_vid_audio(filenames):
    """
    This module should DL a YT video locally and extract audio to /tmp
    /tmp should be cleaned up by end of Day.

    """
    for filename in filenames:
        os.remove(filename)
        logger.debug(f"Removed {filename}...")





# Someone else's PYtube snippet
# from pytube import YouTube
# from pytube.cli import on_progress
# import datetime


# # two videos picked by random for testing only:
# # youtube_episode_id = 'lOPxDEATfHA'  # 2:34 minutes long
# youtube_episode_id = 'Q3ex2rqU2Ik'   # 13:07 minutes long

# youtube_video = 'http://youtube.com/watch?v=' + youtube_episode_id


# yt = YouTube(youtube_video, on_progress_callback=on_progress)

# print(f'options for download: {yt.streams}')
# print(f'---------------------------')

# duration_seconds = YouTube(youtube_video).length
# print(f'duration: {duration_seconds} seconds')

# # itag = 18 # video 360 pixels (THIS DOWNLOAD AT HIGH SPEED)
# itag = 140  # audio only (THIS DOWNLOAD AT AROUND 30 KB/SEC)

# size_bytes = yt.streams.get_by_itag(itag).filesize
# print(f'File size: {size_bytes} bytes')

# stream = yt.streams.get_by_itag(itag)
# print(f'Will start the download:')
# time_before = datetime.datetime.utcnow()
# stream.download(filename=f'{youtube_episode_id}.mp4', skip_existing=True, max_retries=2)
# download_time = datetime.datetime.utcnow() - time_before
# print(f'Downloading time: {download_time.total_seconds()} seconds')
# print(f'Average speed:    {size_bytes/download_time.total_seconds()/1024} kB/s ')
if __name__ == "__main__":
    source = "https://www.youtube.com/watch?v=xLORsLlcT48"
    video = dl_yt_vid(source)
    print("#DEBUG video extracted....", video)
    extract_vid_audio(video)
