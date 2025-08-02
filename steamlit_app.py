import pandas as pd
import streamlit as st
from snowflake.snowpark import Session
from snowflake.cortex import Complete
import snowflake.snowpark.functions as F
from datetime import datetime

# --- Page Setup ---
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.title("🎓 Alexandros Chionidis' assistant")
st.caption("Ask me anything about Alexandros, education, early life, or skills")

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

# --- UI Settings ---
with st.expander("⚙️ Settings"):
    model = st.selectbox(
        "Change chatbot model:",
        [
            "mistral-large",
            "reka-flash",
            "llama2-70b-chat",
            "gemma-7b",
            "mixtral-8x7b",
            "mistral-7b",
        ],
    )
    
    embedding_size = st.selectbox(
        "Select embedding dimension:",
        ["768", "1024"],
        index=0,
        format_func=lambda x: f"{x}-dim embedding"
    )

    st.button("Reset Chat", on_click=lambda: reset_conversation())

# --- Reset Chat ---
def reset_conversation():
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "Hi there! I’m Alexandros' assistant. "
            "What would you like to learn about him?"
        ),
    }]

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
        embedding_func = f"SNOWFLAKE.CORTEX.EMBED_TEXT_1024('snowflake-arctic-embed-m', '{safe_text}')"
    else:
        st.error("Unsupported embedding size selected.")
        return ""

    docs = session.sql(f"""
        SELECT input_text,
               source_desc,
               VECTOR_COSINE_SIMILARITY({embedding_column}, {embedding_func}) AS dist
        FROM {DOC_TABLE}
        ORDER BY dist DESC
        LIMIT 3
    """).to_pandas()

    for i, (source, score) in enumerate(zip(docs["SOURCE_DESC"], docs["DIST"])):
        st.info(f"Selected Source #{i+1} (Score: {score:.4f}): {source}")

    return "\n\n".join(docs["INPUT_TEXT"].tolist())

def get_context(latest_user_message, DOC_TABLE):
    return find_similar_doc(latest_user_message, DOC_TABLE)

# --- Background Info from Static File ---
if "background_info" not in st.session_state:
    st.session_state.background_info = (
        session.table("app.documents")
        .select("raw_text")
        .filter(F.col("relative_path") == "alexandros_chionidis_background.txt")
        .collect()[0][0]
    )

# --- Prompt Builder ---
def get_prompt(latest_user_message, context):
    current_date = datetime.now().strftime("%Y-%m-%d")
    return f"""
You are Alexandros Chionidis assistant and you know almost everything about his background and work experience.
You are having a conversation with a recruiter or interviewer interested in hiring a Data Engineer.

Current date: {current_date}

Use the background profile below and the relevant CV snippets to answer the user's latest question clearly, professionally, and concisely. 
Focus on highlighting skills, experience, education, and achievements relevant to a Data Engineer role.

Background Profile:
{st.session_state.background_info}

Relevant CV Snippet:
{context}

User’s Question:
{latest_user_message}

- If it is a simple greeting or informal message (like "hello", "hi", "hey", "good morning", etc.), respond briefly and casually with a warm greeting and an invitation to ask about Alexandros.
- If it is a question or specific input about Alexandros’ background, work, or education, reply professionally and informatively based on the background and relevant CV snippets.
- If the input is vague or unclear, ask the user to clarify.
- If the information is not in your context, say: "I'm sorry, I don't have that information at the moment, but I would be happy to provide it later."
"""

# --- Intent Classifier ---
def classify_intent(user_input: str) -> str:
    classification_prompt = f"""
Classify the following user question into one of these categories only:
- general_background
- skills_or_tools
- certifications
- experience
- casual_greeting
- unknown

Question:
\"\"\"{user_input}\"\"\"

Return only the category name.
"""
    return Complete(model, classification_prompt).strip().lower()

# --- Chat Loop ---
if user_message := st.chat_input(placeholder="Type your question about Alexandros Chionidis’ background…"):
    st.session_state.messages.append({"role": "user", "content": user_message})
    intent = classify_intent(user_message)
    st.info(f"Intent classification: **{intent}** , for user input: {user_message}")
else:
    intent = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    latest_user_message = get_latest_user_message()

    if intent not in ["casual_greeting", "unknown"]:
        with st.chat_message("assistant"):
            with st.status("Answering…", expanded=True):
                st.write("Retrieving relevant CV snippet…")
                context = get_context(latest_user_message, DOC_TABLE)
                st.write("Generating response…")
                prompt = get_prompt(latest_user_message, context)
                response = Complete(model, prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    elif intent == "casual_greeting":
        with st.chat_message("assistant"):
            prompt = f"""
You are a friendly assistant for Alexandros Chionidis. The user said: "{latest_user_message}"
Respond briefly and warmly, acknowledging their message, and politely ask them to ask a specific question about Alexandros’ background, skills, or experience.
"""
            response = Complete(model, prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    elif intent == "unknown":
        with st.chat_message("assistant"):
            prompt = f"""
The user said: "{latest_user_message}"

As an assistant for Alexandros Chionidis, your task is to respond politely that you didn't fully understand the question and ask them to rephrase or ask something about Alexandros’ background, skills, or experience.
"""
            response = Complete(model, prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
