from snowflake.snowpark import Session
from datetime import datetime

TABLE_NAME = "CHAT_LOGS"

def create_chat_logs_table_if_not_exists(session: Session):
    session.sql(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            session_id STRING,
            timestamp TIMESTAMP,
            role STRING,
            message TEXT
        )
    """).collect()


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
