
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
        
        part_file = output_path + ".part"
        if os.path.exists(part_file):
            os.rename(part_file, output_path)
        
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
        print("Captions successfully fetched:")
        return captions
    else:
        audio_path = "audio.mp3"
        download_audio(video_url, audio_path)
        if not os.path.exists(audio_path):
            print("Audio file not found. Skipping further processing.")
            return None
        
        wav_path = "audio.wav"
        try:
            print("Converting MP3 to WAV format...")
            sound = AudioSegment.from_file(audio_path)
            sound.export(wav_path, format="wav", codec="pcm_s16le")
            print("Conversion to WAV completed.")
        except Exception as e:
            print(f"Error converting MP3 to WAV: {e}")
            return None

        chunks = split_audio_to_chunks(wav_path)
        if not chunks:
            print("No audio chunks generated. Skipping further processing.")
            return None
        
        text = audio_to_text(chunks)

        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

        return text

if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ").strip()
    extracted_text = extract_text_from_video(video_url)
    if extracted_text:
        print("\nExtracted Text:\n")
        print(extracted_text)
    else:
        print("\nFailed to extract text.")
