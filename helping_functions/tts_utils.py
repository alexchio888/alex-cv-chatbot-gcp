# tts_utils.py
from google.cloud import texttospeech
import base64

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

def generate_google_tts_audio(text, voice_name, speaking_rate=1.0):
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name,
        ssml_gender=texttospeech.SsmlVoiceGender.MALE  # Or you can also make gender selectable
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


def autoplay_audio(audio_bytes: bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    md = f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
