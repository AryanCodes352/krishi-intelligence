"""
Multi-Factor Risk Engine
========================
Computes risk scores (0–100) for weather, soil, crop, and market dimensions,
then combines them into an overall farm risk score with per-factor breakdowns.

Risk levels:
  LOW    — 0 to 39
  MEDIUM — 40 to 69
  HIGH   — 70 to 100

Methodology note: This is a prototype risk model combining agronomic rules
with real data inputs. Scores and weights are based on published UP wheat
cultivation guidelines (ICAR Wheat Research Directorate, Karnal).
All scores are clearly labelled as model-derived estimates.
"""

from __future__ import annotations
from typing import Optional


def _level(score: float) -> str:
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def _clamp(v: float) -> float:
    return max(0.0, min(100.0, v))


# ── Crop stage vulnerability to weather/pest stress ─────────────────────────
# Source: ICAR Wheat Research Directorate — stage-specific risk guidelines
STAGE_VULNERABILITY = {
    "Germination":       {"base": 55, "rain_multiplier": 0.30, "humidity_multiplier": 0.20},
    "Seedling":          {"base": 45, "rain_multiplier": 0.25, "humidity_multiplier": 0.25},
    "Tillering":         {"base": 40, "rain_multiplier": 0.20, "humidity_multiplier": 0.25},
    "Jointing":          {"base": 50, "rain_multiplier": 0.30, "humidity_multiplier": 0.30},
    "Booting":           {"base": 65, "rain_multiplier": 0.35, "humidity_multiplier": 0.35},
    "Heading/Flowering": {"base": 75, "rain_multiplier": 0.40, "humidity_multiplier": 0.40},
    "Grain Filling":     {"base": 70, "rain_multiplier": 0.35, "humidity_multiplier": 0.35},
    "Maturity":          {"base": 35, "rain_multiplier": 0.25, "humidity_multiplier": 0.15},
    "Post-harvest":      {"base": 15, "rain_multiplier": 0.10, "humidity_multiplier": 0.05},
}


def compute_risk(
    weather_data: dict,
    soil_data: dict,
    crop_stage: str,
    days_after_sowing: int,
    market_data: dict,
) -> dict:
    """
    Compute a comprehensive multi-factor risk score from real data inputs.

    Returns:
        dict with weather_risk, soil_risk, crop_risk, market_risk, overall_risk,
        each containing score, level, and per-factor breakdown.
    """
    # ─────────────────────────────────────────────────────────────────────
    # 1. WEATHER RISK — derived from real Open-Meteo forecast
    # ─────────────────────────────────────────────────────────────────────
    agri_risk = weather_data.get("agricultural_risk", {})
    forecast = weather_data.get("forecast_7day", [])

    if agri_risk and forecast:
        # Use the pre-computed risk scores from weather_service
        rainfall_score = float(agri_risk.get("rainfall_risk", {}).get("score", 0))
        temperature_score = float(agri_risk.get("temperature_risk", {}).get("score", 0))
        humidity_score = float(agri_risk.get("humidity_risk", {}).get("score", 0))
        weather_overall = float(agri_risk.get("overall_weather_risk", 0))

        max_rain_prob = max((f.get("rain_probability_pct", 0) for f in forecast), default=0)
        total_rain = sum(f.get("precipitation_mm", 0) for f in forecast)
        max_temp = max((f.get("temp_max_c", 30) for f in forecast), default=30)
        current_humidity = weather_data.get("current", {}).get("humidity_pct", 60)
    else:
        # Weather data unavailable — use neutral defaults
        rainfall_score = 0.0
        temperature_score = 0.0
        humidity_score = 0.0
        weather_overall = 0.0
        max_rain_prob = 0
        total_rain = 0
        max_temp = 30
        current_humidity = 60

    weather_factors = [
        {
            "name": "Rainfall probability (7-day peak)",
            "value": f"{int(max_rain_prob)}%",
            "contribution": int(rainfall_score * 0.45),
            "direction": "negative" if rainfall_score > 40 else "neutral",
        },
        {
            "name": "Humidity (fungal disease pressure)",
            "value": f"{current_humidity}%",
            "contribution": int(humidity_score * 0.35),
            "direction": "negative" if humidity_score > 40 else "neutral",
        },
        {
            "name": "Temperature stress (7-day max)",
            "value": f"{max_temp:.0f}°C",
            "contribution": int(temperature_score * 0.20),
            "direction": "negative" if temperature_score > 30 else "neutral",
        },
    ]

    # ─────────────────────────────────────────────────────────────────────
    # 2. SOIL RISK — derived from regional soil parameter data
    # ─────────────────────────────────────────────────────────────────────
    params = soil_data.get("parameters", {})

    def _param_risk(param_name: str, low_weight: float, medium_weight: float) -> float:
        """Map soil parameter status to a risk contribution."""
        status_map = {"GOOD": 0, "HIGH": 5, "MEDIUM": low_weight, "LOW": low_weight * 1.8, "POOR": low_weight * 2.5}
        if isinstance(params.get(param_name), dict):
            status = params[param_name].get("status", "MEDIUM")
        else:
            return medium_weight
        return status_map.get(status, medium_weight)

    ph_risk = 0.0
    if isinstance(params.get("ph"), dict) and params["ph"].get("value") is not None:
        ph_val = params["ph"]["value"]
        # Wheat optimal: 6.5–7.5. Penalty for deviation.
        ph_dev = max(0, ph_val - 7.5) + max(0, 6.5 - ph_val)
        ph_risk = _clamp(ph_dev * 20)


    nitrogen_risk = _param_risk("nitrogen", 18, 10)
    phosphorus_risk = _param_risk("phosphorus", 12, 7)
    potassium_risk = _param_risk("potassium", 6, 3)
    oc_risk = _param_risk("organic_carbon", 22, 12)  # OC low → water stress risk

    soil_overall = _clamp(
        ph_risk * 0.20 + nitrogen_risk * 0.30 + phosphorus_risk * 0.15
        + potassium_risk * 0.10 + oc_risk * 0.25
    )

    soil_factors = [
        {"name": "pH level", "value": str(params.get("ph", {}).get("value", "N/A") if isinstance(params.get("ph"), dict) else "N/A"), "contribution": int(ph_risk * 0.20), "direction": "negative" if ph_risk > 10 else "neutral"},
        {"name": "Nitrogen availability", "value": params.get("nitrogen", {}).get("status", "N/A") if isinstance(params.get("nitrogen"), dict) else "N/A", "contribution": int(nitrogen_risk * 0.30), "direction": "negative" if nitrogen_risk > 10 else "neutral"},
        {"name": "Organic Carbon", "value": params.get("organic_carbon", {}).get("status", "N/A") if isinstance(params.get("organic_carbon"), dict) else "N/A", "contribution": int(oc_risk * 0.25), "direction": "negative" if oc_risk > 15 else "neutral"},
        {"name": "Phosphorus", "value": params.get("phosphorus", {}).get("status", "N/A") if isinstance(params.get("phosphorus"), dict) else "N/A", "contribution": int(phosphorus_risk * 0.15), "direction": "negative" if phosphorus_risk > 8 else "neutral"},
    ]

    # ─────────────────────────────────────────────────────────────────────
    # 3. CROP RISK — stage vulnerability + weather impact on crop
    # ─────────────────────────────────────────────────────────────────────
    stage_info = STAGE_VULNERABILITY.get(crop_stage, STAGE_VULNERABILITY["Post-harvest"])
    base_vulnerability = stage_info["base"]

    # Weather compounds crop risk based on stage sensitivity
    rain_multiplier = stage_info["rain_multiplier"]
    humidity_multiplier = stage_info["humidity_multiplier"]
    weather_modifier = (rainfall_score * rain_multiplier) + (humidity_score * humidity_multiplier)

    crop_overall = _clamp(base_vulnerability + weather_modifier * 0.3)

    crop_factors = [
        {
            "name": f"Crop stage vulnerability ({crop_stage})",
            "value": f"Base risk: {base_vulnerability}/100",
            "contribution": base_vulnerability,
            "direction": "negative" if base_vulnerability > 50 else "neutral",
        },
        {
            "name": "Weather impact on crop",
            "value": f"Rain+Humidity stress ({int(weather_modifier)}%)",
            "contribution": int(weather_modifier * 0.3),
            "direction": "negative" if weather_modifier > 30 else "neutral",
        },
    ]

    hist = (market_data.get("historical") or {}) if market_data else {}
    hist_stats = hist.get("statistics") or {}
    std_price = float(hist_stats.get("std_price", 150))
    curr = (market_data.get("current") or {}) if market_data else {}
    current_price = float(curr.get("modal_price") or (2445 if not market_data else 0))
    seasonal_direction = (hist.get("seasonal_trend") or {}).get("direction", "STABLE")

    # Volatility risk: coefficient of variation scaled to 0–100
    if current_price > 0:
        volatility_risk = _clamp((std_price / current_price) * 500)
    else:
        volatility_risk = 30.0

    # Seasonal trend bonus/penalty
    trend_adjustment = -10 if seasonal_direction == "INCREASING" else (10 if seasonal_direction == "DECREASING" else 0)
    market_overall = _clamp(volatility_risk + trend_adjustment)

    market_factors = [
        {
            "name": "Price volatility (historical std dev)",
            "value": f"Rs. {int(std_price)}/q",
            "contribution": int(volatility_risk),
            "direction": "negative" if volatility_risk > 20 else "neutral",
        },
        {
            "name": "Seasonal price trend",
            "value": seasonal_direction,
            "contribution": abs(trend_adjustment),
            "direction": "positive" if seasonal_direction == "INCREASING" else ("negative" if seasonal_direction == "DECREASING" else "neutral"),
        },
    ]

    # ─────────────────────────────────────────────────────────────────────
    # 5. OVERALL RISK — weighted combination
    # Weights: Crop 35%, Weather 30%, Market 20%, Soil 15%
    # ─────────────────────────────────────────────────────────────────────
    overall = _clamp(
        0.35 * crop_overall
        + 0.30 * weather_overall
        + 0.20 * market_overall
        + 0.15 * soil_overall
    )

    return {
        "weather_risk": {
            "score": int(weather_overall),
            "level": _level(weather_overall),
            "factors": weather_factors,
        },
        "soil_risk": {
            "score": int(soil_overall),
            "level": _level(soil_overall),
            "factors": soil_factors,
        },
        "crop_risk": {
            "score": int(crop_overall),
            "level": _level(crop_overall),
            "factors": crop_factors,
        },
        "market_risk": {
            "score": int(market_overall),
            "level": _level(market_overall),
            "factors": market_factors,
        },
        "overall_risk": {
            "score": int(overall),
            "level": _level(overall),
        },
        "methodology_note": (
            "Prototype risk model. Weights: Crop 35%, Weather 30%, Market 20%, Soil 15%. "
            "Based on agronomic guidelines for UP wheat cultivation. "
            "Scores are model-derived estimates, not measured values."
        ),
    }
