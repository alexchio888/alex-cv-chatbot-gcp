# stt_utils.py
from google.cloud import speech
import streamlit as st
import json
import os

def transcribe_audio(audio_bytes, language_code="en-US", sample_rate_hertz=16000):
    """
    Transcribes raw audio bytes to text using Google Cloud Speech-to-Text.

    Args:
        audio_bytes (bytes): Raw audio data, expected to be LINEAR16 PCM.
        language_code (str): BCP-47 language code, e.g. "en-US".
        sample_rate_hertz (int): Sample rate of the audio.

    Returns:
        str: Transcribed text or empty string if no transcription.
    """
    if not audio_bytes:
        return ""

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(content=audio_bytes)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate_hertz,
        language_code=language_code,
        enable_automatic_punctuation=True,
        model="default",  # or "phone_call", "video", etc. if desired
    )

    response = client.recognize(config=config, audio=audio)

    if not response.results:
        return ""

    # Combine all results' transcripts
    transcripts = [result.alternatives[0].transcript for result in response.results]
    return " ".join(transcripts).strip()