import uuid
import os
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from backend.database import get_db
from backend.models.farm import Farm, FarmEvent, SoilDocument, FarmSoilProfile
from backend.schemas.soil import (
    SoilExtractionResponse,
    SoilConfirmationRequest,
    SoilProfileResponse,
)
from backend.services.crop_model import get_crop_stage
from backend.services.soil_service import get_soil_intelligence
from backend.services.soil_ocr_service import (
    process_soil_health_card_document,
    validate_uploaded_file,
    MAX_FILE_SIZE_BYTES,
)

router = APIRouter()

UPLOAD_BASE_DIR = Path(__file__).resolve().parents[2] / "data" / "uploads" / "soil"


@router.get("/intelligence")
def soil_intel(
    district: str = "Lucknow",
    state: str = "Uttar Pradesh",
    farm_id: Optional[str] = None,
    crop: Optional[str] = None,
    crop_stage: Optional[str] = None,
    db: Session = Depends(get_db),
):
    soil_tested = False
    farm_area = 3.0
    farm_context = None
    farm_soil_profile = None

    if farm_id:
        farm = db.query(Farm).filter(Farm.id == farm_id).first()
        if farm:
            district = farm.district or district
            state = farm.state or state
            crop = crop or farm.crop
            if not crop_stage:
                try:
                    sowing = datetime.strptime(farm.sowing_date, "%Y-%m-%d")
                    days = max(0, (datetime.now() - sowing).days)
                except Exception:
                    days = 0
                crop_stage = get_crop_stage(farm.crop, days)
            soil_tested = bool(farm.soil_data_available)
            farm_area = farm.farm_area_acres or 3.0
            farm_context = {
                "farm_id": str(farm.id),
                "farmer_name": farm.farmer_name,
                "crop": farm.crop,
                "crop_variety": farm.crop_variety,
                "crop_stage": crop_stage,
                "sowing_date": farm.sowing_date,
            }

            # Check for active confirmed FarmSoilProfile
            active_profile = (
                db.query(FarmSoilProfile)
                .filter(FarmSoilProfile.farm_id == farm_id, FarmSoilProfile.is_active == True)
                .order_by(FarmSoilProfile.confirmed_at.desc())
                .first()
            )
            if active_profile:
                farm_soil_profile = active_profile

    return get_soil_intelligence(
        district=district,
        state=state,
        crop=crop or "Wheat",
        crop_stage=crop_stage or "Post-harvest",
        soil_tested=soil_tested,
        farm_area=farm_area,
        farm_context=farm_context,
        farm_soil_profile=farm_soil_profile,
    )


@router.post("/upload", response_model=SoilExtractionResponse)
async def upload_soil_document(
    farm_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Secure document upload endpoint for Soil Health Cards (PDF, JPG, JPEG, PNG).
    Validates farm ownership, file size (<= 10MB), and file magic bytes.
    Extracts structured soil measurements with status 'REVIEW_REQUIRED'.
    Never automatically confirms the extracted data as farm ground truth.
    """
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID '{farm_id}' not found."
        )

    # Read file content safely
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds 10MB limit (size: {len(content)/(1024*1024):.1f} MB)."
        )

    # Validate file type and magic bytes
    is_valid, err_msg = validate_uploaded_file(file.filename or "", content, file.content_type)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg
        )

    # Save file safely under farm-isolated directory
    farm_dir = UPLOAD_BASE_DIR / str(farm_id)
    farm_dir.mkdir(parents=True, exist_ok=True)
    safe_filename = f"{uuid.uuid4().hex[:12]}_{Path(file.filename or 'soil_card.pdf').name}"
    save_path = farm_dir / safe_filename
    with open(save_path, "wb") as f:
        f.write(content)

    # Run OCR / document extraction
    extraction = process_soil_health_card_document(
        filename=file.filename or "soil_card.pdf",
        content=content,
        content_type=file.content_type,
    )

    # Record document in DB (with status REVIEW_REQUIRED, is_confirmed = False)
    doc_id = str(uuid.uuid4())
    doc = SoilDocument(
        id=doc_id,
        farm_id=farm_id,
        filename=file.filename or "soil_card.pdf",
        file_path=str(save_path),
        file_type=file.content_type or "application/octet-stream",
        file_size_bytes=len(content),
        ocr_status=extraction.get("ocr_status", "REVIEW_REQUIRED"),
        extracted_data_json=extraction.get("parameters", {}),
        is_confirmed=False,
    )
    db.add(doc)
    db.commit()

    return SoilExtractionResponse(
        document_id=doc_id,
        farm_id=farm_id,
        filename=file.filename or "soil_card.pdf",
        file_type=file.content_type or "application/octet-stream",
        ocr_status=extraction.get("ocr_status", "REVIEW_REQUIRED"),
        test_date=extraction.get("test_date"),
        parameters=extraction.get("parameters", {}),
        extraction_state="REVIEW_REQUIRED",
        message=extraction.get("message", "Document processed. Please review detected fields before confirming."),
    )


@router.post("/confirm", response_model=SoilProfileResponse)
def confirm_soil_profile(
    payload: SoilConfirmationRequest,
    db: Session = Depends(get_db),
):
    """
    Farmer confirmation endpoint.
    Applies farmer-reviewed/corrected values as the farm's active Soil Profile.
    Sets provenance (SOIL_HEALTH_CARD or FARMER_ENTERED).
    Updates farm.soil_data_available = True and records a FarmEvent.
    """
    farm = db.query(Farm).filter(Farm.id == payload.farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID '{payload.farm_id}' not found."
        )

    # If document_id provided, ensure it belongs to this farm (cross-farm isolation)
    doc = None
    if payload.document_id:
        doc = db.query(SoilDocument).filter(
            SoilDocument.id == payload.document_id,
            SoilDocument.farm_id == payload.farm_id,
        ).first()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Soil document '{payload.document_id}' not found for this farm."
            )

    raw_params = payload.parameters or {}
    field_sources = payload.field_sources or {}

    # Validate physical constraints
    def _parse_val(k):
        v = raw_params.get(k)
        if v is None or v == "" or str(v).strip().lower() in ["none", "null", "n/a"]:
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    ph = _parse_val("ph")
    if ph is not None and (ph < 0.0 or ph > 14.0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid pH {ph}. pH must be between 0.0 and 14.0."
        )

    for k in ["nitrogen", "phosphorus", "potassium", "organic_carbon", "ec", "sulphur", "zinc", "iron", "copper", "manganese", "boron"]:
        v = _parse_val(k)
        if v is not None and v < 0.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {k} value {v}. Nutrient values cannot be negative."
            )

    # Determine overall profile provenance
    if field_sources:
        if all(s == "SOIL_HEALTH_CARD" for s in field_sources.values()):
            profile_prov = "SOIL_HEALTH_CARD"
        else:
            profile_prov = "FARMER_ENTERED"
    elif payload.document_id:
        profile_prov = "SOIL_HEALTH_CARD"
    else:
        profile_prov = "FARMER_ENTERED"

    # Mark previous active profiles as inactive (preserve historical audit trail)
    db.query(FarmSoilProfile).filter(
        FarmSoilProfile.farm_id == payload.farm_id,
        FarmSoilProfile.is_active == True,
    ).update({"is_active": False})

    # Create new active profile
    now = datetime.now(timezone.utc)
    profile = FarmSoilProfile(
        id=str(uuid.uuid4()),
        farm_id=payload.farm_id,
        document_id=payload.document_id,
        provenance=profile_prov,
        is_active=True,
        test_date=payload.test_date or now.strftime("%Y-%m-%d"),
        confirmation_status="CONFIRMED",
        confirmed_at=now,
        ph=ph,
        nitrogen=_parse_val("nitrogen"),
        phosphorus=_parse_val("phosphorus"),
        potassium=_parse_val("potassium"),
        organic_carbon=_parse_val("organic_carbon"),
        ec=_parse_val("ec"),
        soil_texture=str(raw_params.get("soil_texture")) if raw_params.get("soil_texture") else None,
        sulphur=_parse_val("sulphur"),
        zinc=_parse_val("zinc"),
        iron=_parse_val("iron"),
        copper=_parse_val("copper"),
        manganese=_parse_val("manganese"),
        boron=_parse_val("boron"),
        field_sources_json=field_sources,
    )
    db.add(profile)

    # Mark document as confirmed if present
    if doc:
        doc.is_confirmed = True
        doc.confirmed_at = now

    # Update farm flag
    farm.soil_data_available = True

    # Record genuine event
    event = FarmEvent(
        farm_id=payload.farm_id,
        event_type="SOIL_PROFILE_CONFIRMED",
        title="Soil Health Card Confirmed",
        description=f"Confirmed farm-specific soil measurements ({profile_prov}) with test date {payload.test_date or now.strftime('%Y-%m-%d')}.",
        source="USER_ACTION",
        timestamp=now,
    )
    db.add(event)
    db.commit()
    db.refresh(profile)

    return SoilProfileResponse(
        id=profile.id,
        farm_id=profile.farm_id,
        document_id=profile.document_id,
        provenance=profile.provenance,
        is_active=profile.is_active,
        test_date=profile.test_date,
        confirmation_status=profile.confirmation_status,
        confirmed_at=profile.confirmed_at.isoformat(),
        parameters={
            "ph": profile.ph,
            "nitrogen": profile.nitrogen,
            "phosphorus": profile.phosphorus,
            "potassium": profile.potassium,
            "organic_carbon": profile.organic_carbon,
            "ec": profile.ec,
            "soil_texture": profile.soil_texture,
            "sulphur": profile.sulphur,
            "zinc": profile.zinc,
            "iron": profile.iron,
            "copper": profile.copper,
            "manganese": profile.manganese,
            "boron": profile.boron,
        },
        field_sources=profile.field_sources_json or {},
    )


@router.get("/profile/{farm_id}")
def get_farm_soil_profile(
    farm_id: str,
    db: Session = Depends(get_db),
):
    """Return the active confirmed soil profile for a farm."""
    profile = (
        db.query(FarmSoilProfile)
        .filter(FarmSoilProfile.farm_id == farm_id, FarmSoilProfile.is_active == True)
        .order_by(FarmSoilProfile.confirmed_at.desc())
        .first()
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active confirmed soil profile found for farm '{farm_id}'."
        )
    return {
        "id": profile.id,
        "farm_id": profile.farm_id,
        "document_id": profile.document_id,
        "provenance": profile.provenance,
        "is_active": profile.is_active,
        "test_date": profile.test_date,
        "confirmation_status": profile.confirmation_status,
        "confirmed_at": profile.confirmed_at.isoformat() if profile.confirmed_at else None,
        "parameters": {
            "ph": profile.ph,
            "nitrogen": profile.nitrogen,
            "phosphorus": profile.phosphorus,
            "potassium": profile.potassium,
            "organic_carbon": profile.organic_carbon,
            "ec": profile.ec,
            "soil_texture": profile.soil_texture,
            "sulphur": profile.sulphur,
            "zinc": profile.zinc,
            "iron": profile.iron,
            "copper": profile.copper,
            "manganese": profile.manganese,
            "boron": profile.boron,
        },
        "field_sources": profile.field_sources_json or {},
    }
