"""
GeoRisk Pro — Route Optimizer
Uses A* pathfinding with dynamic risk weights to suggest optimal maritime routes.
"""

import math
import heapq
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from apps.api.app import models
from apps.worker.ml.maritime_graph import MaritimeGraph

class RouteOptimizer:
    def __init__(self, db: Session):
        self.db = db
        self.graph = MaritimeGraph(db)
        self.risk_multiplier = 2.0  # How heavily risk affects "cost"

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great-circle distance between two points in KM."""
        R = 6371  # Earth radius in KM
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _get_risk_cost(self, lane_id: int) -> float:
        """Fetches the current risk score for a lane and converts it to a cost penalty."""
        risk = self.db.query(models.RiskScoreCurrent).filter_by(
            entity_type="lane", entity_id=lane_id
        ).first()
        
        score = risk.score if risk else 0
        
        # Non-linear penalty: Risk > 80 becomes extremely expensive to avoid
        if score >= 80 and self.risk_multiplier > 0:
            return 10000.0  # Impassable
        
        return float(score * self.risk_multiplier)

    def find_optimal_route(self, origin_id: int, destination_id: int) -> Optional[Dict[str, Any]]:
        """
        A* Algorithm to find the risk-aware shortest path.
        Cost = Distance (KM) + Risk Penalty
        """
        # (priority, current_port_id, path_so_far, total_distance, cumulative_risk)
        frontier = [(0.0, origin_id, [origin_id], 0.0, 0.0)]
        visited = {origin_id: 0.0}

        while frontier:
            (priority, current_id, path, distance, risk_acc) = heapq.heappop(frontier)

            if current_id == destination_id:
                return {
                    "path_ids": path,
                    "path_names": [self.graph.get_port_name(pid) for pid in path],
                    "total_distance_km": round(distance, 2),
                    "cumulative_risk": round(risk_acc, 2),
                    "total_cost": round(priority, 2)
                }

            for edge in self.graph.get_neighbors(current_id):
                neighbor_id = edge["dest_id"]
                
                # Calculate Base Distance
                c1 = self.graph.get_coordinates(current_id)
                c2 = self.graph.get_coordinates(neighbor_id)
                step_dist = self._haversine(c1[0], c1[1], c2[0], c2[1])
                
                # Calculate Risk Cost
                risk_penalty = self._get_risk_cost(edge["lane_id"])
                
                new_distance = distance + step_dist
                new_risk = risk_acc + risk_penalty
                new_actual_cost = new_distance + new_risk
                
                if neighbor_id not in visited or new_actual_cost < visited[neighbor_id]:
                    visited[neighbor_id] = new_actual_cost
                    
                    # Heuristic: Remaining straight-line distance to goal
                    goal_coords = self.graph.get_coordinates(destination_id)
                    h = self._haversine(c2[0], c2[1], goal_coords[0], goal_coords[1])
                    
                    total_priority = new_actual_cost + h
                    heapq.heappush(frontier, (
                        total_priority, 
                        neighbor_id, 
                        path + [neighbor_id], 
                        new_distance, 
                        new_risk
                    ))

        return None  # No path found

    def suggest_alternatives(self, origin_id: int, destination_id: int) -> List[Dict[str, Any]]:
        """Returns Safest (Shortest path by distance only) vs Risk-Aware path."""
        # 1. Risk-Aware (Current settings)
        risk_aware = self.find_optimal_route(origin_id, destination_id)
        
        # 2. Shortest (Ignore risk)
        old_multiplier = self.risk_multiplier
        self.risk_multiplier = 0.0
        shortest = self.find_optimal_route(origin_id, destination_id)
        self.risk_multiplier = old_multiplier
        
        results = []
        if shortest:
            shortest["type"] = "Shortest (Standard)"
            results.append(shortest)
            
        if risk_aware and (not shortest or risk_aware["path_ids"] != shortest["path_ids"]):
            risk_aware["type"] = "Risk-Aware (Optimization)"
            results.append(risk_aware)
            
        return results
