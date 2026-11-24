from fastapi import APIRouter
from backend.services.weather_service import get_weather_intelligence

router = APIRouter()

@router.get("/intelligence")
async def weather_intel(lat: float, lon: float):
    return await get_weather_intelligence(lat, lon)
