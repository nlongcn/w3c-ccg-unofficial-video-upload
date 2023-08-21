# w3c-ccg-unofficial-video-upload

Tools to download videos from a repository, transcribe them using whisper, summarise the transcription using OpenAI's chatGPT API, before uploading the summary and the video to YouTube.

## Bulk Summarization and Upload

If this is the first time you are creating the channel then you need to summarize existing transcripts and bulk upload to YouTube.
Videos can be found on a shared drive. Contact the ccg administrator for that location.
Add videos to the ccg_videos_new directory

### There are two lists:

- Official list of videos provided by a W3C CCG standards committee editor or chair (updated)
- List of videos already scrapped.
  Both lists can be found in the download_script folder.
  List prevent duplicate downloads.

### There are three folders for videos

- ccg_videos_new, videos that have been downloaded but not yet transcribed
- ccg_videos_new\ccg_videos_transcribed, videos that have been download and transcribed
- ccg_videos_old, videos that have been downloaded, transcribed, summarized and uploaded to youtube

### There are four scripts

- download_script\ccg_download.py, downloads new videos into ccg_videos_new by scraping https://w3c-ccg.github.io/meetings/ for new video names.
- transcribe_summarize\transcribe.py, transcribes new videos using openAi's whisper
- transcribe_summarize\summarize_chatgpt.py, takes transcripts from the transcripts folder, checks the are longer than 100 words and then summarizes them. Short transcripts are not summarized and the relared video is moved into ccg_videos_old.
- upload_script\ccg_upload_openai_new_py, takes videos from ccg_videos_transcribed, uploads them to YouTube with the summary and moves the video into ccg_videos_old

### Pre-requisites

- openAI API key
- YouTube account and client_secret

### Setting up YouTube credentials

To create new credentials for your application using a new Google account, follow these steps:

1. **Google Cloud Platform (GCP) Console**:

   - Go to the [Google Cloud Platform Console](https://console.cloud.google.com/).

2. **Log in with Your New Google Account**:

   - On the top-right corner of the page, click on the profile icon and make sure you're signed in with your new Google account.

3. **Create a New Project**:

   - Click on the project drop-down (next to "Google Cloud Platform" in the header).
   - Click on the `New Project` button on the top-right of the modal.
   - Give your project a name, and you can also edit the project ID if desired.
   - Click `Create`.

4. **Enable YouTube Data API v3**:

   - Once your project is created, in the dashboard's search bar, type "YouTube Data API v3" and select it from the dropdown.
   - Click `Enable` to enable the YouTube Data API v3 for your project.

5. **Create Credentials**:

   - On the left sidebar, click on `Credentials`.
   - Click the `Create Credentials` button and select `OAuth 2.0 Client ID`.
   - Choose the `Desktop app` type (since you'll be running the script from your local machine).
   - Click `Create`.
   - You'll see a modal with your client ID and client secret. Click `OK`.

6. **Download the Credentials**:

   - On the `Credentials` page where you see your client ID listed, on the right side, you'll see a download icon. Click on it to download your credentials as a JSON file.
   - Save this `client_secrets.json` file in the same directory as your script.

7. **OAuth Consent Screen**:
   - Before you can use the credentials, you'll need to configure the OAuth consent screen.
   - On the left sidebar under `Credentials`, click on `OAuth consent screen`.
   - Choose `External` and click `Create`.
   - Fill out the necessary details (e.g., App name, User support email).
   - Under `Scopes`, add the scopes you need (you probably need at least `../auth/youtube.upload`).
   - Under `Test users`, add your email (this is especially important if your app is not yet verified by Google).
   - Click `Save and Continue`, go through the next sections, and save your changes.

With these steps completed, you should now have new credentials set up for your application with your new Google account. When you run your script, it will use the newly downloaded `client_secrets.json` file for authentication.
