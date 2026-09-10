from fastapi import APIRouter
from pydantic import BaseModel
from db.feedback_repository import save_feedback
from graph.graph_builder import graph
from langfuse.langchain import CallbackHandler

langfuse_handler = CallbackHandler()
router = APIRouter()

class FeedbackRequest(BaseModel):
    thread_id: str
    question: str
    answer: str
    feedback: str
    reason: str | None = None
    comment: str | None = None

@router.post("")
async def submit_feedback(req: FeedbackRequest):
    save_feedback(
        thread_id=req.thread_id,
        question=req.question,
        answer=req.answer,
        feedback=req.feedback,
        reason=req.reason,
        comment=req.comment
    )

    return {
        "success": True
    }

class ImproveRequest(BaseModel):
    thread_id: str
    question: str
    answer: str
    reason: str | None = None
    comment: str | None = None
    lang: str | None = "en"
    input_type: str | None = "text"

@router.post("/improve")
async def improve_answer(req: ImproveRequest):

    print("Received request to improve answer:", req)

    config = {
        "configurable": {
            "thread_id": req.thread_id
        },
            "callbacks": [langfuse_handler]
    }

    result = graph.invoke(
        {
            "feedback_mode": True,
            "question": req.question,
            "original_answer": req.answer,
            "feedback_reason": req.reason,
            "feedback_comment": req.comment,
            "user_lang": req.lang,
            "input_type": req.input_type
        },
        config=config
    )

    return {
        "success": True,
        "improved_answer": result["final_answer"]
    }