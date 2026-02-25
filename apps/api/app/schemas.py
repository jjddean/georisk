from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import RiskSeverity

class PortBase(BaseModel):
    name: str
    unlocode: str
    country: str
    latitude: float
    longitude: float

class Port(PortBase):
    id: int
    class Config:
        from_attributes = True

class LaneBase(BaseModel):
    origin_port_id: int
    destination_port_id: int
    mode: str

class Lane(LaneBase):
    id: int
    origin_port: Port
    destination_port: Port
    class Config:
        from_attributes = True

class RiskEventBase(BaseModel):
    event_type: str
    severity: RiskSeverity
    source: str
    external_id: str
    title: str
    description: str
    confidence_score: float = 1.0
    impact_geometry: Optional[Dict] = None
    impacted_entities: List[Dict]
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None

class RiskEvent(RiskEventBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class RiskScoreBase(BaseModel):
    entity_type: str
    entity_id: int
    score: int
    status: RiskSeverity
    breakdown: Dict[str, Any]
    scoring_version: str = "v1.1"
    dataset_snapshot_id: Optional[str] = None

class RiskScore(RiskScoreBase):
    id: int
    updated_at: datetime
    class Config:
        from_attributes = True

class OrganizationBase(BaseModel):
    name: str

class Organization(OrganizationBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    org_id: int

class User(UserBase):
    id: int
    org_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    org_id: int
    severity: RiskSeverity
    title: str
    message: str
    entity_type: str
    entity_id: int

class Alert(AlertBase):
    id: int
    is_read: int
    created_at: datetime
    class Config:
        from_attributes = True

