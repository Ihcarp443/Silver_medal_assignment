from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.sqlite import get_db_connection
from services.auth import hash_password, verify_password

router = APIRouter()

class SignupRequest(BaseModel):
    phone: str
    password: str

@router.post("/signup")
def signup(req: SignupRequest):

    conn = get_db_connection()
    cursor = conn.cursor()

    user = cursor.execute(
        "SELECT * FROM users WHERE phone = ?",
        (req.phone,)
    ).fetchone()

    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = hash_password(req.password)

    cursor.execute(
        "INSERT INTO users (phone, password) VALUES (?, ?)",
        (req.phone, hashed)
    )

    conn.commit()

    user_id = cursor.lastrowid
    conn.close()

    return {
        "success": True,
        "user": {
            "id": user_id,
            "phone": req.phone
        }
    }