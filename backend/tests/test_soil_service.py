"""
Unit & Regression Tests for Context-Aware Soil Intelligence
===========================================================
Verifies:
1. Wheat + Post-harvest stage constraints (no fertilizer on stubble, residue mgmt, soil testing, next-crop planning)
2. Wheat + Standing crop (Tillering) conditional guidance (weather check, no exact doses)
3. Regional soil estimate provenance handling & disclosure note preservation
4. No unsupported exact fertilizer prescriptions ('50 kg/ha urea')
5. Multi-crop adaptability (Paddy, Mustard, etc.)
6. Consistency with Expert Intelligence (no contradictions)
7. Preservation of baseline parameters, suitability score (74/Good), and risk score (28/LOW)
"""

import unittest
from backend.services.soil_service import get_soil_intelligence, generate_soil_recommendations
from backend.services.expert_service import generate_expert_advice


class TestSoilIntelligence(unittest.TestCase):

    def test_case_1_wheat_post_harvest(self):
        """
        Scenario 1: Wheat + Post-harvest
        - Do NOT recommend chemical fertilizer application to harvested stubble.
        - Recommend residue management, FYM organic carbon recharge, soil testing, and next crop planning.
        """
        soil = get_soil_intelligence(crop="Wheat", crop_stage="Post-harvest", soil_tested=False)
        recs = soil["recommendations"]
        recs_text = " ".join(recs).lower()

        # Hard constraint: No fertilizer on harvested crop
        self.assertTrue(
            "do not apply chemical fertilizer" in recs_text or "do not apply" in recs_text,
            "Expected clear directive not to apply chemical fertilizer to harvested crop"
        )
        self.assertFalse(
            "apply 50 kg/ha urea as basal dose" in recs_text,
            "Should not contain legacy basal urea dose"
        )

        # Field residue & FYM
        self.assertTrue(
            "stubble" in recs_text or "residue" in recs_text,
            "Expected residue/stubble management recommendation"
        )
        self.assertTrue(
            "organic carbon" in recs_text or "fym" in recs_text or "manure" in recs_text,
            "Expected organic carbon / FYM recommendation"
        )

        # Soil testing / Soil Health Card
        self.assertTrue(
            "soil testing" in recs_text or "soil health card" in recs_text or "soil test" in recs_text,
            "Expected soil testing / Soil Health Card recommendation"
        )

        # Next crop planning
        self.assertTrue(
            "next crop" in recs_text or "rotation" in recs_text or "upcoming" in recs_text,
            "Expected next-crop planning guidance"
        )

    def test_case_2_wheat_standing_crop(self):
        """
        Scenario 2: Wheat + Standing crop (Tillering)
        - Mentions standing crop nutrition conditionally.
        - Advise weather and moisture caution.
        - Advise on-farm soil test and KVK guidance before determining dose.
        - NO rigid unsupported doses.
        """
        soil = get_soil_intelligence(crop="Wheat", crop_stage="Tillering", soil_tested=False)
        recs = soil["recommendations"]
        recs_text = " ".join(recs).lower()

        # Standing crop context
        self.assertTrue(
            "standing" in recs_text and "wheat" in recs_text,
            "Expected standing wheat context in recommendations"
        )
        # Weather / moisture caution
        self.assertTrue(
            "rain" in recs_text or "moisture" in recs_text,
            "Expected weather or moisture caution"
        )
        # Conditional dosage / KVK consultation
        self.assertTrue(
            "kvk" in recs_text or "soil health card" in recs_text or "soil test" in recs_text,
            "Expected KVK or soil test consultation requirement"
        )
        # No rigid dosage
        self.assertNotIn("50 kg/ha urea", recs_text)

    def test_case_3_regional_soil_estimate_provenance(self):
        """
        Scenario 3: Regional soil estimate
        - Verify provenance type is REGIONAL_ESTIMATE.
        - Verify preserved disclosure note.
        - Verify recommendations advise on-farm soil test.
        """
        soil = get_soil_intelligence(crop="Wheat", crop_stage="Post-harvest", soil_tested=False)
        ds = soil["data_source"]

        self.assertEqual(ds["type"], "REGIONAL_ESTIMATE")
        self.assertEqual(
            ds["note"],
            "Individual farm values may vary. Upload soil test for accurate assessment."
        )

        recs_text = " ".join(soil["recommendations"]).lower()
        self.assertTrue(
            "regional" in recs_text or "icar-nbss&lup" in recs_text,
            "Expected regional provenance note in recommendations"
        )

    def test_case_4_no_unsupported_exact_fertilizer_dose_across_stages(self):
        """
        Scenario 4: Verify NO unsupported exact fertilizer dose is presented
        for regional estimates across all phenological stages.
        """
        stages_to_test = ["Post-harvest", "Pre-sowing", "Tillering", "Jointing", "Flowering", "Grain Filling"]
        for stage in stages_to_test:
            soil = get_soil_intelligence(crop="Wheat", crop_stage=stage, soil_tested=False)
            recs_text = " ".join(soil["recommendations"]).lower()
            self.assertNotIn(
                "apply 50 kg/ha urea as basal dose",
                recs_text,
                f"Found hardcoded legacy prescription in stage {stage}"
            )
            # Ensure any chemical fertilizer guidance requires on-farm soil test
            if "fertilizer" in recs_text and stage != "Post-harvest" and "reproductive" not in stage.lower() and "flowering" not in stage.lower() and "grain filling" not in stage.lower():
                self.assertTrue(
                    "soil test" in recs_text or "kvk" in recs_text or "guidance" in recs_text,
                    f"Stage {stage} mentioned fertilizer without conditional soil test / KVK requirement"
                )

    def test_case_5_multi_crop_adaptability(self):
        """
        Scenario 5: Dynamic handling of different crops (Paddy, Mustard)
        """
        paddy_soil = get_soil_intelligence(crop="Paddy", crop_stage="Post-harvest", soil_tested=False)
        paddy_recs = " ".join(paddy_soil["recommendations"])
        self.assertIn("Paddy", paddy_recs)
        self.assertIn("paddy", paddy_recs.lower())

        # Check suitability factor references paddy
        factors = paddy_soil["crop_suitability"]["factors"]
        reasons_text = " ".join(f.get("reason", "") for f in factors)
        self.assertIn("paddy", reasons_text.lower())

        mustard_soil = get_soil_intelligence(crop="Mustard", crop_stage="Pre-sowing", soil_tested=False)
        mustard_recs = " ".join(mustard_soil["recommendations"])
        self.assertIn("Mustard", mustard_recs)

    def test_case_6_consistency_with_expert_intelligence(self):
        """
        Scenario 6: Verify Soil Intelligence and Expert Intelligence
        never contradict each other for the same farm and crop stage.
        """
        farm_data = {
            "crop": "Wheat",
            "crop_stage": "Post-harvest",
            "district": "Lucknow",
            "state": "Uttar Pradesh",
            "soil_data_available": False,
        }

        expert = generate_expert_advice("What fertilizer should I apply next?", farm_data=farm_data)
        soil = get_soil_intelligence(
            crop="Wheat",
            crop_stage="Post-harvest",
            district="Lucknow",
            state="Uttar Pradesh",
            soil_tested=False,
        )

        expert_ans = expert["answer"].lower()
        expert_why = expert["why"].lower()
        expert_actions = " ".join(expert.get("what_to_do", [])).lower()
        soil_recs = " ".join(soil["recommendations"]).lower()

        # Both MUST forbid fertilizer on harvested wheat
        self.assertTrue(
            "not be applied" in expert_ans or "do not apply" in expert_actions,
            "Expert must forbid fertilizer on post-harvest wheat"
        )
        self.assertTrue(
            "do not apply" in soil_recs or "not be applied" in soil_recs,
            "Soil intelligence must forbid fertilizer on post-harvest wheat"
        )

        # Both MUST recommend soil testing
        self.assertTrue("soil" in expert_actions and "test" in expert_actions)
        self.assertTrue("soil" in soil_recs and "test" in soil_recs)

        # Both MUST recommend organic matter / FYM
        self.assertTrue("fym" in expert_actions or "manure" in expert_actions or "organic" in expert_actions)
        self.assertTrue("fym" in soil_recs or "manure" in soil_recs or "organic" in soil_recs)

        # Both MUST recommend planning for the NEXT crop
        self.assertTrue("next" in expert_actions)
        self.assertTrue("next" in soil_recs)

    def test_case_7_preservation_of_baseline_values(self):
        """
        Scenario 7: Ensure nutrient values, suitability score (74/Good),
        and overall soil risk (28/LOW) remain untouched.
        """
        soil = get_soil_intelligence()
        params = soil["parameters"]

        self.assertEqual(params["ph"]["value"], 7.5)
        self.assertEqual(params["nitrogen"]["value"], 240)
        self.assertEqual(params["phosphorus"]["value"], 18)
        self.assertEqual(params["potassium"]["value"], 220)
        self.assertEqual(params["organic_carbon"]["value"], 0.45)
        self.assertEqual(params["soil_type"], "Sandy Loam")
        self.assertEqual(params["texture"], "Loamy")

        self.assertEqual(soil["crop_suitability"]["score"], 74)
        self.assertEqual(soil["crop_suitability"]["label"], "Good")
        self.assertEqual(soil["overall_soil_risk"]["score"], 28)
        self.assertEqual(soil["overall_soil_risk"]["level"], "LOW")


if __name__ == '__main__':
    unittest.main()
