from services.feedback_improver import improve_answer
from services.helper import add_chat_message 
def feedback_improve_node(state):

    improved_answer = improve_answer(
        question=state["question"],
        answer=state["original_answer"],
        reason=state.get("feedback_reason"),
        comment=state.get("feedback_comment")
    )

    feedback_text = (
        state.get("feedback_reason")
        or state.get("feedback_comment")
        or ""
    )
    return {
        "answer_en": improved_answer,
        "final_answer": improved_answer,
        "feedback_mode": False,
        "chat_history": add_chat_message(
            state,
            "user",
            feedback_text,
            state["user_lang"]
        )
    }
