import httpx
from apps.worker.feeds.base import BaseFeed
from apps.worker.ml.friction_classifier import FrictionClassifier
from apps.worker.ml.port_ner import PortEntityExtractor
from apps.api.app import models
from datetime import datetime, timedelta
import urllib.parse

# Lazy-initialized singletons (no startup cost)
_classifier = None
_extractor = None


def _get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = FrictionClassifier()
    return _classifier


def _get_extractor():
    global _extractor
    if _extractor is None:
        _extractor = PortEntityExtractor()
    return _extractor


# Map friction severity → RiskSeverity enum
SEVERITY_MAP = {
    "severe": models.RiskSeverity.SEVERE,
    "high": models.RiskSeverity.HIGH,
    "medium": models.RiskSeverity.MEDIUM,
    "low": models.RiskSeverity.LOW,
}


class NewsFeed(BaseFeed):
    def fetch(self):
        # GDELT Doc API v2
        # Querying for logistics disruptions, strikes, and port events
        keywords = "(disruption OR strike OR conflict OR closure OR blockade) AND (port OR maritime OR shipping OR freight)"
        encoded_query = urllib.parse.quote(keywords)
        url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={encoded_query}&mode=ArtList&maxrecords=20&format=json&timespan=1d"
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("articles", [])
        except Exception as e:
            print(f"Error fetching from GDELT: {e}")
            
        return []

    def normalize(self, raw_data: dict) -> models.RiskEvent:
        title = raw_data.get("title", "")
        url = raw_data.get("url", "")
        text_for_analysis = f"{title} {url}"

        # ─── NLP Classification ───────────────────────────────
        classifier = _get_classifier()
        signal = classifier.classify(text_for_analysis)

        # Map to RiskSeverity
        severity = SEVERITY_MAP.get(signal.severity, models.RiskSeverity.LOW)

        # ─── Port Entity Extraction ───────────────────────────
        extractor = _get_extractor()
        ports = extractor.extract_ports(text_for_analysis)
        corridors = extractor.extract_corridors(ports)

        # Build impacted entities from extracted ports
        impacted = [{"type": "port", "name": p["name"]} for p in ports]

        # Build rich metadata
        ml_metadata = {
            "friction_category": signal.category,
            "friction_confidence": signal.confidence,
            "friction_explanation": signal.explanation,
            "corridors": corridors,
            "ml_version": "pfe-v1.0",
        }

        return models.RiskEvent(
            event_type=signal.category if signal.category != "none" else "news",
            severity=severity,
            source="Global Disruption Feed",
            external_id=url,  # URL as unique ID
            confidence_score=signal.confidence,

            title=title,
            description=f"[ML] {signal.explanation} | Article: {url}",
            impacted_entities=impacted,
            starts_at=datetime.utcnow(),
            ends_at=datetime.utcnow() + timedelta(days=2),  # News events expire faster
        )
