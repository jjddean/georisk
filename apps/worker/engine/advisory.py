from sqlalchemy.orm import Session
from apps.api.app import models
import json

class AdvisoryEngine:
    def __init__(self, db: Session):
        self.db = db

    def generate_advisory(self, event: models.RiskEvent):
        """
        In a real app, this would call OpenAI/Anthropic to summarize the event
        and suggest actions based on the event type and severity.
        """
        # Simulated AI logic for V1
        what_happened = f"Significant {event.event_type} event detected: {event.title}."
        why_it_matters = f"This {event.severity.value} severity event directly impacts your monitored entities. {event.description}"
        
        recommendations = []
        alternatives = []
        
        if event.event_type == "weather":
            recommendations = [
                "Monitor berthing delays closely for the next 48-72 hours.",
                "Advise clients of a potential 2-4 day delay in arrival times.",
                "Review alternative loading windows for upcoming bookings."
            ]
            # Simple port substitution logic for V1
            for impact in event.impacted_entities:
                if impact["type"] == "port":
                    sub = self.get_alternative_port(impact["name"])
                    if sub:
                        alternatives.append(sub)

        elif event.event_type == "sanctions":
            recommendations = [
                "Immediate compliance review for all active bookings through this region.",
                "Check for any entity names matching the restricted list.",
                "Expect potential customs hold or cargo seizure if compliance is not verified."
            ]
            
        return {
            "what_happened": what_happened,
            "why_it_matters": why_it_matters,
            "recommended_actions": recommendations,
            "suggested_alternatives": alternatives
        }

    def get_alternative_port(self, port_name: str):
        # Hardcoded substitution rules for V1 demo
        mapping = {
            "Shanghai": {"name": "Ningbo", "delay": "Low", "cost": "Low", "risk": 20},
            "Rotterdam": {"name": "Antwerp", "delay": "Medium", "cost": "Low", "risk": 35},
            "Chittagong": {"name": "Kolkata", "delay": "High", "cost": "Medium", "risk": 45}
        }
        return mapping.get(port_name)

    def attach_advisory_to_alert(self, alert_id: int):
        alert = self.db.query(models.Alert).get(alert_id)
        if not alert:
            return
            
        # For simplicity in V1, we find the event that triggered this alert
        # In a real app, we'd have a mapping table
        event = self.db.query(models.RiskEvent).filter(
            models.RiskEvent.event_type == alert.entity_type # Simplification for V1 demo
        ).order_by(models.RiskEvent.created_at.desc()).first()
        
        if event:
            advisory = self.generate_advisory(event)
            # Update alert message with summary - removing 'AI' jargon in output
            alert.message = json.dumps(advisory)
            self.db.commit()

