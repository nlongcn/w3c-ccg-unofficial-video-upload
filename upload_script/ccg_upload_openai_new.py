import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import shutil

# Directories and SCOPES definition
current_directory = os.getcwd()
videos_directory = os.path.join(current_directory, 'ccg_videos_new', 'ccg_videos_complete')
print(f"Expected watching directory: {videos_directory}")
if not os.path.exists(videos_directory):
    print(f"The directory {videos_directory} does not exist!")
    exit()  # Terminate the script

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


def get_authenticated_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('youtube', 'v3', credentials=creds)


def upload_video_to_youtube(file_path):
    # Get the filename without extension
    base_name = os.path.basename(file_path)
    file_name_without_extension = os.path.splitext(base_name)[0]

    # Determine the path to the related summary file
    summary_file_path = os.path.join(current_directory, 'summaries', f"{file_name_without_extension}_summary.txt")

    # Default description if the summary file does not exist or fails to read
    description = "Test Description"
    
    # Read the description from the summary file if it exists
    if os.path.exists(summary_file_path):
        with open(summary_file_path, 'r') as f:
            description = f.read().strip()
        print(f"Description for {file_name_without_extension}: {description}")

    # Check if the description is still the default. If yes, prompt the user
    if description == "Test Description":
        proceed = input(f"No summary found for {file_name_without_extension}. Do you want to proceed with the default description? (yes/no): ")
        if proceed.lower() != 'yes':
            print(f"Skipped upload for {file_name_without_extension}.")
            return

    youtube = get_authenticated_service()
    print("Uploading: " + file_path)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "categoryId": "22",
                "description": description,
                "title": base_name
            },
            "status": {
                "privacyStatus": "private",
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
    old_videos_directory = os.path.join(current_directory, 'ccg_videos_old')
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
