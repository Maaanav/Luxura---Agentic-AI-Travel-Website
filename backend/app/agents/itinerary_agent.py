import logging
import re
from typing import Dict, Any, List
from app.utils.openai_helper import ask_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Return ONLY valid JSON.
Format: An array of objects:
[
  {"day": 1, "morning": "short", "afternoon": "short", "evening": "short"},
  ...
]
Important:
- The 'destination' value you receive may be an IATA code; treat any code as the corresponding CITY NAME.
- If the state contains "trip_type": "business", you may include corporate activities. Otherwise, ALWAYS produce a TOURIST itinerary (no company visits, no headquarters, no R&D tours).
- Keep each slot to one short sentence (no lists). Use dates relative to depart_date if provided.
- RETURN VALID JSON ONLY.
"""

SAMPLE = [
    {"day": 1, "morning": "Arrive and check in to your hotel", "afternoon": "Explore the local market", "evening": "Dinner at a popular local restaurant"},
    {"day": 2, "morning": "Visit the main cultural attraction", "afternoon": "Relax at a nearby park or lake", "evening": "Attend a street food tour"},
    {"day": 3, "morning": "Take a short walking tour of the old town", "afternoon": "Shopping and souvenirs", "evening": "Enjoy a farewell dinner"}
]

_CORPORATE_KEYWORDS = [
    r"\bheadquarter(s)?\b", r"\bR&D\b", r"\bresearch and development\b",
    r"\bseminar\b", r"\bworkshop\b", r"\bpresentation\b", r"\bmeeting\b",
    r"\bnetwork(ing)?\b", r"\bexecutive(s)?\b", r"\bcompany\b", r"\bemployees?\b",
    r"\bbusiness\b", r"\bproduct launch\b"
]
_CORP_RE = re.compile("|".join(_CORPORATE_KEYWORDS), flags=re.IGNORECASE)


def _sanitize_text_for_tourist(text: str) -> str:
    if not text:
        return ""
    if _CORP_RE.search(text):
        substitutions = [
            ("headquarters", "a local museum"),
            ("R&D", "a science/technology exhibit"),
            ("research and development", "a technology museum"),
            ("seminar", "a local cultural talk"),
            ("workshop", "a handicraft workshop"),
            ("presentation", "a guided museum tour"),
            ("meeting", "a leisurely city walk"),
            ("network", "a food tour or cultural meetup"),
            ("executive", "local leaders/historians"),
            ("employees", "locals"),
            ("company", "local attraction"),
            ("business", "leisure"),
            ("product launch", "local festival or event")
        ]
        sanitized = text
        for old, new in substitutions:
            sanitized = re.sub(re.escape(old), new, sanitized, flags=re.IGNORECASE)
        if _CORP_RE.search(sanitized):
            return "Explore a cultural attraction nearby."
        return sanitized
    return text


def _to_itinerary(data: Any, num_days: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    if isinstance(data, list):
        for i, elem in enumerate(data, start=1):
            if not isinstance(elem, dict):
                continue
            daynum = int(elem.get("day", i))
            morning = str(elem.get("morning", "")).strip()
            afternoon = str(elem.get("afternoon", "")).strip()
            evening = str(elem.get("evening", "")).strip()
            out.append({"day": daynum, "morning": morning, "afternoon": afternoon, "evening": evening})
    elif isinstance(data, dict):
        for key in ("itinerary", "days", "plan", "schedule"):
            if key in data and isinstance(data[key], list):
                return _to_itinerary(data[key], num_days)
        items = []
        for k, v in data.items():
            if isinstance(v, dict) and any(slot in v for slot in ("morning", "afternoon", "evening")):
                try:
                    daynum = int(k)
                except Exception:
                    daynum = len(items) + 1
                items.append({"day": daynum, "morning": v.get("morning", ""), "afternoon": v.get("afternoon", ""), "evening": v.get("evening", "")})
        if items:
            out = items

    if len(out) < num_days:
        for i in range(len(out) + 1, num_days + 1):
            if i <= len(SAMPLE):
                out.append(SAMPLE[i - 1])
            else:
                out.append({"day": i, "morning": "", "afternoon": "", "evening": ""})

    out = sorted(out, key=lambda x: x.get("day", 0))
    return out


def itinerary_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        
        dest_city = state.get("destination") or state.get("destination_code") or "Unknown"
        dest_code = state.get("destination_code", "")
        days = int(state.get("num_days", 1))
        trip_type = state.get("trip_type", "tourist").lower()
        depart_date = state.get("depart_date") or ""

        
        extra = f" (IATA: {dest_code})" if dest_code else ""
        prompt = (
            f"Destination: {dest_city}{extra}.\n"
            f"Trip type: {trip_type}.\n"
            f"Create a {days}-day itinerary for {dest_city}. "
            "Keep each slot to one short sentence and avoid any corporate visits unless trip_type='business'."
        )

        raw = ask_llm(prompt, SYSTEM_PROMPT)

        if raw is None:
            logger.warning("itinerary_agent: ask_llm returned None; using SAMPLE")
            return {"itinerary": _to_itinerary(SAMPLE, days)}

        itinerary = _to_itinerary(raw, days)

        
        if trip_type != "business":
            for day in itinerary:
                for slot in ("morning", "afternoon", "evening"):
                    original = day.get(slot, "") or ""
                    sanitized = _sanitize_text_for_tourist(original)
                    if not sanitized.strip() and _CORP_RE.search(original):
                        sanitized = "Explore a cultural attraction nearby."
                    day[slot] = sanitized if sanitized else original

        
        for d in itinerary:
            for slot in ("morning", "afternoon", "evening"):
                d[slot] = (d.get(slot) or "").strip()

        return {"itinerary": itinerary}

    except Exception:
        logger.exception("itinerary_agent error")
        return {"itinerary": _to_itinerary(SAMPLE, int(state.get("num_days", 1)))}
