from apps.api.app.database import SessionLocal
from apps.api.app import models
import enum

db = SessionLocal()

# Cleanup
db.query(models.Port).delete()
db.query(models.Lane).delete()
db.query(models.RiskScoreCurrent).delete()
db.commit()

# Create Ports
shanghai = models.Port(id=1, name="Shanghai", unlocode="CNSHA", country="China", latitude=31.2, longitude=121.5)
rotterdam = models.Port(id=2, name="Rotterdam", unlocode="NLRTM", country="Netherlands", latitude=51.9, longitude=4.5)
singapore = models.Port(id=3, name="Singapore", unlocode="SGSIN", country="Singapore", latitude=1.3, longitude=103.8)
los_angeles = models.Port(id=4, name="Los Angeles", unlocode="USLAX", country="USA", latitude=33.7, longitude=-118.2)
mumbai = models.Port(id=5, name="Mumbai", unlocode="INBOM", country="India", latitude=18.9, longitude=72.8)
felixstowe = models.Port(id=6, name="Felixstowe", unlocode="GBFXT", country="UK", latitude=51.9, longitude=1.3)
dubai = models.Port(id=7, name="Dubai", unlocode="AEDXB", country="UAE", latitude=25.2, longitude=55.3)
tehran = models.Port(id=8, name="Tehran", unlocode="IRTHR", country="Iran", latitude=35.7, longitude=51.4)
odessa = models.Port(id=9, name="Odessa", unlocode="UAODS", country="Ukraine", latitude=46.5, longitude=30.7)
istanbul = models.Port(id=10, name="Istanbul", unlocode="TRIST", country="Turkey", latitude=41.0, longitude=29.0)

db.add_all([shanghai, rotterdam, singapore, los_angeles, mumbai, felixstowe, dubai, tehran, odessa, istanbul])
db.commit()

# Create Lanes
lane1 = models.Lane(id=1, origin_port_id=shanghai.id, destination_port_id=rotterdam.id, mode="ocean")
lane2 = models.Lane(id=2, origin_port_id=singapore.id, destination_port_id=los_angeles.id, mode="ocean")
lane3 = models.Lane(id=3, origin_port_id=mumbai.id, destination_port_id=felixstowe.id, mode="ocean")
lane4 = models.Lane(id=4, origin_port_id=dubai.id, destination_port_id=tehran.id, mode="ocean")
lane5 = models.Lane(id=5, origin_port_id=odessa.id, destination_port_id=istanbul.id, mode="ocean")
db.add_all([lane1, lane2, lane3, lane4, lane5])
db.commit()

# Create Risk Scores
# ... (existing 1-3)
ls1 = models.RiskScoreCurrent(
    entity_type="lane", entity_id=lane1.id, score=85, status=models.RiskSeverity.SEVERE,
    breakdown={"zone": 50, "customs_friction": 25, "route_alternative": {"name": "Cape Of Good Hope", "distance_km": 15420, "savings_risk": 40}}
)
ls2 = models.RiskScoreCurrent(
    entity_type="lane", entity_id=lane2.id, score=62, status=models.RiskSeverity.MEDIUM,
    breakdown={"weather": 10, "customs_friction": 35, "congestion_forecast": {"level": "medium", "trend": "increasing", "forecast_3d": "Labor-linked backlog likely", "forecast_7d": "12-24h Port dwell time increase"}}
)
ls3 = models.RiskScoreCurrent(
    entity_type="lane", entity_id=lane3.id, score=31, status=models.RiskSeverity.MEDIUM,
    breakdown={"zone": 15, "customs_friction": 10, "congestion_forecast": {"level": "low", "trend": "stable", "forecast_3d": "Normal Operations", "forecast_7d": "Slight vessel cluster expected"}}
)
# New: Dubai -> Tehran (High)
ls4 = models.RiskScoreCurrent(
    entity_type="lane", entity_id=lane4.id, score=88, status=models.RiskSeverity.SEVERE,
    breakdown={"zone": 80, "customs_friction": 45}
)
# New: Odessa -> Istanbul (Extreme)
ls5 = models.RiskScoreCurrent(
    entity_type="lane", entity_id=lane5.id, score=95, status=models.RiskSeverity.SEVERE,
    breakdown={"zone": 100, "customs_friction": 50}
)

db.add_all([ls1, ls2, ls3, ls4, ls5])
db.commit()
print("SQLite seeded with five ML scenarios.")
