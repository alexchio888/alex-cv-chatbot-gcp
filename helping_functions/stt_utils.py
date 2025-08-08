import streamlit as st
from google.cloud import speech
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av
import numpy as np
import tempfile

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv_audio_frame(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Convert audio to numpy array
        audio = frame.to_ndarray()
        self.frames.append(audio)
        return frame

    def get_audio_bytes(self):
        if not self.frames:
            return None
        audio_data = np.concatenate(self.frames, axis=1).tobytes()
        self.frames.clear()
        return audio_data


def record_audio():
    """
    Opens a microphone input using streamlit-webrtc and records audio.
    Returns raw audio bytes or None.
    """
    ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False}
    )

    audio_bytes = None
    if ctx.audio_processor:
        if st.button("Stop Recording"):
            audio_bytes = ctx.audio_processor.get_audio_bytes()

    return audio_bytes


def transcribe_audio(audio_bytes, language_code="en-US"):
    """
    Transcribes recorded audio using Google Cloud Speech-to-Text.
    """
    if not audio_bytes:
        return ""

    # Save temporary WAV file (Google API works best with PCM16 WAV)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        tmpfile.write(audio_bytes)
        tmpfile_path = tmpfile.name

    client = speech.SpeechClient()

    with open(tmpfile_path, "rb") as f:
        content = f.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,  # streamlit-webrtc default
        language_code=language_code
    )

    response = client.recognize(config=config, audio=audio)

    if response.results:
        return response.results[0].alternatives[0].transcript.strip()
    return ""
