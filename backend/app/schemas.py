from pydantic import BaseModel
from typing import List, Dict, Optional


class Flight(BaseModel):
    airline: str
    price: str
    duration: str
    stops: str
    airline_logo: Optional[str] = None


class Hotel(BaseModel):
    name: str
    price: str
    area: str
    highlights: List[str]


class Hotels(BaseModel):
    budget: List[Hotel] = []
    mid_range: List[Hotel] = []
    luxury: List[Hotel] = []


class ItineraryDay(BaseModel):
    day: int
    morning: str
    afternoon: str
    evening: str


class TravelPlan(BaseModel):
    source: str
    destination: str
    depart_date: str
    return_date: str
    num_days: int
    theme: str

    flights: List[Flight]
    hotels: Hotels
    attractions: List[Dict]
    restaurants: List[Dict]
    transport: Dict
    weather: Dict
    itinerary: List[ItineraryDay]
