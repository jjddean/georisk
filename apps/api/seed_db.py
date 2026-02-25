from app.database import SessionLocal
from app import models

def seed():
    db = SessionLocal()
    try:
        # 1. Create Organization
        org = db.query(models.Organization).filter_by(name="Global Forwarding Ltd").first()
        if not org:
            org = models.Organization(name="Global Forwarding Ltd")
            db.add(org)
            db.flush()

        # 2. Create Ports
        shanghai = db.query(models.Port).filter_by(unlocode="CNSHA").first()
        if not shanghai:
            shanghai = models.Port(name="Shanghai", unlocode="CNSHA", country="China", latitude=31.2304, longitude=121.4737)
            db.add(shanghai)
            
        rotterdam = db.query(models.Port).filter_by(unlocode="NLRTM").first()
        if not rotterdam:
            rotterdam = models.Port(name="Rotterdam", unlocode="NLRTM", country="Netherlands", latitude=51.9225, longitude=4.4792)
            db.add(rotterdam)
            
        singapore = db.query(models.Port).filter_by(unlocode="SGSIN").first()
        if not singapore:
            singapore = models.Port(name="Singapore", unlocode="SGSIN", country="Singapore", latitude=1.3521, longitude=103.8198)
            db.add(singapore)

        db.flush()

        # 3. Create Lanes
        if not db.query(models.Lane).filter_by(origin_port_id=shanghai.id, destination_port_id=rotterdam.id).first():
            lane1 = models.Lane(origin_port_id=shanghai.id, destination_port_id=rotterdam.id, mode="ocean")
            db.add(lane1)
            
        if not db.query(models.Lane).filter_by(origin_port_id=singapore.id, destination_port_id=rotterdam.id).first():
            lane2 = models.Lane(origin_port_id=singapore.id, destination_port_id=rotterdam.id, mode="ocean")
            db.add(lane2)

        db.commit()
        print("Database seeded successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
