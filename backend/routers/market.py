from fastapi import APIRouter
from backend.services.market_service import get_market_intelligence_async

router = APIRouter()

@router.get("/intelligence")
async def market_intel(commodity: str, district: str, state: str):
    return await get_market_intelligence_async(commodity, district, state)
