from db.memory import get_memories
from graph.state import GraphState

def memory_fetch_node(state: GraphState):
    
    user_id = state["user_id"]

    memories = get_memories(user_id)

    return {
        "memory": memories
    }