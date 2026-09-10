from sarvamai import SarvamAI
from dotenv import load_dotenv
import os
from services.exceptions import(
    TranslationError,
    UnsupportedLanguageError
)
from sarvamai.errors import UnprocessableEntityError

load_dotenv()

# print("API KEY:", os.getenv("SARVAM_API_KEY"))

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)

def translate_to_english(query):
    try:
        response = client.text.translate(
            input=query,
            source_language_code="auto",
            target_language_code="en-IN",
        )

        return {
            "user_lang": response.source_language_code,
            "query": response.translated_text
        }

    except UnprocessableEntityError as e:
        if "detect the language" in str(e).lower():
            raise UnsupportedLanguageError(
                "Language not supported"
            ) from e
        
        raise TranslationError(
            "Translation failed"
        ) from e

    except Exception as e:
        raise TranslationError(
            "Translation service failed"
        ) from e

def chunk_text(text, max_chars=900):
    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end

    return chunks 

def translate_to_user_language(response, user_lang):
    if not response:
        return response

    # If small enough → direct translate
    if len(response) <= 1000:
        llmresponse = client.text.translate(
            input=response,
            source_language_code="auto",
            target_language_code=user_lang,
        )
        return llmresponse.translated_text

    # Otherwise split + translate
    chunks = chunk_text(response, 900)

    translated_parts = []

    for chunk in chunks:
        llmresponse = client.text.translate(
            input=chunk,
            source_language_code="auto",
            target_language_code=user_lang,
        )
        translated_parts.append(llmresponse.translated_text)

    return " ".join(translated_parts)

def speech_to_text(filepath):
    try:
        with open(filepath, "rb") as audio_file:
            response = client.speech_to_text.transcribe(
                file=audio_file
            )
        return {
            "transcript": response.transcript
        }
    except:
        print("Translation to language failed::")
        raise Exception("Translation failed")
    

def text_to_speech(state):
    response = client.text_to_speech.convert(
        text=state["final_answer"],
        target_language_code=state["user_lang"]
    )
    print("TTS:")
    print(state["user_lang"])
    if not response:
        raise ValueError("TTS failed: empty response")
    audio_base64 = response.audios[0]
    return audio_base64


def dictate_text(lang,text):
    response = client.text_to_speech.convert(
        text=text,
        target_language_code=lang
    )
    print("TTS:")
    if not response:
        raise ValueError("TTS failed: empty response")
    audio_base64 = response.audios[0]
    return audio_base64