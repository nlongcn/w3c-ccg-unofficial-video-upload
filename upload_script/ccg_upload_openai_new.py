import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import shutil
import re

# Directories and SCOPES definition

import os

script_dir = os.path.dirname(os.path.abspath(__file__))

while os.path.basename(script_dir) != 'w3c-ccg-unofficial-video-upload' and script_dir != os.path.dirname(script_dir):
    script_dir = os.path.dirname(script_dir)

# At this point, script_directory is either the 'w3c-ccg-unofficial-video-upload' directory or the root directory if not found
if os.path.basename(script_dir) != 'w3c-ccg-unofficial-video-upload':
    print("'w3c-ccg-unofficial-video-upload' directory not found in the path hierarchy of the script.")
    exit(1)

videos_directory = os.path.join(script_dir, 'ccg_videos_new', 'ccg_videos_transcribed')
print(f"Expected watching directory: {videos_directory}")
summaries_folder = os.path.join(script_dir, 'summaries')
print(f"Expected summaries directory: {summaries_folder}")

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    token_path = os.path.join(script_dir, 'token.pickle')
    client_secrets_path = os.path.join(script_dir, 'client_secrets.json')
    
    # Print expected paths
    print(f"Expected token path: {token_path}")
    print(f"Expected client secrets path: {client_secrets_path}")

    creds = None
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
            creds = flow.run_local_server(port=8080)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return build('youtube', 'v3', credentials=creds)

def upload_video_to_youtube(file_path):
    # Get the filename without extension
    base_name = os.path.basename(file_path)
    file_name_without_extension = os.path.splitext(base_name)[0]
    video_title = re.sub(r'(?<=[^\d])-(?=[^\d])', ' ', file_name_without_extension)

    # Determine the path to the related summary file
    summary_file_path = os.path.join(script_dir, 'summaries', f"{file_name_without_extension}_transcript_summary.txt")
    print(f"Expected summaries directory: {summary_file_path}")

    # Default description if the summary file does not exist or fails to read
    description = "Test Description"
    
    # Read the description from the summary file if it exists
    if os.path.exists(summary_file_path):
        with open(summary_file_path, 'r') as f:
            description = f.read().strip()
        print(f"Description for {file_name_without_extension}: {description}")

    # Check if the description is still the default. If yes, skip uploading the video and move it to ccg_video_old_too_short directory.
    if description == "Test Description":
        too_short_directory = os.path.join(script_dir, 'ccg_videos_old', 'ccg_video_old_too_short')
        # Ensure the destination directory exists
        if not os.path.exists(too_short_directory):
            os.makedirs(too_short_directory)
        
        new_file_path = os.path.join(too_short_directory, os.path.basename(file_path))
        
        # Move the file
        shutil.move(file_path, new_file_path)
        print(f"This {file_name_without_extension} was too short to upload, and did not have a summary.")
        print(f"Moved {file_path} to {new_file_path}")
        return

    youtube = get_authenticated_service()
    print("Uploading: " + file_path)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "categoryId": "22",
                "description": description,
                "title": video_title
            },
            "status": {
                "privacyStatus": "public",
                "embeddable": True,
                "license": "youtube",
                "publicStatsViewable": True
            },
        },
        media_body=MediaFileUpload(file_path)
    )
    response = request.execute()
    print(response)

    # This is the new code to move the uploaded video to the 'ccg_videos_old' directory.
    old_videos_directory = os.path.join(script_dir, 'ccg_videos_old')
    new_file_path = os.path.join(old_videos_directory, os.path.basename(file_path))
    
    # Ensure the destination directory exists
    if not os.path.exists(old_videos_directory):
        os.makedirs(old_videos_directory)
    
    # Move the file
    shutil.move(file_path, new_file_path)
    print(f"Moved {file_path} to {new_file_path}")

if __name__ == "__main__":
    # loop through any videos that are already in the directory
    for filename in os.listdir(videos_directory):
        if filename.endswith(".mp4"):
            file_path = os.path.join(videos_directory, filename)
            print(f"Processing file: {file_path}")
            upload_video_to_youtube(file_path)
    print("Finished processing all videos.")
