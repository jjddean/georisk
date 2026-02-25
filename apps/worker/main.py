import os
from celery import Celery
from dotenv import load_dotenv
from apps.worker.feeds.weather import WeatherFeed
from apps.worker.feeds.sanctions import SanctionsFeed
from apps.worker.feeds.news import NewsFeed
from apps.worker.engine.scoring import RiskCalculator
from apps.worker.engine.advisory import AdvisoryGenerator
from apps.worker.ml.hotspot_predictor import HotspotPredictor
from apps.worker.ml.congestion_model import PredictiveCongestionModel
from apps.worker.ml.route_optimizer import RouteOptimizer
from apps.worker.risk.maritime_risk_manager import MaritimeRiskManager
from apps.api.app.database import SessionLocal
from apps.api.app import models
from datetime import datetime
import time

load_dotenv()

@app.task(name="tasks.precompute_route_advisories")
def precompute_route_advisories():
    print("Precomputing risk-aware route advisories...")
    db = SessionLocal()
    try:
        optimizer = RouteOptimizer(db)
        lanes = db.query(models.Lane).all()
        
        for lane in lanes:
            routes = optimizer.suggest_alternatives(lane.origin_port_id, lane.destination_port_id)
            
            # Find the "Risk-Aware" one if it differs from shortest
            risk_aware = next((r for r in routes if "Risk-Aware" in r["type"]), None)
            
            # PERSIST TO UI: Save to lane risk score breakdown
            risk_score = db.query(models.RiskScoreCurrent).filter_by(
                entity_type="lane", entity_id=lane.id
            ).first()
            
            if risk_score:
                breakdown = risk_score.breakdown or {}
                if risk_aware:
                    breakdown["route_alternative"] = {
                        "name": risk_aware["path_names"][1] if len(risk_aware["path_names"]) > 2 else risk_aware["path_names"][-1],
                        "distance_km": risk_aware["total_distance_km"],
                        "savings_risk": round(risk_aware["cumulative_risk"], 2)
                    }
                else:
                    breakdown.pop("route_alternative", None)
                risk_score.breakdown = breakdown
                db.add(risk_score)

        db.commit()
    finally:
        db.close()
    return True

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery("georisk_worker", broker=REDIS_URL, backend=REDIS_URL)

app.conf.beat_schedule = {
    "ingest-feeds-every-30-mins": {
        "task": "tasks.run_ingestion",
        "schedule": 1800.0,
    },
    "recompute-scores-every-hour": {
        "task": "tasks.recompute_all_scores",
        "schedule": 3600.0,
    },
}

@app.task(name="tasks.run_ingestion")
def run_ingestion():
    print("Starting ingestion...")
    db = SessionLocal()
    SNAPSHOT_ID = datetime.utcnow().strftime("%Y%m%d_%H%M")
    try:
        # Legacy feeds
        WeatherFeed(db).ingest(db)
        SanctionsFeed().ingest(db)
        NewsFeed().ingest(db)
        
        # New Maritime Intelligence Feed (Postgres SOR)
        MaritimeRiskManager(db).ingest_piracy_data()
        
        print(f"Ingestion complete. Snapshot: {SNAPSHOT_ID}")
        # Trigger hotspots then scoring and route advisories after ingestion
        recompute_hotspots.delay(dataset_snapshot_id=SNAPSHOT_ID)
        recompute_all_scores.delay(dataset_snapshot_id=SNAPSHOT_ID)
        precompute_route_advisories.delay()
    finally:
        db.close()
    return True

@app.task(name="tasks.recompute_hotspots")
def recompute_hotspots(dataset_snapshot_id: str = "manual"):
    print("Recomputing hotspots and congestion forecasts...")
    db = SessionLocal()
    try:
        predictor = HotspotPredictor(db)
        model = PredictiveCongestionModel()
        
        hotspots = predictor.identify_all_hotspots()
        for hotspot in hotspots:
            port_name = hotspot["port_name"]
            port = db.query(models.Port).filter_by(name=port_name).first()
            if not port: continue

            active_events = db.query(models.RiskEvent).filter(
                models.RiskEvent.ends_at >= datetime.utcnow()
            ).all()
            
            port_events = [
                e for e in active_events 
                if any(i["type"] == "port" and i["name"] == port_name for i in e.impacted_entities)
            ]
            
            if port_events:
                forecast = model.forecast_congestion(port_name, port_events)
                
                # PERSIST TO UI
                risk_score = db.query(models.RiskScoreCurrent).filter_by(
                    entity_type="port", entity_id=port.id
                ).first()
                if risk_score:
                    breakdown = risk_score.breakdown or {}
                    breakdown["congestion_forecast"] = forecast
                    risk_score.breakdown = breakdown
                    db.add(risk_score)
                
                print(f"Hotspot: {port_name} | Intensity: {hotspot['intensity']} | Forecast: {forecast['trend']}")
        db.commit()
    finally:
        db.close()
    return True

@app.task(name="tasks.recompute_all_scores")
def recompute_all_scores(dataset_snapshot_id: str = "manual"):
    print(f"Starting risk score computation for snapshot: {dataset_snapshot_id}")
    db = SessionLocal()
    try:
        calculator = RiskCalculator(db)
        # Recompute all ports
        ports = db.query(models.Port).all()
        for port in ports:
            score, breakdown, status = calculator.compute_score("port", port.id)
            calculator.update_snapshot("port", port.id, score, breakdown, status, dataset_snapshot_id)
        
        # Recompute all lanes
        lanes = db.query(models.Lane).all()
        for lane in lanes:
            score, breakdown, status = calculator.compute_score("lane", lane.id)
            calculator.update_snapshot("lane", lane.id, score, breakdown, status, dataset_snapshot_id)
            
        print("Scoring complete.")
    finally:
        db.close()
    return True
