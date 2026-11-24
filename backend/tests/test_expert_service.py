import unittest
from backend.services.expert_service import generate_expert_advice

class TestExpertService(unittest.TestCase):
    def setUp(self):
        self.sample_farm = {
            "crop": "Wheat",
            "crop_variety": "HD-2967",
            "district": "Lucknow",
            "state": "Uttar Pradesh",
            "location": "Malihabad",
            "sowing_date": "2025-11-15",
            "crop_stage": "Post-harvest",
            "soil_data_available": False,
        }
        self.sample_weather = {
            "forecast_7day": [
                {"rain_probability_pct": 89, "precipitation_mm": 12.5, "temp_max_c": 31},
                {"rain_probability_pct": 75, "precipitation_mm": 8.0, "temp_max_c": 30},
            ],
            "agricultural_risk": {"overall_score": 62}
        }
        self.sample_soil = {
            "parameters": {
                "ph": {"value": 7.5},
                "nitrogen": {"value": 240, "unit": "kg/ha", "status": "MEDIUM"},
                "phosphorus": {"value": 18, "unit": "kg/ha", "status": "MEDIUM"},
                "potassium": {"value": 220, "unit": "kg/ha", "status": "GOOD"},
                "organic_carbon": {"value": 0.45, "unit": "%", "status": "LOW"},
                "soil_type": "Sandy Loam"
            },
            "data_source": {"type": "REGIONAL_ESTIMATE"}
        }
        self.sample_market = {
            "current": {"modal_price": 2605},
            "historical": {"statistics": {"mean_price": 2310, "current_vs_avg_pct": 12.7}}
        }

    # ── Rule 8: Required Test Cases ──────────────────────────────────────────

    def test_case_a_wheat_post_harvest(self):
        """
        Test Case A: Wheat + Post-harvest
        - Verify answer explicitly states NOT to fertilize harvested wheat
        - Verify what_to_do does NOT contain 'top-dressing' or 'tillering'
        - Verify it contains soil testing / Soil Health Card and next-crop planning
        """
        farm = dict(self.sample_farm)
        farm["crop_stage"] = "Post-harvest"

        res = generate_expert_advice(
            question="What fertilizer should I apply next?",
            farm_data=farm,
            weather_data=self.sample_weather,
            soil_data=self.sample_soil,
            market_data=self.sample_market,
        )

        answer = res.get("answer", "").lower()
        self.assertTrue(bool(answer), "Answer must not be empty")
        # Must explicitly state NOT to fertilize harvested wheat
        self.assertTrue(
            "not be applied" in answer or "do not apply" in answer,
            f"Expected explicit guidance not to apply fertilizer to harvested crop, got: {answer}"
        )

        # what_to_do verification
        what_to_do = res.get("what_to_do", [])
        self.assertTrue(len(what_to_do) >= 3, "Expected at least 3 action items")
        actions_text = " ".join(what_to_do).lower()

        # Must NOT recommend top-dressing or tillering fertilizer for the harvested crop
        self.assertNotIn("top-dressing", actions_text)
        self.assertNotIn("tillering", actions_text)

        # Must recommend soil testing / Soil Health Card and next crop planning
        self.assertTrue(
            "soil health card" in actions_text or "soil test" in actions_text,
            "Expected soil testing / Soil Health Card recommendation"
        )
        self.assertTrue(
            "next" in actions_text,
            "Expected next crop planning recommendation"
        )
        self.assertEqual(res.get("confidence"), "HIGH")

    def test_case_b_wheat_early_tillering(self):
        """
        Test Case B: Wheat + Early Tillering
        - Verify top-dressing Urea recommended
        - Rain check included
        - Soil N deficit included
        """
        farm = dict(self.sample_farm)
        farm["crop_stage"] = "Tillering"

        res = generate_expert_advice(
            question="What fertilizer should I apply next?",
            farm_data=farm,
            weather_data=self.sample_weather,
            soil_data=self.sample_soil,
            market_data=self.sample_market,
        )

        answer = res.get("answer", "")
        why = res.get("why", "")
        what_to_do = " ".join(res.get("what_to_do", []))

        # Verify top-dressing Urea recommended
        combined = (answer + " " + why + " " + what_to_do).lower()
        self.assertTrue("urea" in combined, "Expected Urea recommendation in tillering")
        self.assertTrue("top-dressing" in combined, "Expected top-dressing recommendation in tillering")

        # Rain check included (forecast has 89% rain probability)
        self.assertTrue("rain" in combined, "Expected rain check due to high forecast rain")

        # Soil N deficit included
        self.assertTrue("240" in why or "nitrogen" in why.lower(), "Expected soil N deficit reference")

    def test_case_c_wheat_basal_presowing(self):
        """
        Test Case C: Wheat + Basal/Pre-sowing
        - Verify basal DAP/NPK recommended
        - FYM recommended
        - No top-dressing
        """
        farm = dict(self.sample_farm)
        farm["crop_stage"] = "Pre-sowing"

        res = generate_expert_advice(
            question="What fertilizer should I apply next?",
            farm_data=farm,
            weather_data=self.sample_weather,
            soil_data=self.sample_soil,
            market_data=self.sample_market,
        )

        answer = res.get("answer", "")
        why = res.get("why", "")
        what_to_do = " ".join(res.get("what_to_do", []))
        combined = (answer + " " + why + " " + what_to_do).lower()

        # Basal DAP/NPK recommended
        self.assertTrue("dap" in combined or "npk" in combined, "Expected basal DAP/NPK")
        self.assertIn("basal", combined)

        # FYM recommended
        self.assertTrue("fym" in combined or "manure" in combined or "compost" in combined, "Expected FYM recommendation")

        # No top-dressing in action steps
        actions_text = " ".join(res.get("what_to_do", [])).lower()
        self.assertNotIn("top-dressing", actions_text, "Basal stage should not recommend top-dressing")

    def test_case_d_regional_soil_estimate(self):
        """
        Test Case D: Regional soil estimate
        - Verify response explicitly contains 'regional estimate'
        - Disclaims that exact lab testing is required for precise field dosages
        """
        farm = dict(self.sample_farm)
        farm["soil_data_available"] = False

        res = generate_expert_advice(
            question="What fertilizer should I apply next?",
            farm_data=farm,
            weather_data=self.sample_weather,
            soil_data=self.sample_soil,
            market_data=self.sample_market,
        )

        why = res.get("why", "").lower()
        data_used = " ".join(res.get("data_used", [])).lower()

        # Verify explicitly labeled as regional estimate
        self.assertTrue(
            "regional estimate" in why or "regional estimate" in data_used,
            f"Expected 'regional estimate' label, got why: {why}"
        )

        # Verify disclaims that exact field dosages require an on-farm soil test
        self.assertTrue(
            "on-farm soil test" in why or "soil health card" in why or "soil test" in why,
            "Expected disclaimer requiring soil test for exact dosages"
        )
        self.assertEqual(res.get("farm_context", {}).get("soil_source"), "REGIONAL_ESTIMATE")

    # ── Additional Scenarios ────────────────────────────────────────────────

    def test_query_yellow_leaves_post_harvest(self):
        """
        Test 'My wheat leaves are turning yellow' during post-harvest:
        1. Confidence is MEDIUM (no confirmed diagnosis without field inspection)
        2. Needs Field Verification is True
        3. Avoids overconfident diagnosis (replaces active-crop typical cause assertion)
        4. Post-harvest stubble drying explained
        5. Regional soil baseline described as preliminary context, not proof of field deficiency
        6. Visual clues provided conditionally
        7. No fertilizer or pesticide dosage generated
        """
        farm = dict(self.sample_farm)
        farm["crop_stage"] = "Post-harvest"

        res = generate_expert_advice(
            question="My wheat leaves are turning yellow",
            farm_data=farm,
            weather_data=self.sample_weather,
            soil_data=self.sample_soil,
            market_data=self.sample_market,
        )
        answer = res.get("answer", "")
        why = res.get("why", "")
        what_to_do = res.get("what_to_do", [])
        combined = (answer + " " + why + " " + " ".join(what_to_do)).lower()

        # 1. CONFIDENCE & VERIFICATION
        self.assertEqual(res.get("confidence"), "MEDIUM", "Confidence must be MEDIUM without physical inspection")
        self.assertTrue(res.get("expert_verification_required"), "Must require field verification")
        self.assertTrue(res.get("needs_field_verification"), "Must flag needs_field_verification")

        # 2. AVOID OVERCONFIDENT DIAGNOSIS
        self.assertNotIn("active-crop leaf yellowing is typically caused by nitrogen deficiency or yellow rust", combined)
        self.assertIn("field inspection is needed to distinguish the cause", answer.lower())

        # 3. POST-HARVEST LOGIC
        expected_post_harvest_sentence = (
            "Your Wheat crop is currently marked as Post-harvest. Yellowing or browning of remaining straw/stubble after harvest "
            "is expected and normally does not require crop treatment."
        )
        self.assertIn(expected_post_harvest_sentence, answer)

        # 4. REGIONAL SOIL BASELINE
        expected_soil_sentence = (
            "The regional soil baseline provides preliminary context, but it cannot confirm a nutrient deficiency in this specific field. "
            "An on-farm soil test and crop inspection are needed before making field-specific fertilizer decisions."
        )
        self.assertIn(expected_soil_sentence, why)

        # 5. VISUAL CLUES CAREFULLY WORDED
        expected_visual_clue = (
            "Uniform lower-leaf yellowing may be consistent with nitrogen deficiency, while yellow/orange stripe pustules can indicate Yellow Rust."
        )
        self.assertIn(expected_visual_clue, what_to_do)

        # 6. SAFETY: NO FERTILIZER OR PESTICIDE DOSAGES
        self.assertNotIn("2% urea", combined)
        self.assertNotIn("propiconazole", combined)
        self.assertNotIn("1 ml", combined)
        self.assertNotIn("20g", combined)

    def test_query_yellow_leaves_vegetative(self):
        """Test 'My wheat leaves are turning yellow' during standing vegetative stage"""
        farm = dict(self.sample_farm)
        farm["crop_stage"] = "Tillering"

        res = generate_expert_advice(
            question="My wheat leaves are turning yellow",
            farm_data=farm,
            weather_data=self.sample_weather,
            soil_data=self.sample_soil,
            market_data=self.sample_market,
        )
        answer = res.get("answer", "")
        why = res.get("why", "")
        what_to_do = res.get("what_to_do", [])
        combined = (answer + " " + why + " " + " ".join(what_to_do)).lower()

        # Must have MEDIUM confidence and require field inspection
        self.assertEqual(res.get("confidence"), "MEDIUM")
        self.assertTrue(res.get("expert_verification_required"))
        self.assertIn("field inspection is needed", answer.lower())

        # Regional soil context without asserting field proof
        self.assertIn("preliminary context", why.lower())

        # Visual clues present
        self.assertTrue("lower-leaf yellowing" in combined)
        self.assertTrue("yellow rust" in combined)

        # Irrigation / waterlogging checked
        self.assertTrue("waterlogging" in combined or "drainage" in combined)

        # KVK escalation
        self.assertTrue("kvk" in res.get("when_to_escalate", "").lower())

        # No prescriptive chemical dosages
        self.assertNotIn("2% urea", combined)
        self.assertNotIn("propiconazole", combined)

    def test_query_market_selling(self):
        """
        Test 'Is this a good time to sell?':
        1. Market provenance: HISTORICAL_SEED clearly labeled, not presented as live spot price
        2. Actual XGBoost prediction values appear in reasoning (point & range)
        3. Historical dataset average labeled correctly (not '5-year average')
        4. Weather risk framed contextually (not guaranteeing loss)
        5. Confidence is MEDIUM and Needs Field Verification is flagged
        6. Storage costs accounted for
        """
        res = generate_expert_advice(
            question="Is this a good time to sell?",
            farm_data=self.sample_farm,
            weather_data=self.sample_weather,
            soil_data=self.sample_soil,
            market_data=self.sample_market,
        )
        answer = res.get("answer", "")
        why = res.get("why", "")
        combined = (answer + " " + why).lower()

        # 1. MARKET PROVENANCE
        self.assertNotIn("today's lucknow mandi spot price", combined)
        self.assertIn("historical_seed", combined)
        self.assertIn("reference price", combined)

        # 2. ACTUAL XGBOOST PREDICTIONS USED IN REASONING
        self.assertIn("7-day model range", why.lower())
        self.assertIn("7-day model point", why.lower())
        self.assertTrue("point:" in why.lower() or "point estimate" in why.lower() or "model point" in why.lower())
        self.assertIn("signal:", why.lower())
        self.assertIn("decision impact:", why.lower())

        # 3. HISTORICAL DATASET AVERAGE LABEL
        self.assertNotIn("5-year", why.lower())
        self.assertIn("historical dataset average", why.lower())

        # 4. WEATHER RISK CONTEXTUAL REASONING
        self.assertIn("may increase storage/moisture-management risk", why)

        # 5. STORAGE COST
        self.assertIn("storage cost", why.lower())

        # 6. CONFIDENCE
        self.assertEqual(res.get("confidence"), "MEDIUM")
        self.assertTrue(res.get("expert_verification_required"))
        self.assertTrue(len(res.get("what_to_do", [])) >= 3)

    def test_market_selling_dynamic_conditions(self):
        """Test that different market conditions produce different recommendations"""
        # Scenario A: Bullish price appreciation with low weather risk -> WAIT / HOLD
        bullish_pred = {
            "prediction_7d": {"min_price": 2750, "max_price": 2850, "point_estimate": 2800},
            "prediction_15d": {"min_price": 2800, "max_price": 2950, "point_estimate": 2880}
        }
        low_weather = {
            "forecast_7day": [{"rain_probability_pct": 10, "precipitation_mm": 0, "temp_max_c": 30}],
            "agricultural_risk": {"overall_score": 15}
        }
        res_bullish = generate_expert_advice(
            question="Is this a good time to sell?",
            farm_data=self.sample_farm,
            weather_data=low_weather,
            soil_data=self.sample_soil,
            market_data=self.sample_market,
            prediction_data=bullish_pred
        )
        self.assertIn("holding produce for 7–15 days may be justified", res_bullish["answer"].lower())

        # Scenario B: Flat price outlook -> HOLD OR SELECTIVE SELL
        flat_pred = {
            "prediction_7d": {"min_price": 2595, "max_price": 2615, "point_estimate": 2605}
        }
        res_flat = generate_expert_advice(
            question="Is this a good time to sell?",
            farm_data=self.sample_farm,
            weather_data=self.sample_weather,
            soil_data=self.sample_soil,
            market_data=self.sample_market,
            prediction_data=flat_pred
        )
        self.assertIn("hold or selective selling", res_flat["answer"].lower())

    def test_query_insects_standing_crop(self):
        """Test 'There are insects on my crop' during standing vegetative stage"""
        farm = dict(self.sample_farm)
        farm["crop_stage"] = "Tillering"

        res = generate_expert_advice(
            question="There are insects on my crop",
            farm_data=farm,
            weather_data=self.sample_weather,
            soil_data=self.sample_soil,
            market_data=self.sample_market,
        )
        self.assertTrue(bool(res.get("answer")))
        self.assertIn("aphid", (res["answer"] + res["why"]).lower())
        self.assertTrue(len(res.get("what_to_do", [])) >= 3)
        self.assertEqual(res.get("confidence"), "MEDIUM")

        # Confirm NO generic unverified pesticide dosages in standing crop advice
        combined = (res["answer"] + " " + res["why"] + " " + " ".join(res["what_to_do"])).lower()
        self.assertNotIn("100g/acre", combined)
        self.assertNotIn("1 liter/acre", combined)
        self.assertNotIn("300ml/acre", combined)
        self.assertIn("label", combined)

    def test_query_insects_post_harvest(self):
        """
        Test 'There are insects on my crop' during post-harvest:
        1. NO generic pesticide dosage/ratio
        2. Exact safe sanitation text present
        3. Rainfall probability described only as contextual moisture-risk signal
        4. Post-harvest awareness (drying, storage, inspection, next crop)
        5. Confidence MEDIUM and indicates Needs Field Verification
        """
        farm = dict(self.sample_farm)
        farm["crop_stage"] = "Post-harvest"

        res = generate_expert_advice(
            question="There are insects on my crop",
            farm_data=farm,
            weather_data=self.sample_weather,
            soil_data=self.sample_soil,
            market_data=self.sample_market,
        )
        answer = res.get("answer", "")
        why = res.get("why", "")
        what_to_do = res.get("what_to_do", [])
        combined = (answer + " " + why + " " + " ".join(what_to_do)).lower()

        # 1. REMOVE UNSAFE GENERIC PESTICIDE DOSAGE ADVICE
        self.assertNotIn("malathion", combined)
        self.assertNotIn("1:100", combined)
        self.assertNotIn("50% ec", combined)
        self.assertNotIn("chlorpyrifos", combined)

        # Confirm required sanitation replacement text is present
        sanitation_step = (
            "Clean and sanitize the storage room, bins, and equipment before storing grain. "
            "If chemical treatment is required, use only a pesticide or fumigant registered and labelled for the "
            "identified stored-grain pest and storage situation, and follow the product label or guidance from the "
            "local KVK/Agriculture Department."
        )
        self.assertIn(sanitation_step, what_to_do)

        # 2. FIX WEATHER -> STORAGE REASONING
        # Must NOT claim stored grain itself is humid or that forecast definitely caused pests
        self.assertNotIn("stored grains in humid conditions", why.lower())
        # Rainfall described as contextual moisture-risk signal
        expected_why = (
            "Detected crop stage is Post-harvest. The current forecast shows a high rainfall probability (89%). "
            "Poorly sealed or humid storage areas may therefore face increased moisture risk, so keeping grain and "
            "storage structures dry and well sealed is important."
        )
        self.assertEqual(why.strip(), expected_why.strip())

        # 3. KEEP POST-HARVEST STAGE AWARENESS
        # Do NOT recommend fertilizer for harvested crop
        self.assertNotIn("top-dressing", combined)
        self.assertNotIn("tillering", combined)
        self.assertNotIn("urea @", combined)
        self.assertNotIn("dap @", combined)

        # 4. SAFE PEST GUIDANCE (non-chemical priorities)
        actions_text = " ".join(what_to_do).lower()
        self.assertTrue("dry grain" in actions_text or "drying" in actions_text, "Expected grain drying guidance")
        self.assertTrue("clean and sanitize" in actions_text, "Expected sanitation guidance")
        self.assertTrue("inspect" in actions_text, "Expected inspection guidance")
        self.assertTrue("dry and well sealed" in actions_text, "Expected dry/sealed storage guidance")
        self.assertTrue("hermetic" in actions_text or "sealed" in actions_text, "Expected hermetic/sealed storage")

        # Escalation to KVK / Agriculture Department
        when_to_escalate = res.get("when_to_escalate", "")
        self.assertTrue("kvk" in when_to_escalate.lower() and "agriculture department" in when_to_escalate.lower())

        # 5. CONFIDENCE & FIELD VERIFICATION
        self.assertEqual(res.get("confidence"), "MEDIUM")
        self.assertTrue(res.get("expert_verification_required"))
        self.assertTrue(res.get("needs_field_verification"))

    def test_missing_farm_context(self):
        """Ensure service works when farm_data, weather_data, etc. are None/empty"""
        res = generate_expert_advice(
            question="What fertilizer should I apply next?",
            farm_data=None,
            weather_data=None,
            soil_data=None,
            market_data=None,
        )
        self.assertTrue(bool(res.get("answer")), "Answer must not be empty with missing context")
        self.assertNotEqual(res.get("answer"), "")
        self.assertIn(res.get("confidence"), ["HIGH", "MEDIUM", "LOW"])
        self.assertTrue(bool(res.get("farm_context")))

    def test_gemini_unavailable_fallback(self):
        """Ensure service produces full response with krishi_data_engine when Gemini is unavailable"""
        import os
        old_key = os.environ.get("GEMINI_API_KEY")
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        try:
            res = generate_expert_advice(
                question="What fertilizer should I apply next?",
                farm_data=self.sample_farm,
            )
            self.assertEqual(res.get("engine"), "krishi_data_engine")
            self.assertTrue(bool(res.get("answer")))
            self.assertTrue(len(res.get("what_to_do", [])) > 0)
        finally:
            if old_key is not None:
                os.environ["GEMINI_API_KEY"] = old_key

    def test_backwards_compatibility_nesting(self):
        """Ensure both top-level answer and legacy response.preliminary_guidance exist"""
        res = generate_expert_advice(
            question="My wheat leaves are turning yellow",
            farm_data=self.sample_farm,
        )
        self.assertEqual(res["answer"], res["response"]["preliminary_guidance"])
        self.assertEqual(res["confidence"], res["response"]["confidence"])
        self.assertEqual(res["what_to_do"], res["response"]["recommended_actions"])

if __name__ == '__main__':
    unittest.main()
