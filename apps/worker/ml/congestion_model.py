"""
GeoRisk Pro — Predictive Congestion Model
Uses OpenAI to forecast congestion trends based on event clusters.
Provides a "look-ahead" capability (3, 5, 10 days).
"""

import os
import json
from typing import Dict, Any, Optional, List
from apps.api.app import models

class PredictiveCongestionModel:
    def __init__(self):
        self._openai_client = None

    @property
    def openai_client(self):
        if self._openai_client is None:
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self._openai_client = OpenAI(api_key=api_key)
            except ImportError:
                pass
        return self._openai_client

    def forecast_congestion(self, port_name: str, active_events: List[Any]) -> Dict[str, Any]:
        """
        Forecasts future congestion based on current active events.
        Tries OpenAI first, falls back to rule-based trend analysis.
        """
        if not active_events:
            return {
                "current_level": "low",
                "trend": "stable",
                "confidence": 0.9,
                "forecast_3d": "low",
                "forecast_7d": "low",
                "explanation": "No active events detected."
            }

        # Format events for context
        event_summary = [
            f"{e.event_type} ({e.severity}): {e.title}" 
            for e in active_events
        ]

        # Try OpenAI
        forecast = self._forecast_openai(port_name, event_summary)
        if forecast:
            return forecast

        # Fallback to Rule-based
        return self._forecast_rules(port_name, active_events)

    def _forecast_openai(self, port_name: str, event_summary: List[str]) -> Optional[Dict[str, Any]]:
        if not self.openai_client:
            return None

        prompt = f"""You are a maritime logistics analyst. 
Port: {port_name}
Active Events: {json.dumps(event_summary)}

Predict port congestion for the next 10 days. 
Consider how these events (strikes, weather, customs friction) typically compound over time.

Respond ONLY with valid JSON:
{{
  "current_level": "low/medium/high/severe",
  "trend": "increasing/stable/decreasing",
  "confidence": 0.0-1.0,
  "forecast_3d": "expected level in 3 days",
  "forecast_7d": "expected level in 7 days",
  "explanation": "one sentence expert reasoning"
}}"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Maritime Logistics AI"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=200
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"[CongestionModel] OpenAI error: {e}")
            return None

    def _forecast_rules(self, port_name: str, active_events: List[Any]) -> Dict[str, Any]:
        """Simple rule-based trend analysis."""
        severity_counts = {
            models.RiskSeverity.SEVERE: 0,
            models.RiskSeverity.HIGH: 0,
            models.RiskSeverity.MEDIUM: 0,
            models.RiskSeverity.LOW: 0
        }
        
        for e in active_events:
            severity_counts[e.severity] += 1
            
        # Basic heuristic
        if severity_counts[models.RiskSeverity.SEVERE] > 0 or severity_counts[models.RiskSeverity.HIGH] > 1:
            level = "high"
            trend = "increasing"
            expl = "Compounded high-severity events indicate worsening congestion."
        elif severity_counts[models.RiskSeverity.HIGH] > 0 or severity_counts[models.RiskSeverity.MEDIUM] > 1:
            level = "medium"
            trend = "increasing"
            expl = "Multiple medium/high events suggests emerging bottlenecks."
        else:
            level = "low"
            trend = "stable"
            expl = "Isolated low-impact events suggest stable operations."

        return {
            "current_level": level,
            "trend": trend,
            "confidence": 0.6,
            "forecast_3d": level,
            "forecast_7d": level,
            "explanation": f"[Rule-based] {expl}"
        }
