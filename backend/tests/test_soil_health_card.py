"""
Automated Test Suite for Feature 3: Granular Soil Intelligence & Soil Health Card OCR
=====================================================================================
Covers all 25 validation criteria:
1. Soil document upload PDF success
2. Soil document upload image success (JPG/PNG)
3. Soil document upload unsupported file type rejection (HTTP 400)
4. Soil document upload oversized file rejection (HTTP 413 / 400)
5. Soil document upload corrupted magic bytes rejection (HTTP 400)
6. OCR structured extraction from standard Soil Health Card text
7. OCR partial extraction correctly identified
8. OCR invalid pH (<0 or >14) flagged as invalid
9. OCR negative nutrient (<0) flagged as invalid
10. OCR output never auto-confirms (REVIEW_REQUIRED)
11. Unconfirmed upload does not alter farm profile or active intelligence
12. Explicit confirmation creates active FarmSoilProfile
13. Confirming new profile deactivates previous profile (one active profile per farm)
14. Field provenance tracking distinguishes SOIL_HEALTH_CARD vs FARMER_ENTERED
15. Missing soil parameters remain None/null (never coerced to 0)
16. Confirmed soil profile takes precedence over regional estimate
17. Fallback to regional estimate (ICAR-NBSS&LUP) when unconfirmed
18. Digital Twin reflects confirmed soil profile and provenance
19. Digital Twin reflects regional fallback when unconfirmed
20. Expert Intelligence truthful wording for confirmed soil cards
21. Expert Intelligence truthful wording for regional estimate fallback
22. Risk Engine integrates confirmed soil measurements safely
23. Cross-farm data isolation (Farm A card does not affect Farm B)
24. FarmEvent logged upon confirmation (SOIL_PROFILE_CONFIRMED)
25. Crop stage fertilizer recommendation guardrail preserved with confirmed soil
"""
import io
import unittest
from datetime import datetime, date
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import SessionLocal
from backend.models.farm import Farm, FarmEvent, SoilDocument, FarmSoilProfile
from backend.services.soil_ocr_service import (
    validate_uploaded_file,
    parse_soil_health_card_text,
    process_soil_health_card_document,
)
from backend.services.soil_service import get_soil_intelligence
from backend.services.expert_service import generate_expert_advice
from backend.services.risk_engine import compute_risk

client = TestClient(app)

# Minimal valid file payloads for testing
VALID_PDF_BYTES = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\n"
    b"xref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n"
    b"0000000053 00000 n\n0000000102 00000 n\n"
    b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n149\n%%EOF\n"
)

VALID_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00"
    b"\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)

SAMPLE_SOIL_CARD_TEXT = """
GOVERNMENT OF INDIA - MINISTRY OF AGRICULTURE & FARMERS WELFARE
SOIL HEALTH CARD (राष्ट्रीय मृदा स्वास्थ्य कार्ड)
Sample ID: SHC-UP-2026-8891
Farmer Name: Ramesh Kumar
Village: Malihabad, District: Lucknow, State: Uttar Pradesh
Date of Testing: 15-02-2026

TEST RESULTS & NUTRIENT STATUS:
1. Soil Reaction (pH): 7.2 (Neutral)
2. Electrical Conductivity (EC): 0.65 dS/m (Normal)
3. Organic Carbon (OC): 0.62 % (Medium)
4. Available Nitrogen (N): 275.0 kg/ha (Low)
5. Available Phosphorus (P): 24.5 kg/ha (Medium)
6. Available Potassium (K): 260.0 kg/ha (Medium)
7. Available Sulphur (S): 14.2 ppm (Sufficient)
8. Available Zinc (Zn): 0.95 ppm (Sufficient)
9. Available Iron (Fe): 7.8 ppm (Sufficient)
10. Available Copper (Cu): 0.52 ppm (Sufficient)
11. Available Manganese (Mn): 3.8 ppm (Sufficient)
12. Available Boron (B): 0.72 ppm (Sufficient)
Physical Condition: Sandy Loam
"""


class TestSoilHealthCardSuite(unittest.TestCase):

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def _create_farm(self, farmer_name="Test Farmer", crop="Wheat", crop_stage="Tillering") -> str:
        res = client.post("/api/farm/onboard", json={
            "farmer_name": farmer_name,
            "location": "Malihabad",
            "district": "Lucknow",
            "state": "Uttar Pradesh",
            "crop": crop,
            "crop_variety": "HD-2967",
            "sowing_date": "2025-11-15",
            "farm_area_acres": 5.0,
            "soil_data_available": False,
            "phone": "9876543210",
        })
        self.assertEqual(res.status_code, 200)
        return res.json()["farm_id"]

    # 1. Soil document upload PDF success
    def test_01_soil_document_upload_pdf_success(self):
        farm_id = self._create_farm("PDF Test Farmer")
        files = {"file": ("soil_card.pdf", io.BytesIO(VALID_PDF_BYTES), "application/pdf")}
        data = {"farm_id": farm_id}

        res = client.post("/api/soil/upload", data=data, files=files)
        self.assertEqual(res.status_code, 200)
        json_data = res.json()
        self.assertEqual(json_data["farm_id"], farm_id)
        self.assertIn("document_id", json_data)
        self.assertEqual(json_data["extraction_state"], "REVIEW_REQUIRED")

        # Verify DB record
        doc = self.db.query(SoilDocument).filter(SoilDocument.id == json_data["document_id"]).first()
        self.assertIsNotNone(doc)
        self.assertFalse(doc.is_confirmed)

    # 2. Soil document upload image success (PNG)
    def test_02_soil_document_upload_image_success(self):
        farm_id = self._create_farm("Image Test Farmer")
        files = {"file": ("soil_card.png", io.BytesIO(VALID_PNG_BYTES), "image/png")}
        data = {"farm_id": farm_id}

        res = client.post("/api/soil/upload", data=data, files=files)
        self.assertEqual(res.status_code, 200)
        json_data = res.json()
        self.assertEqual(json_data["farm_id"], farm_id)
        self.assertEqual(json_data["extraction_state"], "REVIEW_REQUIRED")

    # 3. Unsupported file type rejection (HTTP 400)
    def test_03_soil_document_upload_unsupported_file_type(self):
        farm_id = self._create_farm("Reject Type Farmer")
        files = {"file": ("malicious.exe", io.BytesIO(b"MZ\x90\x00\x03\x00"), "application/x-msdownload")}
        data = {"farm_id": farm_id}

        res = client.post("/api/soil/upload", data=data, files=files)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Unsupported file extension", res.json()["detail"])

    # 4. Oversized file rejection (> 10MB)
    def test_04_soil_document_upload_oversized_file(self):
        farm_id = self._create_farm("Oversize Farmer")
        oversized_content = b"%PDF" + (b"0" * (11 * 1024 * 1024))
        files = {"file": ("giant_file.pdf", io.BytesIO(oversized_content), "application/pdf")}
        data = {"farm_id": farm_id}

        res = client.post("/api/soil/upload", data=data, files=files)
        self.assertIn(res.status_code, [400, 413])

    # 5. Corrupted magic bytes rejection
    def test_05_soil_document_upload_corrupted_magic_bytes(self):
        farm_id = self._create_farm("Corrupt Header Farmer")
        # Named .pdf but contains plain text without %PDF header
        files = {"file": ("fake.pdf", io.BytesIO(b"This is just plain text, not a PDF!"), "application/pdf")}
        data = {"farm_id": farm_id}

        res = client.post("/api/soil/upload", data=data, files=files)
        self.assertEqual(res.status_code, 400)
        self.assertIn("header", res.json()["detail"].lower())

    # 6. OCR structured extraction from standard Soil Health Card text
    def test_06_ocr_extracts_structured_values_from_text(self):
        result = parse_soil_health_card_text(SAMPLE_SOIL_CARD_TEXT)
        params = result["parameters"]

        self.assertEqual(params["ph"]["value"], 7.2)
        self.assertEqual(params["ph"]["unit"], "")
        self.assertEqual(params["ph"]["status"], "GOOD")
        self.assertTrue(params["ph"]["valid"])

        self.assertEqual(params["ec"]["value"], 0.65)
        self.assertEqual(params["organic_carbon"]["value"], 0.62)
        self.assertEqual(params["nitrogen"]["value"], 275.0)
        self.assertEqual(params["phosphorus"]["value"], 24.5)
        self.assertEqual(params["potassium"]["value"], 260.0)
        self.assertEqual(params["zinc"]["value"], 0.95)
        self.assertEqual(params["soil_texture"]["value"], "Sandy Loam")
        self.assertEqual(result["test_date"], "2026-02-15")

    # 7. OCR partial extraction correctly identified
    def test_07_ocr_partial_extraction_status(self):
        partial_text = "Soil Health Card: pH Value: 6.8, Nitrogen: 220 kg/ha"
        extraction = parse_soil_health_card_text(partial_text)
        params = extraction["parameters"]

        self.assertEqual(params["ph"]["value"], 6.8)
        self.assertEqual(params["nitrogen"]["value"], 220.0)
        # Phosphorus was not in text
        self.assertIsNone(params["phosphorus"]["value"])
        self.assertEqual(params["phosphorus"]["status"], "NOT_DETECTED")

    # 8. OCR invalid pH (<0 or >14) flagged as invalid
    def test_08_ocr_invalid_ph_flagged(self):
        impossible_ph_text = "Soil Test Report: pH: 18.5, Nitrogen: 300 kg/ha"
        extraction = parse_soil_health_card_text(impossible_ph_text)
        params = extraction["parameters"]

        self.assertIsNone(params["ph"]["value"], "Impossible pH must not be passed through as valid value")
        self.assertEqual(params["ph"]["raw_value"], 18.5)
        self.assertFalse(params["ph"]["valid"])
        self.assertEqual(params["ph"]["status"], "INVALID")

    # 9. OCR negative nutrient (<0) flagged as invalid
    def test_09_ocr_negative_nutrient_flagged(self):
        # Directly test validation logic
        from backend.services.soil_ocr_service import PARAMETER_SPECS
        self.assertGreaterEqual(PARAMETER_SPECS["nitrogen"]["min"], 0.0)
        self.assertGreaterEqual(PARAMETER_SPECS["phosphorus"]["min"], 0.0)
        self.assertGreaterEqual(PARAMETER_SPECS["potassium"]["min"], 0.0)

        res = client.post("/api/soil/confirm", json={
            "farm_id": self._create_farm("Negative Nutrient Farmer"),
            "parameters": {"nitrogen": -50.0},
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("cannot be negative", res.json()["detail"].lower())

    # 10. OCR output never auto-confirms (REVIEW_REQUIRED)
    def test_10_ocr_never_auto_confirms(self):
        farm_id = self._create_farm("Auto Confirm Guard Farmer")
        files = {"file": ("soil_card.pdf", io.BytesIO(VALID_PDF_BYTES), "application/pdf")}
        res = client.post("/api/soil/upload", data={"farm_id": farm_id}, files=files)
        self.assertEqual(res.status_code, 200)

        json_data = res.json()
        self.assertEqual(json_data["extraction_state"], "REVIEW_REQUIRED")

        # Verify active profile does not exist yet
        active_prof = self.db.query(FarmSoilProfile).filter(
            FarmSoilProfile.farm_id == farm_id,
            FarmSoilProfile.is_active == True
        ).first()
        self.assertIsNone(active_prof, "Active soil profile must NEVER be created before farmer confirmation!")

    # 11. Unconfirmed upload does not alter farm profile or active intelligence
    def test_11_unconfirmed_upload_does_not_affect_farm_profile(self):
        farm_id = self._create_farm("Unconfirmed Farm")
        # Upload card
        files = {"file": ("card.pdf", io.BytesIO(VALID_PDF_BYTES), "application/pdf")}
        client.post("/api/soil/upload", data={"farm_id": farm_id}, files=files)

        # Query soil intelligence
        intel_res = client.get(f"/api/soil/intelligence?farm_id={farm_id}")
        self.assertEqual(intel_res.status_code, 200)
        soil_data = intel_res.json()

        # Must still be REGIONAL_ESTIMATE because farmer has not confirmed
        self.assertEqual(soil_data["data_source"]["type"], "REGIONAL_ESTIMATE")

    # 12. Explicit confirmation creates active FarmSoilProfile
    def test_12_explicit_confirmation_creates_active_farm_soil_profile(self):
        farm_id = self._create_farm("Confirm Profile Farmer")
        confirm_payload = {
            "farm_id": farm_id,
            "test_date": "2026-02-20",
            "parameters": {
                "ph": 7.1,
                "nitrogen": 290.0,
                "phosphorus": 28.0,
                "potassium": 210.0,
                "organic_carbon": 0.65,
                "ec": 0.70,
                "soil_texture": "Sandy Loam",
            },
            "field_sources": {
                "ph": "SOIL_HEALTH_CARD",
                "nitrogen": "SOIL_HEALTH_CARD",
                "phosphorus": "SOIL_HEALTH_CARD",
                "potassium": "SOIL_HEALTH_CARD",
                "organic_carbon": "SOIL_HEALTH_CARD",
                "ec": "SOIL_HEALTH_CARD",
            }
        }
        res = client.post("/api/soil/confirm", json=confirm_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["farm_id"], farm_id)
        self.assertTrue(data["is_active"])
        self.assertEqual(data["provenance"], "SOIL_HEALTH_CARD")
        self.assertEqual(data["parameters"]["ph"], 7.1)

    # 13. Confirming new profile deactivates previous profile
    def test_13_confirmation_deactivates_previous_soil_profiles(self):
        farm_id = self._create_farm("Multi Confirm Farmer")

        # First confirmation
        payload_1 = {
            "farm_id": farm_id,
            "test_date": "2026-01-10",
            "parameters": {"ph": 6.8, "nitrogen": 250.0},
        }
        res1 = client.post("/api/soil/confirm", json=payload_1)
        self.assertEqual(res1.status_code, 200)
        prof1_id = res1.json()["id"]

        # Second confirmation
        payload_2 = {
            "farm_id": farm_id,
            "test_date": "2026-02-15",
            "parameters": {"ph": 7.3, "nitrogen": 310.0},
        }
        res2 = client.post("/api/soil/confirm", json=payload_2)
        self.assertEqual(res2.status_code, 200)
        prof2_id = res2.json()["id"]

        # Verify in DB: prof1 is inactive, prof2 is active
        prof1 = self.db.query(FarmSoilProfile).filter(FarmSoilProfile.id == prof1_id).first()
        prof2 = self.db.query(FarmSoilProfile).filter(FarmSoilProfile.id == prof2_id).first()

        self.assertFalse(prof1.is_active)
        self.assertTrue(prof2.is_active)

    # 14. Field provenance tracking distinguishes SOIL_HEALTH_CARD vs FARMER_ENTERED
    def test_14_field_provenance_tracking_soil_health_card_vs_farmer_entered(self):
        farm_id = self._create_farm("Field Provenance Farmer")
        payload = {
            "farm_id": farm_id,
            "test_date": "2026-02-18",
            "parameters": {
                "ph": 7.0,
                "nitrogen": 300.0,
                "phosphorus": 35.0,
            },
            "field_sources": {
                "ph": "SOIL_HEALTH_CARD",
                "nitrogen": "SOIL_HEALTH_CARD",
                "phosphorus": "FARMER_ENTERED",  # edited by farmer
            }
        }
        res = client.post("/api/soil/confirm", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertEqual(data["provenance"], "FARMER_ENTERED", "Mixed sources must indicate farmer input occurred")
        self.assertEqual(data["field_sources"]["ph"], "SOIL_HEALTH_CARD")
        self.assertEqual(data["field_sources"]["phosphorus"], "FARMER_ENTERED")

    # 15. Missing soil parameters remain None/null (never coerced to 0)
    def test_15_missing_soil_parameters_remain_null(self):
        farm_id = self._create_farm("Missing Params Farmer")
        payload = {
            "farm_id": farm_id,
            "parameters": {
                "ph": 7.2,
                "nitrogen": None,  # Not tested / missing
                "phosphorus": 22.0,
            },
        }
        res = client.post("/api/soil/confirm", json=payload)
        self.assertEqual(res.status_code, 200)

        intel = client.get(f"/api/soil/intelligence?farm_id={farm_id}").json()
        params = intel["parameters"]

        self.assertEqual(params["ph"]["value"], 7.2)
        self.assertIsNone(params["nitrogen"]["value"], "Missing nitrogen must remain None, never coerced to 0!")
        self.assertEqual(params["nitrogen"]["status"], "UNAVAILABLE")

    # 16. Confirmed soil profile takes precedence over regional estimate
    def test_16_confirmed_soil_profile_takes_precedence_over_regional_estimate(self):
        farm_id = self._create_farm("Precedence Farmer")
        payload = {
            "farm_id": farm_id,
            "parameters": {
                "ph": 6.9,
                "nitrogen": 320.0,
                "phosphorus": 32.0,
                "potassium": 280.0,
                "organic_carbon": 0.85,
            },
            "field_sources": {
                "ph": "SOIL_HEALTH_CARD",
                "nitrogen": "SOIL_HEALTH_CARD",
                "phosphorus": "SOIL_HEALTH_CARD",
                "potassium": "SOIL_HEALTH_CARD",
                "organic_carbon": "SOIL_HEALTH_CARD",
            }
        }
        client.post("/api/soil/confirm", json=payload)

        intel = client.get(f"/api/soil/intelligence?farm_id={farm_id}").json()
        self.assertEqual(intel["data_source"]["type"], "SOIL_HEALTH_CARD")
        self.assertEqual(intel["parameters"]["ph"]["value"], 6.9)
        self.assertEqual(intel["parameters"]["nitrogen"]["value"], 320.0)

    # 17. Fallback to regional estimate (ICAR-NBSS&LUP) when unconfirmed
    def test_17_fallback_to_regional_estimate_when_no_confirmed_profile(self):
        farm_id = self._create_farm("Regional Only Farmer")
        intel = client.get(f"/api/soil/intelligence?farm_id={farm_id}").json()

        self.assertEqual(intel["data_source"]["type"], "REGIONAL_ESTIMATE")
        self.assertIn("ICAR-NBSS&LUP", intel["data_source"]["provider"])
        self.assertEqual(intel["crop_suitability"]["score"], 74)

    # 18. Digital Twin reflects confirmed soil profile and provenance
    def test_18_digital_twin_reflects_confirmed_soil_profile(self):
        farm_id = self._create_farm("Digital Twin Soil Farmer")
        payload = {
            "farm_id": farm_id,
            "parameters": {
                "ph": 7.4,
                "nitrogen": 340.0,
                "soil_texture": "Loam",
            },
            "field_sources": {
                "ph": "SOIL_HEALTH_CARD",
                "nitrogen": "SOIL_HEALTH_CARD",
            }
        }
        client.post("/api/soil/confirm", json=payload)

        dt = client.get(f"/api/farm/{farm_id}/digital-twin").json()
        self.assertEqual(dt["data_provenance"]["soil"], "SOIL_HEALTH_CARD")
        self.assertEqual(dt["intelligence"]["soil"]["parameters"]["texture"], "Loam")

    # 19. Digital Twin reflects regional fallback when unconfirmed
    def test_19_digital_twin_reflects_regional_fallback_when_unconfirmed(self):
        farm_id = self._create_farm("Digital Twin Unconfirmed Farmer")
        dt = client.get(f"/api/farm/{farm_id}/digital-twin").json()
        self.assertEqual(dt["data_provenance"]["soil"], "REGIONAL_ESTIMATE")

    # 20. Expert Intelligence truthful wording for confirmed soil cards
    def test_20_expert_intelligence_truthful_wording_confirmed(self):
        farm_data = {
            "crop": "Wheat",
            "crop_stage": "Tillering",
            "district": "Lucknow",
            "state": "Uttar Pradesh",
            "soil_data_available": True,
            "soil_provenance": "SOIL_HEALTH_CARD",
        }
        expert = generate_expert_advice("How is my soil health looking?", farm_data=farm_data)
        expert_text = f"{expert.get('answer', '')} {expert.get('why', '')}".lower()

        self.assertTrue(
            "soil health card" in expert_text or "soil test" in expert_text,
            "Expert advice must reflect confirmed Soil Health Card testing"
        )

    # 21. Expert Intelligence truthful wording for regional estimate fallback
    def test_21_expert_intelligence_truthful_wording_regional(self):
        farm_data = {
            "crop": "Wheat",
            "crop_stage": "Tillering",
            "district": "Lucknow",
            "state": "Uttar Pradesh",
            "soil_data_available": False,
            "soil_provenance": "REGIONAL_ESTIMATE",
        }
        expert = generate_expert_advice("How is my soil health looking?", farm_data=farm_data)
        expert_text = f"{expert.get('answer', '')} {expert.get('why', '')}".lower()

        self.assertTrue(
            "regional" in expert_text or "estimate" in expert_text,
            "Expert advice must truthfully disclose regional estimate for unconfirmed farm"
        )

    # 22. Risk Engine integrates confirmed soil measurements safely
    def test_22_risk_engine_integrates_confirmed_soil_profile(self):
        # Even with missing fields (e.g. pH is None), compute_risk should not crash
        soil_profile_dict = {
            "parameters": {
                "ph": {"value": None},
                "nitrogen": {"value": 250, "status": "GOOD"},
                "organic_carbon": {"value": 0.6, "status": "MEDIUM"},
                "phosphorus": {"value": 22, "status": "GOOD"},
                "potassium": {"value": 200, "status": "GOOD"},
            }
        }
        risks = compute_risk(
            weather_data={},
            soil_data=soil_profile_dict,
            crop_stage="Tillering",
            days_after_sowing=40,
            market_data={},
        )
        self.assertIn("overall_risk", risks)
        self.assertIn("soil_risk", risks)
        self.assertIsInstance(risks["overall_risk"]["score"], (int, float))

    # 23. Cross-farm data isolation
    def test_23_cross_farm_isolation(self):
        farm_a = self._create_farm("Farm A Farmer")
        farm_b = self._create_farm("Farm B Farmer")

        # Confirm card for Farm A only
        client.post("/api/soil/confirm", json={
            "farm_id": farm_a,
            "parameters": {"ph": 6.7, "nitrogen": 350.0},
            "field_sources": {"ph": "SOIL_HEALTH_CARD", "nitrogen": "SOIL_HEALTH_CARD"},
        })

        # Check Farm A
        res_a = client.get(f"/api/soil/intelligence?farm_id={farm_a}").json()
        self.assertEqual(res_a["data_source"]["type"], "SOIL_HEALTH_CARD")
        self.assertEqual(res_a["parameters"]["ph"]["value"], 6.7)

        # Check Farm B (Must remain REGIONAL_ESTIMATE)
        res_b = client.get(f"/api/soil/intelligence?farm_id={farm_b}").json()
        self.assertEqual(res_b["data_source"]["type"], "REGIONAL_ESTIMATE")
        self.assertEqual(res_b["parameters"]["ph"]["value"], 7.5)

    # 24. FarmEvent logged upon confirmation
    def test_24_farm_event_logged_on_confirmation(self):
        farm_id = self._create_farm("Event Log Farmer")
        client.post("/api/soil/confirm", json={
            "farm_id": farm_id,
            "parameters": {"ph": 7.1},
        })

        event = self.db.query(FarmEvent).filter(
            FarmEvent.farm_id == farm_id,
            FarmEvent.event_type == "SOIL_PROFILE_CONFIRMED"
        ).first()

        self.assertIsNotNone(event, "SOIL_PROFILE_CONFIRMED event must be logged in FarmEvent table")

    # 25. Crop stage fertilizer recommendation guardrail preserved with confirmed soil
    def test_25_crop_stage_fertilizer_guardrail_preserved_with_confirmed_soil(self):
        # When a crop is in reproductive stage (e.g. Flowering / Grain Filling),
        # even with confirmed soil health card, granular chemical fertilizer broadcasting must be CEASED.
        farm_soil_profile = {
            "provenance": "SOIL_HEALTH_CARD",
            "ph": 7.0,
            "nitrogen": 150.0,  # Low nitrogen
            "phosphorus": 15.0,
            "potassium": 180.0,
            "organic_carbon": 0.5,
            "field_sources_json": {},
        }
        intel = get_soil_intelligence(
            crop="Wheat",
            crop_stage="Grain Filling",
            farm_soil_profile=farm_soil_profile,
        )
        recs_text = " ".join(intel["recommendations"]).lower()

        self.assertTrue(
            "cease" in recs_text or "do not apply" in recs_text,
            "Late stage constraint must cease granular fertilizer broadcasting even with confirmed card"
        )


if __name__ == '__main__':
    unittest.main()
