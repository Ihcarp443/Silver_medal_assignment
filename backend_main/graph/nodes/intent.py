# nodes/intent.py
from typing import Optional, Literal
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from services.llm_service import model
from graph.state import GraphState

class GrievanceSchema(BaseModel):
    issue_type: Optional[
        Literal["payment_delay", "application_issue"]
    ] = Field(
        default=None,
        description="Type of grievance if intent is grievance"
    )

parser = JsonOutputParser(
    pydantic_object=GrievanceSchema
)

def extract_grievance_type(state: GraphState):
    query = state["query_en"].lower()

    prompt = f"""
        You are a grievance classification engine.
        
        A user has already been identified as having a grievance related to a government scheme application.
        
        Classify the grievance into one of the following types:
        
        1. payment_delay
        - User has not received payment
        - Payment is pending
        - Amount not credited
        
        2. application_issue
        - Application rejected
        - Status not updated
        - Incorrect information
        - Any other application related problem
        
        Return only valid JSON.
        
        {parser.get_format_instructions()}
        
        User Query:
        {query}
        """

    response = model.invoke(prompt)

    return parser.parse(response.content)
    
def grievance_entry_node(state: GraphState):
    try:
        output = extract_grievance_type(state)
        issue_type = output.get("issue_type")

        print("Intent Detection:", output)

    except Exception as e:
        print("Grievance Detection Error:", e)
        issue_type = None

    return {
        "issue_type": issue_type,
        "complaint_data": {
            "issue_type": issue_type
        }
    }

def intent(state: GraphState):
    query = state["query_en"]
    memory = state.get("memory", {})

    prompt = f"""
    Classify the user's intent into exactly one of these words:

    rag
    grievance
    general

    Rules:
    - rag: scheme information, eligibility, benefits, documents, application process
    - grievance: complaints, payment issues, application status, rejection, delays
    - general: greetings, casual conversation, or unrelated topics

    User Memory:
    {memory}

    Query:
    {query}

    Return only one word.
    """

    response = model.invoke(prompt)

    intent = response.content.strip().lower()

    if intent not in {"rag", "grievance", "general"}:
        intent = "general"

    return {
        "intent": intent
    }


def route_intent(state: GraphState):
    return state["intent"]