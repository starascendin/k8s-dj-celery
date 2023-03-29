# import os
# import google.oauth2.credentials
# import google_auth_oauthlib.flow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

import os
import sys
import json
import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# # Path to your client_secret.json
# CLIENT_SECRET_FILE = 'path/to/your/credential_secret.json'

# # Define the API scopes you need access to
# SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']



# Path to your client_secret.json
CLIENT_SECRET_FILE = 'libs/.client_secret.json'

# BL: This might be the scope needed to login.
# https://ltrgjrountzggshbnltp.supabase.co/auth/v1/authorize?provider=google&https://www.googleapis.com/auth/youtube.force-ssl

# Define the API scopes you need access to
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']


def get_authenticated_service(user_id):
    user_credentials_file = f'user_credentials_{user_id}.json'

    if os.path.exists(user_credentials_file):
        with open(user_credentials_file, 'r') as f:
            credentials_json = json.load(f)
            credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(info=credentials_json)
    else:
        # https://<your-ref>.supabase.co/auth/v1/authorize?provider=google&https://www.googleapis.com/auth/gmail.send

        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        credentials = flow.run_console()
        with open(user_credentials_file, 'w') as f:
            json.dump(json.loads(credentials.to_json()), f)

    return build('youtube', 'v3', credentials=credentials)

def get_playlists(youtube):
    try:
        response = youtube.playlists().list(
            part='snippet,contentDetails',
            mine=True,
            maxResults=25
        ).execute()

        return response['items']
    except HttpError as e:
        print(f'An error occurred: {e}')
        return None

def main():
    if len(sys.argv) < 2:
        print('Usage: python script.py <user_id>')
        sys.exit(1)

    user_id = sys.argv[1]
    youtube = get_authenticated_service(user_id)
    playlists = get_playlists(youtube)

    if playlists:
        print(f'YouTube Playlists for User {user_id}:')
        for playlist in playlists:
            print(f'{playlist["snippet"]["title"]}, Playlist ID: {playlist["id"]}')
    else:
        print('No playlists found.')

if __name__ == '__main__':
    main()
