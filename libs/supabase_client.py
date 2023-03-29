from supabase.lib.client_options import ClientOptions
from supabase.client import create_client
from storage3.utils import StorageException
import os
import pysnooper
import snoop
from libs.storage_client import VultrObjectStorage

class SupabaseClient():

    def __init__(self, url, key, endpoint_url=None, s3_key=None, s3_secret=None) -> None:
        self.url: str = url
        self.key: str = key
        options = ClientOptions()
        self.client = create_client(url, key, options=options)
        self.vultr = VultrObjectStorage(
            endpoint_url=endpoint_url, 
            aws_access_key_id=s3_key,
            aws_secret_access_key=s3_secret,
            )


    def download_transcript_from_bucket(self, filename, file_dir="/tmp", bucket_name="yt-extracts", folder_name="yt_wavs"):
        # bucket_name = "yt-extracts"
        storage = self.client.storage()
        bucket_file_pathname = f"{folder_name}/{filename}"
        filepath_name = f"{file_dir}/{filename}"
        try:
            resp = self.vultr.s3.download_file(bucket_name, bucket_file_pathname, filepath_name)
            print("#DEBUG DL resp", resp)
            # resp = storage.from_(bucket_name).download(
            #     bucket_file_pathname,
            #     )

            # with open(filepath_name, 'wb') as f:
            #     f.write(resp)
            resp = resp.decode('utf-8')
        except Exception as e:
            resp = e
        return (filepath_name, resp)

    @pysnooper.snoop()
    def upload_audio_to_bucket(self, file_dir, filename, folder_name="yt_wavs", bucket_name="yt-extracts"):
        # bucket_name = "yt-extracts"
        file_options = {
            "content-type":"audio/mp3"
        }
        # storage = self.client.storage()
        
        # # create bucket if not found
        # buckets = storage.list_buckets()
        # sets = set([b.name for b in buckets])
        # if bucket_name not in sets:
        #     bucket = storage.create_bucket(bucket_name)

        input_file = file_dir + "/" + filename

        if not os.path.isfile(input_file):
            print(f"#DEBUG input_file {input_file} does not exist....")
            raise Exception('input_file does not exist')
        else:
            print(f"#DEBUG input_file {input_file} exists....")
        upload_filepath = f"{folder_name}/{filename}"
        try:
            # TODO: use vutlr. vultr.upload_file("yt-extracts", "/tmp/test.mp4", "yt_wavs/test.mp4")
            
            resp = self.vultr.upload_file("yt-extracts", input_file, upload_filepath)
            
            # resp = storage.from_(bucket_name).upload(
            #     upload_filepath,
            #     input_file,
            #     file_options=file_options,
            #     )
        except Exception as e:
            print("ERROR in upload_audio_to_bucket", e)
            resp = e
        return (upload_filepath, resp)

import pandas as pd
if __name__ == "__main__":
    # sb = SupabaseClient(
    #     "https://ltrgjrountzggshbnltp.supabase.co", 
    #     "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx0cmdqcm91bnR6Z2dzaGJubHRwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY2ODg3MjY3MiwiZXhwIjoxOTg0NDQ4NjcyfQ.9kZQqNR2Dw_CBBQTGt2TH18phDTc5WC_PryK1DeHBYA",
    #     endpoint_url="https://ewr1.vultrobjects.com",
    #     s3_key="A9ZBNCH9390JAWJEVE59",
    #     s3_secret="J1sZQxZ76ZTBP3Wm9sxhKeZfFayGnFkAIrVrBBHR"
    #     )

    # resp = sb.download_transcript_from_bucket("test.mp4", file_dir="/tmp")
    from supabase.client import create_client
    sb = create_client(
                "https://uukkuoxgayujrukubywa.supabase.co", 
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1a2t1b3hnYXl1anJ1a3VieXdhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY3ODk4NDMzMywiZXhwIjoxOTk0NTYwMzMzfQ.aiWIe-YHaL9Yzp2V6FMWH_drv3nYzQhZ5SFyGzisNhA", 
                )
    resp = sb.from_('sb_users_profile').select('*').execute()
    print("#DEBUG resp", resp)