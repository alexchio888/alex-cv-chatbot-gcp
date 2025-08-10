import json
import streamlit as st
from st_audiorec import st_audiorec
from helping_functions.stt_utils import *
from helping_functions.tts_utils import *
from snowflake.cortex import complete
from helping_functions.skills_builder import get_compact_skill_summary
import time

# --- Load skills summary (same as main page) ---
with open("docs/skills.json", "r") as f:
    skills_data = json.load(f)

skills_summary_text = get_compact_skill_summary(skills_data)
skills_context = skills_summary_text

st.title("Hands-Free Chatbot with Alexandros Clone")
selected_voice = 'en-US-Neural2-D'

# # --- Import or create cached Snowflake session ---
# @st.cache_resource
# def create_session():
#     connection_parameters = {
#         "account": st.secrets["account"],
#         "user": st.secrets["user"],
#         "password": st.secrets["password"],
#         "role": st.secrets["role"],
#         "warehouse": st.secrets["warehouse"],
#         "database": st.secrets["database"],
#         "schema": st.secrets["schema"],
#     }
#     from snowflake.snowpark import Session
#     return Session.builder.configs(connection_parameters).create()

# try:
#     session = create_session()
# except Exception as e:
#     st.error("⚠️ Unable to connect to Snowflake. Please check your credentials.")
#     st.stop()

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

        Respond concisely like you are having a live conversation. Your messages will be spoked back to the user.
        Respond with rich SSML tags exactly like below 

        <speak>....</speak>

        
        """

        # IMPORTANT: Pass the session explicitly to complete() if needed
        # Assuming your cortex complete() can accept a session parameter
        response = complete("mistral-large", prompt)

        audio = generate_google_tts_audio(response, selected_voice)
        autoplay_audio(audio)
        st.audio(audio, format="audio/mp3")


        st.markdown("**Raw model output:**")
        st.text(response)
    else:
        st.markdown(f"**You said:** Nothing")
