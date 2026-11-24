"""
Intelligence Router — Core Decision Engine Endpoint
=====================================================
POST /api/intelligence/analyze

This is the central endpoint that:
1. Loads farm profile from DB
2. Fetches live weather from Open-Meteo
3. Loads soil data from ICAR regional dataset
4. Loads market data from historical seed CSV
5. Runs the ML price prediction model
6. Computes multi-factor risk scores
7. Computes sell-vs-wait decision scenarios
8. Builds explainability evidence
9. Detects what changed since last observation
10. Saves observation to DB for trend tracking
11. Returns the full analysis in the standardised API shape
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone, date
import json

from backend.database import get_db
from backend.schemas.farm import IntelligenceRequest
from backend.models.farm import Farm, FarmObservation, FarmEvent, FarmSoilProfile

from backend.services.weather_service import get_weather_intelligence
from backend.services.market_service import (
    get_market_intelligence,
    get_market_intelligence_async,
    get_current_price,
    get_historical_df,
    is_market_supported,
)
from backend.services.soil_service import get_soil_intelligence
from backend.services.crop_model import get_crop_stage
from backend.services.risk_engine import compute_risk
from backend.services.decision_engine import compute_scenarios
from backend.services.explainability import get_explanation

router = APIRouter()


@router.post("/analyze")
async def analyze(req: IntelligenceRequest, db: Session = Depends(get_db)):
    """
    Run a full farm intelligence analysis and return the complete decision package.
    """
    # ── Load farm profile ─────────────────────────────────────────────────
    farm = db.query(Farm).filter(Farm.id == req.farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    # ── Crop stage ────────────────────────────────────────────────────────
    try:
        sowing = datetime.strptime(farm.sowing_date, "%Y-%m-%d")
        days_after_sowing = (datetime.now() - sowing).days
    except Exception:
        days_after_sowing = 0
    crop_stage = get_crop_stage(farm.crop, days_after_sowing)

    # ── Fetch intelligence data ───────────────────────────────────────────
    active_soil_profile = (
        db.query(FarmSoilProfile)
        .filter(FarmSoilProfile.farm_id == farm.id, FarmSoilProfile.is_active == True)
        .order_by(FarmSoilProfile.confirmed_at.desc())
        .first()
    )
    weather = await get_weather_intelligence(farm.lat, farm.lon)
    soil = get_soil_intelligence(
        district=farm.district,
        state=farm.state,
        crop=farm.crop,
        crop_stage=crop_stage,
        soil_tested=bool(farm.soil_data_available),
        farm_area=farm.farm_area_acres,
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

    market = await get_market_intelligence_async(farm.crop, farm.district, farm.state)

    # ── Current and historical prices ─────────────────────────────────────
    # Only fetch prices/history for crops with real market support.
    # For unsupported crops we use 0 / None throughout — never a Wheat price.
    market_is_supported = is_market_supported(farm.crop)

    if market_is_supported:
        current_price = float(
            market.get("current", {}).get("modal_price") or get_current_price(farm.crop) or 0
        )
        historical_df = get_historical_df(farm.crop)
    else:
        current_price = 0.0
        historical_df = None

    # ── Price prediction via ML model ─────────────────────────────────────
    if market_is_supported:
        from ml.predict import predict_price

        pred_7d = predict_price(
            current_price=current_price,
            current_date=date.today(),
            historical_df=historical_df,
            horizon_days=7,
        )
        pred_15d = predict_price(
            current_price=current_price,
            current_date=date.today(),
            historical_df=historical_df,
            horizon_days=15,
        )
    else:
        pred_7d = {
            "insufficient_data": True,
            "reason": (
                f"Market Intelligence for {farm.crop} is not yet available in "
                "this prototype. Price prediction is planned for a future version."
            ),
            "data_type": "MARKET_UNSUPPORTED",
        }
        pred_15d = pred_7d

    # Build the price_prediction response
    if pred_7d.get("insufficient_data"):
        price_prediction = {
            "insufficient_data": True,
            "reason": pred_7d.get("reason", "Insufficient data"),
            "data_type": pred_7d.get("data_type", "UNAVAILABLE"),
            "market_supported": market_is_supported,
        }
        # Use current price for decision engine
        pred_7d_for_decision = None
        pred_15d_for_decision = None
    else:
        # Merge 7d and 15d into prediction blocks for display
        pred7 = pred_7d.get("prediction", {})
        pred15 = pred_15d.get("prediction", {}) if not pred_15d.get("insufficient_data") else {}
        meta = pred_7d.get("model_info", {})

        norm_pred_7d = {
            "min_price": pred7.get("min_price", int(current_price)),
            "max_price": pred7.get("max_price", int(current_price)),
            "point_estimate": pred7.get("point_estimate", int(current_price)),
            "min": pred7.get("min_price", int(current_price)),
            "max": pred7.get("max_price", int(current_price)),
            "point": pred7.get("point_estimate", int(current_price)),
            "confidence_pct": pred7.get("confidence_pct", 50),
            "confidence_level": pred7.get("confidence_level", "LOW"),
        }

        norm_pred_15d = {
            "min_price": pred15.get("min_price", int(current_price)),
            "max_price": pred15.get("max_price", int(current_price)),
            "point_estimate": pred15.get("point_estimate", int(current_price)),
            "min": pred15.get("min_price", int(current_price)),
            "max": pred15.get("max_price", int(current_price)),
            "point": pred15.get("point_estimate", int(current_price)),
            "confidence_pct": pred15.get("confidence_pct", 40),
            "confidence_level": pred15.get("confidence_level", "LOW"),
        }

        price_prediction = {
            "current_price": int(current_price),
            "unit": "Rs/quintal",
            "prediction": norm_pred_7d,
            "prediction_7d": norm_pred_7d,
            "prediction_15d": norm_pred_15d,
            "model_info": meta,
            "data_used": pred_7d.get("data_used", []),
            "data_type": "MODEL_PREDICTION",
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "insufficient_data": False,
        }
        pred_7d_for_decision = {"point_estimate": pred7.get("point_estimate", current_price), "min_price": pred7.get("min_price"), "max_price": pred7.get("max_price")}
        pred_15d_for_decision = {"point_estimate": pred15.get("point_estimate", current_price), "min_price": pred15.get("min_price"), "max_price": pred15.get("max_price")}

    # ── Risk scores ───────────────────────────────────────────────────────
    risk = compute_risk(weather, soil, crop_stage, days_after_sowing, market)
    weather_risk_score = risk["weather_risk"]["score"]

    # ── Decision scenarios ────────────────────────────────────────────────
    market_src = (market.get("data_source") or {}).get("type", "HISTORICAL_SEED") if market else "HISTORICAL_SEED"
    curr_market = (market.get("current") or {}) if market else {}
    src_market = (market.get("data_source") or {}) if market else {}
    market_dt = curr_market.get("date") or src_market.get("latest_date")

    decision = compute_scenarios(
        farm={"farm_area_acres": farm.farm_area_acres, "crop": farm.crop, "crop_stage": crop_stage},
        current_price=current_price,
        prediction_7d=pred_7d_for_decision,
        prediction_15d=pred_15d_for_decision,
        weather_risk=weather_risk_score,
        market_source=market_src,
        market_date=market_dt,
    )

    # ── Explainability ────────────────────────────────────────────────────
    explainability = get_explanation(
        decision=decision,
        risk=risk,
        market=market,
        price_prediction=price_prediction,
        weather=weather,
        farm={"farm_area_acres": farm.farm_area_acres, "crop": farm.crop, "crop_stage": crop_stage, "district": farm.district, "state": farm.state},
    )

    # ── Intelligence snapshot for dashboard cards ─────────────────────────
    seasonal_dir = market.get("historical", {}).get("seasonal_trend", {}).get("direction", "STABLE") if market.get("historical") else "STABLE"
    intelligence_snapshot = {
        "soil_condition": {
            "score": soil.get("crop_suitability", {}).get("score", 70),
            "label": soil.get("crop_suitability", {}).get("label", "Good"),
            "level": "LOW_RISK" if risk["soil_risk"]["score"] < 40 else ("MEDIUM_RISK" if risk["soil_risk"]["score"] < 70 else "HIGH_RISK"),
        },
        "weather_risk": {
            "score": weather_risk_score,
            "label": risk["weather_risk"]["level"].replace("_", " ").title() + " Risk",
            "level": risk["weather_risk"]["level"],
        },
        "crop_risk": {
            "score": risk["crop_risk"]["score"],
            "label": risk["crop_risk"]["level"].title(),
            "level": risk["crop_risk"]["level"],
        },
        "market_trend": {
            "direction": seasonal_dir if market_is_supported else "UNSUPPORTED",
            "label": (
                {"INCREASING": "Rising", "DECREASING": "Falling", "STABLE": "Stable"}.get(seasonal_dir, "Unknown")
                if market_is_supported else "Not Available"
            ),
            # current_price is 0 for unsupported crops — the frontend reads
            # market_supported to decide whether to display the value.
            "current_price": int(current_price) if market_is_supported else 0,
            "market_supported": market_is_supported,
        },
    }

    # ── What changed (compare with previous observation) ──────────────────
    what_changed = _compute_what_changed(farm, db, risk, current_price, decision)

    # ── Save observation to DB ────────────────────────────────────────────
    try:
        obs = FarmObservation(
            farm_id=farm.id,
            weather_risk_score=weather_risk_score,
            soil_risk_score=risk["soil_risk"]["score"],
            crop_risk_score=risk["crop_risk"]["score"],
            market_risk_score=risk["market_risk"]["score"],
            overall_risk_score=risk["overall_risk"]["score"],
            current_price=int(current_price),
            recommendation_action=decision["recommendation"]["action"],
            recommendation_confidence=decision["recommendation"]["confidence"],
            snapshot_json=json.dumps({"prediction_7d_point": price_prediction.get("prediction_7d", {}).get("point") if not price_prediction.get("insufficient_data") else None}),
        )
        db.add(obs)
        event = FarmEvent(
            farm_id=farm.id,
            event_type="ANALYSIS_RECORDED",
            title="Intelligence Analysis Completed",
            description=f"Risk evaluated at {risk['overall_risk']['score']}/100 ({risk['overall_risk']['level']}). Recommendation: {decision['recommendation']['action']}.",
            source="INTELLIGENCE_ENGINE",
        )
        db.add(event)
        db.commit()
    except Exception:
        db.rollback()  # Don't fail the response if DB write fails

    # ── Return complete analysis ──────────────────────────────────────────
    return {
        "farm_summary": {
            "farm_id": str(farm.id),
            "farmer_name": farm.farmer_name,
            "crop": farm.crop,
            "crop_variety": farm.crop_variety or "",
            "location": farm.location,
            "district": farm.district,
            "state": farm.state,
            "sowing_date": farm.sowing_date,
            "farm_area_acres": farm.farm_area_acres,
            "days_after_sowing": days_after_sowing,
            "crop_stage": crop_stage,
            "lat": farm.lat,
            "lon": farm.lon,
        },
        "intelligence_snapshot": intelligence_snapshot,
        "risk_breakdown": risk,
        "price_prediction": price_prediction,
        "decision": decision,
        "explainability": explainability,
        "what_changed": what_changed,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "data_freshness": {
            "weather": weather.get("data_source", {}).get("status", "UNKNOWN"),
            "market": market.get("data_source", {}).get("type", "HISTORICAL_SEED") if market.get("data_source") else "HISTORICAL_SEED",
            "soil": soil.get("data_source", {}).get("type", "REGIONAL_ESTIMATE") if soil.get("data_source") else "REGIONAL_ESTIMATE",
            "ml_model": "TRAINED_ON_SEED_DATA" if not price_prediction.get("insufficient_data") else "NOT_TRAINED",
            "market_supported": market_is_supported,
        },
    }



def _compute_what_changed(farm, db, current_risk: dict, current_price: float, current_decision: dict) -> dict:
    """
    Compare current analysis against the previous observation.
    Returns structured change report or 'no previous observation' message.
    """
    # Get the last two observations for this farm
    observations = (
        db.query(FarmObservation)
        .filter(FarmObservation.farm_id == farm.id)
        .order_by(FarmObservation.observed_at.desc())
        .limit(2)
        .all()
    )

    if len(observations) < 2:
        return {
            "available": False,
            "message": "First analysis for this farm — no previous observation to compare.",
        }

    prev = observations[1]  # second most recent
    changes = []

    # Overall risk change
    risk_change = current_risk["overall_risk"]["score"] - prev.overall_risk_score
    if abs(risk_change) >= 3:
        changes.append({
            "metric": "Overall farm risk",
            "from": str(prev.overall_risk_score),
            "to": str(current_risk["overall_risk"]["score"]),
            "direction": "up" if risk_change > 0 else "down",
            "unit": "/100",
        })

    # Weather risk change
    weather_change = current_risk["weather_risk"]["score"] - prev.weather_risk_score
    if abs(weather_change) >= 5:
        changes.append({
            "metric": "Weather risk",
            "from": str(prev.weather_risk_score),
            "to": str(current_risk["weather_risk"]["score"]),
            "direction": "up" if weather_change > 0 else "down",
            "unit": "/100",
        })

    # Price change
    price_change = current_price - (prev.current_price or 0)
    if abs(price_change) >= 10:
        changes.append({
            "metric": "Mandi price",
            "from": f"Rs.{prev.current_price}",
            "to": f"Rs.{int(current_price)}",
            "direction": "up" if price_change > 0 else "down",
            "unit": "/q",
        })

    # Recommendation change
    if prev.recommendation_action and prev.recommendation_action != current_decision["recommendation"]["action"]:
        changes.append({
            "metric": "AI recommendation",
            "from": prev.recommendation_action.replace("_", " ").title(),
            "to": current_decision["recommendation"]["action"].replace("_", " ").title(),
            "direction": "changed",
            "unit": "",
        })

    if not changes:
        return {
            "available": True,
            "changes": [],
            "summary": "No significant changes since last analysis.",
        }

    # Build narrative for major risk changes
    if any(c["metric"] == "Weather risk" for c in changes):
        narrative = (
            "Rainfall risk increased — recommendation updated accordingly."
            if any(c["direction"] == "up" for c in changes if c["metric"] == "Weather risk")
            else "Weather conditions improved since last check."
        )
    elif any(c["metric"] == "AI recommendation" for c in changes):
        narrative = f"Recommendation changed to {current_decision['recommendation']['headline']}."
    else:
        narrative = "Market or risk conditions have shifted since last analysis."

    return {
        "available": True,
        "changes": changes,
        "summary": narrative,
        "previous_observed_at": prev.observed_at.isoformat() if prev.observed_at else None,
    }
