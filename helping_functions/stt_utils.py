# stt_utils.py
from google.cloud import speech
import io
import wave
import audioop

def stereo_to_mono_wav(wav_bytes):
    with io.BytesIO(wav_bytes) as wav_io:
        with wave.open(wav_io, 'rb') as wav:
            params = wav.getparams()
            if params.nchannels == 1:
                # Already mono
                return wav_bytes
            frames = wav.readframes(params.nframes)
            # Convert stereo to mono
            mono_frames = audioop.tomono(frames, params.sampwidth, 1, 1)

            # Write mono data to new WAV bytes
            out_io = io.BytesIO()
            with wave.open(out_io, 'wb') as out_wav:
                out_wav.setnchannels(1)
                out_wav.setsampwidth(params.sampwidth)
                out_wav.setframerate(params.framerate)
                out_wav.writeframes(mono_frames)

            return out_io.getvalue()
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
    mono_audio_bytes = stereo_to_mono_wav(audio_bytes)
    audio_bytes = transcribe_audio(mono_audio_bytes)
    if not audio_bytes:
        return ""

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(content=audio_bytes)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=sample_rate_hertz,
        language_code=language_code,
        enable_automatic_punctuation=True,
        model="default",
    )

    response = client.recognize(config=config, audio=audio)

    if not response.results:
        return ""

    transcripts = [result.alternatives[0].transcript for result in response.results]
    return " ".join(transcripts).strip()
