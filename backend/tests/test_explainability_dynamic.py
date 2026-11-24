import unittest
from backend.services.decision_engine import compute_scenarios
from backend.services.explainability import get_explanation

class TestDynamicExplainabilityScenarios(unittest.TestCase):
    """
    Regression test suite proving that Explainability and Decision Logic
    are fully data-driven, dynamic, and adhere to all 6 scenarios (A through F).
    """

    def setUp(self):
        self.sample_weather_normal = {
            "forecast_7day": [{"rain_probability_pct": 35, "precipitation_mm": 5, "temp_max_c": 32}],
            "agricultural_risk": {
                "overall_level": "LOW",
                "overall_weather_risk": 25,
                "rainfall_risk": {"score": 25, "reason": "Normal showers"},
            }
        }
        self.sample_risk = {
            "overall_risk": {"score": 30, "level": "LOW"},
            "weather_risk": {"score": 25, "level": "LOW"},
            "soil_risk": {"score": 20, "level": "LOW"},
            "crop_risk": {"score": 25, "level": "LOW"},
            "market_risk": {"score": 30, "level": "LOW"},
        }

    def test_scenario_a_wheat_lucknow_historical_seed_lower_price(self):
        """
        Scenario A: Wheat + Lucknow + HISTORICAL_SEED + lower predicted price
        - Favours SELL_NOW recommendation
        - Does NOT claim 'today's spot price' or 'live price'
        - Wording reflects HISTORICAL_SEED provenance
        - Financial components strictly reconcile
        """
        farm = {"farm_area_acres": 3.0, "crop": "Wheat"}
        current_price = 2605
        pred_7d = {"point_estimate": 2571, "min_price": 2511, "max_price": 2631, "confidence_pct": 80}
        pred_15d = {"point_estimate": 2572, "min_price": 2494, "max_price": 2650, "confidence_pct": 70}
        weather_risk = 62

        market = {
            "current": {"modal_price": current_price, "date": "2026-09-06"},
            "historical": {
                "years": 7,
                "data_points": 349,
                "statistics": {"current_vs_avg_pct": 12.7, "std_price": 140},
                "seasonal_trend": {"direction": "STABLE"},
            },
            "data_source": {
                "type": "HISTORICAL_SEED",
                "date_range": "2020-01-05 to 2026-09-06",
                "total_observations": 349,
            }
        }
        weather = {
            "forecast_7day": [{"rain_probability_pct": 89, "precipitation_mm": 20, "temp_max_c": 33}],
            "agricultural_risk": {
                "overall_level": "MEDIUM",
                "overall_weather_risk": 62,
                "rainfall_risk": {"score": 62, "reason": "High rainfall probability"},
            }
        }
        risk = dict(self.sample_risk)
        risk["weather_risk"]["score"] = 62

        decision = compute_scenarios(
            farm=farm,
            current_price=current_price,
            prediction_7d=pred_7d,
            prediction_15d=pred_15d,
            weather_risk=weather_risk,
            market_source="HISTORICAL_SEED",
        )
        self.assertEqual(decision["recommendation"]["action"], "SELL_NOW")
        self.assertEqual(decision["recommendation"]["confidence"], "MEDIUM")  # Capped due to HISTORICAL_SEED
        self.assertNotIn("today's live mandi", decision["recommendation"]["summary"])

        expl = get_explanation(
            decision=decision,
            risk=risk,
            market=market,
            price_prediction={"prediction_7d": pred_7d, "insufficient_data": False},
            weather=weather,
            farm=farm,
        )
        combined_reasoning = " ".join(expl["reasoning_steps"])

        # Provenance checks
        self.assertNotIn("today's spot price", combined_reasoning.lower())
        self.assertNotIn("live price", combined_reasoning.lower())
        self.assertNotIn("5-year average", combined_reasoning.lower())
        self.assertIn("349 observations", expl["reasoning_steps"][0])

        # Numerical reconciliation check
        sn_net = decision["scenarios"]["sell_now"]["net_realization"]
        w7_net = decision["scenarios"]["wait_7d"]["net_realization"]
        expected_diff = sn_net - w7_net
        self.assertIn(f"Rs.{expected_diff:,}", combined_reasoning)
        self.assertNotIn("discrepancy detected", combined_reasoning)

    def test_scenario_b_higher_predicted_price_changes_recommendation(self):
        """
        Scenario B: Change prediction to higher than reference price
        - Verifies recommendation switches to WAIT_7_DAYS
        - Proves recommendation engine is NOT locked to SELL_NOW
        - Explainability explains positive net advantage
        """
        farm = {"farm_area_acres": 2.0, "crop": "Mustard"}
        current_price = 5400
        # Bullish projection: +Rs.350/q
        pred_7d = {"point_estimate": 5750, "min_price": 5600, "max_price": 5900, "confidence_pct": 85}
        pred_15d = {"point_estimate": 5800, "min_price": 5650, "max_price": 6000, "confidence_pct": 75}
        weather_risk = 15  # Low risk

        market = {
            "current": {"modal_price": current_price},
            "historical": {"statistics": {"current_vs_avg_pct": 4.5, "std_price": 200}, "seasonal_trend": {"direction": "INCREASING"}},
            "data_source": {"type": "HISTORICAL_SEED"}
        }

        decision = compute_scenarios(
            farm=farm,
            current_price=current_price,
            prediction_7d=pred_7d,
            prediction_15d=pred_15d,
            weather_risk=weather_risk,
            market_source="HISTORICAL_SEED",
        )
        self.assertEqual(decision["recommendation"]["action"], "WAIT_7_DAYS")
        self.assertIn("Wait 7 days", decision["recommendation"]["headline"])
        self.assertIn("improve net realization", decision["recommendation"]["summary"])

        expl = get_explanation(
            decision=decision,
            risk=self.sample_risk,
            market=market,
            price_prediction={"prediction_7d": pred_7d, "insufficient_data": False},
            weather=self.sample_weather_normal,
            farm=farm,
        )
        self.assertIn("Waiting 7 days is projected to improve net realization", expl["conclusion"])
        self.assertIn("exceeds combined holding deductions", " ".join(expl["reasoning_steps"]))

    def test_scenario_c_provenance_wording_changes_with_live_data(self):
        """
        Scenario C: Change market provenance from HISTORICAL_SEED to LIVE
        - Provenance labels and phrasing dynamically switch
        - LIVE allows HIGH decision confidence when model confidence is high
        """
        farm = {"farm_area_acres": 2.0}
        current_price = 2605
        pred_7d = {"point_estimate": 2450, "min_price": 2400, "max_price": 2500, "confidence_pct": 85}

        # Sub-case 1: HISTORICAL_SEED
        dec_seed = compute_scenarios(
            farm=farm,
            current_price=current_price,
            prediction_7d=pred_7d,
            prediction_15d=None,
            weather_risk=30,
            market_source="HISTORICAL_SEED",
        )
        self.assertEqual(dec_seed["recommendation"]["confidence"], "MEDIUM")
        self.assertIn("HISTORICAL_SEED", dec_seed["recommendation"]["summary"])

        # Sub-case 2: LIVE
        dec_live = compute_scenarios(
            farm=farm,
            current_price=current_price,
            prediction_7d=pred_7d,
            prediction_15d=None,
            weather_risk=30,
            market_source="LIVE",
            market_date="2026-09-11 10:00",
        )
        self.assertEqual(dec_live["recommendation"]["confidence"], "HIGH")
        self.assertIn("today's live mandi reference price", dec_live["recommendation"]["summary"])

        # Explainability check under LIVE
        market_live = {
            "current": {"modal_price": current_price, "date": "2026-09-11 10:00"},
            "data_source": {"type": "LIVE"}
        }
        expl_live = get_explanation(
            decision=dec_live,
            risk=self.sample_risk,
            market=market_live,
            price_prediction={"prediction_7d": pred_7d, "insufficient_data": False},
            weather={"data_source": {"status": "LIVE"}, "forecast_7day": [{"rain_probability_pct": 10}]},
        )
        self.assertIn("today's price", expl_live["conclusion"])
        self.assertIn("Current live mandi price", expl_live["reasoning_steps"][0])
        self.assertEqual(expl_live["data_quality_overall"], "HIGH")

    def test_scenario_d_acreage_scaling(self):
        """
        Scenario D: Change acreage
        - All financial totals scale strictly proportionately (5x)
        """
        current_price = 2500
        pred_7d = {"point_estimate": 2400}

        dec_1_acre = compute_scenarios(
            farm={"farm_area_acres": 1.0},
            current_price=current_price,
            prediction_7d=pred_7d,
            prediction_15d=None,
            weather_risk=40,
        )
        dec_5_acres = compute_scenarios(
            farm={"farm_area_acres": 5.0},
            current_price=current_price,
            prediction_7d=pred_7d,
            prediction_15d=None,
            weather_risk=40,
        )

        # 5x ratio checks
        sn_1 = dec_1_acre["scenarios"]["sell_now"]["net_realization"]
        sn_5 = dec_5_acres["scenarios"]["sell_now"]["net_realization"]
        self.assertEqual(sn_5, sn_1 * 5)

        sc_1 = dec_1_acre["scenarios"]["wait_7d"]["storage_cost"]
        sc_5 = dec_5_acres["scenarios"]["wait_7d"]["storage_cost"]
        self.assertEqual(sc_5, sc_1 * 5)

        wp_1 = dec_1_acre["scenarios"]["wait_7d"]["weather_risk_penalty"]
        wp_5 = dec_5_acres["scenarios"]["wait_7d"]["weather_risk_penalty"]
        self.assertEqual(wp_5, wp_1 * 5)

    def test_scenario_e_historical_date_range_and_average_labeling(self):
        """
        Scenario E: Change historical date range / observations
        - Verifies dynamic average labeling (5-year vs full dataset vs insufficient data)
        """
        farm = {"farm_area_acres": 1.0}
        current_price = 2500
        decision = compute_scenarios(farm, current_price, None, None, 20)

        # Case 1: Exactly 5 years
        market_5yr = {
            "current": {"modal_price": current_price},
            "historical": {"years": 5, "data_points": 260, "statistics": {"current_vs_avg_pct": 5.0}},
        }
        expl_5yr = get_explanation(decision, self.sample_risk, market_5yr)
        self.assertIn("5-year historical average", expl_5yr["reasoning_steps"][0])

        # Case 2: 7 years / 349 points
        market_7yr = {
            "current": {"modal_price": current_price},
            "historical": {"years": 7, "data_points": 349, "statistics": {"current_vs_avg_pct": 5.0}},
        }
        expl_7yr = get_explanation(decision, self.sample_risk, market_7yr)
        self.assertIn("historical dataset average (349 observations across 7 years)", expl_7yr["reasoning_steps"][0])

        # Case 3: Empty historical data
        market_empty = {"current": {"modal_price": current_price}, "historical": {}}
        expl_empty = get_explanation(decision, self.sample_risk, market_empty)
        self.assertIn("historical average (insufficient data)", expl_empty["data_signals"][2]["signal"])

    def test_scenario_f_weather_risk_impact_updates(self):
        """
        Scenario F: Change weather risk
        - Verifies weather signal, direction, penalty, and rationale update dynamically
        """
        farm = {"farm_area_acres": 2.0}
        current_price = 2500
        pred_7d = {"point_estimate": 2550, "min_price": 2500, "max_price": 2600}

        # Case 1: Low weather risk (15)
        dec_low_weather = compute_scenarios(farm, current_price, pred_7d, None, weather_risk=15)
        wp_low = dec_low_weather["scenarios"]["wait_7d"]["weather_risk_penalty"]

        # Case 2: High weather risk (85)
        dec_high_weather = compute_scenarios(farm, current_price, pred_7d, None, weather_risk=85)
        wp_high = dec_high_weather["scenarios"]["wait_7d"]["weather_risk_penalty"]

        self.assertTrue(wp_high > wp_low * 5)

        # High weather risk should tilt decision or highlight risk
        weather_extreme = {
            "forecast_7day": [{"rain_probability_pct": 95}],
            "agricultural_risk": {"rainfall_risk": {"score": 85}}
        }
        risk_extreme = dict(self.sample_risk)
        risk_extreme["weather_risk"]["score"] = 85

        expl_extreme = get_explanation(dec_high_weather, risk_extreme, weather=weather_extreme)
        # Weather signal direction should be negative
        weather_signal = next(s for s in expl_extreme["data_signals"] if "rainfall" in s["signal"].lower())
        self.assertEqual(weather_signal["direction"], "negative")
        self.assertIn("HIGH risk", " ".join(expl_extreme["reasoning_steps"]))

if __name__ == "__main__":
    unittest.main()
