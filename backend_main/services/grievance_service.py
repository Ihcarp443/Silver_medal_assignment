# import re
# import random
# def extract_application_data(
#     query: str,
#     required_fields: list
# ):

#     data = {}

#     match = re.search(r"\d+", query)

#     if match:
#         data["application_id"] = match.group()

#     return data

# def simulate_payment_status(data):

#     responses = [
#         {
#             "status": "submitted",
#             "message": "Application submitted successfully and awaiting review."
#         },
#         {
#             "status": "under_review",
#             "message": "Your application is currently under review by the concerned department."
#         },
#         {
#             "status": "verification_in_progress",
#             "message": "Field and document verification is in progress."
#         },
#         {
#             "status": "approved",
#             "message": "Your application has been approved."
#         },
#         {
#             "status": "rejected",
#             "message": "Your application has been rejected due to eligibility criteria not being met."
#         },
#         {
#             "status": "payment_processing",
#             "message": "Benefit disbursement has been initiated and is being processed."
#         },
#         {
#             "status": "success",
#             "message": "Payment has been credited successfully to your bank account."
#         },
#         {
#             "status": "pending",
#             "message": "Payment is under processing."
#         },
#         {
#             "status": "failed",
#             "message": "Bank account verification failed."
#         },
#         {
#             "status": "payment_failed",
#             "message": "Payment could not be processed due to bank account issues."
#         },
#         {
#             "status": "on_hold",
#             "message": "Application is temporarily on hold pending further verification."
#         }
#     ]

#     result = random.choice(responses)

#     return {
#         "application_id": data["application_id"],
#         "status": result["status"],
#         "message": result["message"]
#     }

import re
import random
import hashlib


def extract_application_data(query: str, required_fields: list):
    data = {}

    if "application_id" in required_fields:
        match = re.search(r"\b\d{4,}\b", query)  # require 4+ digits, avoids grabbing stray small numbers
        if match:
            data["application_id"] = match.group()

    if "phone_number" in required_fields:
        match = re.search(r"\b\d{10}\b", query)
        if match:
            data["phone_number"] = match.group()

    if "email" in required_fields:
        match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", query)
        if match:
            data["email"] = match.group()

    return data


def validate_field(field: str, value: str):
    value = (value or "").strip()

    if not value:
        return False, "That doesn't look right --"

    if field == "application_id":
        if not re.fullmatch(r"\d{4,}", value):
            return False, "Application ID should be numbers only (4+ digits)."
        return True, ""

    if field == "phone_number":
        if not re.fullmatch(r"\d{10}", value):
            return False, "Phone number should be exactly 10 digits."
        return True, ""

    if field == "email":
        if not re.fullmatch(r"[\w\.-]+@[\w\.-]+\.\w+", value):
            return False, "That doesn't look like a valid email address."
        return True, ""

    return True, ""


def simulate_payment_status(data):
    """Deterministic based on application_id so the same ID always
    returns the same status within a session -- more realistic for
    testing/demo than fully random on every call."""

    responses = [
        {"status": "submitted", "message": "Application submitted successfully and awaiting review."},
        {"status": "under_review", "message": "Your application is currently under review by the concerned department."},
        {"status": "verification_in_progress", "message": "Field and document verification is in progress."},
        {"status": "approved", "message": "Your application has been approved."},
        {"status": "rejected", "message": "Your application has been rejected due to eligibility criteria not being met."},
        {"status": "payment_processing", "message": "Benefit disbursement has been initiated and is being processed."},
        {"status": "success", "message": "Payment has been credited successfully to your bank account."},
        {"status": "pending", "message": "Payment is under processing."},
        {"status": "failed", "message": "Bank account verification failed."},
        {"status": "payment_failed", "message": "Payment could not be processed due to bank account issues."},
        {"status": "on_hold", "message": "Application is temporarily on hold pending further verification."},
    ]

    app_id = data.get("application_id", "")
    seed = int(hashlib.md5(app_id.encode()).hexdigest(), 16)
    result = responses[seed % len(responses)]

    return {
        "application_id": app_id,
        "status": result["status"],
        "message": result["message"]
    }
