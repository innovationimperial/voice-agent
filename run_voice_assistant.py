# voice_assistant/main.py

import logging
import time
from colorama import Fore, init
from voice_assistant.audio import record_audio, play_audio
from voice_assistant.transcription import transcribe_audio
from voice_assistant.response_generation import generate_response
from voice_assistant.text_to_speech import text_to_speech
from voice_assistant.utils import delete_file
from voice_assistant.config import Config
from voice_assistant.api_key_manager import get_transcription_api_key, get_response_api_key, get_tts_api_key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize colorama
init(autoreset=True)

def main():
    """
    Main function to run the voice assistant.
    """
    chat_history = [
        {"role": "system", "content": """ You are a helpful Assistant called AgroImperial from innovation imperial. 
         You are friendly and  proffesional and you understand everything about farming from production to business you know all the organic 
         regulations and laws ,permits and certifications especially in INTER AFRICAN TRADE AND ORGANIC FARMING
         your answers are  insightfull but short and well summarized in a text format mark down clean format like this (
  response format: Local African Suppliers:

Ecoorganic Fertilizers (Kenya): Offers a range of organic fertilizers, including compost tea, bokashi, and worm casting.
Agricola Organic Fertilizers (Ghana): Provides organic fertilizers like neem cake, bone meal, and fish bone meal.
Greenbelt Fertilizers (South Africa): Supplies organic fertilizers like compost, manure, and vermicompost." DO NOT PUT ASTERIX LIKE THI ** IN THE RESPONSE FORMAT)"""}
    ]

    while True:
        try:
            # Record audio from the microphone and save it as 'test.wav'
            wav_file_path = record_audio(Config.INPUT_AUDIO)
            if not wav_file_path:
                logging.error("Failed to record audio. Retrying...")
                continue

            # Get the API key for transcription
            transcription_api_key = get_transcription_api_key()
            
            # Transcribe the audio file
            user_input = transcribe_audio(Config.TRANSCRIPTION_MODEL, transcription_api_key, wav_file_path, Config.LOCAL_MODEL_PATH)

            # Check if the transcription is empty and restart the recording if it is
            if not user_input:
                logging.info("No transcription was returned. Starting recording again.")
                continue
            logging.info(Fore.GREEN + "You said: " + user_input + Fore.RESET)

            # Check if the user wants to exit the program
            if "goodbye" in user_input.lower() or "arrivederci" in user_input.lower():
                break

            # Append the user's input to the chat history
            chat_history.append({"role": "user", "content": user_input})

            # Get the API key for response generation
            response_api_key = get_response_api_key()

            # Generate a response
            response_text = generate_response(Config.RESPONSE_MODEL, response_api_key, chat_history, Config.LOCAL_MODEL_PATH)
            logging.info(Fore.CYAN + "Response: " + response_text + Fore.RESET)

            # Append the assistant's response to the chat history
            chat_history.append({"role": "assistant", "content": response_text})

            # Determine the output file format based on the TTS model
            if Config.TTS_MODEL in ['openai', 'elevenlabs', 'melotts', 'cartesia']:
                output_file = 'output.mp3'
            else:
                output_file = 'output.wav'

            # Get the API key for TTS
            tts_api_key = get_tts_api_key()

            # Convert the response text to speech and save it to the appropriate file
            text_to_speech(Config.TTS_MODEL, tts_api_key, response_text, output_file, Config.LOCAL_MODEL_PATH)

            # Play the generated speech audio
            if Config.TTS_MODEL != "cartesia":
                play_audio(output_file)
            
            # Clean up audio files (uncomment if needed)
            # delete_file(wav_file_path)
            # delete_file(output_file)

        except Exception as e:
            logging.error(Fore.RED + f"An error occurred: {e}" + Fore.RESET)
            if 'wav_file_path' in locals():
                delete_file(wav_file_path)
            if 'output_file' in locals():
                delete_file(output_file)
            time.sleep(1)

if __name__ == "__main__":
    main()