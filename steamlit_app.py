# streamlit_app.py

import pandas as pd
import streamlit as st
from snowflake.snowpark import Session
from snowflake.cortex import Complete
import snowflake.snowpark.functions as F

# --- Page Setup ---
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.title(":truck: Sou aresoun ta large??? Tasty Bytes Support: Customer Q&A Assistant :truck:")
st.caption(
    "This app suggests answers to customer questions based on documentation and past support chats."
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
CHAT_MEMORY = 20
DOC_TABLE = "app.vector_store"

# --- Reset Chat ---
def reset_conversation():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "What question do you need assistance answering?",
        }
    ]

# --- Model Selection ---
with st.expander(":gear: Settings"):
    model = st.selectbox(
        "Change chatbot model:",
        ["mistral-large", "reka-flash", "llama2-70b-chat", "gemma-7b", "mixtral-8x7b", "mistral-7b"],
    )
    st.button("Reset Chat", on_click=reset_conversation)

# --- RAG Helpers ---
def get_context(chat):
    summary = Complete(model, f"Summarize this support chat: {chat}")
    return find_similar_doc(summary)

def find_similar_doc(text):
    query = f"""
        SELECT input_text, source_desc,
            VECTOR_COSINE_SIMILARITY(chunk_embedding,
                SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', '{text.replace("'", "''")}')
            ) AS dist
        FROM {DOC_TABLE}
        ORDER BY dist DESC
        LIMIT 1
    """
    doc = session.sql(query).to_pandas()
    st.info("Selected Source: " + doc["SOURCE_DESC"].iloc[0])
    return doc["INPUT_TEXT"].iloc[0]

# --- Load Background Info ---
@st.cache_data
def load_background_info():
    return (
        session.table("app.documents")
        .select("raw_text")
        .filter(F.col("relative_path") == "tasty_bytes_who_we_are.pdf")
        .collect()[0][0]
    )

background_info = load_background_info()

# --- Prompt Construction ---
def get_prompt(chat, context):
    return f"""
    Answer the customer's latest question based on this chat: <chat> {chat} </chat>.
    Use this context from internal documents or past support chats: <context> {context} </context>.
    Include this background info: <background_info> {background_info} </background_info>.
    Be concise, helpful, and only answer the question.
    """.replace("'", "")

# --- Chat UI ---
if "messages" not in st.session_state:
    reset_conversation()

if user := st.chat_input("Ask a support question..."):
    st.session_state.messages.append({"role": "user", "content": user})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    chat = str(st.session_state.messages[-CHAT_MEMORY:]).replace("'", "")
    with st.chat_message("assistant"):
        with st.status("Answering...", expanded=True) as status:
            st.write("Finding relevant documents...")
            context = get_context(chat)
            st.write("Generating response...")
            prompt = get_prompt(chat, context)
            response = Complete(model, prompt)
            status.update(label="Complete!", state="complete", expanded=False)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
