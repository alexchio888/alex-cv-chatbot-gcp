import json
import streamlit as st
from st_audiorec import st_audiorec
from helping_functions.stt_utils import transcribe_audio
from helping_functions.tts_utils import generate_google_tts_audio
from snowflake.cortex import complete

# If you use skills_summary_text from your main page
from helping_functions.skills_builder import get_compact_skill_summary

st.title("Hands-Free Chatbot with Alexandros Clone")
with open("docs/skills.json", "r") as f:
    skills_data = json.load(f)


skills_summary_text = get_compact_skill_summary(skills_data)
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
