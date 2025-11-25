import logging
from typing import Dict, Any, List
from app.utils.openai_helper import ask_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Return ONLY valid JSON.
Format:
[
  {"name":"", "cuisine":"", "must_try": ["dish1", "dish2"]}
]
"""

SAMPLE = [
    {"name": "The Seaside Café", "cuisine": "Seafood", "must_try": ["Grilled Prawns"]},
    {"name": "Heritage Dhaba", "cuisine": "Local", "must_try": ["Thali"]},
    {"name": "Rooftop Bistro", "cuisine": "Continental", "must_try": ["Steak"]}
]

def _to_restaurants(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("restaurants", "items", "results", "data"):
            if key in data and isinstance(data[key], list):
                return [item for item in data[key] if isinstance(item, dict)]
        maybe = []
        for k, v in data.items():
            if isinstance(v, str):
                maybe.append({"name": k, "cuisine": "", "must_try": [v]})
        if maybe:
            return maybe
    return []

def restaurants_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        dest = state.get("destination", "Unknown")
        prompt = f"Suggest 6 restaurants in {dest} covering budget, mid-range and splurge options. For each include cuisine and 1-2 must-try dishes."
        raw = ask_llm(prompt, SYSTEM_PROMPT)
        if raw is None:
            logger.warning("restaurants_agent: ask_llm returned None")
            return {"restaurants": SAMPLE}
        normalized = _to_restaurants(raw)
        if not normalized:
            logger.warning("restaurants_agent: normalization empty; raw=%s", repr(raw)[:1000])
            return {"restaurants": SAMPLE}
        return {"restaurants": normalized}
    except Exception:
        logger.exception("restaurants_agent error")
        return {"restaurants": SAMPLE}
