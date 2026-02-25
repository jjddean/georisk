from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database
from .database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="GeoRisk API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to GeoRisk API"}

@app.get("/lanes/", response_model=List[schemas.Lane])
def read_lanes(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    lanes = db.query(models.Lane).offset(skip).limit(limit).all()
    return lanes

@app.post("/lanes/", response_model=schemas.Lane)
def create_lane(lane: schemas.LaneBase, db: Session = Depends(database.get_db)):
    db_lane = models.Lane(**lane.dict())
    db.add(db_lane)
    db.commit()
    db.refresh(db_lane)
    return db_lane

@app.get("/risk-scores/", response_model=List[schemas.RiskScore])
def read_risk_scores(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    scores = db.query(models.RiskScoreCurrent).offset(skip).limit(limit).all()
    return scores

@app.get("/alerts/", response_model=List[schemas.Alert])
def read_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    alerts = db.query(models.Alert).order_by(models.Alert.created_at.desc()).offset(skip).limit(limit).all()
    return alerts

@app.get("/reports/lane/{lane_id}")
def generate_report(lane_id: int, db: Session = Depends(database.get_db)):
    from .reporting import ReportingUtility
    report = ReportingUtility(db).generate_lane_report(lane_id)
    if not report:
        raise HTTPException(status_code=404, detail="Lane not found")
    return report


