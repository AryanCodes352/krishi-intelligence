import unittest
from backend.services.risk_engine import compute_risk
from backend.services.decision_engine import compute_scenarios
from backend.services.explainability import get_explanation

class TestRiskEngine(unittest.TestCase):
    def test_compute_risk_normal(self):
        weather = {"forecast_7day": [{"rain_probability_pct": 10, "precipitation_mm": 0, "temp_max_c": 30}], "current": {"humidity_pct": 50}}
        soil = {"parameters": {"ph": {"value": 7.0}}}
        res = compute_risk(weather, soil, "Tillering", 35, {})
        self.assertTrue(0 <= res["overall_risk"]["score"] <= 100)
        
    def test_compute_risk_extreme_rain(self):
        weather = {
            "forecast_7day": [{"rain_probability_pct": 95, "precipitation_mm": 50, "temp_max_c": 30}], 
            "current": {"humidity_pct": 90},
            "agricultural_risk": {
                "overall_weather_risk": 75,
                "overall_level": "HIGH",
                "rainfall_risk": {"score": 85, "reason": "Heavy rain"},
                "humidity_risk": {"score": 70, "reason": "High humidity"},
                "temperature_risk": {"score": 20, "reason": "Normal"},
            }
        }
        soil = {"parameters": {"ph": {"value": 7.0}}}
        res = compute_risk(weather, soil, "Grain Filling", 100, {})
        self.assertTrue(res["weather_risk"]["score"] > 60)
        self.assertTrue(res["overall_risk"]["score"] <= 100)
        
    def test_compute_risk_insufficient_data(self):
        res = compute_risk({}, {}, "Unknown", 0, {})
        self.assertTrue(0 <= res["overall_risk"]["score"] <= 100)

    def test_compute_risk_bounds(self):
        weather = {"forecast_7day": [{"rain_probability_pct": 100, "precipitation_mm": 100, "temp_max_c": 50}], "current": {"humidity_pct": 100}}
        soil = {"parameters": {"ph": {"value": 1.0}}}
        res = compute_risk(weather, soil, "Heading/Flowering", 85, {})
        self.assertTrue(0 <= res["overall_risk"]["score"] <= 100)

class TestDecisionEngineSemanticConsistency(unittest.TestCase):
    def test_sell_now_when_predicted_price_is_lower(self):
        # Current price: 2605, 7d point: 2571 (predicted price is lower)
        farm = {"farm_area_acres": 1.0}
        current_price = 2605
        pred_7d = {"point_estimate": 2571, "min_price": 2511, "max_price": 2631}
        pred_15d = {"point_estimate": 2572, "min_price": 2494, "max_price": 2650}
        weather_risk = 62

        res = compute_scenarios(farm, current_price, pred_7d, pred_15d, weather_risk)
        rec = res["recommendation"]
        
        self.assertEqual(rec["action"], "SELL_NOW")
        # Ensure explanation accurately states that predicted price is below current price
        self.assertIn("below", rec["summary"])
        # Ensure it does NOT falsely claim an expected price gain
        self.assertNotIn("offsets the expected price gain", rec["summary"])

    def test_sell_now_when_price_higher_but_weather_offsets(self):
        # Current price: 2400, 7d point: 2420, but high weather risk
        farm = {"farm_area_acres": 1.0}
        current_price = 2400
        pred_7d = {"point_estimate": 2420, "min_price": 2350, "max_price": 2450}
        pred_15d = {"point_estimate": 2410, "min_price": 2340, "max_price": 2440}
        weather_risk = 75

        res = compute_scenarios(farm, current_price, pred_7d, pred_15d, weather_risk)
        rec = res["recommendation"]
        self.assertEqual(rec["action"], "SELL_NOW")
        self.assertIn("exceed", rec["summary"])

    def test_explainability_consistency(self):
        farm = {"farm_area_acres": 1.0}
        current_price = 2605
        pred_7d = {"point_estimate": 2571, "min_price": 2511, "max_price": 2631, "confidence_pct": 85}
        pred_15d = {"point_estimate": 2572, "min_price": 2494, "max_price": 2650, "confidence_pct": 70}
        weather_risk = 62

        decision = compute_scenarios(farm, current_price, pred_7d, pred_15d, weather_risk)
        risk = {
            "overall_risk": {"score": 34, "level": "LOW"},
            "weather_risk": {"score": 62, "level": "MEDIUM"},
            "soil_risk": {"score": 28, "level": "LOW"},
            "crop_risk": {"score": 30, "level": "LOW"},
            "market_risk": {"score": 30, "level": "LOW"},
        }
        price_prediction = {
            "current_price": 2605,
            "prediction_7d": pred_7d,
            "prediction_15d": pred_15d,
            "insufficient_data": False,
        }
        weather = {
            "agricultural_risk": {
                "overall_level": "MEDIUM",
                "rainfall_risk": {"score": 62, "reason": "moderate"},
            },
            "forecast_7day": [{"rain_probability_pct": 89}],
        }
        market = {
            "current": {"modal_price": 2605},
            "historical": {"statistics": {"current_vs_avg_pct": 12.7, "std_price": 140}, "seasonal_trend": {"direction": "STABLE"}},
        }

        expl = get_explanation(decision, risk, market, price_prediction, weather)
        self.assertIn("below", expl["conclusion"])
        self.assertNotIn("offsets the expected price gain", expl["conclusion"])

if __name__ == "__main__":
    unittest.main()
