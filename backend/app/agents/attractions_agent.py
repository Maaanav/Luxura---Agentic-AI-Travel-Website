from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime
from dotenv import load_dotenv
import os

from app.planner import generate_plan
from app.schemas import TravelPlan

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY missing in .env file")


limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TravelRequest(BaseModel):
    source: str
    destination: str
    depart_date: str
    return_date: str
    theme: str = "Luxury"
    num_days: Optional[int] = None


@app.get("/health")
async def health():
    return {"status": "healthy", "server_time": datetime.now().isoformat()}


@app.post("/api/generate_plan")
@limiter.limit("5/minute")
async def create_plan(request: Request, req: TravelRequest):

    if not req.depart_date or not req.return_date:
        raise HTTPException(400, "Both depart_date and return_date are required")

    if not req.num_days:
        d1 = datetime.fromisoformat(req.depart_date)
        d2 = datetime.fromisoformat(req.return_date)
        req.num_days = max(1, (d2 - d1).days)

    city_map = {"GOI": "Goa", "DEL": "Delhi", "JAI": "Jaipur", "BOM": "Mumbai"}
    destination_city = city_map.get(req.destination.upper(), req.destination)

    payload = {
        "source": req.source.upper(),
        "destination": req.destination.upper(),
        "destination_city": destination_city,
        "depart_date": req.depart_date,
        "return_date": req.return_date,
        "num_days": req.num_days,
        "theme": req.theme,
    }

    try:
        result = generate_plan(payload)
        return TravelPlan(**result).model_dump()
    except Exception as e:
        raise HTTPException(500, f"Travel plan generation failed: {str(e)}")
