# from langgraph.types import interrupt
# from langchain_core.messages import HumanMessage, AIMessage
# from graph.state import GraphState
# from services.grievance_service import ( simulate_payment_status,extract_application_data)
# from services.llm_service import model

# def grievance_formatter_node(state: GraphState):
#     grievance_response = state.get(
#         "final_answer",
#         ""
#     )

#     prompt = f"""
# Convert the following system response
# into a user-friendly message.

# Response:
# {grievance_response}

# Instructions:
# - Keep it polite
# - Keep it concise
# - Do not change meaning
# - Do not add information
# """

#     response = model.invoke(
#         prompt
#     )

#     return {
#         "answer_en":
#         response.content,
#         "messages": [
#             AIMessage(content=response.content)
#         ]
#     }

# GRIEVANCE_TYPES = {
#     "payment_delay": ["application_id", "phone_number", "email"],
#     "application_issue": ["application_id"]
# }

# def grievance_tool_node(state: GraphState):

#     print(
#         "complaint_data:",
#         state.get("complaint_data")
#     )

#     query = state.get("query_en")

#     data = dict(
#         state.get(
#             "complaint_data",
#             {}
#         )
#     )

#     issue_type = state.get("issue_type")

#     required = GRIEVANCE_TYPES.get(
#         issue_type,
#         []
#     )

#     extracted = extract_application_data(
#         query,
#         required
#     )

#     for k, v in extracted.items():
#         if v and not data.get(k):
#             data[k] = v

#     missing = [
#         field
#         for field in required
#         if not data.get(field)
#     ]

#     print("Missing:", missing)

#     questions_map = {
#         "application_id":
#             "Please provide your application ID",
#         "phone_number":
#             "Please provide your phone number",
#         "email":
#             "Please provide your email address"
#     }

#     # Ask for each missing field
#     for field in missing:

#         user_answer = interrupt({
#             "type": "ASK_USER",
#             "field": field,
#             "question": questions_map[field],
#             "partial_data": data
#         })

#         print(
#             f"Received {field}:",
#             user_answer
#         )

#         data[field] = user_answer

#     print(
#         "Updated complaint_data:",
#         data
#     )
#     # Persist updated data
#     if issue_type == "application_issue":

#         result = simulate_payment_status(
#             data
#         )

#         return {
#             "complaint_data": data,
#             "final_answer": f"""
# Status: {result['status'].upper()}
# Message: {result['message']}
# """
#         }

#     elif issue_type == "payment_delay":

#         preview = f"""
# Complaint Preview

# Application ID: {data['application_id']}
# Phone: {data.get('phone_number', 'N/A')}
# Email: {data.get('email', 'N/A')}

# Issue:
# {query}
# """
#     return {
#         "complaint_data": data,
#         "final_answer":
#             "Unable to process grievance."
#     }
from langgraph.types import interrupt
from langchain_core.messages import AIMessage
from graph.state import GraphState
from services.grievance_service import (
    simulate_payment_status,
    extract_application_data,
    validate_field,
)
from services.llm_service import model


def grievance_formatter_node(state: GraphState):
    grievance_response = state.get("final_answer", "")

    prompt = f"""
Convert the following system response into a user-friendly message.

Response:
{grievance_response}

Instructions:
- Keep it polite
- Keep it concise
- Do not change meaning
- Do not add information
"""
    response = model.invoke(prompt)

    return {
        "answer_en": response.content,
        "messages": [AIMessage(content=response.content)]
    }


GRIEVANCE_TYPES = {
    "payment_delay": ["application_id", "phone_number", "email"],
    "application_issue": ["application_id"]
}

QUESTIONS_MAP = {
    "application_id": "Please provide your application ID (numbers only).",
    "phone_number": "Please provide your 10-digit phone number.",
    "email": "Please provide your email address.",
}


def grievance_tool_node(state: GraphState):

    print("complaint_data:", state.get("complaint_data"))

    query = state.get("query_en")
    data = dict(state.get("complaint_data", {}))
    issue_type = state.get("issue_type")
    required = GRIEVANCE_TYPES.get(issue_type, [])

    extracted = extract_application_data(query, required)
    for k, v in extracted.items():
        if v and not data.get(k):
            data[k] = v

    missing = [field for field in required if not data.get(field)]
    print("Missing:", missing)

    for field in missing:
        question = QUESTIONS_MAP[field]

        while True:
            user_answer = interrupt({
                "type": "ASK_USER",
                "field": field,
                "question": question,
                "partial_data": data
            })

            print(f"Received {field}:", user_answer)

            is_valid, error_msg = validate_field(field, user_answer)
            if is_valid:
                data[field] = user_answer.strip()
                break

            # invalid -- re-ask with a clarifying message, don't move on
            question = f"{error_msg} {QUESTIONS_MAP[field]}"

    print("Updated complaint_data:", data)

    if issue_type == "application_issue":
        result = simulate_payment_status(data)
        return {
            "complaint_data": data,
            "final_answer": f"""
Status: {result['status'].upper()}
Message: {result['message']}
"""
        }

    elif issue_type == "payment_delay":
        result = simulate_payment_status(data)

        preview = f"""
Complaint Preview

Application ID: {data['application_id']}
Phone: {data.get('phone_number', 'N/A')}
Email: {data.get('email', 'N/A')}

Issue:
{query}

Current Status Check:
{result['status'].upper()} - {result['message']}
"""
        ticket = "TICKET-" + str(abs(hash(str(data))) % 100000)

        return {
            "complaint_data": data,
            "final_answer": f"{preview}\n\n✅ Complaint submitted successfully.\nTicket: {ticket}"
        }

    return {
        "complaint_data": data,
        "final_answer": "Unable to process grievance."
    }