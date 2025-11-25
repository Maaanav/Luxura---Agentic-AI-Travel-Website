import json
import time
import logging
import os
from typing import Any, Dict
from datetime import datetime, timedelta

from app.agents.flights_agent import flights_agent
from app.agents.hotels_agent import hotels_agent
from app.agents.attractions_agent import attractions_agent
from app.agents.restaurants_agent import restaurants_agent
from app.agents.transport_agent import transport_agent
from app.agents.weather_agent import weather_agent
from app.agents.itinerary_agent import itinerary_agent
from app.schemas import TravelPlan

logger = logging.getLogger(__name__)


def _load_iata_map() -> Dict[str, str]:
    """
    Load a small IATA->City mapping JSON shipped with the repo.
    """
    base = os.path.dirname(__file__)  
    path = os.path.join(base, "utils", "iata_city_map.json")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
           
            return {k.upper(): v for k, v in data.items()}
    except FileNotFoundError:
        logger.warning("iata_city_map.json not found at %s — falling back to empty map", path)
        return {}
    except Exception:
        logger.exception("Failed to load iata_city_map.json")
        return {}


IATA_TO_CITY = _load_iata_map()


def _resolve_city_from_code(code: str) -> str:
    """
    Return a human-readable city name for a given IATA code.
    If unknown, return the code itself so the LLM receives something (but we prefer explicit names).
    """
    if not code:
        return ""
    code_u = code.upper()
    return IATA_TO_CITY.get(code_u, code_u)


def generate_plan(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sequential planner (Option B).
    State contains both:
      - destination_code: IATA code (used by flights_agent/SerpAPI)
      - destination: human-readable city name (used by LLM agents)
    """

    source_code = (data.get("source") or "BOM").upper()
    dest_code = (data.get("destination") or data.get("destination_code") or "GOI").upper()

    
    destination_city = data.get("destination_city") or data.get("destination_name") or _resolve_city_from_code(dest_code)

    days = int(data.get("num_days", 3))
    theme = data.get("theme", "Luxury")
    depart = data.get("depart_date")
    return_d = data.get("return_date")
    if not return_d and depart:
        try:
            return_d = (datetime.strptime(depart, "%Y-%m-%d") + timedelta(days=days)).strftime("%Y-%m-%d")
        except Exception:
            return_d = depart

    
    state = {
        "source": source_code,               
        "destination_code": dest_code,       
        "destination": destination_city,      
        "num_days": days,
        "theme": theme,
        "depart_date": depart,
        "return_date": return_d,
        "flights": [],
        "hotels": {},
        "attractions": [],
        "restaurants": [],
        "transport": {},
        "weather": {},
        "itinerary": []
    }

    try:
        state.update(flights_agent(state))
    except Exception:
        logger.exception("planner: flights_agent failed; continuing with available data")

    try:
        state.update(hotels_agent(state))
    except Exception:
        logger.exception("planner: hotels_agent failed; continuing")

    try:
        state.update(attractions_agent(state))
    except Exception:
        logger.exception("planner: attractions_agent failed; continuing")

    try:
        state.update(restaurants_agent(state))
    except Exception:
        logger.exception("planner: restaurants_agent failed; continuing")

    try:
        state.update(transport_agent(state))
    except Exception:
        logger.exception("planner: transport_agent failed; continuing")

    try:
        state.update(weather_agent(state))
    except Exception:
        logger.exception("planner: weather_agent failed; continuing")

    try:
        state.update(itinerary_agent(state))
    except Exception:
        logger.exception("planner: itinerary_agent failed; continuing")

    result = {
        "source": state.get("source"),
        "destination": state.get("destination"), 
        "depart_date": state.get("depart_date"),
        "return_date": state.get("return_date"),
        "num_days": state.get("num_days"),
        "theme": state.get("theme"),
        "flights": state.get("flights", []),
        "hotels": state.get("hotels", {"budget": [], "mid_range": [], "luxury": []}),
        "attractions": state.get("attractions", []),
        "restaurants": state.get("restaurants", []),
        "transport": state.get("transport", {}),
        "weather": state.get("weather", {}),
        "itinerary": state.get("itinerary", []),
        "meta": {
            "planner": "sequential",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }

    try:
        return TravelPlan(**result).model_dump()
    except Exception:
        
        logger.exception("TravelPlan validation failed — returning best-effort result")
        return result
