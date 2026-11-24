from fastapi import APIRouter
from backend.schemas.farm import PricePredictionRequest
from backend.services.market_service import get_current_price, get_historical_df, is_market_supported
import os
import json
from datetime import date, datetime, timezone
from ml.predict import predict_price as ml_predict_price

router = APIRouter()

@router.post("/price")
def predict_price(req: PricePredictionRequest):
    # ── Unsupported crop guard ────────────────────────────────────────────
    # Never run the Wheat XGBoost model for a different crop.
    if not is_market_supported(req.commodity):
        display_name = req.commodity.strip().title()
        return {
            "insufficient_data": True,
            "reason": (
                f"Price prediction for {display_name} is not yet available in "
                "this prototype. Prediction is planned for the next version."
            ),
            "data_type": "MARKET_UNSUPPORTED",
            "commodity": display_name,
        }

    model_meta_path = "./ml/models/wheat_lucknow_meta.json"
    if not os.path.exists(model_meta_path):
        return {
          "insufficient_data": True,
          "reason": "Model not trained. Run: python ml/train_price_model.py",
          "minimum_required": 52,
          "available_observations": 0,
          "data_type": "UNAVAILABLE"
        }

    current_price = get_current_price(req.commodity)
    if current_price is None:
        return {
            "insufficient_data": True,
            "reason": f"No price data available for {req.commodity}.",
            "data_type": "UNAVAILABLE",
        }
    historical_df = get_historical_df(req.commodity)

    res = ml_predict_price(
        current_price=current_price,
        current_date=date.today(),
        historical_df=historical_df,
        horizon_days=req.horizon_days,
    )

    if res.get("insufficient_data"):
        return res

    pred = res.get("prediction", {})
    # Return full normalized payload
    return {
        "commodity": req.commodity,
        "market": req.market,
        "current_price": int(current_price),
        "horizon_days": req.horizon_days,
        "prediction": {
            "min_price": pred.get("min_price", int(current_price)),
            "max_price": pred.get("max_price", int(current_price)),
            "point_estimate": pred.get("point_estimate", int(current_price)),
            "min": pred.get("min_price", int(current_price)),
            "max": pred.get("max_price", int(current_price)),
            "point": pred.get("point_estimate", int(current_price)),
            "confidence_pct": pred.get("confidence_pct", 70),
            "confidence_level": pred.get("confidence_level", "MEDIUM"),
        },
        "model_info": res.get("model_info", {}),
        "data_used": res.get("data_used", []),
        "data_type": "MODEL_PREDICTION",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "insufficient_data": False,
    }
