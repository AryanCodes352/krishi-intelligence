from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from backend.database import get_db
from backend.models.farm import Farm
from backend.schemas.farm import ExpertRequest
from backend.services.expert_service import generate_expert_advice
from backend.services.weather_service import get_weather_intelligence
from backend.services.soil_service import get_soil_intelligence
from backend.services.market_service import get_market_intelligence, is_market_supported
from backend.services.crop_model import get_crop_stage

router = APIRouter()

@router.post("/ask")
async def expert_ask(req: ExpertRequest, db: Session = Depends(get_db)):
    """
    AI Agronomist guidance endpoint.
    Loads real farm profile from database and generates contextual advice.
    """
    farm = None
    if req.farm_id:
        farm = db.query(Farm).filter(Farm.id == req.farm_id).first()

    if farm:
        crop = farm.crop or "Wheat"
        variety = farm.crop_variety or ""
        district = farm.district or "Lucknow"
        state = farm.state or "Uttar Pradesh"
        location = farm.location or district
        sowing_date = farm.sowing_date or "2025-11-15"
        soil_tested = bool(farm.soil_data_available)
        lat = farm.lat or 26.8467
        lon = farm.lon or 80.9462
    else:
        # Fallback profile for ad-hoc or unpersisted farm query
        crop = "Wheat"
        variety = "HD-2967"
        district = "Lucknow"
        state = "Uttar Pradesh"
        location = "Malihabad"
        sowing_date = "2025-11-15"
        soil_tested = False
        lat = 26.8467
        lon = 80.9462

    try:
        sowing_dt = datetime.strptime(sowing_date, "%Y-%m-%d")
        days_after_sowing = max(0, (datetime.now() - sowing_dt).days)
    except Exception:
        days_after_sowing = 0
    crop_stage = get_crop_stage(crop, days_after_sowing)

    farm_data = {
        "crop": crop,
        "crop_variety": variety,
        "district": district,
        "state": state,
        "location": location,
        "sowing_date": sowing_date,
        "crop_stage": crop_stage,
        "soil_data_available": soil_tested,
        "lat": lat,
        "lon": lon,
    }

    # Fetch contextual layers
    try:
        weather_data = await get_weather_intelligence(lat, lon)
    except Exception:
        weather_data = {}

    try:
        soil_data = get_soil_intelligence(
            district=district,
            state=state,
            crop=crop,
            crop_stage=crop_stage,
            soil_tested=soil_tested,
            farm_context=farm_data,
        )
    except Exception:
        soil_data = {}

    # Only fetch market data and run ML prediction for supported crops.
    # For unsupported crops pass empty dicts so expert advice never references
    # Wheat prices when answering questions about Rice, Mustard, etc.
    if is_market_supported(crop):
        try:
            market_data = get_market_intelligence(crop, district, state)
        except Exception:
            market_data = {}

        prediction_data = None
        try:
            from ml.predict import predict_price
            from backend.services.market_service import get_historical_df, get_current_price
            from datetime import date
            curr_p = float(market_data.get("current", {}).get("modal_price") or get_current_price(crop) or 0)
            if curr_p > 0:
                h_df = get_historical_df(crop)
                p7 = predict_price(curr_p, date.today(), h_df, 7)
                p15 = predict_price(curr_p, date.today(), h_df, 15)
                prediction_data = {
                    "prediction_7d": p7.get("prediction", {}) if not p7.get("insufficient_data") else {},
                    "prediction_15d": p15.get("prediction", {}) if not p15.get("insufficient_data") else {},
                }
        except Exception:
            prediction_data = None
    else:
        # Market intelligence and ML prediction not available for this crop.
        # Use an empty dict so the expert service knows no price data is available.
        market_data = {}
        prediction_data = None

    advice = generate_expert_advice(
        question=req.question,
        farm_data=farm_data,
        weather_data=weather_data,
        soil_data=soil_data,
        market_data=market_data,
        prediction_data=prediction_data,
    )

    return advice
