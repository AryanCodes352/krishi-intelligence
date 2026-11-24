from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone, date
from typing import Optional, Dict, Any, List

from backend.database import get_db
from backend.schemas.farm import (
    FarmOnboardRequest,
    FarmResponse,
    FarmUpdateRequest,
    FarmEventResponse,
    DigitalTwinResponse,
    DigitalTwinFarmer,
    DigitalTwinFarm,
    DigitalTwinCrop,
    DigitalTwinMetadata,
)
from backend.models.farm import Farm, FarmEvent, FarmObservation, FarmSoilProfile

from backend.services.crop_model import get_crop_stage
from backend.services.market_service import (
    is_market_supported,
    get_market_intelligence,
    get_market_intelligence_async,
    get_current_price,
    get_historical_df,
)
from backend.services.weather_service import get_weather_intelligence
from backend.services.soil_service import get_soil_intelligence
from backend.services.risk_engine import compute_risk
from backend.services.decision_engine import compute_scenarios

router = APIRouter()

LOCATION_COORDS = {
    ("Lucknow", "Uttar Pradesh"): (26.8467, 80.9462),
    ("Kanpur Nagar", "Uttar Pradesh"): (26.4499, 80.3319),
    ("Unnao", "Uttar Pradesh"): (26.5456, 80.4882),
}

@router.post("/onboard", response_model=FarmResponse)
def onboard_farm(req: FarmOnboardRequest, db: Session = Depends(get_db)):
    if not is_market_supported(req.crop):
        raise HTTPException(
            status_code=400,
            detail=(
                "This prototype currently supports Wheat only. "
                "Market Intelligence and ML price prediction are available for Wheat. "
                "Rice, Mustard and other crops will be supported in a future version."
            ),
        )

    coords = LOCATION_COORDS.get((req.district, req.state))
    lat, lon = coords if coords else (None, None)
    db_farm = Farm(
        farmer_name=req.farmer_name,
        location=req.location,
        district=req.district,
        state=req.state,
        crop=req.crop,
        crop_variety=req.crop_variety,
        sowing_date=req.sowing_date,
        farm_area_acres=req.farm_area_acres,
        soil_data_available=req.soil_data_available,
        lat=lat,
        lon=lon,
        phone=req.phone
    )
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    
    # Genuine Farm Event: Registration
    try:
        event = FarmEvent(
            farm_id=db_farm.id,
            event_type="FARM_CREATED",
            title="Farm Registered",
            description=f"Farm profile created for {db_farm.farmer_name} with {db_farm.farm_area_acres} acres in {db_farm.district}, {db_farm.state}.",
            source="USER_ACTION",
        )
        db.add(event)
        db.commit()
    except Exception:
        db.rollback()

    try:
        sowing = datetime.strptime(req.sowing_date, "%Y-%m-%d")
        days = (datetime.now() - sowing).days
    except:
        days = 0
        
    return FarmResponse(
        farm_id=db_farm.id,
        farmer_name=db_farm.farmer_name,
        crop=db_farm.crop,
        crop_variety=db_farm.crop_variety,
        location=db_farm.location,
        district=db_farm.district,
        state=db_farm.state,
        sowing_date=db_farm.sowing_date,
        farm_area_acres=db_farm.farm_area_acres,
        days_after_sowing=days,
        crop_stage=get_crop_stage(db_farm.crop, days),
        lat=db_farm.lat,
        lon=db_farm.lon,
        created_at=db_farm.created_at.isoformat() if db_farm.created_at else datetime.now(timezone.utc).isoformat()
    )

@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(farm_id: str, db: Session = Depends(get_db)):
    db_farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not db_farm:
        raise HTTPException(status_code=404, detail="Farm not found")
        
    try:
        sowing = datetime.strptime(db_farm.sowing_date, "%Y-%m-%d")
        days = (datetime.now() - sowing).days
    except:
        days = 0
        
    return FarmResponse(
        farm_id=db_farm.id,
        farmer_name=db_farm.farmer_name,
        crop=db_farm.crop,
        crop_variety=db_farm.crop_variety,
        location=db_farm.location,
        district=db_farm.district,
        state=db_farm.state,
        sowing_date=db_farm.sowing_date,
        farm_area_acres=db_farm.farm_area_acres,
        days_after_sowing=days,
        crop_stage=get_crop_stage(db_farm.crop, days),
        lat=db_farm.lat,
        lon=db_farm.lon,
        created_at=db_farm.created_at.isoformat() if db_farm.created_at else datetime.now(timezone.utc).isoformat()
    )

async def _build_digital_twin_payload(farm: Farm, db: Session) -> DigitalTwinResponse:
    """
    Assemble the complete Farm Digital Twin by aggregating persistent farm identity,
    crop phenology, existing intelligence services, provenance metadata, and genuine events.
    """
    # 1. Phenology
    try:
        sowing = datetime.strptime(farm.sowing_date, "%Y-%m-%d")
        days = max(0, (datetime.now() - sowing).days)
    except Exception:
        days = 0
    crop_stage = get_crop_stage(farm.crop or "Wheat", days)

    # 2. Weather intelligence — only call service when GPS coordinates are known
    if farm.lat is None or farm.lon is None:
        weather = {
            "current": None,
            "forecast_7day": [],
            "agricultural_risk": {
                "rainfall_risk": {"score": 0, "level": "UNKNOWN"},
                "temperature_risk": {"score": 0, "level": "UNKNOWN"},
                "humidity_risk": {"score": 0, "level": "UNKNOWN"},
                "overall_weather_risk": 0,
                "overall_level": "UNKNOWN",
            },
            "data_source": {
                "status": "COORDINATES_UNAVAILABLE",
                "note": (
                    f"Precise coordinates are unavailable for district "
                    f"'{farm.district or 'unknown'}', {farm.state or 'unknown'}. "
                    "Weather intelligence requires GPS coordinates."
                ),
            },
        }
    else:
        try:
            weather = await get_weather_intelligence(farm.lat, farm.lon)
        except Exception as e:
            weather = {
                "current": None,
                "forecast_7day": [],
                "agricultural_risk": {
                    "rainfall_risk": {"score": 0, "level": "UNKNOWN"},
                    "temperature_risk": {"score": 0, "level": "UNKNOWN"},
                    "humidity_risk": {"score": 0, "level": "UNKNOWN"},
                    "overall_weather_risk": 0,
                    "overall_level": "UNKNOWN",
                },
                "data_source": {"status": "UNAVAILABLE", "error": str(e)},
            }

    # 3. Soil intelligence
    active_soil_profile = (
        db.query(FarmSoilProfile)
        .filter(FarmSoilProfile.farm_id == farm.id, FarmSoilProfile.is_active == True)
        .order_by(FarmSoilProfile.confirmed_at.desc())
        .first()
    )
    try:
        soil = get_soil_intelligence(
            district=farm.district or "Lucknow",
            state=farm.state or "Uttar Pradesh",
            crop=farm.crop or "Wheat",
            crop_stage=crop_stage,
            soil_tested=bool(farm.soil_data_available),
            farm_area=farm.farm_area_acres or 1.0,
            farm_context={
                "farm_id": str(farm.id),
                "farmer_name": farm.farmer_name,
                "crop": farm.crop,
                "crop_variety": farm.crop_variety,
                "crop_stage": crop_stage,
                "sowing_date": farm.sowing_date,
            },
            farm_soil_profile=active_soil_profile,
        )

    except Exception as e:
        soil = {
            "parameters": {},
            "crop_suitability": {"score": 0, "label": "Unknown"},
            "overall_soil_risk": {"score": 0, "level": "UNKNOWN"},
            "data_source": {"type": "DATA_UNAVAILABLE", "status": "UNAVAILABLE", "error": str(e)},
        }

    # 4. Market intelligence & price prediction
    market_is_supported = is_market_supported(farm.crop or "")
    if market_is_supported:
        market = await get_market_intelligence_async(farm.crop, farm.district, farm.state)
        current_price = float(
            market.get("current", {}).get("modal_price") or get_current_price(farm.crop) or 0
        )
        historical_df = get_historical_df(farm.crop)
        try:
            from ml.predict import predict_price
            pred_7d = predict_price(
                current_price=current_price,
                current_date=date.today(),
                historical_df=historical_df,
                horizon_days=7,
            )
        except Exception:
            pred_7d = {"insufficient_data": True, "reason": "Prediction service error"}
    else:
        market = {
            "current": None,
            "historical": None,
            "mandi_comparison": [],
            "data_source": {
                "type": "MARKET_UNSUPPORTED",
                "commodity": farm.crop,
                "status": "MARKET_UNSUPPORTED",
                "reason": f"Market Intelligence for {farm.crop} is not yet available in this prototype. Market prediction is planned for a future version.",
            },
        }
        current_price = 0.0
        pred_7d = {
            "insufficient_data": True,
            "reason": f"Market Intelligence for {farm.crop} is not yet available in this prototype.",
            "data_type": "MARKET_UNSUPPORTED",
        }

    # 5. Risk evaluation
    risk = compute_risk(weather, soil, crop_stage, days, market)
    weather_risk_score = risk.get("weather_risk", {}).get("score", 0)

    # 6. Decision engine
    market_src = (market.get("data_source") or {}).get("type", "HISTORICAL_SEED") if market else "HISTORICAL_SEED"
    curr_market = (market.get("current") or {}) if market else {}
    src_market = (market.get("data_source") or {}) if market else {}
    market_dt = curr_market.get("date") or src_market.get("latest_date")
    pred_7d_for_decision = (
        {
            "point_estimate": pred_7d.get("prediction", {}).get("point_estimate", current_price),
            "min_price": pred_7d.get("prediction", {}).get("min_price"),
            "max_price": pred_7d.get("prediction", {}).get("max_price"),
        }
        if not pred_7d.get("insufficient_data")
        else None
    )

    decision = compute_scenarios(
        farm={"farm_area_acres": farm.farm_area_acres, "crop": farm.crop, "crop_stage": crop_stage},
        current_price=current_price,
        prediction_7d=pred_7d_for_decision,
        prediction_15d=None,
        weather_risk=weather_risk_score,
        market_source=market_src,
        market_date=market_dt,
    )

    # 7. Normalize price prediction representation
    if pred_7d.get("insufficient_data"):
        norm_prediction = {
            "current_price": int(current_price),
            "insufficient_data": True,
            "reason": pred_7d.get("reason", "Data unavailable"),
            "data_type": pred_7d.get("data_type", "DATA_UNAVAILABLE"),
            "market_supported": market_is_supported,
        }
    else:
        p = pred_7d.get("prediction", {})
        norm_prediction = {
            "current_price": int(current_price),
            "unit": "Rs/quintal",
            "prediction": {
                "min_price": p.get("min_price", int(current_price)),
                "max_price": p.get("max_price", int(current_price)),
                "point_estimate": p.get("point_estimate", int(current_price)),
                "confidence_pct": p.get("confidence_pct", 60),
                "confidence_level": p.get("confidence_level", "MEDIUM"),
            },
            "model_info": pred_7d.get("model_info", {}),
            "data_type": "MODEL_PREDICTION",
            "insufficient_data": False,
        }

    # 8. Data provenance mapping
    weather_prov = weather.get("data_source", {}).get("status", "UNAVAILABLE")
    soil_prov = soil.get("data_source", {}).get("type", "REGIONAL_ESTIMATE")
    market_prov = (
        market.get("data_source", {}).get("type", "HISTORICAL_SEED")
        if market_is_supported
        else "MARKET_UNSUPPORTED"
    )
    pred_prov = (
        "MODEL_PREDICTION"
        if market_is_supported and not pred_7d.get("insufficient_data")
        else ("MARKET_UNSUPPORTED" if not market_is_supported else "DATA_UNAVAILABLE")
    )

    provenance = {
        "farmer_profile": "USER_ONBOARDED",
        "weather": weather_prov,
        "soil": soil_prov,
        "market": market_prov,
        "prediction": pred_prov,
        "decision": "CALCULATED" if market_is_supported else "MARKET_UNAVAILABLE",
    }

    # 9. Query genuine events
    db_events = (
        db.query(FarmEvent)
        .filter(FarmEvent.farm_id == farm.id)
        .order_by(FarmEvent.timestamp.desc())
        .limit(20)
        .all()
    )
    events_res = [
        FarmEventResponse(
            id=ev.id,
            farm_id=ev.farm_id,
            event_type=ev.event_type,
            timestamp=ev.timestamp.isoformat() if ev.timestamp else datetime.now(timezone.utc).isoformat(),
            title=ev.title,
            description=ev.description,
            source=ev.source or "SYSTEM",
        )
        for ev in db_events
    ]

    # 10. Query recent decision observations
    db_obs = (
        db.query(FarmObservation)
        .filter(FarmObservation.farm_id == farm.id)
        .order_by(FarmObservation.observed_at.desc())
        .limit(5)
        .all()
    )
    decision_history = [
        {
            "observed_at": obs.observed_at.isoformat() if obs.observed_at else None,
            "overall_risk_score": obs.overall_risk_score,
            "current_price": obs.current_price,
            "recommendation_action": obs.recommendation_action,
            "recommendation_confidence": obs.recommendation_confidence,
        }
        for obs in db_obs
    ]

    created_at_str = farm.created_at.isoformat() if farm.created_at else datetime.now(timezone.utc).isoformat()
    updated_at_str = farm.updated_at.isoformat() if farm.updated_at else created_at_str

    return DigitalTwinResponse(
        farm_id=farm.id,
        farmer=DigitalTwinFarmer(
            name=farm.farmer_name or "Farmer",
            phone=farm.phone or "",
        ),
        farm=DigitalTwinFarm(
            state=farm.state or "",
            district=farm.district or "",
            location=farm.location or "",
            acreage=float(farm.farm_area_acres or 0.0),
            soil_data_available=bool(farm.soil_data_available),
            lat=farm.lat,
            lon=farm.lon,
        ),
        crop=DigitalTwinCrop(
            name=farm.crop or "Wheat",
            variety=farm.crop_variety or "",
            sowing_date=farm.sowing_date or "",
            stage=crop_stage,
            days_after_sowing=days,
        ),
        metadata=DigitalTwinMetadata(
            created_at=created_at_str,
            updated_at=updated_at_str,
        ),
        intelligence={
            "weather": weather,
            "soil": soil,
            "market": market,
            "risk": risk,
            "prediction": norm_prediction,
            "decision": decision,
        },
        data_provenance=provenance,
        events=events_res,
        decision_history=decision_history,
    )

@router.get("/{farm_id}/digital-twin", response_model=DigitalTwinResponse)
async def get_digital_twin(farm_id: str, db: Session = Depends(get_db)):
    """
    Retrieve the complete persistent Farm Digital Twin.
    Aggregates farm profile, phenology, multi-layer intelligence, provenance, and genuine events.
    """
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    return await _build_digital_twin_payload(farm, db)

@router.put("/{farm_id}", response_model=DigitalTwinResponse)
async def update_farm(farm_id: str, req: FarmUpdateRequest, db: Session = Depends(get_db)):
    """
    Update persistent farm profile fields, enforce multi-crop guardrails,
    record genuine PROFILE_UPDATED event, and return the updated Digital Twin.
    """
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    updated_fields = []
    if req.farmer_name is not None and req.farmer_name.strip():
        farm.farmer_name = req.farmer_name.strip()
        updated_fields.append("farmer_name")

    if req.farm_area_acres is not None and req.farm_area_acres > 0:
        farm.farm_area_acres = float(req.farm_area_acres)
        updated_fields.append("farm_area_acres")

    if req.location is not None and req.location.strip():
        farm.location = req.location.strip()
        updated_fields.append("location")

    if req.district is not None and req.district.strip():
        farm.district = req.district.strip()
        updated_fields.append("district")

    if req.state is not None and req.state.strip():
        farm.state = req.state.strip()
        updated_fields.append("state")

    if req.district or req.state:
        coords = LOCATION_COORDS.get((farm.district, farm.state))
        if coords:
            farm.lat, farm.lon = coords

    if req.sowing_date is not None and req.sowing_date.strip():
        farm.sowing_date = req.sowing_date.strip()
        updated_fields.append("sowing_date")

    if req.crop is not None and req.crop.strip():
        farm.crop = req.crop.strip()
        updated_fields.append("crop")
        # Multi-crop guardrail: if crop is not wheat, do not keep wheat variety
        if not is_market_supported(farm.crop):
            if farm.crop_variety and farm.crop_variety.strip().upper() in ["HD-2967", "PBW-343", "WH-542", "DBW-187"]:
                farm.crop_variety = ""
        else:
            if req.crop_variety is not None:
                farm.crop_variety = req.crop_variety.strip()
                updated_fields.append("crop_variety")
    elif req.crop_variety is not None:
        if is_market_supported(farm.crop or ""):
            farm.crop_variety = req.crop_variety.strip()
            updated_fields.append("crop_variety")
        else:
            farm.crop_variety = ""

    if req.soil_data_available is not None:
        farm.soil_data_available = req.soil_data_available
        updated_fields.append("soil_data_available")

    if req.phone is not None:
        farm.phone = req.phone.strip()
        updated_fields.append("phone")

    farm.updated_at = datetime.now(timezone.utc)

    # Record genuine event
    desc = f"Updated fields: {', '.join(updated_fields)}." if updated_fields else "Profile refreshed."
    event = FarmEvent(
        farm_id=farm.id,
        event_type="PROFILE_UPDATED",
        title="Farm Profile Updated",
        description=desc,
        source="USER_ACTION",
    )
    db.add(event)
    db.commit()
    db.refresh(farm)

    return await _build_digital_twin_payload(farm, db)

