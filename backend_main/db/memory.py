from db.sqlite import get_db_connection


def create_memory_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            user_id TEXT,
            key TEXT,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            PRIMARY KEY (user_id, key)
        )
    """)

    conn.commit()
    conn.close()

def save_memory(
    user_id: str,
    key: str,
    value: str
):
    conn = get_db_connection()

    conn.execute("""
        INSERT OR REPLACE INTO memories (
            user_id,
            key,
            value,
            updated_at
        )
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """,
    (
        user_id,
        key,
        value
    ))
    
    conn.commit()
    conn.close()



def get_memories(user_id: str):
    conn = get_db_connection()

    cursor = conn.execute("""
        SELECT key, value
        FROM memories
        WHERE user_id = ?
    """,
    (user_id,))

    rows = cursor.fetchall()

    memory = {}
    conn.close()
    for key, value in rows:
        memory[key] = value

    return memory