"""
GeoRisk Pro — NLP Pipeline Test
Tests friction classification and port entity extraction.
Run: python apps/worker/ml/test_nlp_pipeline.py
"""

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from apps.worker.ml.friction_classifier import FrictionClassifier
from apps.worker.ml.port_ner import PortEntityExtractor


def test_friction_classifier():
    print("=" * 60)
    print("TEST 1: Friction Classifier (Rule-Based Mode)")
    print("=" * 60)
    
    classifier = FrictionClassifier()
    
    test_cases = [
        {
            "text": "HMRC systems experiencing severe delays at Felixstowe causing customs backlog",
            "expected_category": "customs_friction",
            "expected_severity": "high",
        },
        {
            "text": "Hurricane warning issued for Caribbean shipping lanes, ports preparing for closure",
            "expected_category": "weather_force_majeure",
            "expected_severity": "severe",
        },
        {
            "text": "OFAC adds 3 vessels to sanctions list affecting Red Sea trade",
            "expected_category": "sanctions_compliance",
            "expected_severity": "severe",
        },
        {
            "text": "Rotterdam port reports normal operations and steady throughput this quarter",
            "expected_category": "none",
            "expected_severity": "low",
        },
        {
            "text": "Dock workers announce indefinite strike at Lagos Apapa terminal",
            "expected_category": "labor_action",
            "expected_severity": "severe",
        },
        {
            "text": "Port congestion worsens at Chittagong as vessel queue extends to 15 ships",
            "expected_category": "port_disruption",
            "expected_severity": "high",
        },
        {
            "text": "New tariff increase on Chinese imports announced by US Trade Representative",
            "expected_category": "trade_policy",
            "expected_severity": "high",
        },
        {
            "text": "Piracy attack reported near Gulf of Aden, armed robbery on container vessel",
            "expected_category": "conflict_security",
            "expected_severity": "severe",
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, tc in enumerate(test_cases, 1):
        signal = classifier._classify_rules(tc["text"])
        
        cat_ok = signal.category == tc["expected_category"]
        sev_ok = signal.severity == tc["expected_severity"]
        status = "✓" if (cat_ok and sev_ok) else "✗"
        
        if cat_ok and sev_ok:
            passed += 1
        else:
            failed += 1
        
        print(f"\n  {status} Test {i}: {tc['text'][:60]}...")
        print(f"    Category: {signal.category} (expected: {tc['expected_category']}) {'✓' if cat_ok else '✗'}")
        print(f"    Severity: {signal.severity} (expected: {tc['expected_severity']}) {'✓' if sev_ok else '✗'}")
        print(f"    Confidence: {signal.confidence}")
        print(f"    Explanation: {signal.explanation}")
    
    print(f"\n  Results: {passed}/{passed + failed} passed")
    return failed == 0


def test_port_extractor():
    print("\n" + "=" * 60)
    print("TEST 2: Port Entity Extraction")
    print("=" * 60)
    
    extractor = PortEntityExtractor()
    print(f"\n  Port database: {extractor.get_port_count()} ports, {extractor.get_alias_count()} searchable terms")
    
    test_cases = [
        {
            "text": "Severe congestion reported at Lagos Apapa terminal, impacting vessels heading to Rotterdam",
            "expected_ports": ["Lagos", "Rotterdam"],
            "expected_corridor": "africa_west → eu",
        },
        {
            "text": "HMRC delays at Felixstowe cause backlog for imports from Chittagong and Karachi",
            "expected_ports": ["Felixstowe", "Chittagong", "Karachi"],
            "expected_corridor": "bangladesh → uk",
        },
        {
            "text": "Hurricane warning near Kingston Jamaica and Port of Spain Trinidad",
            "expected_ports": ["Kingston", "Port of Spain"],
            "expected_corridor": "caribbean",
        },
        {
            "text": "New tariffs on goods arriving at Newark from Shanghai and Yantian",
            "expected_ports": ["Newark", "Shanghai", "Shenzhen"],  # Yantian → Shenzhen
            "expected_corridor": "china → usa",
        },
        {
            "text": "Strike at Mersin port disrupts Turkish exports to Hamburg and Antwerp",
            "expected_ports": ["Mersin", "Hamburg", "Antwerp"],
            "expected_corridor": "turkey → eu",
        },
        {
            "text": "Santos port in Brazil reports record throughput for exports to Savannah",
            "expected_ports": ["Santos", "Savannah"],
            "expected_corridor": "brazil → usa",
        },
        {
            "text": "Mombasa port delays as Kenya dockworkers threaten action",
            "expected_ports": ["Mombasa"],
            "expected_corridor": "africa_east",
        },
        {
            "text": "Cat Lai terminal sees congestion spike for Vietnam exports",
            "expected_ports": ["Ho Chi Minh City"],  # Cat Lai → Ho Chi Minh City
            "expected_corridor": "vietnam",
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, tc in enumerate(test_cases, 1):
        ports = extractor.extract_ports(tc["text"])
        port_names = [p["name"] for p in ports]
        corridors = extractor.extract_corridors(ports)
        
        ports_ok = all(ep in port_names for ep in tc["expected_ports"])
        corridor_ok = any(tc["expected_corridor"] in c for c in corridors) if corridors else "?" not in tc.get("expected_corridor", "")
        
        status = "✓" if ports_ok else "✗"
        if ports_ok:
            passed += 1
        else:
            failed += 1
        
        print(f"\n  {status} Test {i}: {tc['text'][:60]}...")
        print(f"    Extracted: {port_names}")
        print(f"    Expected:  {tc['expected_ports']}")
        print(f"    Corridors: {corridors}")
    
    print(f"\n  Results: {passed}/{passed + failed} passed")
    return failed == 0


def test_combined_pipeline():
    print("\n" + "=" * 60)
    print("TEST 3: Combined Pipeline (Classifier + Extractor)")
    print("=" * 60)
    
    classifier = FrictionClassifier()
    extractor = PortEntityExtractor()
    
    headline = "OFAC sanctions warning: vessels flagged near Jebel Ali as customs hold intensifies at Felixstowe for Bangladesh imports from Chittagong"
    
    signal = classifier._classify_rules(headline)
    ports = extractor.extract_ports(headline)
    corridors = extractor.extract_corridors(ports)
    
    print(f"\n  Headline: {headline}")
    print(f"\n  Friction:")
    print(f"    Category:   {signal.category}")
    print(f"    Severity:   {signal.severity}")
    print(f"    Confidence: {signal.confidence}")
    print(f"\n  Ports: {[p['name'] for p in ports]}")
    print(f"  Corridors: {corridors}")
    print(f"\n  Full signal: {signal.to_dict()}")
    
    return True


if __name__ == "__main__":
    print("\n🔬 GeoRisk Pro — NLP Pipeline Tests")
    print("─" * 60)
    
    r1 = test_friction_classifier()
    r2 = test_port_extractor()
    r3 = test_combined_pipeline()
    
    print("\n" + "=" * 60)
    if r1 and r2 and r3:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60)
