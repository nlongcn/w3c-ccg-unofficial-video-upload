import os
import requests
from bs4 import BeautifulSoup
import urllib.request
import re
import logging

# checks an official file, and a list of all videos already scrapped, before 
# downloading new videos. All videos in the 'ccg_videos_new' folder will be 
# processed (transcribed and summarized)

# Set up logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR)

# Load already known video names from the files
known_video_names = set()

# Ensure both files exist, else stop execution
script_dir = os.path.dirname(os.path.realpath(__file__))
for filename in ['ccg-all-video-names.txt', 'ccg-all-video-names-scrapped.txt']:
    file_path = os.path.join(script_dir, filename)
    if not os.path.exists(file_path):
        print(f"Error: {filename} not found in {script_dir}. Stopping execution.")
        exit()
    with open(file_path, 'r') as f:
        known_video_names.update(f.read().splitlines())

# URL of the page we want to scrape
url = "https://w3c-ccg.github.io/meetings/"
response = requests.get(url)

# Check the response status
print(f"Response status code: {response.status_code}")

# Parse the html content
soup = BeautifulSoup(response.content, 'html.parser')

# Find all the lines that contain "Meeting"
lines = soup.find_all(lambda tag: 'Meeting' in tag.text)

# Check the number of lines found
print(f"Number of lines found: {len(lines)}")

# Base URL for the video files
base_url = "https://meet.w3c-ccg.org/archives/w3c-ccg"

# Create a directory to store videos
directory = "ccg_videos_new"
if not os.path.exists(directory):
    os.makedirs(directory)

# Regular expression to match a valid meeting line
regex = re.compile(r'^Meeting for \d{4}-\d{2}-\d{2}(-.*)?$')

# Extract video URLs
video_urls = set()
for line in lines:
    if not regex.match(line.text):
        continue

    words = line.text.split()
    meeting_date_type = words[-1]
    elements = meeting_date_type.split('-')

    if len(elements) == 3:
        meeting_date = meeting_date_type
        meeting_type = 'weekly'
    else:
        meeting_date = '-'.join(elements[0:3])
        meeting_type = elements[-1] if elements[-2] == 'vc' else '-'.join(elements[3:])

    video_url = f"{base_url}-{meeting_type}-{meeting_date}.mp4"
    video_urls.add(video_url)

# Verify and download the videos
for video_url in video_urls:
    video_name = video_url.split('/')[-1]
    
    # Check if video_name is in known_video_names
    if video_name in known_video_names:
        print(f"{video_name} is already known. Skipping download.")
        continue

    # Path to store the video
    output_path = os.path.join(directory, video_name)

    # Print the URL and output path
    print(f"URL: {video_url}")
    print(f"Output path: {output_path}")

    # Check if the file already exists
    if os.path.isfile(output_path):
        print(f"The file {output_path} already exists, skipping download.")
        continue

    # Download the video
    print(f"Attempting to download {video_url}...")
    try:
        urllib.request.urlretrieve(video_url, output_path)
        print(f"Saved as {output_path}")
    except Exception as e:
        print(f"Failed to download {video_url}. Error: {e}")
        logging.error(f"Failed to download {video_url}. Error: {e}")

print("Finished processing.")
