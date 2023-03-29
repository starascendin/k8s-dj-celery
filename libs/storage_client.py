# BL: use boto to upload to vultr bucket

import boto3

class VultrObjectStorage:
    def __init__(self, endpoint_url, aws_access_key_id, aws_secret_access_key):
        self.s3 = boto3.client(
            's3',
            region_name="", # this is not needed for vultr
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
    def upload_file(self, bucket_name, file_path, object_name):
        resp = self.s3.upload_file(file_path, bucket_name, object_name)
        return resp
        
    def download_file(self, bucket_name, object_name, file_path):
        resp = self.s3.download_file(bucket_name, object_name, file_path)
        return resp
        
        

if __name__ == '__main__':
    vultr = VultrObjectStorage(
        endpoint_url="https://ewr1.vultrobjects.com",
        aws_access_key_id="A9ZBNCH9390JAWJEVE59",
        aws_secret_access_key="J1sZQxZ76ZTBP3Wm9sxhKeZfFayGnFkAIrVrBBHR"
        )

    vultr.upload_file("yt-extracts", "/tmp/test.mp4", "yt_wavs/test.mp4")
    