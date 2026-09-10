from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class ChatMessage(TypedDict):
    role: str
    text: str
    lang: str
    image_url: str | None 

class GraphState(TypedDict, total=False):
    user_id: str
    memory: dict
    input_text: str
    input_type: str
    expanded_query:str
    channel:str
    user_lang: str
    query_en: str
    docs: list
    answer_en: str
    final_answer: str
    filename:str
    intent: str
    issue_type: str
    complaint_data: dict
    selected_route: str
    messages: Annotated[List[BaseMessage], add_messages]
    chat_history: List[ChatMessage]
    suggested_ques: List[str]
    feedback_mode: bool
    question: str
    original_answer: str
    feedback_reason: str
    feedback_comment: str
    web_context: str
    agent_trace: list  
    agent_summary: str

    image_path: str             
    has_image: bool              
    disease_predictions: list    
    disease_prediction: dict    
    disease_context: str 
