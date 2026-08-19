import os
import socket
import pandas as pd
from googleapiclient.discovery import build
import isodate
from dotenv import load_dotenv

# Force IPv4 socket resolution on Windows to eliminate WinError 10060 timeouts
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4_only

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_HANDLE = "@rajshamani"

def get_channel_id(youtube, handle):
    req = youtube.search().list(part="snippet", type="channel", q=handle, maxResults=1)
    res = req.execute()
    if res.get("items"):
        return res["items"][0]["snippet"]["channelId"]
    return None

def fetch_latest_episodes(output_csv="data/raw_episodes.csv", target_podcast_count=60):
    if not API_KEY:
        raise ValueError("YOUTUBE_API_KEY is not set.")
        
    youtube = build("youtube", "v3", developerKey=API_KEY)
    
    # 1. Fetch channel uploads playlist ID
    try:
        ch_req = youtube.channels().list(part="contentDetails", forHandle=CHANNEL_HANDLE.replace("@", ""))
        ch_res = ch_req.execute()
    except Exception:
        ch_res = {}
    
    if not ch_res.get("items"):
        channel_id = get_channel_id(youtube, CHANNEL_HANDLE) or "UCw6XbK3f4pT4u4u7d1b6v8w"
        ch_req = youtube.channels().list(part="contentDetails", id=channel_id)
        ch_res = ch_req.execute()
        
    uploads_playlist_id = ch_res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    
    # 2. Paginate through uploads until target podcast count is reached
    podcast_records = []
    next_page_token = None
    
    while len(podcast_records) < target_podcast_count:
        playlist_req = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        playlist_res = playlist_req.execute()
        
        video_ids = [item["contentDetails"]["videoId"] for item in playlist_res.get("items", [])]
        if not video_ids:
            break
            
        # Batch fetch video duration and metrics
        videos_req = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=",".join(video_ids)
        )
        videos_res = videos_req.execute()
        
        for item in videos_res.get("items", []):
            duration_iso = item["contentDetails"]["duration"]
            duration_sec = isodate.parse_duration(duration_iso).total_seconds()
            
            # Filter: Keep only full-length podcast episodes (>= 20 minutes)
            if duration_sec >= 1200:
                podcast_records.append({
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "published_at": item["snippet"]["publishedAt"],
                    "view_count": int(item["statistics"].get("viewCount", 0)),
                    "like_count": int(item["statistics"].get("likeCount", 0)),
                    "comment_count": int(item["statistics"].get("commentCount", 0)),
                    "duration_seconds": duration_sec
                })
                if len(podcast_records) >= target_podcast_count:
                    break
                    
        next_page_token = playlist_res.get("nextPageToken")
        if not next_page_token:
            break
            
    df = pd.DataFrame(podcast_records)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    return df

if __name__ == "__main__":
    fetch_latest_episodes()