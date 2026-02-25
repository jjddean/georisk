"""
Maritime Geopolitical Risk Dataset Manager - Postgres Version
============================================================
Consolidated version using Postgres as the single system of record.
"""

import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import math
from sqlalchemy.orm import Session
from apps.api.app import models

class MaritimeRiskManager:
    """
    Manages maritime geopolitical risk data for route planning.
    Standardized on Postgres as the System of Record.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def ingest_piracy_data(self, dataset_snapshot_id: str):
        """
        Download piracy incidents and normalize into RiskEvent schema.
        Includes evidence trails and confidence scoring.
        """
        # In V1, we simulate the feeds with robust metadata
        piracy_incidents = [
            {
                "external_id": "PI-2024-001",
                "event_type": "piracy",
                "severity": models.RiskSeverity.MEDIUM,
                "source": "IMB Piracy Reporting Centre",
                "source_url": "https://www.icc-ccs.org/piracy-reporting-centre",
                "title": "Armed Robbery - Malacca Strait",
                "description": "Attempted boarding of tanker while at anchor.",
                "confidence_score": 0.95,
                "impact_geometry": {"type": "Circle", "coordinates": [103.85, 1.25], "radius_km": 100},
                "impacted_entities": [{"type": "port", "name": "Singapore"}]
            }
        ]
        
        for p in piracy_incidents:
            event = models.RiskEvent(
                external_id=p["external_id"],
                event_type=p["event_type"],
                severity=p["severity"],
                source=p["source"],
                source_url=p["source_url"],
                title=p["title"],
                description=p["description"],
                confidence_score=p["confidence_score"],
                impact_geometry=p["impact_geometry"],
                impacted_entities=p["impacted_entities"],
                starts_at=datetime.now(),
                ends_at=datetime.now() + timedelta(days=7) # Active for 7 days
            )
            existing = self.db.query(models.RiskEvent).filter_by(external_id=p["external_id"]).first()
            if not existing:
                self.db.add(event)
        
        self.db.commit()

    def ingest_conflict_data(self, dataset_snapshot_id: str):
        """Download and normalize conflict data from ACLED."""
        conflicts = [
            {
                "external_id": "ACLED-2024-001",
                "event_type": "conflict",
                "severity": models.RiskSeverity.HIGH,
                "source": "ACLED",
                "source_url": "https://acleddata.com/data/",
                "title": "Coastal Conflict - Yemen",
                "description": "Armed clash near Hodeidah port infrastructure.",
                "confidence_score": 0.85,
                "impact_geometry": {"type": "Polygon", "coordinates": [[[43, 14], [45, 14], [45, 16], [43, 16], [43, 14]]]},
                "impacted_entities": [{"type": "chokepoint", "name": "Bab-el-Mandeb"}]
            }
        ]
        
        for c in conflicts:
            event = models.RiskEvent(
                external_id=c["external_id"],
                event_type=c["event_type"],
                severity=c["severity"],
                source=c["source"],
                source_url=c["source_url"],
                title=c["title"],
                description=c["description"],
                confidence_score=c["confidence_score"],
                impact_geometry=c["impact_geometry"],
                impacted_entities=c["impacted_entities"],
                starts_at=datetime.now(),
                ends_at=datetime.now() + timedelta(days=14)
            )
            existing = self.db.query(models.RiskEvent).filter_by(external_id=c["external_id"]).first()
            if not existing:
                self.db.add(event)
        
        self.db.commit()

    def assess_route_risk(self, lane_id: int, snapshot_id: str) -> Dict:
        """
        Assess risk for a given lane using Postgres intersection logic.
        """
        lane = self.db.query(models.Lane).get(lane_id)
        if not lane: return {"error": "Lane not found"}
        
        active_events = self.db.query(models.RiskEvent).filter(
            models.RiskEvent.ends_at >= datetime.now()
        ).all()
        
        score = 0
        evidence_trail = []
        
        for event in active_events:
            is_intersecting = False
            for impact in event.impacted_entities:
                if impact["type"] == "port" and impact.get("name") in [lane.origin_port.name, lane.destination_port.name]:
                    is_intersecting = True
            
            if is_intersecting:
                impact_points = {
                    models.RiskSeverity.SEVERE: 50,
                    models.RiskSeverity.HIGH: 30,
                    models.RiskSeverity.MEDIUM: 15,
                    models.RiskSeverity.LOW: 5
                }.get(event.severity, 0)
                
                score += impact_points
                evidence_trail.append({
                    "event_id": event.external_id,
                    "title": event.title,
                    "source": event.source,
                    "confidence": event.confidence_score,
                    "impact": event.event_type
                })

        score = min(score, 100)
        status = self._classify_status(score)
        
        return {
            "score": score,
            "status": status,
            "evidence": evidence_trail,
            "snapshot_id": snapshot_id,
            "version": "v1.1-postgres"
        }

    def _classify_status(self, score: int) -> models.RiskSeverity:
        if score >= 80: return models.RiskSeverity.SEVERE
        if score >= 60: return models.RiskSeverity.HIGH
        if score >= 30: return models.RiskSeverity.MEDIUM
        return models.RiskSeverity.LOW
