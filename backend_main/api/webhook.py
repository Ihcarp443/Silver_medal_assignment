from fastapi import Request, APIRouter, BackgroundTasks
import os, uuid, requests
from twilio.rest import Client
from dotenv import load_dotenv
from graph.graph_builder import graph
from services.disease_service import predict_disease
from services.exceptions import TranslationError, UnsupportedLanguageError
from langfuse.langchain import CallbackHandler


router = APIRouter()

load_dotenv()
langfuse_handler = CallbackHandler()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
client = Client(ACCOUNT_SID, AUTH_TOKEN)


def download_whatsapp_media(media_url: str, content_type: str) -> str:
    """Twilio media URLs require Basic Auth with your account credentials."""
    resp = requests.get(media_url, auth=(ACCOUNT_SID, AUTH_TOKEN))
    resp.raise_for_status()

    ext = ".jpg" if "jpeg" in content_type else ".png"
    os.makedirs("temp/images", exist_ok=True)
    file_id = str(uuid.uuid4())
    path = f"temp/images/{file_id}{ext}"

    with open(path, "wb") as f:
        f.write(resp.content)

    return path


def process_message(user_msg, user_number, media_url=None, media_content_type=None):
    thread_id = user_number + '009'
    config = {"configurable": {"thread_id": thread_id}, "callbacks": [langfuse_handler]}

    disease_prediction = {}
    image_path = None

    if media_url and media_content_type and media_content_type.startswith("image/"):
        try:
            image_path = download_whatsapp_media(media_url, media_content_type)
            top_predictions = predict_disease(image_path, top_k=3)
            disease_prediction = top_predictions[0]
            print(f"WhatsApp image prediction: {disease_prediction}")
        except Exception as e:
            print("Image processing error:", e)

    state = {
        "user_id": "10005",
        "input_type": "text",
        "input_text": user_msg,
        "channel": "whatsapp",
        "messages": [],
        "complaint_data": {},
        "suggested_ques": [],
        "image_path": image_path,
        "has_image": bool(image_path),
        "disease_prediction": disease_prediction,
        "disease_predictions": top_predictions if disease_prediction else [],
    }

    try:
        from langgraph.types import Command
        snapshot = graph.get_state(config)

        if snapshot.interrupts:
            result = graph.invoke(Command(resume=user_msg), config=config)
        else:
            result = graph.invoke(state, config=config)

        if "__interrupt__" in result:
            interrupt_data = result["__interrupt__"][0].value
            answer = interrupt_data.get("question", "Please provide the required information.")
        else:
            answer = result.get("final_answer") or result.get("answer_en", "Sorry, I couldn't process your request.")

    except (TranslationError, UnsupportedLanguageError) as e:
        print("Translation Error:", e)
        answer = "Sorry, something wrong on our end."
    except Exception as e:
        print("BACKGROUND ERROR:", e)
        answer = "Sorry, something went wrong. Please try again later."

    user_number_env = os.getenv("USER_WHATSAPP_NUMBER")
    try:
        message = client.messages.create(from_=TWILIO_NUMBER, to=user_number_env, body=answer)
        print("WhatsApp message sent:", message.sid)
    except Exception as e:
        print("TWILIO SEND ERROR:", e)


@router.post("/whatsapp/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()

    user_msg = form.get("Body") or "Hi"
    user_number = form.get("From")
    media_url = form.get("MediaUrl0")
    media_content_type = form.get("MediaContentType0")

    print("Message:", user_msg, "| From:", user_number, "| Media:", media_url)

    background_tasks.add_task(
        process_message, user_msg, user_number, media_url, media_content_type
    )

    return {"status": "received"}