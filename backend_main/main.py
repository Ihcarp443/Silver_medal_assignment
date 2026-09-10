from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.sqlite import init_db
from api.chat import router as chat_router
from api.audio import router as audio_router
# from api.grievance import router as grievance_router
from api.threads import router as threads_router
from api.dictate_text  import router as dictate_router
from api.webhook import router as whatsapp_router
from api.feedback import router as feedback_router
from api.login import router as login_router
from api.signup import router as signup_router
from api.image import router as image_router
# from api.upload_audio import router as upload_audio_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Scheme Bot API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(audio_router, prefix="/audio", tags=["Audio"])
app.include_router(threads_router, prefix="/threads", tags=["Threads"])
app.include_router(dictate_router, prefix="/play", tags=["playback"])
app.include_router(whatsapp_router, prefix="", tags=["whatsapp"])
app.include_router(login_router, prefix="/auth", tags=["login"])
app.include_router(signup_router, prefix="/auth", tags=["signup"])
app.include_router(feedback_router,prefix="/feedback",tags=["Feedback"])

app.include_router(image_router, prefix="/image")
app.mount("/static/images", StaticFiles(directory="temp/images"), name="images")


init_db()


@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "Scheme Bot API"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }