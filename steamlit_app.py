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
st.title("🎓 Alexandros Chionidis' clone")
st.caption("Ask me anything about my education, early life, or skills")

# Load JSON file
with open("docs/timeline.json", "r") as f:
    timeline_json = json.load(f)

# # Generate timeline HTML
# timeline_html = timeline_builder(timeline_json)

# # Render timeline in Streamlit
# st.components.v1.html(timeline_html, height=600, scrolling=True)

with st.expander("Show Timeline Gantt Chart"):
    gantt_fig = build_gantt_from_json(timeline_json)
    st.plotly_chart(gantt_fig, use_container_width=True)

# # --- Real Me Contact Card ---
# with st.sidebar.expander("📇 Contact Alexandros", expanded=True):
#     st.markdown("**Alexandros Chionidis**")
#     maps_url = "https://www.google.com/maps/place/Melissia,+Athens,+Greece"
#     st.markdown(
#         f"""
#     <a href="{maps_url}" target="_blank" style="text-decoration:none; font-weight:bold;">
#         🏠 Melissia, Athens, Greece
#     </a>
#     """,
#         unsafe_allow_html=True,
#     )

#     linkedin_html = """
#     <a href="https://www.linkedin.com/in/alexandros-chionidis-51579421b/" target="_blank" style="text-decoration:none;">
#         <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="24" style="vertical-align:middle; margin-right:8px;"/> LinkedIn
#     </a>
#     """

#     github_html = """
#     <a href="https://github.com/alexchio888" target="_blank" style="text-decoration:none;">
#         <img src="https://cdn-icons-png.flaticon.com/512/733/733553.png" width="24" style="vertical-align:middle; margin-right:8px;"/> GitHub
#     </a>
#     """

#     email_html = """
#     <a href="mailto:alexandroschio@gmail.com" target="_blank" style="text-decoration:none;">
#         <img src="https://cdn-icons-png.flaticon.com/512/732/732200.png" width="24" style="vertical-align:middle; margin-right:8px;"/> Email
#     </a>
#     """

#     st.markdown(linkedin_html, unsafe_allow_html=True)
#     st.markdown(github_html, unsafe_allow_html=True)
#     st.markdown(email_html, unsafe_allow_html=True)

#     cv_html = """
#     <a href="https://github.com/alexchio888/cv-chatbot/raw/main/docs/Alexandros_Chionidis_CV.pdf" target="_blank" style="text-decoration:none;">
#         <img src="https://cdn-icons-png.flaticon.com/512/337/337946.png" width="24" style="vertical-align:middle; margin-right:8px;"/> Download CV
#     </a>
#     """
#     st.markdown(cv_html, unsafe_allow_html=True)

# # --- Suggested Prompts (Sidebar) ---
# st.sidebar.markdown("---")  # separator line

# st.sidebar.markdown("### 💡 Try asking about:")
# categories = {
#     "Education": [
#         "Where did you study?",
#         "Tell me about your academic background.",
#     ],
#     "Work Experience": [
#         "What was your role at Intrasoft?",
#         "Describe your work at Waymore.",
#         "What projects did you do in retail before tech?",
#     ],
#     "Skills & Tools": [
#         "What technologies are you proficient with?",
#         "How do you use Spark and Kafka in your work?",
#         "Tell me about your experience with GCP.",
#     ],
#     "Certifications": [
#         "Do you have any certifications?",
#         "Are you planning to get any certifications soon?",
#     ],
#     "Projects": [
#         "Can you describe a key data engineering project?",
#         "What was your biggest technical challenge?",
#     ],
# }

# for category, prompts in categories.items():
#     with st.sidebar.expander(category, expanded=False):
#         for prompt in prompts:
#             if st.button(prompt, key=prompt):
#                 # Insert prompt as a user message and rerun app to trigger chat
#                 st.session_state.messages.append({"role": "user", "content": prompt})



# --- Formatters ---
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


# # --- Sidebar: Download Chat History ---
# with st.sidebar.expander("💬 Download Chat History", expanded=False):
#     if "messages" in st.session_state and st.session_state.messages:
#         chat_txt = generate_chat_text()
#         chat_json = generate_chat_json()
#         chat_md = generate_chat_markdown()

#         st.download_button(
#             label="📄 Download as TXT",
#             data=chat_txt,
#             file_name="alexandros_clone_chat.txt",
#             mime="text/plain",
#         )

#         st.download_button(
#             label="🧾 Download as JSON",
#             data=chat_json,
#             file_name="alexandros_clone_chat.json",
#             mime="application/json",
#         )

#         st.download_button(
#             label="📝 Download as Markdown",
#             data=chat_md,
#             file_name="alexandros_clone_chat.md",
#             mime="text/markdown",
#         )
#     else:
#         st.info("No chat history to download yet.")


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

# # --- UI Settings ---
# with st.expander("⚙️ Settings"):
#     model = st.selectbox(
#         "Change chatbot model:",
#         [
#             "mistral-large",
#             "reka-flash",
#             "llama2-70b-chat",
#             "gemma-7b",
#             "mixtral-8x7b",
#             "mistral-7b",
#         ],
#     )

#     embedding_size = st.selectbox(
#         "Select embedding dimension:",
#         ["1024", "768"],
#         index=0,
#         format_func=lambda x: f"{x}-dim embedding",
#     )

#     st.button("Reset Chat", on_click=lambda: reset_conversation())




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
    response = complete(model, classification_prompt)
    intent = "".join(response).strip().lower()
    return intent

latest_user_message = ""

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
        response = complete(model, prompt)
        simulate_typing(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

elif intent == "unknown":
    with st.chat_message("assistant"):
        prompt = f"""
The user said: "{latest_user_message}"

As Alexandros Chionidis, politely say you didn’t fully understand and ask them to rephrase or ask about your background, skills, or experience.
"""
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
