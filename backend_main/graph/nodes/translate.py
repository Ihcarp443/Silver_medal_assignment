from services.sarvam_service import (
    translate_to_english,
    translate_to_user_language,
    text_to_speech
)

from services.helper import (add_chat_message)
from langchain_core.messages import HumanMessage,AIMessage


def text_input_node(state):
    result = translate_to_english(
        state["input_text"]
    )
    print("user_lang",result["user_lang"])
    print("result",result)
    return {
        "query_en": result["query"],
        "user_lang": result["user_lang"],
        "messages": [
            HumanMessage(content=result["query"])
        ],
        "chat_history": add_chat_message(
        state,
        "user",
        state["input_text"],
        result["user_lang"],
        state['image_path']
    )
    }


def translate_node_for_user(state):

    print("Translate for user: ")
    print(state["user_lang"])
    translated = translate_to_user_language(
        state["answer_en"],
        state["user_lang"]
    )
    questions = state["suggested_ques"]

    suggestion_translation = []
    for ques in questions:
        q_translated = translate_to_user_language(
            ques,
            state["user_lang"]
        )
        suggestion_translation.append(q_translated)
    
    print("Sugg. translation: ",suggestion_translation)
    print(len(suggestion_translation))
    return {
        "final_answer": translated,
        "suggested_ques":suggestion_translation,
        "messages": [
            AIMessage(content=state["answer_en"])
        ],
        "chat_history": add_chat_message(
        state,
        "assistant",
        translated,
        state["user_lang"],
    )
    }

def dictate_answer_node(state):
    print("Entered dictate node")
    result = text_to_speech(state)
    return {"filename":result}

def route_translation(state):
    if state["input_type"] == "text":
        return "text"

    return "audio"