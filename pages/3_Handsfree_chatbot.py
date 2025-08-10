import json
import streamlit as st
from st_audiorec import st_audiorec
from helping_functions.stt_utils import transcribe_audio
from helping_functions.tts_utils import generate_google_tts_audio
from snowflake.cortex import complete
from helping_functions.skills_builder import get_compact_skill_summary

# --- Load skills summary (same as main page) ---
with open("docs/skills.json", "r") as f:
    skills_data = json.load(f)

skills_summary_text = get_compact_skill_summary(skills_data)
skills_context = skills_summary_text

st.title("Hands-Free Chatbot with Alexandros Clone")

# --- Import or create cached Snowflake session ---
@st.cache_resource
def create_session():
    connection_parameters = {
        "account": st.secrets["account"],
        "user": st.secrets["user"],
        "password": st.secrets["password"],
        "role": st.secrets["role"],
        "warehouse": st.secrets["warehouse"],
        "database": st.secrets["database"],
        "schema": st.secrets["schema"],
    }
    from snowflake.snowpark import Session
    return Session.builder.configs(connection_parameters).create()

try:
    session = create_session()
except Exception as e:
    st.error("⚠️ Unable to connect to Snowflake. Please check your credentials.")
    st.stop()

# --- Record audio ---
audio_bytes = st_audiorec()

if audio_bytes:
    transcript = transcribe_audio(audio_bytes)
    if transcript:
        st.markdown(f"**You said:** {transcript}")

        prompt = f"""
        You are Alexandros Chionidis' virtual clone with this career summary:
        {skills_context}

        Answer this question concisely:
        {transcript}

        Respond only with SSML text for TTS (no other text).
        """

        # IMPORTANT: Pass the session explicitly to complete() if needed
        # Assuming your cortex complete() can accept a session parameter
        try:
            response = complete("mistral-small", prompt, session=session)
        except TypeError:
            # If complete() does not accept session param, 
            # it should pick credentials from environment / config
            response = complete("mistral-small", prompt)

        st.markdown("**Raw model output:**")
        st.text(response)
