import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3.util.connection as urllib3_cn
import socket
import pandas as pd
import isodate
from dotenv import load_dotenv

# Force IPv4 to prevent Windows socket routing errors
def force_ipv4(*args, **kwargs):
    return socket.AF_INET

urllib3_cn.allowed_gai_family = force_ipv4

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
PLAYLIST_ID = "UUzwCEE_PchiBULMnAJqhGVg"
BASE_URL = "https://www.googleapis.com/youtube/v3"

def create_resilient_session():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    return session

def fetch_playlist_video_ids(session, playlist_id, target_count=200):
    video_ids = []
    next_page_token = None
    url = f"{BASE_URL}/playlistItems"

    while len(video_ids) < target_count:
        params = {
            "part": "contentDetails",
            "playlistId": playlist_id,
            "maxResults": min(50, target_count - len(video_ids)),
            "key": API_KEY,
        }
        if next_page_token:
            params["pageToken"] = next_page_token

        try:
            response = session.get(url, params=params, timeout=15)
            data = response.json()

            if "error" in data:
                print(f"API Warning: {data['error']['message']}")
                break

            items = data.get("items", [])
            if not items:
                break

            for item in items:
                video_ids.append(item["contentDetails"]["videoId"])

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

            time.sleep(0.5)
        except Exception as e:
            print(f"Connection notice during video ID fetch: {e}. Proceeding with retrieved IDs.")
            break

    return video_ids

def fetch_video_details(session, video_ids):
    records = []
    url = f"{BASE_URL}/videos"

    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(chunk),
            "key": API_KEY
        }

        try:
            response = session.get(url, params=params, timeout=15)
            data = response.json()

            if "error" in data:
                print(f"API Warning: {data['error']['message']}")
                continue

            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                content = item.get("contentDetails", {})

                raw_duration = content.get("duration", "PT0S")
                try:
                    duration_sec = int(isodate.parse_duration(raw_duration).total_seconds())
                except Exception:
                    duration_sec = 0

                # Filter: Keep episodes > 15 mins (900 seconds)
                if duration_sec < 900:
                    continue

                records.append({
                    "video_id": item.get("id"),
                    "title": snippet.get("title"),
                    "published_at": snippet.get("publishedAt"),
                    "duration_minutes": round(duration_sec / 60, 2),
                    "view_count": int(stats.get("viewCount", 0)),
                    "like_count": int(stats.get("likeCount", 0)),
                    "comment_count": int(stats.get("commentCount", 0)),
                    "description": snippet.get("description", "")[:500]
                })

            time.sleep(0.5)
        except Exception as e:
            print(f"Batch fetch notice: {e}. Continuing with next chunk.")

    return pd.DataFrame(records)

def main():
    if not API_KEY or API_KEY == "your_actual_api_key_here":
        raise ValueError("Please set your YOUTUBE_API_KEY in the .env file.")

    session = create_resilient_session()

    print(f"Fetching video IDs from uploads playlist: {PLAYLIST_ID}...")
    video_ids = fetch_playlist_video_ids(session, PLAYLIST_ID, target_count=200)
    print(f"Successfully retrieved {len(video_ids)} video IDs.")

    if not video_ids:
        print("No videos retrieved.")
        return

    print("Fetching detailed metrics for podcast episodes...")
    df = fetch_video_details(session, video_ids)

    os.makedirs("data", exist_ok=True)
    output_path = "data/raw_episodes.csv"
    df.to_csv(output_path, index=False)

    print(f"\nSUCCESS: Extracted {len(df)} long-form podcast episodes to {output_path}")

if __name__ == "__main__":
    main()