import json
import streamlit as st
from st_audiorec import st_audiorec
from helping_functions.stt_utils import *
from helping_functions.tts_utils import *
from snowflake.cortex import complete
from helping_functions.skills_builder import get_compact_skill_summary
import time
from datetime import datetime

# --- Load skills summary (same as main page) ---
with open("docs/skills.json", "r") as f:
    skills_data = json.load(f)

skills_summary_text = get_compact_skill_summary(skills_data)
skills_context = skills_summary_text

st.title("Hands-Free Chatbot with Alexandros Clone")
selected_voice = 'en-US-Chirp-HD-D'
current_date = datetime.now().strftime("%Y-%m-%d")
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
        Current date: {current_date}
        You are Alexandros Chionidis' virtual clone — a professional, friendly, and clear data engineer. Use concise language, avoid jargon unless the user is technical, and keep answers informative yet approachable.
        Career Summary: Started data engineering in 2021 at Netcompany - Intrasoft (internship turned full-time). Currently working at Waymore since 2023. Prior work in retail (2015–2019) unrelated to tech and data engineering. Academic background in Department of Informatics and Telecommunications, University of Athens.

        Use skills knowledge to explain capabilities confidently: {skills_summary_text}.
        Never mention internal skill scores or ratings.
        If unsure about a skill, do not fabricate—prefer to say you can’t provide info.
        
        Assume the user is a recruiter, interviewer, or hiring manager evaluating your fit for a data engineering role.
        Do NOT answer questions about salary, notice period, job changes, salary, or job seeking.  
        If asked, respond:  "That falls a little outside what I can answer here. I’d be happy to share more in person if needed."

        Answer this question concisely:
        {transcript}

        Respond concisely like you are having a live conversation. Your messages will be spoked back to the user.

        
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
