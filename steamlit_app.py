import pandas as pd
import streamlit as st
from snowflake.snowpark import Session
from snowflake.cortex import Complete
import snowflake.snowpark.functions as F
from datetime import datetime

# --- Page Setup ---
st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.title("🎓 Alexandros Chionidis' clone")
st.caption("Ask me anything about my education, early life, or skills")

# --- Real Me Contact Card ---
with st.sidebar.expander("📇 Contact Alexandros", expanded=True):
    st.markdown("**Alexandros Chionidis**")
    st.markdown("📍Melissia, Athens, Greece")
    st.markdown("📧 [alexchionidis@gmail.com](mailto:alexchionidis@gmail.com)")
    st.markdown("🔗 [LinkedIn](https://www.linkedin.com/in/alexandros-chionidis-51579421b/)")
    st.markdown("📁 [GitHub](https://github.com/alexchio888)")
    st.markdown("🧾 [CV Download](https://github.com/alexchio888/cv-chatbot/blob/main/docs/Alexandros_Chionidis_CV.pdf)")

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
        ["1024", "768"],
        index=0,
        format_func=lambda x: f"{x}-dim embedding"
    )

    st.button("Reset Chat", on_click=lambda: reset_conversation())

# --- Reset Chat ---
def reset_conversation():
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "Hi! I'm Alexandros Chionidis' virtual clone. "
            "Feel free to ask me anything about my background, skills, or experience."
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
        embedding_func = f"SNOWFLAKE.CORTEX.EMBED_TEXT_1024('snowflake-arctic-embed-l-v2.0', '{safe_text}')"
    else:
        st.error("Unsupported embedding size selected.")
        return ""

    docs = session.sql(f"""
        SELECT input_text,
               source_desc,
               VECTOR_COSINE_SIMILARITY({embedding_column}, {embedding_func}) AS dist
        FROM {DOC_TABLE}
        ORDER BY dist DESC
        LIMIT 2
    """).to_pandas()

    for i, (source, score) in enumerate(zip(docs["SOURCE_DESC"], docs["DIST"])):
        st.info(f"Selected Source #{i+1} (Score: {score:.4f}): {source}")

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
    return Complete(model, classification_prompt).strip().lower()

# --- Chat Loop ---
if user_message := st.chat_input(placeholder="Type your question about my background…"):
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

    if intent not in ["casual_greeting", "unknown","farewell"]:
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
You are Alexandros Chionidis. The user said: "{latest_user_message}"
Respond briefly and warmly in first person, acknowledging their message, and invite them to ask a specific question about your background, skills, or experience.
"""
            response = Complete(model, prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    elif intent == "unknown":
        with st.chat_message("assistant"):
            prompt = f"""
The user said: "{latest_user_message}"

As Alexandros Chionidis, politely say you didn’t fully understand and ask them to rephrase or ask about your background, skills, or experience.
"""
            response = Complete(model, prompt)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    elif intent == "farewell":
        with st.chat_message("assistant"):
            response = (
                "Thank you for your time! I'm wrapping up the session now. "
                "If you have more questions about my background or skills later, feel free to return anytime."
            )
            st.markdown(response)

        # Optionally clear or flag the session
        st.session_state["session_ended"] = True
        st.session_state.messages.append({"role": "assistant", "content": response})
