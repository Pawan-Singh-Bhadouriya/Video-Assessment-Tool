import os
from pocketsphinx import AudioFile
from pydub import AudioSegment


# Configuration for PocketSphinx
config = {
    "hmm": "Backend/model/en-us",  # Path to acoustic model
    "lm": "Backend/model/en-us/en-us.lm.bin",  # Language model file
    "dict": "Backend/model/en-us/cmudict-en-us.dict",  # Pronunciation dictionary
}

def calculate_speech_rate(audio_file):
    """
    Calculate speech rate from an audio file.
    """
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file {audio_file} not found!")

    # Load audio using Pydub
    audio = AudioSegment.from_file(audio_file)

    # Convert duration to seconds
    duration_seconds = len(audio) / 1000.0  # Pydub stores length in milliseconds

    # Process with PocketSphinx
    config["audio_file"] = audio_file
    decoder = AudioFile(**config)
    
    word_count = 0
    for segment in decoder:
        word_count += len(segment.hypothesis().split())

    # Calculate speech rate (words per minute)
    speech_rate = word_count / (duration_seconds / 60)  
    return speech_rate

    """
    Calculate speech rate from an audio file.
    """
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file {audio_file} not found!")

    config["audio_file"] = audio_file  # Ensure the audio file is provided
    decoder = AudioFile(**config)
    
    word_count = 0
    for segment in decoder:
        word_count += len(segment.hypothesis().split())

    duration_seconds = len(audio_file) / audio_file.frame_rate  # Calculate total duration in seconds
    speech_rate = word_count / (duration_seconds / 60)  # Words per minute  
    # speech_rate = word_count / (decoder.total_time() / 60)  # Words per minute
    return speech_rate

def evaluate_speech_rate(speech_rate):
    """
    Evaluates the speech rate and returns feedback.
    """
    if speech_rate < 100:
        return "Slow speech rate."
    elif 100 <= speech_rate <= 160:
        return "Normal speech rate."
    else:
        return "Fast speech rate."

