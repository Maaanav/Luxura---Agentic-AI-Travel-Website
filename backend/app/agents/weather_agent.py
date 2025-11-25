import logging
from typing import Dict, Any
from app.utils.openai_helper import ask_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Return ONLY valid JSON.
Format:
{
  "summary": "short text",
  "temperature": "e.g. 28°C",
  "recommendation": "short advice"
}
"""

def weather_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Uses ONLY OpenAI structured output.
    You don't have openweather_helper so no real API calls.
    """
    try:
        dest = state.get("destination", "Unknown")
        days = int(state.get("num_days", 3))

        prompt = f"Provide a {days}-day weather summary for {dest} and a short recommendation for travelers."
        data = ask_llm(prompt, SYSTEM_PROMPT)

        if not isinstance(data, dict):
            raise ValueError("Invalid weather response")

        return {"weather": data}

    except Exception as e:
        logger.exception("weather_agent error")
        return {
            "weather": {
                "summary": "Not available",
                "temperature": "",
                "recommendation": ""
            }
        }
