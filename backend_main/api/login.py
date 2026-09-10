from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.sqlite import get_db_connection
from services.auth import verify_password

router=APIRouter()

class LoginRequest(BaseModel):
    phone: str
    password: str


@router.post("/login")
def login(req: LoginRequest):

    conn = get_db_connection()
    cursor = conn.cursor()

    user = cursor.execute(
        "SELECT * FROM users WHERE phone = ?",
        (req.phone,)
    ).fetchone()

    conn.close()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # user tuple: (id, name, phone, password, created_at)
    if not verify_password(req.password, user[2]):
        raise HTTPException(status_code=400, detail="Invalid password")

    return {
        "success": True,
        "user": {
            "id": user[0],
            "phone": user[1]
        }
    }