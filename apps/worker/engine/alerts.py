from sqlalchemy.orm import Session
from apps.api.app import models
from datetime import datetime
import json

class AlertManager:
    def __init__(self, db: Session):
        self.db = db
        # We'll import inside to avoid circular deps if they arise
        from apps.worker.engine.advisory import AdvisoryEngine
        self.advisory_engine = AdvisoryEngine(db)

    def create_alert(self, org_id: int, severity: models.RiskSeverity, title: str, message: str, entity_type: str, entity_id: int):
        alert = models.Alert(
            org_id=org_id,
            severity=severity,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id
        )
        self.db.add(alert)
        self.db.flush() # Get the ID
        
        # Attach AI advisory
        self.advisory_engine.attach_advisory_to_alert(alert.id)
        
        self.db.commit()
        
        # In a real app, this is where we'd trigger an email task
        print(f"ALERT CREATED: {title} for Org {org_id}")

    def check_score_change(self, entity_type: str, entity_id: int, old_score: int, new_score: int, status: models.RiskSeverity):
        # Trigger alert if score jumps significantly or crosses threshold
        if new_score >= 80 and old_score < 80:
            # Finding orgs that watch this entity
            watchlists = self.db.query(models.Watchlist).filter_by(
                entity_type=entity_type, entity_id=entity_id
            ).all()
            
            for watch in watchlists:
                self.create_alert(
                    org_id=watch.org_id,
                    severity=status,
                    title=f"Critical Risk: {entity_type.capitalize()} #{entity_id}",
                    message=f"The risk score for this {entity_type} has reached {new_score}.",
                    entity_type=entity_type,
                    entity_id=entity_id
                )
