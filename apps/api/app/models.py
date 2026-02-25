from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

class RiskSeverity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    SEVERE = "severe"

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="organization")
    watchlists = relationship("Watchlist", back_populates="organization")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="users")

class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    unlocode = Column(String, unique=True, index=True)
    country = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)

class Lane(Base):
    __tablename__ = "lanes"

    id = Column(Integer, primary_key=True, index=True)
    origin_port_id = Column(Integer, ForeignKey("ports.id"))
    destination_port_id = Column(Integer, ForeignKey("ports.id"))
    mode = Column(String)  # ocean, air

    origin_port = relationship("Port", foreign_keys=[origin_port_id])
    destination_port = relationship("Port", foreign_keys=[destination_port_id])

class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    entity_type = Column(String)  # lane, port, region
    entity_id = Column(Integer)  # ID of the lane, port, or region

    organization = relationship("Organization", back_populates="watchlists")

class RiskEvent(Base):
    __tablename__ = "risk_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)  # weather, strike, sanctions, piracy, conflict
    severity = Column(Enum(RiskSeverity))
    source = Column(String)  # e.g., "ACLED", "OFAC"
    external_id = Column(String, index=True)
    title = Column(String)
    description = Column(String)
    
    # --- EVIDENCE & AUDITABILITY ---
    confidence_score = Column(Float, default=1.0) # 0.0 to 1.0
    source_url = Column(String, nullable=True)
    freshened_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # --- GEOSPATIAL PRIMITIVES ---
    # For V1, we store geo-impact as a standardized JSON structure 
    # that can be indexed or converted to PostGIS later.
    impact_geometry = Column(JSON)  # {type: 'Polygon'|'Point'|'Circle', coordinates: [...], radius_km: float}
    
    impacted_entities = Column(JSON) 
    starts_at = Column(DateTime(timezone=True))
    ends_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RiskScoreCurrent(Base):
    __tablename__ = "risk_scores_current"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, index=True)
    entity_id = Column(Integer, index=True)
    score = Column(Integer)  # 0-100
    status = Column(Enum(RiskSeverity))
    breakdown = Column(JSON)
    
    # --- VERSIONING ---
    scoring_version = Column(String, default="v1.0")
    dataset_snapshot_id = Column(String) # e.g. "20260214_0430"
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class RiskScoreSnapshot(Base):
    __tablename__ = "risk_score_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, index=True)
    entity_id = Column(Integer, index=True)
    score = Column(Integer)
    breakdown = Column(JSON)
    scoring_version = Column(String)
    dataset_snapshot_id = Column(String)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    severity = Column(Enum(RiskSeverity))
    title = Column(String)
    message = Column(String)
    entity_type = Column(String)
    entity_id = Column(Integer)
    is_read = Column(Integer, default=0) # 0: unread, 1: read
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization")

