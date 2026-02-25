"""
GeoRisk Pro — Maritime Graph Engine
Represents the network of ports and lanes as a graph.
Used by the Route Optimizer for pathfinding.
"""

from typing import Dict, List, Tuple, Any
from sqlalchemy.orm import Session
from apps.api.app import models

class MaritimeGraph:
    def __init__(self, db: Session):
        self.db = db
        self._graph: Dict[int, List[Dict[str, Any]]] = {}  # origin_id -> list of destination/lane info
        self._port_coords: Dict[int, Tuple[float, float]] = {}
        self._port_names: Dict[int, str] = {}
        self._load_network()

    def _load_network(self):
        """Builds the adjacency list from the database."""
        # 1. Load Ports for metadata/heuristics
        ports = self.db.query(models.Port).all()
        for port in ports:
            self._port_coords[port.id] = (port.latitude, port.longitude)
            self._port_names[port.id] = port.name
            self._graph[port.id] = []

        # 2. Load Lanes (edges)
        lanes = self.db.query(models.Lane).all()
        for lane in lanes:
            # Note: In our current schema, lanes are directional
            edge_info = {
                "lane_id": lane.id,
                "dest_id": lane.destination_port_id,
                "mode": lane.mode
            }
            if lane.origin_port_id in self._graph:
                self._graph[lane.origin_port_id].append(edge_info)

    def get_neighbors(self, port_id: int) -> List[Dict[str, Any]]:
        """Returns reachable ports from the given port_id."""
        return self._graph.get(port_id, [])

    def get_coordinates(self, port_id: int) -> Tuple[float, float]:
        """Returns (lat, lon) for heuristic calculation."""
        return self._port_coords.get(port_id, (0.0, 0.0))

    def get_port_name(self, port_id: int) -> str:
        """Returns port name for display/logging."""
        return self._port_names.get(port_id, f"Port {port_id}")

    def get_all_port_ids(self) -> List[int]:
        """Returns a list of all port IDs in the graph."""
        return list(self._port_coords.keys())
