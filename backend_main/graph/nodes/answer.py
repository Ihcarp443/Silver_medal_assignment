# from services.llm_service import model
# import json


# def answer_node(state):

#     context = "\n\n".join(doc for doc in state["docs"])
#     web_context = state.get("web_context", "")
#     question = state["query_en"]
#     history = state["messages"]
#     user_memory = state.get("memory", {})
#     channel = state.get("channel", "website")
#     disease_prediction = state.get("disease_prediction") or {}

#     image_context = ""
#     if disease_prediction:
#         crop = disease_prediction.get("crop", "")
#         disease = disease_prediction.get("disease", "")
#         confidence = disease_prediction.get("confidence", 0)
#         image_context = f"Detected from uploaded photo: {crop} - {disease} ({confidence * 100:.0f}% confidence)"

#     web_prompt = f"""
#     You are a helpful AI assistant for a farming app -- covering crop disease
#     diagnosis/treatment and government schemes/subsidies for farmers.

#     Use the available information in the following priority order:

#     1. Image Analysis Result (if present -- this is ground truth for what disease was detected)
#     2. Retrieved Context (disease KB / scheme KB -- highest priority for factual answers)
#     3. Web Context (only if retrieved context was insufficient)
#     4. User Profile Memory (for personalization)
#     5. Conversation History (for continuity)

#     ---------------------
#     Image Analysis Result:
#     {image_context or "No image provided."}

#     ---------------------
#     User Profile Memory:
#     {user_memory}

#     ---------------------
#     Conversation History:
#     {history}

#     ---------------------
#     Retrieved Context:
#     {context}

#     ---------------------
#     Web Context (supplementary, use only if retrieved context is missing something):
#     {web_context or "None."}

#     ---------------------
#     Current Question:
#     {question}

#     ---------------------
#     Suggested questions should help the user:
#     - understand disease treatment/prevention next steps
#     - explore related scheme eligibility (e.g. subsidy for treatment/equipment)
#     - ask about weather-based timing for spraying/irrigation
#     - or ask "what next steps"

#     ---------------------
#     Instructions:
#     - If an image analysis result is present, ground your answer in that detected crop/disease.
#     - Retrieved context is the primary source of truth for treatment/scheme facts.
#     - Use web context only to fill gaps retrieved context doesn't cover.
#     - Use user profile memory only to personalize the answer or determine eligibility.
#     - Do not make assumptions about missing user information.
#     - Use conversation history only for understanding references like "that scheme" or "my previous question".
#     - If the answer is not available in the retrieved/web context, say:
#       "I don't know based on the available data."
#     - Keep the answer clear, accurate, and concise.

#     ----------------------
#     RULES:
#     - suggested_questions MUST be 2 to 3 items
#     - questions must be short and related to user query
#     - no extra text outside JSON
#     - no markdown

#     FINAL OUTPUT FORMAT (STRICT JSON ONLY):

#     Return ONLY valid JSON in this format:

#     {{
#       "answer": "final user answer here",
#       "suggested_questions": [
#         "question 1",
#         "question 2",
#         "question 3"
#       ]
#     }}
#     Answer:
#     """

#     wp_prompt = f"""
#     You are a helpful AI assistant for a farming app -- covering crop disease
#     diagnosis/treatment and government schemes/subsidies.

#     You are answering on WhatsApp. So your response MUST be:

#     - extremely concise
#     - mobile-friendly
#     - structured
#     - easy to scan in 3 seconds
#     - NO long paragraphs

#     You must preserve important information, but compress it intelligently.

#     ---------------------
#     Image Analysis Result:
#     {image_context or "No image provided."}

#     ---------------------
#     User Profile Memory:
#     {user_memory}

#     ---------------------
#     Conversation History:
#     {history}

#     ---------------------
#     Retrieved Context:
#     {context}

#     ---------------------
#     Web Context:
#     {web_context or "None."}

#     ---------------------
#     Current Question:
#     {question}

#     ---------------------
#     CRITICAL INSTRUCTIONS:

#     1. If an image analysis result is present, ground your answer in that detected crop/disease.
#     2. Retrieved context is the PRIMARY source of truth.
#     3. Do NOT hallucinate missing information.
#     4. Keep response short but complete.
#     5. Use bullet points / numbering only.
#     6. NO long explanations.
#     7. NO paragraphs longer than 2 lines.

#     ---------------------
#     🚨 STRICT WHATSAPP OUTPUT FORMAT (FOLLOW EXACTLY):

#     Your answer MUST follow this structure:

#     🎯 ANSWER:
#     - 1–2 line direct answer only

#     📌 KEY POINTS:
#     - Bullet points (max 4–6 points)
#     - Each point should be short (1 line)

#     🧾 DETAILS (ONLY IF NECESSARY):
#     - Treatment / eligibility / steps (very brief bullets)

#     ⚠️ If information is missing:
#     - Say: "I don't know based on available data."

#     ---------------------
#     STYLE RULES:

#     - Use emojis ONLY for section headers (🎯📌🧾⚠️)
#     - Do NOT use emojis in bullet points
#     - Do NOT write essays
#     - Do NOT repeat information
#     - Do NOT add unnecessary context
#     - Keep total response under ~10–12 lines
#     - Make it scannable in WhatsApp preview

#     ---------------------
#     ANSWER:
#     """

#     if channel == "website":
#         prompt = web_prompt
#     elif channel == "whatsapp":
#         prompt = wp_prompt
#     else:
#         prompt = web_prompt

#     response = model.invoke(prompt)
#     # response = prompt[:1000]  
    
#     if channel == "website":
#         raw_output = response.content.strip()
#         data = json.loads(raw_output)
#         return {
#             "answer_en": data["answer"].strip(),
#             "suggested_ques": data.get("suggested_questions", [])
#         }
#     else:
#         return {
#             "answer_en": response.content.strip()
#         }

from services.llm_service import model
import json


def answer_node(state):

    context = "\n\n".join(doc for doc in state["docs"])
    web_context = state.get("web_context", "")
    agent_summary = state.get("agent_summary", "")
    question = state["query_en"]
    history = state["messages"]
    user_memory = state.get("memory", {})
    channel = state.get("channel", "website")
    disease_prediction = state.get("disease_prediction") or {}

    image_context = ""
    if disease_prediction:
        crop = disease_prediction.get("crop", "")
        disease = disease_prediction.get("disease", "")
        confidence = disease_prediction.get("confidence", 0)
        image_context = f"Detected from uploaded photo: {crop} - {disease} ({confidence * 100:.0f}% confidence)"

    web_prompt = f"""
    You are a helpful AI assistant for a farming app -- covering crop disease
    diagnosis/treatment and government schemes/subsidies for farmers.

    Use the available information in the following priority order:

    1. Image Analysis Result (if present -- ground truth for detected disease)
    2. Agent Summary (includes live tool results: weather data, flagged findings -- treat this as factual, already-verified information)
    3. Retrieved Context (disease KB / scheme KB)
    4. Web Context (only if retrieved context was insufficient)
    5. User Profile Memory (for personalization)
    6. Conversation History (for continuity)

    ---------------------
    Image Analysis Result:
    {image_context or "No image provided."}

    ---------------------
    Agent Summary (live tool results -- weather, etc.):
    {agent_summary or "None."}

    ---------------------
    User Profile Memory:
    {user_memory}

    ---------------------
    Conversation History:
    {history}

    ---------------------
    Retrieved Context:
    {context}

    ---------------------
    Web Context (supplementary, use only if retrieved context is missing something):
    {web_context or "None."}

    ---------------------
    Current Question:
    {question}

    ---------------------
    Suggested questions should help the user:
    - understand disease treatment/prevention next steps
    - explore related scheme eligibility (e.g. subsidy for treatment/equipment)
    - ask about weather-based timing for spraying/irrigation
    - or ask "what next steps"

    ---------------------
    Instructions:
    - If Agent Summary contains weather data (temperature, humidity, precipitation), use those EXACT figures directly in your answer -- this is real, already-fetched data, not something you lack access to. Never say "I don't have access to weather" if Agent Summary contains weather data.
    - If an image analysis result is present, ground your answer in that detected crop/disease.
    - Retrieved context is the primary source of truth for treatment/scheme facts.
    - Use web context only to fill gaps retrieved context doesn't cover.
    - Use user profile memory only to personalize the answer or determine eligibility.
    - Do not make assumptions about missing user information.
    - Use conversation history only for understanding references like "that scheme" or "my previous question".
    - If the answer is not available in any of the above, say:
      "I don't know based on the available data."
    - Keep the answer clear, accurate, and concise.

    ----------------------
    RULES:
    - suggested_questions MUST be 2 to 3 items
    - questions must be short and related to user query
    - no extra text outside JSON
    - no markdown

    FINAL OUTPUT FORMAT (STRICT JSON ONLY):

    Return ONLY valid JSON in this format:

    {{
      "answer": "final user answer here",
      "suggested_questions": [
        "question 1",
        "question 2",
        "question 3"
      ]
    }}
    Answer:
    """

    wp_prompt = f"""
    You are a helpful AI assistant for a farming app -- covering crop disease
    diagnosis/treatment and government schemes/subsidies.

    You are answering on WhatsApp. So your response MUST be:

    - extremely concise
    - mobile-friendly
    - structured
    - easy to scan in 3 seconds
    - NO long paragraphs

    You must preserve important information, but compress it intelligently.

    ---------------------
    Image Analysis Result:
    {image_context or "No image provided."}

    ---------------------
    Agent Summary (live tool results -- weather, etc.):
    {agent_summary or "None."}

    ---------------------
    User Profile Memory:
    {user_memory}

    ---------------------
    Conversation History:
    {history}

    ---------------------
    Retrieved Context:
    {context}

    ---------------------
    Web Context:
    {web_context or "None."}

    ---------------------
    Current Question:
    {question}

    ---------------------
    CRITICAL INSTRUCTIONS:

    1. If Agent Summary contains weather data, use those exact figures -- it's real fetched data, never claim you lack weather access if it's present here.
    2. If an image analysis result is present, ground your answer in that detected crop/disease.
    3. Retrieved context is the PRIMARY source of truth.
    4. Do NOT hallucinate missing information.
    5. Keep response short but complete.
    6. Use bullet points / numbering only.
    7. NO long explanations.
    8. NO paragraphs longer than 2 lines.

    ---------------------
    🚨 STRICT WHATSAPP OUTPUT FORMAT (FOLLOW EXACTLY):

    Your answer MUST follow this structure:

    🎯 ANSWER:
    - 1–2 line direct answer only

    📌 KEY POINTS:
    - Bullet points (max 4–6 points)
    - Each point should be short (1 line)

    🧾 DETAILS (ONLY IF NECESSARY):
    - Treatment / eligibility / steps (very brief bullets)

    ⚠️ If information is missing:
    - Say: "I don't know based on available data."

    ---------------------
    STYLE RULES:

    - Use emojis ONLY for section headers (🎯📌🧾⚠️)
    - Do NOT use emojis in bullet points
    - Do NOT write essays
    - Do NOT repeat information
    - Do NOT add unnecessary context
    - Keep total response under ~10–12 lines
    - Make it scannable in WhatsApp preview

    ---------------------
    ANSWER:
    """

    if channel == "website":
        prompt = web_prompt
    elif channel == "whatsapp":
        prompt = wp_prompt
    else:
        prompt = web_prompt

    response = model.invoke(prompt)

    if channel == "website":
        raw_output = response.content.strip()
        try:
            data = json.loads(raw_output)
            return {
                "answer_en": data["answer"].strip(),
                "suggested_ques": data.get("suggested_questions", [])
            }
        except Exception:
            return {
                "answer_en": raw_output,
                "suggested_ques": []
            }
    else:
        return {
            "answer_en": response.content.strip()
        }