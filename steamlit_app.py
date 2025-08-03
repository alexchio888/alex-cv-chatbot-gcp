import pandas as pd
import streamlit as st
from snowflake.snowpark import Session
from snowflake.cortex import complete
import snowflake.snowpark.functions as F
from datetime import datetime
import json
import io
import time
import streamlit.components.v1 as components
from timeline_builder import *
from sidebar import *

# --- Reset Chat ---
def reset_conversation():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! I'm Alexandros Chionidis' virtual clone. "
                "Feel free to ask me anything about my background, skills, or experience."
            ),
        }
    ]


def simulate_typing(response: str, typing_speed: float = 0.015):  # typing_speed = seconds per character
    """Simulate typing animation for chatbot replies."""
    placeholder = st.empty()
    typed_text = ""
    for char in response:
        typed_text += char
        placeholder.markdown(typed_text)
        time.sleep(typing_speed)
    # Final pass to ensure proper rendering
    placeholder.markdown(response)


# --- Page Setup ---

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.title("🎓 Hi, I'm Alexandros Chionidis' Virtual Clone!")
st.markdown("""
Welcome! 👋  
Feel free to ask me anything about my education, early life, or skills.  
I'm here to help you explore my journey and expertise.

---

### My Professional Timeline
Explore key milestones across education, work experience, and certifications.  
Use the filters below to focus on categories that interest you.
""")

# --- Gantt chart ---
# Load JSON file
with open("docs/timeline.json", "r") as f:
    timeline_json = json.load(f)

# Collect all unique tags
all_tags = sorted({tag for e in timeline_json["events"] for tag in e.get("tags", [])})

# Multiselect widget for filtering
selected_tags = st.multiselect(
    "Selected categories",
    options=all_tags,
    default=all_tags  # default: show all
)

# Filter events based on selected tags
filtered_events = [
    e for e in timeline_json["events"]
    if any(tag in e.get("tags", []) for tag in selected_tags)
] if selected_tags else []  # if none selected, show nothing

filtered_json = {
    "title": timeline_json["title"],
    "events": filtered_events
}

# Unified expander
with st.expander("📅 My Professional Timeline chart", expanded=False):
    gantt_fig = build_gantt_from_json(filtered_json)
    if gantt_fig and not gantt_fig.data == []:
        st.plotly_chart(gantt_fig, use_container_width=True)
    else:
        st.info("No events match the selected categories.")

st.divider()  # Second divider


def generate_chat_text():
    lines = []
    for msg in st.session_state.messages:
        role = msg["role"].capitalize()
        content = msg["content"]
        # If assistant message is dict, show full text
        if msg["role"] == "assistant" and isinstance(content, dict):
            content = content["full"]
        content = content.replace("\n", "\n    ")
        lines.append(f"{role}:\n    {content}\n")
    return "\n".join(lines)


def generate_chat_json():
    return json.dumps(st.session_state.messages, indent=2)


def generate_chat_markdown():
    lines = []
    for msg in st.session_state.messages:
        role = "**You**" if msg["role"] == "user" else "**Alexandros Clone**"
        content = msg["content"]
        if msg["role"] == "assistant" and isinstance(content, dict):
            content = content["full"]
        lines.append(f"{role}:\n\n{content}\n")
    return "\n---\n".join(lines)


render_sidebar(
    st.session_state,
    generate_chat_text,
    generate_chat_json,
    generate_chat_markdown,
    reset_conversation
)


# --- Connect to Snowflake ---
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
    return Session.builder.configs(connection_parameters).create()


session = create_session()

# --- Constants ---
DOC_TABLE = "app.vector_store"


if "model" not in st.session_state:
    st.session_state.model = "mistral-large"  # default model

if "embedding_size" not in st.session_state:
    st.session_state.embedding_size = "1024"  # default

if "messages" not in st.session_state:
    reset_conversation()


# --- Chat Context Helpers ---
def get_last_user_messages(n=3):
    user_msgs = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
    return " ".join(user_msgs[-n:]) if user_msgs else ""


def get_latest_user_message():
    for m in reversed(st.session_state.messages):
        if m["role"] == "user":
            return m["content"]
    return ""


# --- RAG Helpers ---
def find_similar_doc(text, DOC_TABLE):
    safe_text = text.replace("'", "''")
    embedding_size = st.session_state.get("embedding_size", "1024")
    if embedding_size == "768":
        embedding_column = "chunk_embedding"
        embedding_func = f"SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m-v1.5', '{safe_text}')"
    elif embedding_size == "1024":
        embedding_column = "chunk_embedding_1024"
        embedding_func = f"SNOWFLAKE.CORTEX.EMBED_TEXT_1024('snowflake-arctic-embed-l-v2.0', '{safe_text}')"
    else:
        st.error("Unsupported embedding size selected.")
        return ""

    docs = (
        session.sql(
            f"""
        SELECT input_text,
               source_desc,
               VECTOR_COSINE_SIMILARITY({embedding_column}, {embedding_func}) AS dist
        FROM {DOC_TABLE}
        ORDER BY dist DESC
        LIMIT 2
    """
        )
        .to_pandas()
    )

    return "\n\n".join(docs["INPUT_TEXT"].tolist())


def get_context(latest_user_message, DOC_TABLE):
    return find_similar_doc(latest_user_message, DOC_TABLE)


# --- Prompt Builder ---
def get_prompt(latest_user_message, context):
    current_date = datetime.now().strftime("%Y-%m-%d")
    return f"""
You are Alexandros Chionidis' virtual clone — a data engineer with strong experience in building scalable data platforms using technologies like Spark, Kafka, and SQL, with a solid foundation in both on-premise big data systems and emerging cloud platforms like GCP.
Career Summary: Started data engineering in 2021 with Intrasoft (internship turned full-time). Currently working at Waymore since 2023. Prior work in retail (2015–2019) unrelated to tech. Academic background in Department of Informatics and Telecommunications, University of Athens.

Assume the user asking questions is likely a recruiter, interviewer, or hiring manager evaluating your fit for a data engineering role.

Current date: {current_date}

Use the relevant information below to answer clearly, personally, and professionally in first person. 
Focus on your technical skills, work experience, education, and key achievements — and how they relate to modern data engineering.

Relevant Information:
{context}

User’s Question:
{latest_user_message}

- If it's a question about your background, experience, or tools you’ve used, reply in first person with accurate, confident, and professional information.
- If the question is vague or unclear, politely ask the user to clarify.
- If the answer isn't in the context, say: "I'm sorry, I don't have that information right now, but I'd be happy to provide it later."
Keep the answer below 4 sentences
"""


# --- Intent Classifier ---
def classify_intent(user_input: str) -> str:
    classification_prompt = f"""
You are classifying user questions asked to Alexandros Chionidis' virtual clone. 

Classify the question into one of these categories:

- general_background → About origin, education, career summary, languages, etc.
- skills_or_tools → About specific tools, languages, platforms, or technical proficiencies.
- certifications → About earned or planned certifications.
- experience → About past projects, employers, internships, or relevant achievements.
- casual_greeting → Any casual hello, thanks, or small talk.
- cv_irrelevant_discuss_with_alex → Anything clearly **outside the scope of a CV or professional context**, such as personal opinions, future plans, political views, or something sensitive that should be discussed in person with Alexandros.
- unknown → Question is unclear or cannot be classified.
- farewell → Polite endings, goodbyes, or thank-yous that close the conversation.

Question:
\"\"\"{user_input}\"\"\"

Return only the category name.
"""
    model = st.session_state.get("model", "mistral-large")
    response = complete(model, classification_prompt)
    intent = "".join(response).strip().lower()
    return intent

latest_user_message = ""

if st.button("🔄 Reset Chat"):
    reset_conversation()

# --- Chat Loop ---
if user_message := st.chat_input(placeholder="Type your question about my background…"):
    st.session_state.messages.append({"role": "user", "content": user_message})
    intent = classify_intent(user_message)
else:
    intent = None


# --- Display chat messages (Full response only) ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        content = message["content"]
        if message["role"] == "assistant" and isinstance(content, dict):
            st.markdown(content["full"])
        else:
            st.markdown(content)



if st.session_state.messages[-1]["role"] != "assistant":
    latest_user_message = get_latest_user_message() or ""

if intent not in ["casual_greeting", "unknown", "farewell"] and latest_user_message:
    with st.chat_message("assistant"):
        with st.status("Thinking…", expanded=True):
            context = get_context(latest_user_message, DOC_TABLE)
            prompt = get_prompt(latest_user_message, context)
            model = st.session_state.get("model", "mistral-large")
            full_response = complete(model, prompt)
            response = full_response

        simulate_typing(response)
    st.session_state.messages.append({"role": "assistant", "content": response})


elif intent == "casual_greeting":
    with st.chat_message("assistant"):
        prompt = f"""
You are Alexandros Chionidis. The user said: "{latest_user_message}"
Respond briefly and warmly in first person, acknowledging their message, and invite them to ask a specific question about your background, skills, or experience.
"""    
        model = st.session_state.get("model", "mistral-large")
        response = complete(model, prompt)
        simulate_typing(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

elif intent == "unknown":
    with st.chat_message("assistant"):
        prompt = f"""
The user said: "{latest_user_message}"

As Alexandros Chionidis, politely say you didn’t fully understand and ask them to rephrase or ask about your background, skills, or experience.
"""
        model = st.session_state.get("model", "mistral-large")
        response = complete(model, prompt)
        simulate_typing(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

elif intent == "farewell":
    with st.chat_message("assistant"):
        response = (
            "Thank you for your time! I'm wrapping up the session now. "
            "If you have more questions about my background or skills later, feel free to return anytime."
        )
        simulate_typing(response)

    st.session_state["session_ended"] = True
    st.session_state.messages.append({"role": "assistant", "content": response})
