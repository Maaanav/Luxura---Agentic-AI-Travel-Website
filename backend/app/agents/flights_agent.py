import logging
from typing import Dict, Any
from app.utils.serpapi_helper import fetch_flights

logger = logging.getLogger(__name__)

def flights_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    STRICT: Only fetch flights from SerpAPI.
    No LLM fallback. No sample fallback unless SerpAPI hard fails.
    """
    try:
        src = state.get("source", "BOM")
        dest_code = state.get("destination_code", "GOI")
        depart = state.get("depart_date")
        ret = state.get("return_date")

        flights = fetch_flights(src, dest_code, depart, ret)

        # If fetch_flights returned None or invalid, return empty list
        if not isinstance(flights, list):
            flights = []

        return {"flights": flights}

    except Exception:
        logger.exception("flights_agent error")
        return {"flights": []}
