from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from apps.api.app import models

class BaseFeed(ABC):
    @abstractmethod
    def fetch(self) -> List[dict]:
        """Fetch raw data from the source."""
        pass

    @abstractmethod
    def normalize(self, raw_data: dict) -> models.RiskEvent:
        """Normalize raw data into a RiskEvent model."""
        pass

    def ingest(self, db: Session):
        raw_items = self.fetch()
        new_events = []
        for item in raw_items:
            event = self.normalize(item)
            # Basic deduplication by external_id
            existing = db.query(models.RiskEvent).filter_by(
                external_id=event.external_id, 
                source=event.source
            ).first()
            
            if not existing:
                db.add(event)
                new_events.append(event)
        
        db.commit()
        return new_events
