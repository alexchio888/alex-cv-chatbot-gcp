# tts_utils.py
from google.cloud import texttospeech
import base64
import streamlit as st
import xml.etree.ElementTree as ET
import re

def is_valid_ssml(ssml_text):
    try:
        ET.fromstring(ssml_text)
        return True
    except ET.ParseError:
        return False

def strip_ssml_tags(ssml_text: str) -> str:
    # Remove anything between <...> including the tags
    return re.sub(r'<[^>]+>', '', ssml_text)

def get_voices():
    client = texttospeech.TextToSpeechClient()
    voices_response = client.list_voices()
    voices = voices_response.voices

    # Filter for en-US voices (adjust if needed)
    filtered_voices = []
    for voice in voices:
        if any("en-US" in lang for lang in voice.language_codes):
            filtered_voices.append(voice.name)
    return filtered_voices

def generate_google_tts_audio(text, voice_name='en-US-Neural2-D', speaking_rate=1):
    if not is_valid_ssml(text):
        # Fallback: strip tags or log the issue
        text = strip_ssml_tags(text)

    client = texttospeech.TextToSpeechClient()

    # Detect if it's SSML
    if text.strip().startswith("<speak>"):
        synthesis_input = texttospeech.SynthesisInput(ssml=text)
    else:
        synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name,
        ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=speaking_rate
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    return response.audio_content


def autoplay_audio(audio_bytes: bytes, volume: float = 1.0):
    b64 = base64.b64encode(audio_bytes).decode()
    volume_js = f"{volume:.2f}"
    md = f"""
    <audio id="tts_audio" autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    <div>
      <button onclick="document.getElementById('tts_audio').play()">▶️ Play</button>
      <button onclick="document.getElementById('tts_audio').pause()">⏸️ Pause</button>
    </div>
    <script>
      const audio = document.getElementById('tts_audio');
      audio.volume = {volume_js};
    </script>
    """
    st.markdown(md, unsafe_allow_html=True)