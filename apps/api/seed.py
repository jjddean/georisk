from app.database import SessionLocal, engine
from app import models

def seed():
    db = SessionLocal()
    
    # 1. Create Ports
    ports_data = [
        {"name": "Shanghai", "unlocode": "CNSHA", "country": "China", "latitude": 31.23, "longitude": 121.47},
        {"name": "Rotterdam", "unlocode": "NLRTM", "country": "Netherlands", "latitude": 51.92, "longitude": 4.47},
        {"name": "Chittagong", "unlocode": "BDCGP", "country": "Bangladesh", "latitude": 22.33, "longitude": 91.83},
        {"name": "Kolkata", "unlocode": "INCCU", "country": "India", "latitude": 22.57, "longitude": 88.36},
        {"name": "Newark", "unlocode": "USNWK", "country": "USA", "latitude": 40.73, "longitude": -74.17},
        {"name": "St. Petersburg", "unlocode": "RULED", "country": "Russia", "latitude": 59.93, "longitude": 30.33},
    ]
    
    db_ports = []
    for p in ports_data:
        db_port = db.query(models.Port).filter_by(unlocode=p["unlocode"]).first()
        if not db_port:
            db_port = models.Port(**p)
            db.add(db_port)
            db.flush()
        db_ports.append(db_port)
    
    # 2. Create Lanes
    port_map = {p.unlocode: p.id for p in db_ports}
    lanes_data = [
        {"origin_port_id": port_map["CNSHA"], "destination_port_id": port_map["NLRTM"], "mode": "ocean"},
        {"origin_port_id": port_map["BDCGP"], "destination_port_id": port_map["NLRTM"], "mode": "ocean"},
        {"origin_port_id": port_map["CNSHA"], "destination_port_id": port_map["USNWK"], "mode": "ocean"},
    ]
    
    for l in lanes_data:
        db_lane = db.query(models.Lane).filter_by(
            origin_port_id=l["origin_port_id"], 
            destination_port_id=l["destination_port_id"]
        ).first()
        if not db_lane:
            db_lane = models.Lane(**l)
            db.add(db_lane)
    
    # 3. Create a Test Organization
    org = db.query(models.Organization).filter_by(name="GeoRisk Forwarder A").first()
    if not org:
        org = models.Organization(name="GeoRisk Forwarder A")
        db.add(org)
    
    db.commit()
    db.close()
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
