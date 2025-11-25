# serpapi_helper.py
import os
import requests
import logging

logger = logging.getLogger(__name__)
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def _as_rupee_string(value):
    try:
        n = int(value)
        return f"₹{n:,}"
    except Exception:
        return str(value) if value else ""

def _as_duration_string(value):
    """Convert numeric minutes to 'Xh Ym'. Accepts strings too."""
    if value is None:
        return ""
    try:
        n = int(value)
        h = n // 60
        m = n % 60
        if h > 0:
            return f"{h}h {m}m"
        return f"{m}m"
    except:
        return str(value)

def _extract_duration(flight_info):
    """
    SerpAPI data is inconsistent. Try multiple patterns to find duration.
    """
    # Best flights → f["duration"]["value"]
    dur = flight_info.get("duration")

    if isinstance(dur, dict):
        # {"value": 70, "text": "1h 10m"}
        if "value" in dur:
            return _as_duration_string(dur["value"])
        if "text" in dur:
            return dur["text"]

    # Direct numeric or string
    if isinstance(dur, (int, float, str)):
        return _as_duration_string(dur)

    # Look inside flight legs
    flights = flight_info.get("flights") or [{"duration": None}]
    leg = flights[0]
    if "duration" in leg:
        return _as_duration_string(leg["duration"])

    # If still nothing:
    return ""

def fetch_flights(source: str, dest: str, depart: str = None, ret: str = None):
    if not SERPAPI_KEY:
        logger.error("SERPAPI_KEY missing — cannot fetch flights")
        return []

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_flights",
        "departure_id": source,
        "arrival_id": dest,
        "currency": "INR",
        "hl": "en",
        "api_key": SERPAPI_KEY,
    }

    if depart:
        params["outbound_date"] = depart
    if ret:
        params["return_date"] = ret

    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("best_flights") or data.get("other_flights") or []
        flights = []

        for f in results[:6]:
            # Extract base structure
            first_leg = (f.get("flights") or [{}])[0]

            price = f.get("price")
            if isinstance(price, dict):
                price = price.get("price_display") or price.get("amount")

            price = _as_rupee_string(price)
            duration = _extract_duration(f)
            airline = first_leg.get("airline_name") or first_leg.get("airline", "Unknown")

            stops = "Non-stop" if f.get("total_layovers", 0) == 0 else f"{f.get('total_layovers')} stop(s)"

            logo = (
                first_leg.get("airline_logo")
                or f.get("airline_logo")
                or None
            )
            
            flights.append({
                "airline": airline,
                "price": price,
                "duration": duration,
                "stops": stops,
                "airline_logo": logo
            })

        return flights

    except Exception as e:
        logger.exception("SerpAPI error")
        return []
