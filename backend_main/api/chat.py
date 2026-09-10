from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
import uuid
import traceback
from graph.graph_builder import graph
from db.thread_repository import save_thread
from services.exceptions import(
    TranslationError,
    UnsupportedLanguageError
)
from langfuse.langchain import CallbackHandler

router = APIRouter()

print("Chat triggered successfully")

class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None
    input_type: str
    user_id:str

    image_id: str | None = None
    image_path: str | None = None
    image_url: str | None = None
    disease_prediction: dict | None = None
    disease_predictions: list[dict] | None = None

@router.post("/chat")
async def chat(req: ChatRequest):
    print(req)
    if req.thread_id is None:
        thread_id = req.thread_id or str(uuid.uuid4())
        save_thread(
            thread_id,
            user_id=req.user_id,
            title=req.message[:50],
        )
    else:
        thread_id = req.thread_id
    
    user_id = req.user_id
    
    langfuse_handler = CallbackHandler()

    config = {
        "configurable": {
            "thread_id": thread_id   
        },
        "callbacks": [langfuse_handler]
    }
    
    state = {
        "user_id": req.user_id,
        "input_type": req.input_type,
        "input_text": req.message,
        "channel": "website",
        "messages": [],
        "complaint_data": {},
        "suggested_ques": [],
        "image_path": req.image_url,
        "has_image": bool(req.image_path),
        "disease_predictions": req.disease_predictions or [],
        "disease_prediction": req.disease_prediction or {},
    }

    try:
        # result = graph.invoke(
        #     state,
        #     config=config
        # )
        from langgraph.types import Command
        snapshot = graph.get_state(config)

        if snapshot.interrupts:
            result = graph.invoke(Command(resume=state.input_text), config=config)
        else:
            result = graph.invoke(state, config=config)
        

        # Handle LangGraph interrupts
        if "__interrupt__" in result:

            interrupt_data = (
                result["__interrupt__"][0]
                .value
            )

            return {
                "success": True,
                "thread_id": thread_id,
                "interrupt": True,
                "data": interrupt_data
            }
        return {
            "success": True,
            "thread_id": thread_id,
            "interrupt": False,
            "answer": result.get("final_answer", ""),
            "audio": result.get("filename",""),
            "user_lang":result.get("user_lang"),
            "suggested_ques":result.get("suggested_ques"),
            "input_type": result.get("input_type")
        }
    except UnsupportedLanguageError:
        traceback.print_exc()
        raise HTTPException(
            status_code=400,
            detail="Language not supported"
        )
    except TranslationError as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Unable to process your message. Please try again."
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."
        )