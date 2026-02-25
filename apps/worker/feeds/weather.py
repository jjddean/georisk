import httpx
from apps.worker.feeds.base import BaseFeed
from apps.api.app import models
from datetime import datetime, timedelta

class WeatherFeed(BaseFeed):
    def __init__(self, db_session=None):
        self.db = db_session

    def fetch(self):
        if not self.db:
            return []
            
        # Get all ports to check weather for them
        ports = self.db.query(models.Port).all()
        weather_events = []
        
        for port in ports:
            if not port.latitude or not port.longitude:
                continue
                
            url = f"https://api.open-meteo.com/v1/forecast?latitude={port.latitude}&longitude={port.longitude}&current=wind_speed_10m,weather_code&timezone=auto"
            
            try:
                with httpx.Client(timeout=5.0) as client:
                    res = client.get(url)
                    if res.status_code == 200:
                        data = res.json()
                        current = data.get("current", {})
                        
                        # Weather codes: 95, 96, 99 are thunderstorms. > 51 is significant rain/snow.
                        code = current.get("weather_code", 0)
                        wind = current.get("wind_speed_10m", 0)
                        
                        severity = None
                        if code in [95, 96, 99] or wind > 60:
                            severity = "severe"
                        elif code > 70 or wind > 40:
                            severity = "high"
                        elif code > 50 or wind > 20:
                            severity = "medium"
                            
                        if severity:
                            weather_events.append({
                                "id": f"wx-{port.unlocode}-{datetime.now().strftime('%Y%m%d%H')}",
                                "type": "weather",
                                "severity": severity,
                                "title": f"Severe Weather at Port of {port.name}",
                                "description": f"Weather code {code} and wind speeds of {wind} km/h detected at {port.name}.",
                                "impacted": [{"type": "port", "name": port.name}],
                                "starts_at": datetime.now().isoformat(),
                                "ends_at": (datetime.now() + timedelta(hours=24)).isoformat(),
                            })
            except Exception as e:
                print(f"Error fetching weather for {port.name}: {e}")
                
        return weather_events

    def normalize(self, raw_data: dict) -> models.RiskEvent:
        severity_map = {
            "low": models.RiskSeverity.LOW,
            "medium": models.RiskSeverity.MEDIUM,
            "high": models.RiskSeverity.HIGH,
            "severe": models.RiskSeverity.SEVERE,
        }
        return models.RiskEvent(
            event_type=raw_data["type"],
            severity=severity_map.get(raw_data["severity"], models.RiskSeverity.LOW),
            source="Open-Meteo",
            external_id=raw_data["id"],
            title=raw_data["title"],
            description=raw_data["description"],
            impacted_entities=raw_data["impacted"],
            starts_at=datetime.fromisoformat(raw_data["starts_at"]),
            ends_at=datetime.fromisoformat(raw_data["ends_at"]),
        )

