from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from db.checkpoint import checkpoint_conn
from graph.state import GraphState

from graph.nodes.translate import (
    text_input_node,
    translate_node_for_user,
    dictate_answer_node,
    route_translation
)
from graph.nodes.answer import answer_node
from graph.nodes.update_memory import memory_update_node
from graph.nodes.feedback import feedback_improve_node
from graph.nodes.agentic_rag import agentic_rag_node
from graph.nodes.grievance import grievance_tool_node, grievance_formatter_node


def start_router(state):
    return "feedback" if state.get("feedback_mode") else "normal"


def route_after_agent(state):
    return "grievance" if state.get("selected_route") == "grievance" else "answer"


checkpointer = SqliteSaver(conn=checkpoint_conn)
builder = StateGraph(GraphState)

# =========================
# Nodes
# =========================
builder.add_node("text_input", text_input_node)
builder.add_node("agent", agentic_rag_node)
builder.add_node("answer", answer_node)
builder.add_node("grievance", grievance_tool_node)
builder.add_node("grievance_formatter", grievance_formatter_node)
builder.add_node("translate", translate_node_for_user)
builder.add_node("dictate", dictate_answer_node)
builder.add_node("update_memory", memory_update_node)
builder.add_node("feedback_improve", feedback_improve_node)

# =========================
# Flow
# =========================
builder.add_conditional_edges(
    START, start_router,
    {"feedback": "feedback_improve", "normal": "text_input"}
)

builder.add_edge("text_input", "agent")

builder.add_conditional_edges(
    "agent", route_after_agent,
    {"grievance": "grievance", "answer": "answer"}
)

builder.add_edge("answer", "update_memory")
builder.add_edge("grievance", "grievance_formatter")
builder.add_edge("grievance_formatter", "update_memory")

builder.add_edge("feedback_improve", "translate")
builder.add_edge("update_memory", "translate")

builder.add_conditional_edges(
    "translate", route_translation,
    {"text": END, "audio": "dictate"}
)
builder.add_edge("dictate", END)

graph = builder.compile(checkpointer=checkpointer)
print("Graph Compiled successfully")