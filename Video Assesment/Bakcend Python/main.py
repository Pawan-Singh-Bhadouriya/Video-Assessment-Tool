from youtube_comments import get_video_quality_based_on_comments
from speech_analysis import calculate_speech_rate, evaluate_speech_rate
from keyword_analysis import keyword_coverage
from readability_analysis import evaluate_readability
from yt_dlp import YoutubeDL
from pydub import AudioSegment
import speech_recognition as sr
import os

def fetch_captions(video_url):
    try:
        from pytube import YouTube
        yt = YouTube(video_url)
        captions = yt.captions.get_by_language_code('en')
        if captions:
            return captions.generate_srt_captions()
        else:
            print("No captions available. Proceeding with audio extraction.")
            return None
    except Exception as e:
        print(f"Error fetching captions: {e}")
        return None

def download_audio(video_url, output_path="audio.mp3"):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': output_path,
            'noplaylist': True,
            'retries': 5,
            'socket_timeout': 30,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        if not os.path.exists(output_path):
            raise FileNotFoundError("Audio download failed.")
        
        print("Audio downloaded successfully.")
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

def split_audio_to_chunks(wav_path, chunk_length=60000):
    try:
        audio = AudioSegment.from_file(wav_path)
        chunks = [audio[i:i+chunk_length] for i in range(0, len(audio), chunk_length)]
        return chunks
    except Exception as e:
        print(f"Error splitting audio: {e}")
        return []

def audio_to_text(wav_chunks):
    recognizer = sr.Recognizer()
    full_text = ""
    for i, chunk in enumerate(wav_chunks):
        try:
            chunk_path = f"chunk_{i}.wav"
            chunk.export(chunk_path, format="wav")
            with sr.AudioFile(chunk_path) as source:
                print(f"Processing chunk {i+1}/{len(wav_chunks)}...")
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
                full_text += text + " "
            os.remove(chunk_path)
        except Exception as e:
            print(f"Error processing chunk {i+1}: {e}")
    return full_text.strip()

def extract_text_from_video(video_url):
    captions = fetch_captions(video_url)
    if captions:
        return captions
    else:
        audio_path = "audio.mp3"
        download_audio(video_url, audio_path)
        if not os.path.exists(audio_path):
            return None
        
        wav_path = "audio.wav"
        try:
            sound = AudioSegment.from_file(audio_path)
            sound.export(wav_path, format="wav", codec="pcm_s16le")
        except Exception as e:
            print(f"Error converting MP3 to WAV: {e}")
            return None

        chunks = split_audio_to_chunks(wav_path)
        if not chunks:
            return None
        
        text = audio_to_text(chunks)

        os.remove(audio_path)
        # os.remove(wav_path)

        return text

def generate_overall_result(comment, speech, keyword, readability):
    """
    Combines all assessments into a single overall evaluation.
    """

    # Convert textual scores into numerical values for weighting
    scores = {
        "Excellent": 5, "Good": 4, "Average": 3, "Below Average": 2, "Poor": 1,
        "Slow speech rate.": 2, "Normal speech rate.": 4, "Fast speech rate.": 3
    }

    total_score = sum([
        scores.get(comment, 3),
        scores.get(speech, 3),
        scores.get(keyword, 3),
        scores.get(readability, 3)
    ])

    # Determine final category
    if total_score >= 18:
        return "🌟 Excellent"
    elif total_score >= 14:
        return "✅ Good"
    elif total_score >= 10:
        return "⚖️ Average"
    elif total_score >= 7:
        return "⚠️ Below Average"
    else:
        return "❌ Poor"


def analyze_video(video_url):
    extracted_text = extract_text_from_video(video_url)
    if not extracted_text:
        print("Failed to extract text.")
        return
    
    print("\nEvaluating Video Quality...\n")
    
    comment_quality = get_video_quality_based_on_comments(video_url)
    speech_rate = calculate_speech_rate("audio.wav")
    speech_quality = evaluate_speech_rate(speech_rate)
    keyword_quality = keyword_coverage(extracted_text)
    readability_quality = evaluate_readability(extracted_text)
    overall_result = generate_overall_result(comment_quality, speech_quality, keyword_quality, readability_quality)
    os.remove("audio.wav") #changes i made

    print(f"1. User Feedback: {comment_quality}")
    print(f"2. Speech Clarity: {speech_quality}")
    print(f"3. Keyword Coverage: {keyword_quality}")
    print(f"4. Readability Score: {readability_quality}")
    print(f"\n🔹 Overall Video Quality Assessment: {overall_result}")

if __name__ == "__main__":
    video_url = input("Enter YouTube video URL: ").strip()
    analyze_video(video_url)
