# streamlit_app.py

import pandas as pd
import streamlit as st
from snowflake.snowpark import Session
from snowflake.cortex import Complete
import snowflake.snowpark.functions as F

# --- Page Setup ---
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.title("🎓 Alexandros Chionidis' assistant")
st.caption(
    """Ask me anything about Alexandros, education, early life, or skills"""
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

# Reset chat conversation
def reset_conversation():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi there! I’m Alexandros' assistant. "
                "What would you like to learn about him?"
            ),
        }
    ]

##########################################
#       Select LLM
##########################################
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
    st.button("Reset Chat", on_click=reset_conversation)

##########################################
#       RAG Helpers (unchanged)
##########################################
def get_context(chat, DOC_TABLE):
    chat_summary = summarize(chat)
    return find_similar_doc(chat_summary, DOC_TABLE)

def summarize(chat):
    summary = Complete(
        model,
        "Provide the most recent question with essential context from this support chat: "
        + chat,
    )
    return summary.replace("'", "")

def find_similar_doc(text, DOC_TABLE):
    docs = session.sql(f"""
        SELECT input_text,
               source_desc,
               VECTOR_COSINE_SIMILARITY(chunk_embedding, SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', '{text.replace("'", "''")}')) AS dist
        FROM {DOC_TABLE}
        ORDER BY dist DESC
        LIMIT 3
    """).to_pandas()
    
    for i, (source, score) in enumerate(zip(docs["SOURCE_DESC"], docs["DIST"])):
        st.info(f"Selected Source #{i+1} (Score: {score:.4f}): {source}")
    
    combined_text = "\n\n".join(docs["INPUT_TEXT"].tolist())
    return combined_text


##########################################
#       Prompt Construction
##########################################
if "background_info" not in st.session_state:
    st.session_state.background_info = (
        session.table("app.documents")
        .select("raw_text")
        .filter(F.col("relative_path") == "alexandros_chionidis_background.txt")
        .collect()[0][0]
    )

def get_prompt(chat, context):
    prompt = f"""
You are Alexandros Chionidis assistant and you know almost everything about his background and work experience.
You are having a conversation with a recruiter or interviewer interested in hiring a Data Engineer.

Use the background profile below and the relevant CV snippets to answer the user's latest question clearly, professionally, and concisely. 
Focus on highlighting skills, experience, education, and achievements relevant to a Data Engineer role.

Background Profile:
{st.session_state.background_info}

Relevant CV Snippet:
{context}

User’s Question:
{chat}

If you do not know the answer based on the information provided, reply politely:
"I'm sorry, I don't have that information at the moment, but I would be happy to provide it later."
If the user says a simple greeting like "hello" or "hi", respond with a short friendly greeting.

If the user input is unclear or empty, ask them to clarify.

Otherwise, answer the question clearly and professionally.
"""
    return prompt


##########################################
#       Chat with LLM
##########################################
if "messages" not in st.session_state:
    reset_conversation()

if user_message := st.chat_input(placeholder="Type your question about Alexandros Chionidis’ background…"):
    st.session_state.messages.append({"role": "user", "content": user_message})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    chat = str(st.session_state.messages[-CHAT_MEMORY:]).replace("'", "")
    with st.chat_message("assistant"):
        with st.status("Answering…", expanded=True):
            st.write("Retrieving relevant CV snippet…")
            context = get_context(chat, DOC_TABLE)
            st.write("Generating response…")
            prompt = get_prompt(chat, context)
            response = Complete(model, prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
