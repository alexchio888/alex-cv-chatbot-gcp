# Career.py

import streamlit as st
import json
from helping_functions.timeline_builder import *
from helping_functions.sidebar import *
from helping_functions.skills_builder import *


st.set_page_config(
    page_title="Career Timeline & Skills",
    page_icon="📊",
    layout="wide"
)
st.title("Skills & Career Overview")
st.markdown("Explore my professional timeline and, soon, a skills overview.")
if st.button("Take Me Back to the Chatbot ➡️"):
    st.switch_page("1_Alexandros_chatbot.py")
st.markdown("---")

render_sidebar(st.session_state, show_tabs=False)


# --- Skills ---
st.subheader("🧠 Skills Overview")
display_mode = st.selectbox(
    "Skill display mode:",
    ["Stars", "Text"]
)

with open("docs/skills.json", "r") as f:
    skills_json = json.load(f)

# Render the skills dashboard
render_skills_dashboard(skills_json)


# --- Timeline ---
st.markdown("---")
st.subheader("📅 Professional Timeline")

with open("docs/timeline.json", "r") as f:
    timeline_json = json.load(f)

# Collect unique tags
all_tags = sorted({tag for e in timeline_json["events"] for tag in e.get("tags", [])})

selected_tags = st.multiselect("Filter categories:", all_tags, default=all_tags)

filtered_events = [
    e for e in timeline_json["events"]
    if any(tag in e.get("tags", []) for tag in selected_tags)
]

filtered_json = {
    "title": timeline_json["title"],
    "events": filtered_events
}

if st.checkbox("Show timeline chart", value=True):
    fig = build_gantt_from_json(filtered_json)
    if fig and not fig.data == []:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No events match the selected categories.")

