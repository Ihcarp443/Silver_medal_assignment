from fastapi import APIRouter
from pydantic import BaseModel
from services.sarvam_service import (
    dictate_text
)
router = APIRouter()
class DictateRequest(BaseModel):
    user_lang: str
    text: str


@router.post("/dictate_text")
async def dictate(req:DictateRequest):
    print(req)
    user_lang=req.user_lang
    text=req.text
    try:
        result = dictate_text(user_lang,text)

        # Handling LangGraph interrupts
        return {
            "success": True,
            "interrupt": False,
            "audio": result,
        }
        

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }