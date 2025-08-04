# Career.py

import streamlit as st
import json
from pages.timeline_builder import build_gantt_from_json


st.set_page_config(
    page_title="Career Timeline & Skills",
    page_icon="📊",
    layout="wide"
)
st.title("Alexandros' Career Overview")
st.markdown("Explore my professional timeline and, soon, a skills overview.")

# --- Timeline ---
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

# --- Skills placeholder ---
st.subheader("🧠 Skills Overview (Coming Soon)")
st.info("This section will show my ranked skills, tools, and strengths in the near future.")
