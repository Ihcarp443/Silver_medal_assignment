def add_chat_message(state, role, text, lang, image_url=None):
    history = state.get("chat_history", [])

    return history + [
        {
            "role": role,
            "text": text,
            "lang": lang,
            "image_url": image_url
        }
    ]