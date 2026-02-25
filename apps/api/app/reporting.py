from sqlalchemy.orm import Session
from . import models
import json

class ReportingUtility:
    def __init__(self, db: Session):
        self.db = db

    def generate_lane_report(self, lane_id: int):
        lane = self.db.query(models.Lane).get(lane_id)
        if not lane:
            return None
            
        score = self.db.query(models.RiskScoreCurrent).filter_by(
            entity_type="lane", entity_id=lane_id
        ).first()
        
        # Fetch recent alerts for this lane
        alerts = self.db.query(models.Alert).filter_by(
            entity_type="lane", entity_id=lane_id
        ).order_by(models.Alert.created_at.desc()).limit(5).all()
        
        report_data = {
            "title": f"Risk Advisory Report: {lane.origin_port.name} to {lane.destination_port.name}",
            "lane_summary": {
                "origin": lane.origin_port.name,
                "destination": lane.destination_port.name,
                "mode": lane.mode,
                "current_risk": score.score if score else "N/A",
                "status": score.status.value if score else "Stable"
            },
            "recent_events": [],
            "recommendations": []
        }
        
        for alert in alerts:
            try:
                advisory = json.loads(alert.message)
                report_data["recent_events"].append({
                    "title": alert.title,
                    "date": alert.created_at.isoformat(),
                    "summary": advisory.get("what_happened", alert.message)
                })
                # Collect unique recommendations
                for rec in advisory.get("recommended_actions", []):
                    if rec not in report_data["recommendations"]:
                        report_data["recommendations"].append(rec)
            except:
                continue
                
        # In V1, we return this as JSON. 
        # In production, we'd pipe this into a PDF generator like ReportLab or WeasyPrint.
        return report_data
