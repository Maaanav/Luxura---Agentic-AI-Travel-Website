import logging
from typing import Dict, Any
from app.utils.openai_helper import ask_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Return ONLY valid JSON.
Format:
{
  "budget": [
    {"name":"", "price":"", "area":"", "highlights":["",""]}
  ],
  "mid_range": [
    {"name":"", "price":"", "area":"", "highlights":["",""]}
  ],
  "luxury": [
    {"name":"", "price":"", "area":"", "highlights":["",""]}
  ]
}
"""

def hotels_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        dest = state.get("destination", "Unknown")
        theme = state.get("theme", "General")
        prompt = f"Suggest 3 hotels each for budget, mid-range and luxury in {dest}. Theme: {theme} in Indian currency."
        data = ask_llm(prompt, SYSTEM_PROMPT)
      
        if not isinstance(data, dict):
            raise ValueError("Invalid hotels response")
        for k in ["budget", "mid_range", "luxury"]:
            if k not in data:
                data[k] = []
        return {"hotels": data}
    except Exception as e:
        logger.exception("hotels_agent error")
        return {"hotels": {"budget": [], "mid_range": [], "luxury": []}}
