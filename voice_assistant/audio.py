import speech_recognition as sr
import pygame
import time
import logging
import os
from pydub import AudioSegment
from io import BytesIO

def record_audio(file_path, timeout=10, phrase_time_limit=None, retries=3, energy_threshold=2000, pause_threshold=1, phrase_threshold=0.1, dynamic_energy_threshold=True, calibration_duration=1):
    """
    Record audio from the microphone and save it as a WAV file.
    
    Args:
    file_path (str): The path to save the recorded audio file.
    timeout (int): Maximum time to wait for a phrase to start (in seconds).
    phrase_time_limit (int): Maximum time for the phrase to be recorded (in seconds).
    retries (int): Number of retries if recording fails.
    energy_threshold (int): Energy threshold for considering whether a given chunk of audio is speech or not.
    pause_threshold (float): How much silence the recognizer interprets as the end of a phrase (in seconds).
    phrase_threshold (float): Minimum length of a phrase to consider for recording (in seconds).
    dynamic_energy_threshold (bool): Whether to enable dynamic energy threshold adjustment.
    calibration_duration (float): Duration of the ambient noise calibration (in seconds).
    
    Returns:
    str: The path to the saved audio file.
    """
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = energy_threshold
    recognizer.pause_threshold = pause_threshold
    recognizer.phrase_threshold = phrase_threshold
    recognizer.dynamic_energy_threshold = dynamic_energy_threshold
    
    wav_file_path = os.path.splitext(file_path)[0] + '.wav'
    
    for attempt in range(retries):
        try:
            with sr.Microphone() as source:
                logging.info("Calibrating for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=calibration_duration)
                logging.info("Recording started")
                audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                logging.info("Recording complete")
                
                with open(wav_file_path, "wb") as f:
                    f.write(audio_data.get_wav_data())
                
                logging.info(f"Audio saved as WAV: {wav_file_path}")
                return wav_file_path
        except sr.WaitTimeoutError:
            logging.warning(f"Listening timed out, retrying... ({attempt + 1}/{retries})")
        except Exception as e:
            logging.error(f"Failed to record audio: {e}")
    
    logging.error("Recording failed after all retries")
    return None

def convert_to_mp3(wav_file_path, mp3_file_path):
    """
    Convert a WAV file to MP3 format.
    
    Args:
    wav_file_path (str): The path to the input WAV file.
    mp3_file_path (str): The path to save the output MP3 file.
    
    Returns:
    str: The path to the saved MP3 file.
    """
    try:
        audio = AudioSegment.from_wav(wav_file_path)
        audio.export(mp3_file_path, format="mp3", bitrate="128k")
        logging.info(f"Audio converted to MP3: {mp3_file_path}")
        return mp3_file_path
    except Exception as e:
        logging.error(f"Failed to convert audio to MP3: {e}")
        return None

def play_audio(file_path):
    """
    Play an audio file using pygame.
    
    Args:
    file_path (str): The path to the audio file to play.
    """
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
    except pygame.error as e:
        logging.error(f"Failed to play audio: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while playing audio: {e}")
