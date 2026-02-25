from apps.worker.feeds.base import BaseFeed
from apps.api.app import models
from datetime import datetime, timedelta

class SanctionsFeed(BaseFeed):
    def fetch(self):
        # Simulate OFAC/UK sanctions updates
        return [
            {
                "id": "sanc-001",
                "type": "sanctions",
                "severity": "high",
                "title": "New Restricted Entity List - EU",
                "description": "European Union adds several maritime logistics entities to the restricted parties list.",
                "impacted": [{"type": "region", "name": "Russia"}, {"type": "port", "name": "St. Petersburg"}],
                "starts_at": datetime.now().isoformat(),
                "ends_at": (datetime.now() + timedelta(days=365)).isoformat(), # Longer horizon
            }
        ]

    def normalize(self, raw_data: dict) -> models.RiskEvent:
        from datetime import timedelta # Needed inside if not imported at top
        severity_map = {
            "low": models.RiskSeverity.LOW,
            "medium": models.RiskSeverity.MEDIUM,
            "high": models.RiskSeverity.HIGH,
            "severe": models.RiskSeverity.SEVERE,
        }
        return models.RiskEvent(
            event_type=raw_data["type"],
            severity=severity_map.get(raw_data["severity"], models.RiskSeverity.LOW),
            source="Official Sanctions Feed",
            external_id=raw_data["id"],
            title=raw_data["title"],
            description=raw_data["description"],
            impacted_entities=raw_data["impacted"],
            starts_at=datetime.fromisoformat(raw_data["starts_at"]),
            ends_at=datetime.fromisoformat(raw_data["ends_at"]),
        )
