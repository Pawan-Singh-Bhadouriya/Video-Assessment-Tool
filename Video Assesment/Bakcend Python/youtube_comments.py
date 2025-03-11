import googleapiclient.discovery
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

YOUTUBE_API_KEY = "AIzaSyDjoKIz4Lx85ItCNMU_E5S-gHn5bV8EFL8"

def get_video_id(video_url):
    if "youtube.com/watch?v=" in video_url:
        return video_url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in video_url:
        return video_url.split("youtu.be/")[-1].split("?")[0]
    return None

def fetch_youtube_comments(video_url):
    video_id = get_video_id(video_url)
    if not video_id:
        return []

    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.commentThreads().list(part="snippet", videoId=video_id, maxResults=50)
    response = request.execute()

    comments = [item["snippet"]["topLevelComment"]["snippet"]["textDisplay"] for item in response.get("items", [])]
    return comments

def analyze_sentiment(comments):
    analyzer = SentimentIntensityAnalyzer()
    total_score = sum(analyzer.polarity_scores(comment)['compound'] for comment in comments)
    avg_score = total_score / len(comments) if comments else 0
    return "Best" if avg_score > 0.5 else "Good" if avg_score > 0.2 else "Average"

def get_video_quality_based_on_comments(video_url):
    comments = fetch_youtube_comments(video_url)
    return analyze_sentiment(comments)
