"""
GeoRisk Pro — Phase 3 Route Optimization Test
Tests A* pathfinding with risk clustering and deviations.
Run: python apps/worker/ml/test_routing_pipeline.py
"""

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from apps.worker.ml.route_optimizer import RouteOptimizer
from apps.api.app import models
from unittest.mock import MagicMock

def test_risk_aware_deviation():
    print("=" * 60)
    print("TEST 6: Risk-Aware Route Deviation (Phase 3)")
    print("=" * 60)
    
    # Mock DB session
    db = MagicMock()
    
    # Setup Ports
    p1 = models.Port(id=1, name="Shanghai", latitude=31.2, longitude=121.5)
    p2 = models.Port(id=2, name="Singapore", latitude=1.3, longitude=103.8)
    p3 = models.Port(id=3, name="Rotterdam", latitude=51.9, longitude=4.4)
    p4 = models.Port(id=4, name="Cape Town", latitude=-33.9, longitude=18.4)
    
    ports = [p1, p2, p3, p4]
    
    # Setup Lanes
    l1 = models.Lane(id=1, origin_port_id=1, destination_port_id=2, mode="ocean") # SHG -> SIN
    l2 = models.Lane(id=2, origin_port_id=2, destination_port_id=3, mode="ocean") # SIN -> ROT (Standard)
    l3 = models.Lane(id=3, origin_port_id=1, destination_port_id=4, mode="ocean") # SHG -> CPT
    l4 = models.Lane(id=4, origin_port_id=4, destination_port_id=3, mode="ocean") # CPT -> ROT (Alternative)
    
    lanes = [l1, l2, l3, l4]

    # Global state for risk score
    # We'll use a dict to store scores for specific lanes
    lane_risk_scores = {}

    # Mock DB queries
    def db_query_side_effect(model):
        q = MagicMock()
        if model == models.Port:
            q.all.return_value = ports
        elif model == models.Lane:
            q.all.return_value = lanes
        elif model == models.RiskScoreCurrent:
            # Handle .filter_by(...).first()
            def filter_by_side_effect(**kwargs):
                lane_id = kwargs.get("entity_id")
                mock_first = MagicMock()
                score = lane_risk_scores.get(lane_id, 0)
                if score > 0:
                    mock_first.first.return_value = models.RiskScoreCurrent(score=score)
                else:
                    mock_first.first.return_value = None
                return mock_first
                
            q.filter_by.side_effect = filter_by_side_effect
        return q
    
    db.query.side_effect = db_query_side_effect
    
    optimizer = RouteOptimizer(db)
    
    # --- SCENARIO 1: Standard Search (No Risk) ---
    print("\n  Scenario 1: No Risk (Standard Route)")
    lane_risk_scores.clear()
    
    routes = optimizer.suggest_alternatives(1, 3)
    shortest_path = next((r for r in routes if "Shortest" in r["type"]), None)
    
    if shortest_path:
        print(f"    Selected Path: {' -> '.join(shortest_path['path_names'])}")
        print(f"    Distance:      {shortest_path['total_distance_km']} km")
    
    # --- SCENARIO 2: High Risk on Singapore -> Rotterdam ---
    print("\n  Scenario 2: High Risk (85) on Singapore -> Rotterdam")
    lane_risk_scores[2] = 85 # SIN -> ROT is now 85 risk

    routes = optimizer.suggest_alternatives(1, 3)
    
    safest_path = next((r for r in routes if "Risk-Aware" in r["type"]), None)
    standard_path = next((r for r in routes if "Shortest" in r["type"]), None)
    
    if safest_path:
        print(f"    🔥 RISK DETECTED ON STANDARD ROUTE")
        print(f"    Safest Route:   {' -> '.join(safest_path['path_names'])}")
        print(f"    Safest Cost:    {safest_path['total_cost']}")
        print(f"    Standard Route: {' -> '.join(standard_path['path_names'])}")
        print(f"    Standard Cost:  {standard_path['total_cost']}")
        
        # Verify that Safest Route bypasses Singapore (Port 2) and goes via Cape Town (Port 4)
        passed = 2 not in safest_path['path_ids'] and 4 in safest_path['path_ids']
        print(f"    Deviation Successful: {'✅ YES' if passed else '❌ NO'}")
        return passed
    else:
        print("    ❌ No alternative path found!")
    
    return False

if __name__ == "__main__":
    print("\n🔬 GeoRisk Pro — Phase 3 ML Tests")
    print("─" * 60)
    
    r6 = test_risk_aware_deviation()
    
    print("\n" + "=" * 60)
    if r6:
        print("✓ PHASE 3 VERIFIED")
    else:
        print("✗ PHASE 3 ISSUES DETECTED")
    print("=" * 60)
