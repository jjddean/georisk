"""
GeoRisk Pro — Phase 2 Congestion Test
Tests hotspot detection and congestion forecasting.
Run: python apps/worker/ml/test_congestion_pipeline.py
"""

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from apps.worker.ml.hotspot_predictor import HotspotPredictor
from apps.worker.ml.congestion_model import PredictiveCongestionModel
from apps.api.app import models
from unittest.mock import MagicMock
from datetime import datetime, timedelta

def test_hotspot_accumulation():
    print("=" * 60)
    print("TEST 4: Hotspot Accumulation (Phase 2)")
    print("=" * 60)
    
    # Mock DB session
    db = MagicMock()
    
    # Simulate 3 high-impact events for Shanghai
    shanghai_events = [
        models.RiskEvent(
            event_type="port_disruption",
            severity=models.RiskSeverity.HIGH,
            title="Dock strike at Shanghai",
            starts_at=datetime.utcnow(),
            impacted_entities=[{"type": "port", "name": "Shanghai"}],
            confidence_score=0.9
        ),
        models.RiskEvent(
            event_type="weather_force_majeure",
            severity=models.RiskSeverity.SEVERE,
            title="Typhoon approaching Ningbo-Shanghai",
            starts_at=datetime.utcnow(),
            impacted_entities=[{"type": "port", "name": "Shanghai"}],
            confidence_score=1.0
        ),
        models.RiskEvent(
            event_type="customs_friction",
            severity=models.RiskSeverity.MEDIUM,
            title="Manual clearance delays",
            starts_at=datetime.utcnow(),
            impacted_entities=[{"type": "port", "name": "Shanghai"}],
            confidence_score=0.8
        )
    ]
    
    db.query.return_value.filter.return_value.all.return_value = shanghai_events
    
    predictor = HotspotPredictor(db)
    acc = predictor.calculate_accumulation("Shanghai")
    
    print(f"\n  Port: Shanghai")
    print(f"  Recent Events: {acc['event_count']}")
    print(f"  Intensity Score: {acc['intensity']} (0.0-1.0)")
    print(f"  Primary Drivers: {acc['primary_drivers']}")
    
    is_hotspot = acc["intensity"] > 0.6
    print(f"  Status: {'🔥 HOTSPOT DETECTED' if is_hotspot else 'STABLE'}")
    
    penalty = predictor.get_hotspot_penalty("Shanghai")
    print(f"  Scoring Penalty: +{penalty}")
    
    return is_hotspot and penalty == 20

def test_congestion_forecasting():
    print("\n" + "=" * 60)
    print("TEST 5: Congestion Forecasting (Phase 2)")
    print("=" * 60)
    
    model = PredictiveCongestionModel()
    
    # Mock events
    events = [
        MagicMock(event_type="labor_action", severity=models.RiskSeverity.HIGH, title="Indefinite strike starting tomorrow"),
        MagicMock(event_type="customs_friction", severity=models.RiskSeverity.MEDIUM, title="New regulatory checks")
    ]
    
    print("\n  Scenario: Strike + Customs Friction at Felixstowe")
    # Using rule-based for consistent test results without API keys
    forecast = model._forecast_rules("Felixstowe", events)
    
    print(f"    Current Level: {forecast['current_level']}")
    print(f"    Trend:         {forecast['trend']}")
    print(f"    Explanation:   {forecast['explanation']}")
    
    passed = forecast["trend"] == "increasing" and forecast["current_level"] == "medium"
    return passed

if __name__ == "__main__":
    print("\n🔬 GeoRisk Pro — Phase 2 ML Tests")
    print("─" * 60)
    
    r4 = test_hotspot_accumulation()
    r5 = test_congestion_forecasting()
    
    print("\n" + "=" * 60)
    if r4 and r5:
        print("✓ PHASE 2 VERIFIED")
    else:
        print("✗ PHASE 2 ISSUES DETECTED")
    print("=" * 60)
