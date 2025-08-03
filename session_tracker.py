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


def log_message_to_snowflake(session: Session, session_id: str, role: str, message: str):
    timestamp = datetime.utcnow().isoformat()
    message = message.replace("'", "''")[:2000]  # escape single quotes and truncate
    session_id = session_id.replace("'", "''")
    role = role.replace("'", "''")

    session.sql(f"""
        INSERT INTO {TABLE_NAME} (session_id, timestamp, role, message)
        VALUES ('{session_id}', '{timestamp}', '{role}', '{message}')
    """).collect()
