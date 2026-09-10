from fastapi import APIRouter

from db.thread_repository import get_all_threads, delete_thread
from graph.graph_builder import graph
router = APIRouter()


@router.get("/thread/{user_id}")
async def list_threads(user_id:str):
    return {
        "success": True,
        "threads": get_all_threads(user_id)
    }

@router.get("/{thread_id}")
async def get_thread_messages(thread_id: str):
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    try:

        state = graph.get_state(config)
        print("thread-grpah-state")
        print(state)
        return {
            "success": True,
            "thread_id": thread_id,
            "state": state.values
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }
    
@router.delete("/{thread_id}")
def remove_thread(thread_id: str):
    try:
        print(f"Deleting thread with id: {thread_id}")
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }
        
        state = graph.get_state(config)
        user_id = state.values.get("user_id")
        print(f"User ID associated with thread: {user_id} {state.values}")
        delete_thread(thread_id, user_id)
        return {
            "success": True,
            "message": "Thread deleted successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
