"""
Price Prediction Module — XGBoost Inference
============================================
Loads the trained XGBoost model and produces price predictions
with honest confidence intervals based on measured model error.

IMPORTANT:
- Never returns a prediction if fewer than MIN_OBSERVATIONS rows are available.
- Confidence bounds are derived from the model's measured RMSE on test data.
- Confidence is reduced for longer horizons (more uncertainty).
- If model files don't exist, returns a clear instruction to train first.
"""

import joblib
import json
import os
from datetime import date, timedelta
from pathlib import Path

# Paths relative to project root
_ROOT = Path(__file__).resolve().parent.parent
_MODEL_PATH = _ROOT / "ml" / "models" / "wheat_lucknow_xgb.joblib"
_META_PATH = _ROOT / "ml" / "models" / "wheat_lucknow_meta.json"

MIN_OBSERVATIONS = 52  # minimum 1 year of weekly data

# MSP lookup for feature building
MSP_BY_YEAR = {
    2019: 1925, 2020: 1975, 2021: 2015, 2022: 2015,
    2023: 2275, 2024: 2275, 2025: 2425, 2026: 2425,
}

# Seasonal index for each month (from the generator — same source)
SEASONAL_INDEX = {
    1: 1.085, 2: 1.070, 3: 1.030, 4: 1.005, 5: 1.000,
    6: 1.008, 7: 1.025, 8: 1.045, 9: 1.070, 10: 1.090,
    11: 1.095, 12: 1.088,
}


def _model_available() -> bool:
    return _MODEL_PATH.exists() and _META_PATH.exists()


def _load_meta() -> dict:
    with open(_META_PATH, "r") as f:
        return json.load(f)


def predict_price(
    current_price: float,
    current_date: date,
    historical_df,  # pandas DataFrame
    horizon_days: int = 7,
) -> dict:
    """
    Predict the wheat modal price `horizon_days` from now using the trained XGBoost model.

    Uses real feature engineering (same features as training) to build the prediction
    vector, then returns a point estimate with a confidence interval derived from
    the model's measured test-set RMSE.

    Returns:
        dict with prediction details, model metadata, and data_used list.
        Returns insufficient_data dict if model/data conditions aren't met.
    """
    import numpy as np

    # ── Pre-checks ───────────────────────────────────────────────────────
    if not _model_available():
        return {
            "insufficient_data": True,
            "reason": "ML model not yet trained. Run: python ml/train_price_model.py",
            "data_type": "UNAVAILABLE",
        }

    if historical_df is None or len(historical_df) < MIN_OBSERVATIONS:
        avail = len(historical_df) if historical_df is not None else 0
        return {
            "insufficient_data": True,
            "reason": f"Fewer than {MIN_OBSERVATIONS} weekly observations available for this market/crop combination.",
            "minimum_required": MIN_OBSERVATIONS,
            "available_observations": avail,
            "data_type": "UNAVAILABLE",
        }

    # ── Load model and metadata ───────────────────────────────────────────
    try:
        model = joblib.load(_MODEL_PATH)
        meta = _load_meta()
    except Exception as e:
        return {
            "insufficient_data": True,
            "reason": f"Could not load model files: {e}",
            "data_type": "UNAVAILABLE",
        }

    rmse = meta.get("rmse", 110.0)
    mae = meta.get("mae", 85.0)
    mape = meta.get("mape_pct", 4.0)
    features = meta.get("features", [])

    # ── Build feature vector for the target date ──────────────────────────
    target_date = current_date + timedelta(days=horizon_days)

    # We need lag features — use the most recent observations from historical_df
    # Sort by date to get accurate lags
    df = historical_df.copy()
    if "date" in df.columns:
        df = df.sort_values("date").reset_index(drop=True)
    prices = df["modal_price"].values

    # Compute lag values from the most recent observations
    def _lag(n_weeks: int) -> float:
        idx = len(prices) - n_weeks
        return float(prices[idx]) if idx >= 0 else current_price

    lag_1w = _lag(1)
    lag_2w = _lag(2)
    lag_4w = _lag(4)
    lag_8w = _lag(8)

    recent_4w = prices[-4:] if len(prices) >= 4 else prices
    recent_8w = prices[-8:] if len(prices) >= 8 else prices
    rolling_mean_4w = float(np.mean(recent_4w))
    rolling_mean_8w = float(np.mean(recent_8w))
    rolling_std_4w = float(np.std(recent_4w)) if len(recent_4w) > 1 else 50.0

    price_4w_ago = _lag(4)
    price_change_4w_pct = ((current_price - price_4w_ago) / price_4w_ago * 100) if price_4w_ago > 0 else 0.0

    tgt_month = target_date.month
    tgt_year = target_date.year
    seasonal_idx = SEASONAL_INDEX.get(tgt_month, 1.05)
    msp = MSP_BY_YEAR.get(tgt_year, 2425)

    feature_row = {
        "month": tgt_month,
        "day_of_year": target_date.timetuple().tm_yday,
        "year": tgt_year,
        "week_of_year": target_date.isocalendar()[1],
        "lag_1w": lag_1w,
        "lag_2w": lag_2w,
        "lag_4w": lag_4w,
        "lag_8w": lag_8w,
        "rolling_mean_4w": rolling_mean_4w,
        "rolling_mean_8w": rolling_mean_8w,
        "rolling_std_4w": rolling_std_4w,
        "seasonal_index": seasonal_idx,
        "msp_year": msp,
        "price_change_4w_pct": price_change_4w_pct,
    }

    # Build the feature vector in the correct column order
    import pandas as pd
    X = pd.DataFrame([feature_row])

    # Use only the columns the model was trained on (in order)
    if features:
        available_features = [f for f in features if f in X.columns]
        X = X[available_features]

    # ── Predict ──────────────────────────────────────────────────────────
    try:
        point_estimate = float(model.predict(X)[0])
    except Exception as e:
        return {
            "insufficient_data": True,
            "reason": f"Prediction failed: {e}",
            "data_type": "UNAVAILABLE",
        }

    # ── Confidence interval from measured RMSE ─────────────────────────
    # Scale RMSE by horizon factor (longer = wider uncertainty)
    horizon_factor = 1.0 if horizon_days <= 7 else (1.3 if horizon_days <= 15 else 1.6)
    scaled_rmse = rmse * horizon_factor

    min_price = round(point_estimate - 0.85 * scaled_rmse)
    max_price = round(point_estimate + 0.85 * scaled_rmse)
    point_price = round(point_estimate)

    # Confidence level from MAPE
    if mape < 5:
        conf_level = "HIGH"
        base_conf = 85
    elif mape <= 10:
        conf_level = "MEDIUM"
        base_conf = 70
    else:
        conf_level = "LOW"
        base_conf = 45

    # Reduce confidence for longer horizons
    conf_pct = round(base_conf * (1.0 if horizon_days <= 7 else 0.82))
    conf_pct = max(30, min(95, conf_pct))

    return {
        "current_price": int(current_price),
        "unit": "Rs/quintal",
        "horizon_days": horizon_days,
        "prediction": {
            "min_price": int(min_price),
            "max_price": int(max_price),
            "point_estimate": int(point_price),
            "confidence_pct": conf_pct,
            "confidence_level": conf_level,
        },
        "model_info": {
            "type": "XGBoost Regressor",
            "training_data_points": meta.get("training_data_points", len(df)),
            "test_data_points": meta.get("test_data_points", 52),
            "training_period": meta.get("training_period", "2020–2026"),
            "mae": round(mae, 1),
            "rmse": round(rmse, 1),
            "mape_pct": round(mape, 2),
            "trained_at": meta.get("trained_at", ""),
        },
        "data_used": [
            f"{len(df)} weekly historical mandi prices (AGMARKNET calibrated seed data, 2020–2026)",
            f"Seasonal price index for {target_date.strftime('%B')}",
            "Recent 4-week price momentum (lag features)",
            "Year-over-year price trend",
            f"MSP reference: Rs.{msp}/q ({tgt_year})",
        ],
        "data_type": "MODEL_PREDICTION",
        "timestamp": date.today().isoformat(),
        "insufficient_data": False,
    }
