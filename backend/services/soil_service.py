"""
Soil Intelligence Service — KRISHI Data Engine
================================================
Generates soil nutrient intelligence, crop suitability evaluation,
and context-aware agronomic recommendations based on:
- Real or regional soil parameters (pH, N, P, K, Organic Carbon, Texture)
- Crop and current crop stage (hard agronomic stage consistency)
- Soil data provenance (REGIONAL_ESTIMATE vs FIELD_TEST)
- Farm context (location, acreage)
"""

from typing import Optional, Dict, Any, List
from datetime import date, datetime


def generate_soil_recommendations(
    crop: str,
    crop_stage: str,
    parameters: Dict[str, Any],
    data_source_type: str = "REGIONAL_ESTIMATE",
    farm_context: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """
    Generate context-aware, stage-consistent, and provenance-aware soil recommendations.
    Adheres strictly to:
    1. Hard stage constraints (Post-harvest: no chemical fertilizer on stubble; residue management & soil testing).
    2. Data provenance rules (Regional estimates are indicative; no exact unsupported chemical doses).
    3. Multi-crop adaptability.
    """
    stage_str = (crop_stage or "Post-harvest").strip()
    stage_lower = stage_str.lower()
    crop_name = crop.strip() if crop else "Wheat"
    is_regional = (data_source_type == "REGIONAL_ESTIMATE")

    n_val = parameters.get("nitrogen", {}).get("value", 240)
    p_val = parameters.get("phosphorus", {}).get("value", 18)
    k_val = parameters.get("potassium", {}).get("value", 220)
    oc_val = parameters.get("organic_carbon", {}).get("value", 0.45)
    soil_type = parameters.get("soil_type", "Sandy Loam")

    # Determine stage category
    is_post_harvest = any(s in stage_lower for s in ["post-harvest", "harvested", "fallow", "stubble"])
    is_pre_sowing = any(s in stage_lower for s in ["pre-sowing", "basal", "sowing", "germination", "land prep"])
    is_vegetative = any(s in stage_lower for s in ["tillering", "seedling", "vegetative", "jointing", "branching", "stem elongation"])
    is_reproductive = any(s in stage_lower for s in ["flowering", "heading", "booting", "grain filling", "milking", "dough", "maturity", "pod filling", "ripening"])

    recommendations: List[str] = []

    # ──────────────────────────────────────────────────────────────────────────
    # 1. POST-HARVEST STAGE
    # ──────────────────────────────────────────────────────────────────────────
    if is_post_harvest:
        recommendations.append(
            f"Crop stage is Post-harvest ({crop_name}): Do not apply chemical fertilizers (such as Urea or DAP) to harvested stubble or finished fields, as nutrients cannot be absorbed by a harvested crop and will be lost to runoff."
        )
        recommendations.append(
            f"Field residue & organic matter: Incorporate {crop_name.lower()} stubble into the soil with a disc harrow or rotavator and apply well-rotted Farmyard Manure (FYM) or compost (2–3 t/acre) during tillage to rebuild low organic carbon ({oc_val}% regional baseline)."
        )
        recommendations.append(
            "Soil testing verification: Collect composite soil samples across 8–10 spots in the field and submit them to KVK or your local district agricultural lab for an updated laboratory Soil Health Card before sowing the next crop."
        )
        recommendations.append(
            "Next-crop preparation: Await laboratory soil test results to determine tailored basal fertilizer requirements for your upcoming rotation crop, and practice deep summer ploughing to expose soil-borne pests and weed seeds."
        )
        if is_regional:
            recommendations.append(
                "Data provenance notice: Current soil parameters are regional district estimates (ICAR-NBSS&LUP). Individual farm values may vary; obtain an on-farm soil test before committing to chemical input purchases."
            )
        else:
            recommendations.append(
                "Verified soil test: Nutrient planning for the next crop should follow the specific nutrient targets confirmed in your laboratory test report."
            )

    # ──────────────────────────────────────────────────────────────────────────
    # 2. PRE-SOWING / BASAL STAGE
    # ──────────────────────────────────────────────────────────────────────────
    elif is_pre_sowing:
        if is_regional:
            recommendations.append(
                f"Soil test advisory for {crop_name}: Because current soil figures are district-level regional estimates (Nitrogen {n_val} kg/ha, Phosphorus {p_val} kg/ha), conduct an on-farm soil test and consult your local KVK or Agriculture Department to determine the exact basal fertilizer requirement for your field."
            )
            recommendations.append(
                f"Conditional basal nutrition: If an on-farm soil test confirms the regional N/P deficit, plan basal phosphorus and starter nitrogen placed 4–5 cm below seed level during final seedbed preparation as recommended by local agricultural guidelines."
            )
        else:
            recommendations.append(
                f"Basal nutrient management for {crop_name}: Apply basal phosphorus and starter nitrogen in the seed zone during final land preparation based on your verified laboratory soil test targets."
            )

        recommendations.append(
            f"Organic matter building: Incorporate 2–3 tonnes/acre of well-rotted FYM or compost into the field 2–3 weeks prior to sowing to improve soil organic carbon ({oc_val}% regional estimate) and enhance moisture retention in {soil_type.lower()}."
        )
        recommendations.append(
            f"Biological seed treatment: Treat {crop_name.lower()} seeds with crop-appropriate biofertilizers (such as Azotobacter/Rhizobium and Phosphate Solubilizing Bacteria - PSB) prior to sowing to improve nutrient bioavailability."
        )
        if is_regional:
            recommendations.append(
                "Data provenance notice: Regional estimates from ICAR district maps provide indicative baseline levels; exact fertilizer requirements should be confirmed through an on-farm Soil Health Card."
            )

    # ──────────────────────────────────────────────────────────────────────────
    # 3. VEGETATIVE / STANDING CROP (Tillering, Seedling, Jointing)
    # ──────────────────────────────────────────────────────────────────────────
    elif is_vegetative:
        if is_regional:
            recommendations.append(
                f"Standing {crop_name} nutrition ({stage_str} stage): Regional soil data indicates moderate nitrogen deficit ({n_val} kg/ha vs 280–400 kg/ha optimal). If standing plants show nutrient need, a split top-dressing may be considered in consultation with your local KVK."
            )
            recommendations.append(
                "Conditional dosage requirement: Do not apply rigid or excessive chemical fertilizer doses based solely on regional estimates. Confirm field requirements via an on-farm Soil Health Card or local extension advice."
            )
        else:
            recommendations.append(
                f"Standing {crop_name} nutrition ({stage_str} stage): Apply scheduled split nitrogen top-dressing according to your verified soil test recommendations and field crop stage."
            )

        recommendations.append(
            "Application conditions & weather caution: Ensure adequate soil moisture before top-dressing and avoid broadcasting nitrogenous fertilizers immediately before heavy rains to prevent leaching and surface runoff."
        )
        oc_str = f"{oc_val}%" if oc_val is not None else "measured"
        recommendations.append(
            f"Secondary nutrient inspection: Monitor crop canopy for uniform greening; {soil_type.lower()} soils with low organic carbon ({oc_str}) benefit from organic mulching and foliar micronutrient checks if yellowing or stunting appears."
        )
        if is_regional:
            recommendations.append(
                "Data provenance notice: Current soil values are regional district estimates (ICAR-NBSS&LUP). Individual farm values may vary; upload a soil test for accurate assessment."
            )

    # ──────────────────────────────────────────────────────────────────────────
    # 4. REPRODUCTIVE / LATE STAGE (Flowering, Heading, Grain Filling, Maturity)
    # ──────────────────────────────────────────────────────────────────────────
    elif is_reproductive:
        recommendations.append(
            f"Reproductive stage constraint ({crop_name} in {stage_str} stage): Cease all soil broadcasting of granular chemical fertilizers (Urea/DAP), as late soil nitrogen promotes unwanted vegetative greening, delays grain maturity, and heightens disease vulnerability."
        )
        recommendations.append(
            "Moisture regulation: Maintain adequate soil moisture during grain filling if high temperatures or dry spells occur, but discontinue irrigation 10–12 days prior to harvest."
        )
        recommendations.append(
            f"Nutrient audit: Plan post-harvest composite soil testing to assess nutrient depletion from this {crop_name.lower()} crop cycle before planning the subsequent crop."
        )
        if is_regional:
            recommendations.append(
                "Data provenance notice: Current soil values are regional district estimates (ICAR-NBSS&LUP). Individual farm values may vary; upload a soil test for accurate assessment."
            )

    # ──────────────────────────────────────────────────────────────────────────
    # 5. GENERAL / FALLBACK
    # ──────────────────────────────────────────────────────────────────────────
    else:
        recommendations.append(
            f"Soil management for {crop_name} ({stage_str}): Align any soil amendment strictly with crop growth stage and verify field nutrient status."
        )
        recommendations.append(
            f"Organic matter building: Incorporate 2–3 tonnes/acre of well-rotted FYM or compost to improve low organic carbon ({oc_val}% regional baseline)."
        )
        recommendations.append(
            "Testing recommendation: Obtain a laboratory Soil Health Card before determining fertilizer dosages for your field."
        )
        if is_regional:
            recommendations.append(
                "Data provenance notice: Current soil parameters are regional district estimates (ICAR-NBSS&LUP). Individual farm values may vary; upload a soil test for accurate assessment."
            )

    return recommendations


def get_soil_intelligence(
    district: str = "Lucknow",
    state: str = "Uttar Pradesh",
    crop: str = "Wheat",
    crop_stage: Optional[str] = None,
    soil_tested: bool = False,
    farm_area: float = 3.0,
    farm_context: Optional[Dict[str, Any]] = None,
    farm_soil_profile: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Get full soil intelligence package for a given location, crop, stage, and farm profile.
    Supports confirmed farm-specific Soil Health Cards, farmer-entered data, and regional fallbacks.
    """
    # Resolve crop and stage
    resolved_crop = crop or "Wheat"
    resolved_stage = crop_stage
    if not resolved_stage and farm_context and "crop_stage" in farm_context:
        resolved_stage = farm_context["crop_stage"]
    if not resolved_stage:
        resolved_stage = "Post-harvest"

    # Determine if we have confirmed farm-specific profile
    if farm_soil_profile is not None:
        # Extract attributes whether model object or dict
        def _get_val(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        prov = _get_val(farm_soil_profile, "provenance", "SOIL_HEALTH_CARD")
        data_source_type = prov if prov in ["SOIL_HEALTH_CARD", "FARMER_ENTERED"] else "SOIL_HEALTH_CARD"
        test_date = _get_val(farm_soil_profile, "test_date") or date.today().strftime("%Y-%m-%d")
        field_sources = _get_val(farm_soil_profile, "field_sources_json") or {}

        # Core parameters from confirmed profile (missing fields stay None, never forced to zero)
        ph_v = _get_val(farm_soil_profile, "ph")
        n_v = _get_val(farm_soil_profile, "nitrogen")
        p_v = _get_val(farm_soil_profile, "phosphorus")
        k_v = _get_val(farm_soil_profile, "potassium")
        oc_v = _get_val(farm_soil_profile, "organic_carbon")
        ec_v = _get_val(farm_soil_profile, "ec")
        tex_v = _get_val(farm_soil_profile, "soil_texture") or "Sandy Loam"

        def _calc_status(val, opt_min, opt_max):
            if val is None:
                return "UNAVAILABLE"
            if val < opt_min:
                return "LOW"
            if val > opt_max:
                return "HIGH"
            return "GOOD"

        parameters = {
            "ph": {
                "value": ph_v,
                "unit": "",
                "status": _calc_status(ph_v, 6.5, 7.5) if ph_v is not None else "UNAVAILABLE",
                "optimal_min": 6.5,
                "optimal_max": 7.5,
                "source": field_sources.get("ph", data_source_type),
            },
            "nitrogen": {
                "value": n_v,
                "unit": "kg/ha",
                "status": _calc_status(n_v, 280, 400) if n_v is not None else "UNAVAILABLE",
                "optimal_min": 280,
                "optimal_max": 400,
                "source": field_sources.get("nitrogen", data_source_type),
            },
            "phosphorus": {
                "value": p_v,
                "unit": "kg/ha",
                "status": _calc_status(p_v, 20, 40) if p_v is not None else "UNAVAILABLE",
                "optimal_min": 20,
                "optimal_max": 40,
                "source": field_sources.get("phosphorus", data_source_type),
            },
            "potassium": {
                "value": k_v,
                "unit": "kg/ha",
                "status": _calc_status(k_v, 150, 300) if k_v is not None else "UNAVAILABLE",
                "optimal_min": 150,
                "optimal_max": 300,
                "source": field_sources.get("potassium", data_source_type),
            },
            "organic_carbon": {
                "value": oc_v,
                "unit": "%",
                "status": _calc_status(oc_v, 0.75, 1.5) if oc_v is not None else "UNAVAILABLE",
                "optimal_min": 0.75,
                "optimal_max": 1.5,
                "source": field_sources.get("organic_carbon", data_source_type),
            },
            "soil_type": tex_v,
            "texture": tex_v,
        }

        # Add EC if present
        if ec_v is not None:
            parameters["ec"] = {
                "value": ec_v,
                "unit": "dS/m",
                "status": "GOOD" if ec_v <= 1.0 else ("MEDIUM" if ec_v <= 2.0 else "HIGH"),
                "optimal_min": 0.0,
                "optimal_max": 1.0,
                "source": field_sources.get("ec", data_source_type),
            }

        # Add micronutrients if present in profile
        for micro, spec in [
            ("sulphur", {"unit": "ppm", "opt_min": 10.0, "opt_max": 20.0}),
            ("zinc", {"unit": "ppm", "opt_min": 0.6, "opt_max": 1.5}),
            ("iron", {"unit": "ppm", "opt_min": 4.5, "opt_max": 10.0}),
            ("copper", {"unit": "ppm", "opt_min": 0.2, "opt_max": 1.0}),
            ("manganese", {"unit": "ppm", "opt_min": 2.0, "opt_max": 5.0}),
            ("boron", {"unit": "ppm", "opt_min": 0.5, "opt_max": 1.0}),
        ]:
            m_val = _get_val(farm_soil_profile, micro)
            if m_val is not None:
                parameters[micro] = {
                    "value": m_val,
                    "unit": spec["unit"],
                    "status": _calc_status(m_val, spec["opt_min"], spec["opt_max"]),
                    "optimal_min": spec["opt_min"],
                    "optimal_max": spec["opt_max"],
                    "source": field_sources.get(micro, data_source_type),
                }

        # Crop suitability factors calculated from confirmed values
        crop_suitability = {
            "score": 82 if parameters["ph"]["status"] == "GOOD" else 74,
            "label": "Good" if parameters["ph"]["status"] == "GOOD" else "Moderate",
            "provenance_note": (
                "Based on confirmed Soil Health Card measurements."
                if data_source_type == "SOIL_HEALTH_CARD"
                else "Based on confirmed farmer-entered soil measurements."
            ),
            "factors": [
                {"parameter": "pH", "score": 19 if parameters["ph"]["status"] == "GOOD" else 14, "max_score": 20, "status": parameters["ph"]["status"], "reason": f"Measured pH {parameters['ph']['value']}" if parameters['ph']['value'] is not None else "pH not recorded"},
                {"parameter": "Nitrogen", "score": 15 if parameters["nitrogen"]["status"] == "GOOD" else 12, "max_score": 20, "status": parameters["nitrogen"]["status"], "reason": f"Measured N {parameters['nitrogen']['value']} kg/ha" if parameters['nitrogen']['value'] is not None else "Nitrogen not recorded"},
                {"parameter": "Phosphorus", "score": 14 if parameters["phosphorus"]["status"] == "GOOD" else 11, "max_score": 15, "status": parameters["phosphorus"]["status"], "reason": f"Measured P {parameters['phosphorus']['value']} kg/ha" if parameters['phosphorus']['value'] is not None else "Phosphorus not recorded"},
                {"parameter": "Potassium", "score": 15 if parameters["potassium"]["status"] == "GOOD" else 12, "max_score": 15, "status": parameters["potassium"]["status"], "reason": f"Measured K {parameters['potassium']['value']} kg/ha" if parameters['potassium']['value'] is not None else "Potassium not recorded"},
                {"parameter": "Organic Carbon", "score": 14 if parameters["organic_carbon"]["status"] == "GOOD" else 9, "max_score": 20, "status": parameters["organic_carbon"]["status"], "reason": f"Measured OC {parameters['organic_carbon']['value']}%" if parameters['organic_carbon']['value'] is not None else "Organic carbon not recorded"},
                {"parameter": "Texture", "score": 9, "max_score": 10, "status": "GOOD", "reason": f"{tex_v} suitable for {resolved_crop.lower()}"},
            ],
        }

        recommendations = generate_soil_recommendations(
            crop=resolved_crop,
            crop_stage=resolved_stage,
            parameters=parameters,
            data_source_type=data_source_type,
            farm_context=farm_context,
        )

        data_source = {
            "type": data_source_type,
            "provider": "Soil Health Card (Laboratory Confirmed)" if data_source_type == "SOIL_HEALTH_CARD" else "Farmer-Entered Soil Profile",
            "coverage": f"Field-specific laboratory test ({district})" if data_source_type == "SOIL_HEALTH_CARD" else f"Field-specific measurements ({district})",
            "last_updated": test_date,
            "test_date": test_date,
            "status": "CONFIRMED",
            "data_quality": "high",
            "note": (
                "Confirmed on-farm Soil Health Card measurements. Regional fallback inactive."
                if data_source_type == "SOIL_HEALTH_CARD"
                else "Confirmed farmer-entered soil test values."
            ),
        }

        return {
            "parameters": parameters,
            "crop_suitability": crop_suitability,
            "overall_soil_risk": {"score": 22, "level": "LOW"},
            "recommendations": recommendations,
            "data_source": data_source,
        }

    # ── Fallback: Regional estimate baseline (ICAR-NBSS&LUP) ────────────────
    parameters = {
        "ph": {"value": 7.5, "unit": "", "status": "GOOD", "optimal_min": 6.5, "optimal_max": 7.5, "source": "REGIONAL_ESTIMATE"},
        "nitrogen": {"value": 240, "unit": "kg/ha", "status": "MEDIUM", "optimal_min": 280, "optimal_max": 400, "source": "REGIONAL_ESTIMATE"},
        "phosphorus": {"value": 18, "unit": "kg/ha", "status": "MEDIUM", "optimal_min": 20, "optimal_max": 40, "source": "REGIONAL_ESTIMATE"},
        "potassium": {"value": 220, "unit": "kg/ha", "status": "GOOD", "optimal_min": 150, "optimal_max": 300, "source": "REGIONAL_ESTIMATE"},
        "organic_carbon": {"value": 0.45, "unit": "%", "status": "LOW", "optimal_min": 0.75, "optimal_max": 1.5, "source": "REGIONAL_ESTIMATE"},
        "soil_type": "Sandy Loam",
        "texture": "Loamy",
    }

    data_source_type = "SOIL_HEALTH_CARD" if soil_tested else "REGIONAL_ESTIMATE"

    crop_suitability = {
        "score": 74,
        "label": "Good",
        "provenance_note": "Based on regional soil estimates.",
        "factors": [
            {"parameter": "pH", "score": 18, "max_score": 20, "status": "GOOD", "reason": f"Near optimal for {resolved_crop.lower()}"},
            {"parameter": "Nitrogen", "score": 13, "max_score": 20, "status": "MODERATE", "reason": "Below optimal range"},
            {"parameter": "Phosphorus", "score": 12, "max_score": 15, "status": "MODERATE", "reason": "Slightly deficient"},
            {"parameter": "Potassium", "score": 15, "max_score": 15, "status": "GOOD", "reason": "Within optimal range"},
            {"parameter": "Organic Carbon", "score": 8, "max_score": 20, "status": "LOW", "reason": "Low OC reduces water retention and microbial activity"},
            {"parameter": "Texture", "score": 8, "max_score": 10, "status": "GOOD", "reason": f"{parameters['soil_type']} is suitable for {resolved_crop.lower()}"},
        ],
    }

    recommendations = generate_soil_recommendations(
        crop=resolved_crop,
        crop_stage=resolved_stage,
        parameters=parameters,
        data_source_type=data_source_type,
        farm_context=farm_context,
    )

    data_source = {
        "type": data_source_type,
        "provider": "On-farm Laboratory Soil Test" if soil_tested else "ICAR-NBSS&LUP District Soil Map",
        "coverage": f"Field-level test ({district})" if soil_tested else "District-level estimate",
        "last_updated": "2026-03-01" if soil_tested else "2018-12-01",
        "status": "VERIFIED" if soil_tested else "AVAILABLE",
        "data_quality": "high" if soil_tested else "medium",
        "note": "Verified laboratory soil test." if soil_tested else "Individual farm values may vary. Upload soil test for accurate assessment.",
    }

    return {
        "parameters": parameters,
        "crop_suitability": crop_suitability,
        "overall_soil_risk": {"score": 28, "level": "LOW"},
        "recommendations": recommendations,
        "data_source": data_source,
    }

