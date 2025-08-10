import streamlit as st
from helping_functions.stt_utils import transcribe_audio
from helping_functions.tts_utils import generate_google_tts_audio
from snowflake.cortex import complete

st.title("Hands-Free Chatbot with Alexandros Clone")

skills_context = skills_summary_text  # your compact CV text

audio_bytes = st_audiorec()  # record user audio
if audio_bytes:
    transcript = transcribe_audio(audio_bytes)
    if transcript:
        st.markdown(f"**You said:** {transcript}")

        # Compose prompt: just compact CV + question
        prompt = f"""
        You are Alexandros Chionidis' virtual clone with this career summary:
        {skills_context}

        Answer this question concisely:
        {transcript}
        Respond with JSON: {{"text": "...", "tts": "<speak>...</speak>"}}
        """

        # Call model
        response_json = complete("mistral-small", prompt)
        response = json.loads(response_json)
        text_reply = response["text"]
        tts_ssml = response["tts"]

        st.markdown(f"**Alexandros:** {text_reply}")

        # Generate and play audio
        audio_mp3 = generate_google_tts_audio(tts_ssml)
        st.audio(audio_mp3, format="audio/mp3", start_time=0)

        # No typing animation, just instant display + playback
