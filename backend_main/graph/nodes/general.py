from graph.state import GraphState
from langchain_core.messages import AIMessage, HumanMessage
import json
from graph.state import GraphState

def general_node(state: GraphState):
    print("General Node State:", state)
    chat_history = state.get("chat_history", [])
    last_assistant_message = ""

    for msg in reversed(chat_history):
        if msg["role"] == "assistant":
            last_assistant_message = msg["text"]
            break

    SYSTEM_PROMPT = f"""
        You are a helpful assistant.

        Current user query:
        {state["query_en"]}

        Last assistant response:
        {last_assistant_message}

        Rules:

        1. If the user is asking to translate the previous response into another language:
        - Do not translate it.
        - Return the previous assistant response in the "answer" field.
        - Detect the target language requested by the user.
        - Return the correct language code.

        Format:
        {{
            "type": "translation_request",
            "answer": "text to be translated",
            "language_code": "target language code"
        }}

        Language codes:
        Hindi: hi-IN
        English: en-IN
        French: fr-FR
        Tamil: ta-IN
        Telugu: te-IN
        Kannada: kn-IN
        Malayalam: ml-IN
        Marathi: mr-IN
        Gujarati: gu-IN
        Punjabi: pa-IN
        Bengali: bn-IN

        2. For all other user queries:
        - Answer normally.
        - Do not detect or change the user's language.
        - Set "language_code" to "same".
        Format:
        {{
            "type": "normal",
            "answer": "your response",
            "language_code": "same"
        }}

        Important:
        - Always return only valid JSON.
        - Never return markdown.
        - Never add explanations.
        - Never include any text outside JSON.
        """

    from services.llm_service import model

    response = model.invoke(SYSTEM_PROMPT)

    data = json.loads(response.content)

    print("General node data:")

    if data["type"] == "normal":
        user_lang = state["user_lang"]
    else:
        user_lang = data["language_code"]

    return {
        "answer_en": data["answer"],
        "user_lang": user_lang
    }