from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class SoilFieldItem(BaseModel):
    value: Optional[float] = None
    unit: str = ""
    status: str = "EXTRACTED"  # EXTRACTED, NOT_DETECTED, INVALID
    source: str = "SOIL_HEALTH_CARD"  # SOIL_HEALTH_CARD, FARMER_ENTERED
    valid: bool = True
    note: Optional[str] = None


class SoilExtractionResponse(BaseModel):
    document_id: str
    farm_id: str
    filename: str
    file_type: str
    ocr_status: str  # SUCCESS, PARTIAL_EXTRACTION, OCR_FAILED
    test_date: Optional[str] = None
    parameters: Dict[str, Any]
    extraction_state: str = "REVIEW_REQUIRED"
    message: str


class SoilConfirmationRequest(BaseModel):
    farm_id: str
    document_id: Optional[str] = None
    test_date: Optional[str] = None
    parameters: Dict[str, Any]
    field_sources: Optional[Dict[str, str]] = None


class SoilProfileResponse(BaseModel):
    id: str
    farm_id: str
    document_id: Optional[str] = None
    provenance: str
    is_active: bool
    test_date: Optional[str] = None
    confirmation_status: str
    confirmed_at: str
    parameters: Dict[str, Any]
    field_sources: Dict[str, str] = Field(default_factory=dict)
