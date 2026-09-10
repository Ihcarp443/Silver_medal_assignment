"""
graph/nodes/agentic_rag.py
"""

import json
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from services.llm_service import model
from graph.state import GraphState
from rag.retriever import retrieve_disease_documents, retrieve_scheme_documents
from db.memory import get_memories
from ddgs import DDGS


@tool
def fetch_user_memory(user_id: str) -> str:
    """Retrieve the user's long-term profile (age, income, location, occupation, etc).
    Use this when the query is personal (e.g. 'my eligibility', 'schemes for me')
    and you don't yet have enough context to search effectively."""
    try:
        memories = get_memories(user_id)
        return json.dumps(memories) if memories else "No memory found for this user."
    except Exception as e:
        return f"Memory fetch failed: {e}"


@tool
def rewrite_query(query: str, memory_json: str = "{}") -> str:
    """Expand a vague query into a retrieval-optimized query, optionally using
    known user memory (pass as JSON string). Use this when the raw query is
    too short or ambiguous for good retrieval."""
    memory = json.loads(memory_json) if memory_json else {}

    prompt = f"""
    You are a query rewriting engine for a farming assistant covering crop
    disease treatment and government schemes.
    Rewrite the query for document retrieval.

    RULES:
    - DO NOT hallucinate or invent new attributes
    - ONLY use information present in memory
    - Keep original intent unchanged
    - Do NOT answer the question

    Return ONLY valid JSON: {{"expanded_query": "...", "keywords": ["..."]}}

    User Memory: {json.dumps(memory)}
    User Query: {query}
    """
    response = model.invoke(prompt)
    try:
        content = response.content.strip().replace("```json", "").replace("```", "")
        result = json.loads(content)
        return json.dumps(result)
    except Exception:
        return json.dumps({"expanded_query": query, "keywords": []})


@tool
def retrieve_disease_kb(query: str, crop: str = "", disease: str = "") -> str:
    """Search the crop disease knowledge base: symptoms, organic/chemical
    treatment, prevention, and weather sensitivity for known crop diseases.
    Use this for anything about disease diagnosis, treatment, or prevention.
    If crop/disease is already known exactly (e.g. from an image classifier
    result already given to you), pass them as filters for a precise lookup
    instead of relying on semantic search alone."""
    try:
        print(f"Retrieving disease KB for query: '{query}', crop: '{crop}', disease: '{disease}'")
        results = retrieve_disease_documents(query=query, crop=crop, disease=disease)
        results_content = [doc.page_content for doc in results]
    except Exception as e:
        return f"Disease KB retrieval failed: {e}"

    if not results_content:
        return "No results found in disease knowledge base."
    return json.dumps(results_content)


@tool
def retrieve_schemes(query: str, sector: str = "") -> str:
    """Search the government scheme knowledge base: subsidies, loans,
    eligibility, and application info for farming-related schemes.
    Use this for anything about subsidies, financial assistance, loans,
    or scheme eligibility. This is the primary source for scheme queries --
    try it first."""
    try:
        print(f"Retrieving scheme KB for query: '{query}', sector: '{sector}'")
        results = retrieve_scheme_documents(query=query, sector=sector)
        results_content = [doc.page_content for doc in results]
    except Exception as e:
        return f"Scheme KB retrieval failed: {e}"

    if not results_content:
        return "No results found in scheme knowledge base."
    return json.dumps(results_content)


@tool
def duckduckgo_search(query: str) -> str:
    """Search the web. ONLY use this for newly launched schemes, recent
    amendments, government notifications, or anything neither internal
    knowledge base has -- i.e. after retrieve_disease_kb / retrieve_schemes
    have come up empty or clearly insufficient. Do not use as the first tool."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return "No web results found."
        return json.dumps([
            {"title": r.get("title"), "snippet": r.get("body"), "url": r.get("href")}
            for r in results
        ])
    except Exception as e:
        return f"Web search failed: {e}"


# @tool
# def get_weather(location: str) -> str:
#     """Get current weather / short-term forecast for a location. Use when
#     the user asks about spray timing, irrigation, or when a disease's
#     weather_note suggests checking current conditions before advising action
#     (e.g. late blight risk in wet weather).

#     DUMMY IMPLEMENTATION -- returns fixed fake data for now."""
#     # TODO: replace with real weather API call
#     return json.dumps({
#         "location": location,
#         "temperature_c": 27,
#         "humidity_pct": 78,
#         "condition": "Light rain expected in next 6 hours",
#         "note": "DUMMY DATA -- not a real forecast"
#     })
import json
import httpx

from langchain_core.tools import tool


GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def resolve_coordinates(location: str):
    """Convert a location name into latitude and longitude."""

    with httpx.Client(timeout=10.0) as client:
        response = client.get(
            GEOCODE_URL,
            params={
                "name": location,
                "count": 1
            }
        )

        response.raise_for_status()
        data = response.json()

    results = data.get("results")

    if not results:
        return None, None, None

    place = results[0]

    return (
        place["latitude"],
        place["longitude"],
        place.get("name", location)
    )


@tool
def get_weather(location: str) -> str:
    """Get current weather and short-term forecast for a location.

    Use when the user asks about spray timing, irrigation, or when
    weather conditions are relevant to plant disease treatment.

    Args:
        location: City, village, district, or other location name.
    """

    if not location:
        return json.dumps({
            "error": "Please provide a location."
        })

    # --------------------------------------------------
    # 1. Resolve location to coordinates
    # --------------------------------------------------

    try:
        latitude, longitude, resolved_name = resolve_coordinates(location)

        if latitude is None:
            return json.dumps({
                "error": f"Could not find coordinates for '{location}'."
            })

    except Exception as e:
        return json.dumps({
            "error": f"Location lookup failed: {str(e)}"
        })

    # --------------------------------------------------
    # 2. Get weather from Open-Meteo
    # --------------------------------------------------

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                FORECAST_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": (
                        "temperature_2m,"
                        "relative_humidity_2m,"
                        "precipitation,"
                        "weather_code"
                    ),
                    "hourly": "precipitation_probability",
                    "forecast_days": 1
                }
            )

            response.raise_for_status()
            data = response.json()

    except Exception as e:
        return json.dumps({
            "error": f"Weather API request failed: {str(e)}"
        })

    # --------------------------------------------------
    # 3. Extract current weather
    # --------------------------------------------------

    current = data.get("current", {})

    result = {
        "location": resolved_name,
        "latitude": latitude,
        "longitude": longitude,
        "temperature_c": current.get("temperature_2m"),
        "humidity_pct": current.get("relative_humidity_2m"),
        "precipitation_mm": current.get("precipitation"),
        "weather_code": current.get("weather_code")
    }

    return json.dumps(result)
@tool
def flag_grievance(issue_type: str, description: str) -> str:
    """Call this when the user wants to report a problem needing formal
    tracking -- e.g. subsidy payment not received, application rejected,
    application status stuck. issue_type must be exactly 'payment_delay'
    or 'application_issue'. Do NOT use for general questions about
    eligibility or how schemes work."""
    return json.dumps({"issue_type": issue_type, "description": description})
# ==========================================================
# AGENT
# ==========================================================

SYSTEM_PROMPT = """You are an agentic assistant for a farming app covering two
distinct domains: crop disease diagnosis/treatment, and government schemes/subsidies.

Your goal is to gather enough context to answer the user's query, then stop --
do not answer the question yourself, just report the gathered context.

Guidelines:
- If the query is about disease symptoms, treatment, or prevention, or an
  [Image analysis] result is present in the message -- use retrieve_disease_kb.
  Pass the crop/disease from the image result as filters when available.
- If the query is about subsidies, loans, eligibility, or schemes --
  use retrieve_schemes.
- If the user reports NOT receiving a payment, a rejected application, or
  any complaint about an existing application/subsidy -- call flag_grievance
  IMMEDIATELY as your first action, even if you don't yet know which scheme.
  Do not try to gather scheme context first; the grievance flow itself will
  ask for missing details like application ID.
- Some queries need BOTH (e.g. "how do I treat this and is there a subsidy
  for the pesticide?") -- call both tools in that case.
- Use fetch_user_memory only when the query is personal/needs profile context.
- Use rewrite_query only if the raw query is too vague to search well.
- Use get_weather when spray/irrigation timing is relevant, or a disease's
  weather sensitivity makes current conditions relevant.
- Use duckduckgo_search ONLY as a supplement, after the internal KBs come up
  empty or insufficient.
- Do not call the same tool more than twice.
"""

agentic_rag_agent = create_agent(
    model,
    tools=[
        fetch_user_memory,
        rewrite_query,
        retrieve_disease_kb,
        retrieve_schemes,
        duckduckgo_search,
        get_weather,
        flag_grievance
    ],
    system_prompt=SYSTEM_PROMPT
)

# ==========================================================
# GRAPH NODE
# ==========================================================

def agentic_rag_node(state: GraphState):
    print("===== Agentic RAG (ReAct) Started =====")

    query = state["query_en"]
    user_id = state.get("user_id", "")
    disease_prediction = state.get("disease_prediction") or {}

    user_msg = f"user_id: {user_id}\n"
    if disease_prediction:
        crop = disease_prediction.get("crop", "")
        disease = disease_prediction.get("disease", "")
        confidence = disease_prediction.get("confidence", 0)
        user_msg += (
            f"[Image analysis]: Detected {crop} - {disease} "
            f"({confidence * 100:.0f}% confidence)\n"
        )
    user_msg += f"query: {query}"
    print(f"Agentic RAG user message: {user_msg}")

    result = agentic_rag_agent.invoke({
        "messages": [HumanMessage(content=user_msg)]
    })

    print("Agent result", result)

    messages = result["messages"]
    docs = []
    web_context = ""
    tool_calls_made = []

    for msg in messages:
        tool_name = getattr(msg, "name", None)
        if tool_name == "flag_grievance":
            try:
                parsed = json.loads(msg.content)
                print("Grievance flagged:", parsed)
                return {
                    "selected_route": "grievance",
                    "issue_type": parsed.get("issue_type"),
                    "complaint_data": {"issue_type": parsed.get("issue_type")},
                    "agent_trace": ["flag_grievance"],
                }
            except Exception as e:
                print("flag_grievance parse error:", e)
                continue

        elif tool_name in ("retrieve_disease_kb", "retrieve_schemes"):
            try:
                parsed = json.loads(msg.content)
                print(f"parsed from {tool_name}", parsed)
                if isinstance(parsed, list):
                    docs.extend(parsed)
            except Exception:
                pass
            tool_calls_made.append(tool_name)

        elif tool_name == "duckduckgo_search":
            try:
                parsed = json.loads(msg.content)
                print(f"parsed from {tool_name}", parsed)
                if isinstance(parsed, list):
                    web_context += "\n\n".join(
                        f"{item['title']}\n{item['snippet']}" for item in parsed
                    )
            except Exception:
                pass
            tool_calls_made.append("duckduckgo_search")

        elif tool_name:
            print(f"parsed from {tool_name}", msg.content)
            tool_calls_made.append(tool_name)

        

    final_summary = messages[-1].content if messages else ""

    print("Tools actually used:", tool_calls_made)

    return {
        "docs": docs,
        "web_context": web_context,
        "agent_trace": tool_calls_made,
        "agent_summary": final_summary
    }