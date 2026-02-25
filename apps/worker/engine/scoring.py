from sqlalchemy.orm import Session
from apps.api.app import models
from datetime import datetime
from apps.worker.engine.alerts import AlertManager
from apps.worker.ml.hotspot_predictor import HotspotPredictor
import json

class RiskCalculator:
    def __init__(self, db: Session):
        self.db = db
        self.alert_manager = AlertManager(db)
        self.hotspot_predictor = HotspotPredictor(db)

    def compute_score(self, entity_type: str, entity_id: int):
        # Refined Scoring Engine v1.2 (Predictive Phase 2)
        # Uses event accumulation and hotspot forecasting
        
        active_events = self.db.query(models.RiskEvent).filter(
            models.RiskEvent.ends_at >= datetime.now()
        ).all()
        
        score = 0
        breakdown = {}
        
        entity = None
        if entity_type == "port":
            entity = self.db.query(models.Port).get(entity_id)
        elif entity_type == "lane":
            entity = self.db.query(models.Lane).get(entity_id)
        
        if not entity:
            return 0, {}, models.RiskSeverity.LOW
            
        # 1. BASE EVENT SCORING
        for event in active_events:
            is_impacted = False
            # DETERMINISTIC INTERSECTION (Refined V1)
            # Check impacted_entities JSON or impact_geometry
            for impact in event.impacted_entities:
                if impact["type"] == entity_type:
                    if entity_type == "port" and impact.get("name") == entity.name:
                        is_impacted = True
                    elif entity_type == "lane":
                        if impact.get("name") in [entity.origin_port.name, entity.destination_port.name]:
                            is_impacted = True
            
            if is_impacted: # Simplified intersection logic
                # Scale by confidence score
                weight = event.confidence_score or 1.0
                points = {
                    models.RiskSeverity.SEVERE: 50,
                    models.RiskSeverity.HIGH: 30,
                    models.RiskSeverity.MEDIUM: 15,
                    models.RiskSeverity.LOW: 5
                }.get(event.severity, 0)
                
                weighted_points = int(points * weight)

                # ML Friction Bonus: customs and sanctions events compound risk
                friction_type = getattr(event, 'event_type', '')
                if friction_type == 'customs_friction':
                    weighted_points += 10
                elif friction_type == 'sanctions_compliance':
                    weighted_points += 15
                elif friction_type == 'labor_action':
                    weighted_points += 5

                score += weighted_points
                factor = event.event_type
                breakdown[factor] = breakdown.get(factor, 0) + weighted_points

        # 2. PREDICTIVE HOTSPOT PENALTY (Phase 2)
        if entity_type == "port":
            penalty = self.hotspot_predictor.get_hotspot_penalty(entity.name)
            if penalty > 0:
                score += penalty
                breakdown["predictive_hotspot"] = penalty
        elif entity_type == "lane":
            # Lanes inherit hotspot penalties from their origin/destination ports
            o_penalty = self.hotspot_predictor.get_hotspot_penalty(entity.origin_port.name)
            d_penalty = self.hotspot_predictor.get_hotspot_penalty(entity.destination_port.name)
            total_penalty = max(o_penalty, d_penalty)
            if total_penalty > 0:
                score += total_penalty
                breakdown["predictive_hotspot"] = total_penalty

        score = min(score, 100)
        status = models.RiskSeverity.LOW
        if score >= 80: status = models.RiskSeverity.SEVERE
        elif score >= 60: status = models.RiskSeverity.HIGH
        elif score >= 30: status = models.RiskSeverity.MEDIUM
        
        return score, breakdown, status

    def update_snapshot(self, entity_type: str, entity_id: int, score: int, breakdown: dict, status: models.RiskSeverity, dataset_snapshot_id: str):
        SCORING_VERSION = "v1.1-postgres-defensible"
        
        # Update current score
        current = self.db.query(models.RiskScoreCurrent).filter_by(
            entity_type=entity_type, entity_id=entity_id
        ).first()
        
        if not current:
            current = models.RiskScoreCurrent(
                entity_type=entity_type, entity_id=entity_id, score=0
            )
            self.db.add(current)
            self.db.flush()
        
        old_score = current.score
        current.score = score
        current.breakdown = breakdown
        current.status = status
        current.scoring_version = SCORING_VERSION
        current.dataset_snapshot_id = dataset_snapshot_id
        current.updated_at = datetime.now()
        
        # Trigger alerts with evidence context
        self.alert_manager.check_score_change(entity_type, entity_id, old_score, score, status)
        
        # Create immutable snapshot for audit trail
        snapshot = models.RiskScoreSnapshot(
            entity_type=entity_type,
            entity_id=entity_id,
            score=score,
            breakdown=breakdown,
            scoring_version=SCORING_VERSION,
            dataset_snapshot_id=dataset_snapshot_id,
            computed_at=datetime.now()
        )
        self.db.add(snapshot)
        self.db.commit()
