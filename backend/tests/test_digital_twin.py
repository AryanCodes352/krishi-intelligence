import unittest
import time
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models.farm import Farm, FarmEvent

client = TestClient(app)

class TestFarmDigitalTwin(unittest.TestCase):
    """
    Test suite for FEATURE 1: FARM DIGITAL TWIN.
    Covers the 9 specified testing scenarios:
    1. Digital Twin creation/retrieval
    2. Existing farm can be retrieved
    3. Invalid farm ID (404)
    4. Missing optional farm data
    5. Unsupported crop behavior
    6. Provenance is preserved
    7. Existing intelligence remains accessible
    8. Update timestamp changes after a genuine update
    9. No fake values are generated
    """

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def _create_wheat_farm(self, farmer_name="Aryan Sharma", acreage=10.0) -> str:
        res = client.post("/api/farm/onboard", json={
            "farmer_name": farmer_name,
            "location": "Malihabad",
            "district": "Lucknow",
            "state": "Uttar Pradesh",
            "crop": "Wheat",
            "crop_variety": "HD-2967",
            "sowing_date": "2025-11-15",
            "farm_area_acres": acreage,
            "soil_data_available": False,
            "phone": "9876543210",
        })
        self.assertEqual(res.status_code, 200)
        return res.json()["farm_id"]

    # ── Test 1: Digital Twin creation/retrieval ──────────────────────────────
    def test_digital_twin_creation_and_retrieval(self):
        farm_id = self._create_wheat_farm("Rajesh Singh", 5.5)
        res = client.get(f"/api/farm/{farm_id}/digital-twin")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Verify root identity
        self.assertEqual(data["farm_id"], farm_id)
        self.assertEqual(data["farmer"]["name"], "Rajesh Singh")
        self.assertEqual(data["farm"]["acreage"], 5.5)
        self.assertEqual(data["farm"]["district"], "Lucknow")
        self.assertEqual(data["farm"]["state"], "Uttar Pradesh")
        self.assertEqual(data["crop"]["name"], "Wheat")
        self.assertEqual(data["crop"]["variety"], "HD-2967")
        self.assertIn("stage", data["crop"])
        self.assertIn("days_after_sowing", data["crop"])

        # Verify event was logged on creation
        self.assertTrue(len(data["events"]) >= 1)
        self.assertEqual(data["events"][-1]["event_type"], "FARM_CREATED")

    # ── Test 2: Existing farm can be retrieved ───────────────────────────────
    def test_existing_farm_can_be_retrieved(self):
        farm_id = self._create_wheat_farm("Vikas Patel", 12.0)
        res = client.get(f"/api/farm/{farm_id}/digital-twin")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["farmer"]["name"], "Vikas Patel")
        self.assertEqual(data["farm"]["acreage"], 12.0)

    # ── Test 3: Invalid farm ID ──────────────────────────────────────────────
    def test_invalid_farm_id_returns_404(self):
        res = client.get("/api/farm/non-existent-farm-uuid-9999/digital-twin")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json()["detail"], "Farm not found")

    # ── Test 4: Missing optional farm data ────────────────────────────────────
    def test_missing_optional_farm_data_handled_gracefully(self):
        # Insert a farm directly in DB with nullable optional fields
        bare_farm = Farm(
            farmer_name="Farmer Without Optional Data",
            location="Unknown Village",
            district="Lucknow",
            state="Uttar Pradesh",
            crop="Wheat",
            crop_variety="",
            sowing_date="2025-11-15",
            farm_area_acres=2.0,
            soil_data_available=False,
            phone="",
            lat=None,
            lon=None,
        )
        self.db.add(bare_farm)
        self.db.commit()
        self.db.refresh(bare_farm)

        res = client.get(f"/api/farm/{bare_farm.id}/digital-twin")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["farmer"]["name"], "Farmer Without Optional Data")
        self.assertEqual(data["farmer"]["phone"], "")
        self.assertEqual(data["crop"]["variety"], "")
        # Should not crash on null lat/lon - default fallback coordinates used
        self.assertIn("weather", data["intelligence"])

    # ── Test 5: Unsupported crop behavior ─────────────────────────────────────
    def test_unsupported_crop_behavior(self):
        # Insert a farm with an unsupported crop directly in DB
        rice_farm = Farm(
            farmer_name="Anil Kumar",
            location="Barabanki",
            district="Barabanki",
            state="Uttar Pradesh",
            crop="Rice",
            crop_variety="",
            sowing_date="2025-07-01",
            farm_area_acres=4.0,
            soil_data_available=False,
            lat=26.9,
            lon=81.2,
        )
        self.db.add(rice_farm)
        self.db.commit()
        self.db.refresh(rice_farm)

        res = client.get(f"/api/farm/{rice_farm.id}/digital-twin")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # Crop verification
        self.assertEqual(data["crop"]["name"], "Rice")
        self.assertNotEqual(data["crop"]["variety"], "HD-2967")  # Never attach wheat variety

        # Market verification: must be clearly MARKET_UNSUPPORTED
        market_intel = data["intelligence"]["market"]
        self.assertIsNone(market_intel.get("current"))
        self.assertEqual(market_intel.get("data_source", {}).get("type"), "MARKET_UNSUPPORTED")

        # Prediction verification: must be insufficient_data with MARKET_UNSUPPORTED
        pred = data["intelligence"]["prediction"]
        self.assertTrue(pred.get("insufficient_data"))
        self.assertIn(pred.get("data_type"), ["MARKET_UNSUPPORTED", "DATA_UNAVAILABLE"])

        # Decision verification: action must be MARKET_UNAVAILABLE
        decision = data["intelligence"]["decision"]
        self.assertEqual(decision["recommendation"]["action"], "MARKET_UNAVAILABLE")

        # Provenance verification
        prov = data["data_provenance"]
        self.assertEqual(prov["market"], "MARKET_UNSUPPORTED")
        self.assertEqual(prov["prediction"], "MARKET_UNSUPPORTED")
        self.assertEqual(prov["decision"], "MARKET_UNAVAILABLE")

    # ── Test 6: Provenance is preserved ──────────────────────────────────────
    def test_provenance_is_strictly_preserved(self):
        farm_id = self._create_wheat_farm("Suresh Verma", 8.0)
        res = client.get(f"/api/farm/{farm_id}/digital-twin")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        prov = data["data_provenance"]

        self.assertEqual(prov["farmer_profile"], "USER_ONBOARDED")
        self.assertIn(prov["weather"], ["LIVE", "UNAVAILABLE"])
        self.assertEqual(prov["soil"], "REGIONAL_ESTIMATE")
        self.assertEqual(prov["market"], "HISTORICAL_SEED")
        self.assertEqual(prov["prediction"], "MODEL_PREDICTION")
        self.assertEqual(prov["decision"], "CALCULATED")

    # ── Test 7: Existing intelligence remains accessible ──────────────────────
    def test_existing_intelligence_accessible(self):
        farm_id = self._create_wheat_farm("Amitabh Tiwari", 3.0)
        res = client.get(f"/api/farm/{farm_id}/digital-twin")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        intel = data["intelligence"]

        # Weather state exists
        self.assertIn("weather", intel)
        # Soil state exists
        self.assertIn("soil", intel)
        self.assertIn("parameters", intel["soil"])
        self.assertIn("crop_suitability", intel["soil"])
        # Market state exists
        self.assertIn("market", intel)
        self.assertIn("current", intel["market"])
        # Risk score exists
        self.assertIn("risk", intel)
        self.assertIn("overall_risk", intel["risk"])
        # Decision state exists
        self.assertIn("decision", intel)
        self.assertIn("recommendation", intel["decision"])

    # ── Test 8: Update timestamp changes after a genuine update ──────────────
    def test_update_timestamp_changes_after_genuine_update(self):
        farm_id = self._create_wheat_farm("Manish Gupta", 5.0)

        # First read
        res1 = client.get(f"/api/farm/{farm_id}/digital-twin")
        self.assertEqual(res1.status_code, 200)
        twin1 = res1.json()
        orig_updated_at = twin1["metadata"]["updated_at"]

        # Brief pause to ensure timestamp advances
        time.sleep(0.05)

        # Perform update
        update_res = client.put(f"/api/farm/{farm_id}", json={
            "farmer_name": "Manish Kumar Gupta",
            "farm_area_acres": 7.5,
            "location": "Kakori",
        })
        self.assertEqual(update_res.status_code, 200)
        updated_twin = update_res.json()

        # Check fields changed
        self.assertEqual(updated_twin["farmer"]["name"], "Manish Kumar Gupta")
        self.assertEqual(updated_twin["farm"]["acreage"], 7.5)
        self.assertEqual(updated_twin["farm"]["location"], "Kakori")

        # Check updated_at changed
        new_updated_at = updated_twin["metadata"]["updated_at"]
        self.assertNotEqual(orig_updated_at, new_updated_at)

        # Check genuine event logged
        events = updated_twin["events"]
        profile_update_events = [e for e in events if e["event_type"] == "PROFILE_UPDATED"]
        self.assertTrue(len(profile_update_events) >= 1)
        self.assertEqual(profile_update_events[0]["source"], "USER_ACTION")

    # ── Test 9: No fake values are generated ──────────────────────────────────
    def test_no_fake_values_generated_for_missing_or_unsupported_data(self):
        # For an unsupported crop, market price must NEVER default to Wheat MSP or fake numbers
        mustard_farm = Farm(
            farmer_name="Harish Chandra",
            location="Sitapur",
            district="Sitapur",
            state="Uttar Pradesh",
            crop="Mustard",
            crop_variety="",
            sowing_date="2025-10-15",
            farm_area_acres=3.0,
            soil_data_available=False,
            lat=27.5,
            lon=80.6,
        )
        self.db.add(mustard_farm)
        self.db.commit()
        self.db.refresh(mustard_farm)

        res = client.get(f"/api/farm/{mustard_farm.id}/digital-twin")
        self.assertEqual(res.status_code, 200)
        data = res.json()

        # No fake market modal price
        self.assertIsNone(data["intelligence"]["market"]["current"])
        # No fake price prediction
        self.assertTrue(data["intelligence"]["prediction"]["insufficient_data"])
        self.assertEqual(data["intelligence"]["prediction"]["current_price"], 0)
        # No fake wheat variety
        self.assertEqual(data["crop"]["variety"], "")


if __name__ == "__main__":
    unittest.main()
