from typing import List, Dict, Any, Optional
from .state import State

try:
    import langgraph as lg  # pragma: no cover - optional
except Exception:
    lg = None

from app.agents.intent import parse_intent
from app.agents.neighborhood import score_neighborhoods
from app.agents.retrieval import fetch_and_normalize_listings
from app.agents.scoring import rank_listings
from app.agents.explanation import generate_explanation


def build_graph():
    """If LangGraph is available, build and return the compiled graph.
    This is a placeholder; projects should replace with a full LangGraph
    compilation using the project's conventions.
    """
    if lg is None:
        raise RuntimeError("LangGraph not installed; use run_pipeline fallback")
    # Real implementation would go here — returning a compiled graph object
    return None


async def _run_async_pipeline(state: State, client=None) -> State:
    # 1. Intent
    intent = parse_intent(state.user_query)
    state.intent = intent.model_dump() if hasattr(intent, "model_dump") else intent.__dict__

    # 2. Neighborhoods (placeholder: derive from intent tags)
    neighborhoods = [
        {"name": "Default", "median_price": 1000000, "walk_score": 70}
    ]
    n_scores = score_neighborhoods(neighborhoods)
    state.neighborhood_scores = [ns.model_dump() if hasattr(ns, "model_dump") else ns.__dict__ for ns in n_scores]

    # 3. Retrieval
    neighborhood_names = [n["name"] for n in state.neighborhood_scores]
    if client is None:
        from app.clients.real_estate_api import RealEstateAPIClient

        client = RealEstateAPIClient()

    listings = await fetch_and_normalize_listings(neighborhood_names, client, limit_per=12)
    state.listings = [l.model_dump() if hasattr(l, "model_dump") else l.__dict__ for l in listings]

    # 4. Scoring + ranking — filter by budget/bedrooms and re-sort by a
    # preference-weighted score so results change with the query (cheaper,
    # bigger, quieter, near transit, etc.).
    top_ns = state.neighborhood_scores[0] if state.neighborhood_scores else {}
    ns_score = top_ns.get("score")
    ranked = rank_listings(listings, intent, ns_score)
    state.scored = [
        {"listing": l.model_dump() if hasattr(l, "model_dump") else l.__dict__, "score": s}
        for l, s in ranked
    ]

    # 5. Explanation — in ranked order so the UI lines up.
    explained = []
    for l, _ in ranked:
        explanation = generate_explanation(l, intent)
        explained.append({"listing_id": l.id, "explanation": explanation})
    state.explained = explained

    return state


async def arun_pipeline(user_query: str, thread_id: Optional[str] = None, client=None) -> Dict[str, Any]:
    """Async entry point. Use this from async contexts (e.g. FastAPI routes)
    where an event loop is already running.
    """
    s = State(user_query=user_query, thread_id=thread_id)
    result = await _run_async_pipeline(s, client=client)
    return result.to_dict()


def run_pipeline(user_query: str, thread_id: Optional[str] = None, client=None) -> Dict[str, Any]:
    """Synchronous wrapper that runs the async pipeline and returns a dict state.
    This function is a safe fallback used in tests when LangGraph isn't present.
    """
    import asyncio

    s = State(user_query=user_query, thread_id=thread_id)
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(_run_async_pipeline(s, client=client))
        return result.to_dict()
    finally:
        loop.close()
