import streamlit as st
from st_audiorec import st_audiorec
from google.cloud import speech
import os

def record_audio():
    """
    Records audio from the microphone using st_audiorec.
    Returns audio bytes or None if nothing was recorded.
    """
    st.write("🎙 Click below to record your question")
    audio_bytes = st_audiorec()
    return audio_bytes


def transcribe_audio(audio_bytes, language_code="en-US"):
    """
    Transcribes recorded audio using Google Cloud Speech-to-Text.
    Returns the transcribed text or an empty string.
    """
    if not audio_bytes:
        return ""

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(content=audio_bytes)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code
    )

    response = client.recognize(config=config, audio=audio)

    if response.results:
        return response.results[0].alternatives[0].transcript.strip()
    return ""
