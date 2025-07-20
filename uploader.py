import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# CONFIG
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
SERVICE_ACCOUNT_FILE = "service_account.json"
VIDEO_FOLDER = "shorts"
LOG_FILE = "uploaded.txt"
PRIVACY_STATUS = "public"  # Or "private" or "unlisted"

def authenticate_youtube():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    youtube = build("youtube", "v3", credentials=creds)
    return youtube

def upload_video(youtube, file_path, title, description, tags=[]):
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"  # People & Blogs
        },
        "status": {
            "privacyStatus": PRIVACY_STATUS
        }
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading {file_path}: {int(status.progress() * 100)}%")
    print(f"✅ Uploaded: https://youtu.be/{response['id']}")
    return response['id']

def load_uploaded_log():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def log_uploaded(video_name):
    with open(LOG_FILE, "a") as f:
        f.write(video_name + "\n")

def main():
    youtube = authenticate_youtube()
    uploaded = load_uploaded_log()

    videos = sorted([v for v in os.listdir(VIDEO_FOLDER) if v.endswith(".mp4")])
    for video in videos:
        if video in uploaded:
            print(f"⏩ Already uploaded: {video}")
            continue

        file_path = os.path.join(VIDEO_FOLDER, video)
        title = f"{video} #shorts"
        description = "Automated daily upload #shorts"
        tags = ["shorts", "automation"]

        try:
            upload_video(youtube, file_path, title, description, tags)
            log_uploaded(video)
        except Exception as e:
            print(f"❌ Failed to upload {video}: {e}")
            continue

        # Upload only one video per run
        break

if __name__ == "__main__":
    main()
