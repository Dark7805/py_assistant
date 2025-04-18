import time
from pytube import Search
from googleapiclient.discovery import build

def search_video_with_retry(song_name, retries=3, delay=5):
    attempt = 0
    while attempt < retries:
        try:
            search = Search(song_name)
            search_results = search.results
            if search_results:
                return search_results[0].watch_url  # Return the first video URL
        except Exception as e:
            print(f"Error: {e}")
            attempt += 1
            print(f"Retrying... ({attempt}/{retries})")
            time.sleep(delay)  # Wait for a few seconds before retrying
    return "No video found afterfrom googleapiclient.discovery import build"
import webbrowser

# Set up the YouTube API with your API key
api_key = 'AIzaSyCVAw9RdB1BZrJ9KLXyUwm_UPs_A4pRD-0'
youtube = build("youtube", "v3", developerKey=api_key)

def search_video(song_name):
    request = youtube.search().list(
        part="snippet",
        q=song_name,
        type="video",
        videoDuration="medium"  # Filter for videos longer than 4 minutes
    )
    response = request.execute()

    if response["items"]:
        video_id = response['items'][0]['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        return video_url
    return "No suitable video found."

# Example usage
song_name = "Baby Justin Bieber"
video_url = search_video(song_name)

print(f"Video URL: {video_url}")
webbrowser.open(video_url)

