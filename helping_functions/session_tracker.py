from snowflake.snowpark import Session
from datetime import datetime
import uuid
import streamlit as st
import streamlit.components.v1 as components

TABLE_NAME = "CHAT_LOGS"

def log_message_to_snowflake(
    session: Session,
    session_id: str,
    role: str,
    message: str,
    *,
    intent: str = None,
    model_used: str = None,
    embedding_size: str = None,
    context_snippet: str = None,
    prompt: str = None,
    message_type: str = None
):
    timestamp = datetime.utcnow().isoformat()
    
    # Escape strings
    escape = lambda s: s.replace("'", "''") if s else None
    message = escape(message)[:2000] if message else None
    prompt = escape(prompt)[:5000] if prompt else None
    context_snippet = escape(context_snippet)[:5000] if context_snippet else None
    
    session.sql(f"""
        INSERT INTO {TABLE_NAME} (
            session_id, timestamp, role, message,
            intent, model_used, embedding_size,
            context_snippet, prompt, message_type
        )
        VALUES (
            '{escape(session_id)}', '{timestamp}', '{escape(role)}', '{message}',
            {'NULL' if not intent else f"'{escape(intent)}'"},
            {'NULL' if not model_used else f"'{escape(model_used)}'"},
            {'NULL' if not embedding_size else f"'{escape(embedding_size)}'"},
            {'NULL' if not context_snippet else f"'{context_snippet}'"},
            {'NULL' if not prompt else f"'{prompt}'"},
            {'NULL' if not message_type else f"'{escape(message_type)}'"}
        )
    """).collect()


def ensure_user_id():
    """Ensures a persistent user_id using browser cookie via JS."""
    if "user_id" in st.session_state:
        return st.session_state["user_id"]

    generated_id = str(uuid.uuid4())

    # This JS reads the cookie or sets it if missing, then passes it to Streamlit via window.postMessage
    components.html(f"""
        <script>
        const COOKIE_NAME = "user_id";
        function setCookie(name, value, days) {{
            let expires = "";
            if (days) {{
                const date = new Date();
                date.setTime(date.getTime() + (days*24*60*60*1000));
                expires = "; expires=" + date.toUTCString();
            }}
            document.cookie = name + "=" + (value || "") + expires + "; path=/";
        }}

        function getCookie(name) {{
            const nameEQ = name + "=";
            const ca = document.cookie.split(';');
            for(let i=0;i < ca.length;i++) {{
                let c = ca[i].trim();
                if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
            }}
            return null;
        }}

        const uid = getCookie(COOKIE_NAME) || "{generated_id}";
        setCookie(COOKIE_NAME, uid, 365);

        window.parent.postMessage({{ user_id: uid }}, "*");
        </script>
    """, height=0)

    # Temporary placeholder — updated below via JS event
    st.session_state["user_id"] = generated_id
    return generated_id