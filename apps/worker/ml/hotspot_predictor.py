"""
GeoRisk Pro — Hotspot Predictor
Identifies "Risk Hotspots" by analyzing event accumulation (clusters of events).
Calculates intensity based on weighted event counts in specific regions/ports.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from apps.api.app import models
from sqlalchemy.orm import Session
from sqlalchemy import func

class HotspotPredictor:
    def __init__(self, db: Session):
        self.db = db

    def calculate_accumulation(self, port_name: str, lookback_hours: int = 72) -> Dict[str, Any]:
        """
        Calculates event accumulation for a specific port.
        Looks for events affecting this port in the last X hours.
        """
        since = datetime.utcnow() - timedelta(hours=lookback_hours)
        
        # This is a bit tricky with JSON storage for impacted_entities
        # In a real production app, we'd have a join table or Gin index.
        # For our "no-bloat" worker, we'll scan recent events.
        
        all_recent_events = self.db.query(models.RiskEvent).filter(
            models.RiskEvent.starts_at >= since
        ).all()
        
        impacting_events = []
        total_weight = 0.0
        
        for event in all_recent_events:
            for impact in event.impacted_entities:
                if impact.get("type") == "port" and impact.get("name") == port_name:
                    impacting_events.append(event)
                    
                    # Weighting based on severity
                    weight = {
                        models.RiskSeverity.SEVERE: 1.0,
                        models.RiskSeverity.HIGH: 0.7,
                        models.RiskSeverity.MEDIUM: 0.4,
                        models.RiskSeverity.LOW: 0.1
                    }.get(event.severity, 0.1)
                    
                    # Boost by confidence
                    total_weight += weight * (event.confidence_score or 0.5)
                    break
        
        count = len(impacting_events)
        
        # Intensity is a non-linear scale based on accumulation
        # 1-2 events = Low/Medium
        # 3+ events = High/Hotspot
        intensity = min(total_weight / 3.0, 1.0)
        
        return {
            "port_name": port_name,
            "event_count": count,
            "total_weight": round(total_weight, 2),
            "intensity": round(intensity, 2),
            "primary_drivers": [e.event_type for e in impacting_events[:3]]
        }

    def identify_all_hotspots(self, min_intensity: float = 0.3) -> List[Dict[str, Any]]:
        """
        Scans all ports in the database and identifies active hotspots.
        """
        # Get all unique port names currently in the Port table
        ports = self.db.query(models.Port.name).distinct().all()
        port_names = [p[0] for p in ports]
        
        hotspots = []
        for name in port_names:
            acc = self.calculate_accumulation(name)
            if acc["intensity"] >= min_intensity:
                hotspots.append(acc)
        
        # Sort by intensity
        hotspots.sort(key=lambda x: x["intensity"], reverse=True)
        return hotspots

    def get_hotspot_penalty(self, port_name: str) -> int:
        """
        Returns a score penalty (0-20) based on hotspot intensity.
        Used to boost Risk Scores when a port is under "compound stress".
        """
        acc = self.calculate_accumulation(port_name)
        if acc["intensity"] > 0.6:
            return 20
        elif acc["intensity"] > 0.4:
            return 12
        elif acc["intensity"] > 0.2:
            return 5
        return 0
