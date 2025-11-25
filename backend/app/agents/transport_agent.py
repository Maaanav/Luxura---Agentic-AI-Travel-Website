import logging
from typing import Dict, Any
from app.utils.openai_helper import ask_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Return ONLY valid JSON.
Format:
{"best_way":"e.g. taxi/metro", "avg_cost":"e.g. ₹500/day", "tips":"short tips"}
"""

def transport_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        dest = state.get("destination", "Unknown")
        prompt = f"Best ways to get around {dest} for tourists. Provide an average per-day cost and short practical tips."
        data = ask_llm(prompt, SYSTEM_PROMPT)
        if not isinstance(data, dict):
            raise ValueError("Invalid transport response")
        return {"transport": data}
    except Exception as e:
        logger.exception("transport_agent error")
        return {"transport": {"best_way": "", "avg_cost": "", "tips": ""}}
