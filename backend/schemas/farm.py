from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class FarmOnboardRequest(BaseModel):
    farmer_name: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    district: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    crop: str = Field(..., min_length=1)
    crop_variety: str = ""
    sowing_date: str = Field(..., min_length=1)
    farm_area_acres: float = Field(..., gt=0)
    soil_data_available: bool = False
    phone: str = ""

class FarmResponse(BaseModel):
    farm_id: str
    farmer_name: str
    crop: str
    crop_variety: str
    location: str
    district: str
    state: str
    sowing_date: str
    farm_area_acres: float
    days_after_sowing: int
    crop_stage: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    created_at: str

class IntelligenceRequest(BaseModel):
    farm_id: str

class PricePredictionRequest(BaseModel):
    commodity: str
    market: str
    state: str
    horizon_days: int = 7

class ExpertRequest(BaseModel):
    farm_id: str
    question: str

class FarmUpdateRequest(BaseModel):
    farmer_name: Optional[str] = None
    location: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    crop: Optional[str] = None
    crop_variety: Optional[str] = None
    sowing_date: Optional[str] = None
    farm_area_acres: Optional[float] = None
    soil_data_available: Optional[bool] = None
    phone: Optional[str] = None

class FarmEventResponse(BaseModel):
    id: str
    farm_id: str
    event_type: str
    timestamp: str
    title: str
    description: Optional[str] = None
    source: str = "SYSTEM"

class DigitalTwinFarmer(BaseModel):
    name: str
    phone: Optional[str] = ""

class DigitalTwinFarm(BaseModel):
    state: str
    district: str
    location: str
    acreage: float
    soil_data_available: bool = False
    lat: Optional[float] = None
    lon: Optional[float] = None

class DigitalTwinCrop(BaseModel):
    name: str
    variety: Optional[str] = ""
    sowing_date: str
    stage: str
    days_after_sowing: int

class DigitalTwinMetadata(BaseModel):
    created_at: str
    updated_at: str

class DigitalTwinResponse(BaseModel):
    farm_id: str
    farmer: DigitalTwinFarmer
    farm: DigitalTwinFarm
    crop: DigitalTwinCrop
    metadata: DigitalTwinMetadata
    intelligence: Dict[str, Any]
    data_provenance: Dict[str, str]
    events: List[FarmEventResponse] = []
    decision_history: List[Dict[str, Any]] = []
