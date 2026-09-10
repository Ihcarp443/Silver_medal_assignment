# db/feedback_repository.py

from db.sqlite import get_db_connection


def save_feedback(
    thread_id: str,
    question: str,
    answer: str,
    feedback: str,
    reason: str | None = None,
    comment: str | None = None
):
    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO feedback
        (
            thread_id,
            question,
            answer,
            feedback,
            reason,
            comment
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            thread_id,
            question,
            answer,
            feedback,
            reason,
            comment
        )
    )

    conn.commit()
    conn.close()