from db.sqlite import get_db_connection

def create_threads_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS threads (
            thread_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()


def save_thread(
    thread_id: str,
    user_id :str,
    title: str
):
    
    conn = get_db_connection()

    conn.execute(
        """
        INSERT OR REPLACE INTO threads (
            thread_id,
            user_id,
            title
        )
        VALUES (?, ?, ?)
        """,
        (thread_id, user_id, title)
    )

    conn.commit()
    conn.close()


def get_all_threads(user_id :str):
    conn = get_db_connection()

    cursor = conn.execute(
        """
        SELECT
            thread_id,
            title,
            created_at
        FROM threads
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "thread_id": row[0],
            "title": row[1],
            "created_at": row[2]
        }
        for row in rows
    ]
    

def get_thread(thread_id: str, user_id: str):

    conn = get_db_connection()

    cursor = conn.execute(
        """
        SELECT
            thread_id,
            title,
            created_at
        FROM threads
        WHERE thread_id = ? AND user_id = ?
        """,
        (thread_id, user_id)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "thread_id": row[0],
        "title": row[1],
        "created_at": row[2]
    }
def delete_thread(thread_id: str, user_id: str):

    conn = get_db_connection()

    conn.execute(
        """
        DELETE FROM threads
        WHERE thread_id = ? AND user_id = ?
        """,
        (thread_id, user_id)
    )
    print(f"Deleted thread with id: {thread_id} for user: {user_id}")
    conn.commit()
    conn.close()