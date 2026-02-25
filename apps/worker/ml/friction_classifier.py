"""
GeoRisk Pro — Friction Classifier
Hybrid NLP pipeline: OpenAI (primary) + rule-based (fallback).
Classifies maritime/customs news into friction categories with severity.
"""

import os
import json
import re
from dataclasses import dataclass, asdict
from typing import Optional
from enum import Enum


class FrictionCategory(str, Enum):
    CUSTOMS_FRICTION = "customs_friction"
    PORT_DISRUPTION = "port_disruption"
    SANCTIONS_COMPLIANCE = "sanctions_compliance"
    CONFLICT_SECURITY = "conflict_security"
    WEATHER_FORCE_MAJEURE = "weather_force_majeure"
    TRADE_POLICY = "trade_policy"
    LABOR_ACTION = "labor_action"
    OPERATIONAL = "operational"
    NONE = "none"


class FrictionSeverity(str, Enum):
    SEVERE = "severe"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class FrictionSignal:
    category: str
    severity: str
    confidence: float
    explanation: str
    raw_text: str = ""

    def to_dict(self):
        return asdict(self)


# ─── Keyword Rules ────────────────────────────────────────────────

FRICTION_RULES = {
    FrictionCategory.CUSTOMS_FRICTION: {
        "severe": [
            "customs shutdown", "customs system failure", "border closure",
            "import ban", "export ban", "trade embargo",
        ],
        "high": [
            "customs delay", "clearance backlog", "hmrc", "cbp",
            "tariff dispute", "regulatory change", "customs inspection",
            "import restriction", "declaration error", "duty increase",
            "trade barrier", "customs hold", "customs seizure",
            "clearance suspended", "import duty",
        ],
        "medium": [
            "customs", "tariff", "clearance", "regulatory",
            "compliance issue", "documentation", "certificate",
            "phytosanitary", "fumigation", "quarantine",
        ],
    },
    FrictionCategory.PORT_DISRUPTION: {
        "severe": [
            "port closure", "port shut", "terminal shutdown",
            "port blockade", "canal blocked", "canal closure",
        ],
        "high": [
            "port congestion", "severe congestion", "vessel queue",
            "berth shortage", "terminal delay", "port strike",
            "dock strike", "tugboat shortage",
        ],
        "medium": [
            "congestion", "delays at port", "waiting time",
            "yard capacity", "equipment shortage",
        ],
    },
    FrictionCategory.SANCTIONS_COMPLIANCE: {
        "severe": [
            "ofac", "sanctioned vessel", "blacklisted",
            "un sanctions", "eu sanctions", "asset freeze",
        ],
        "high": [
            "sanctions list", "restricted entity", "export control",
            "dual-use", "sanctions screening", "denied party",
            "specially designated", "sdn list",
        ],
        "medium": [
            "sanctions", "compliance", "screening",
            "restricted", "embargo",
        ],
    },
    FrictionCategory.CONFLICT_SECURITY: {
        "severe": [
            "piracy attack", "vessel hijack", "armed attack",
            "missile strike", "naval blockade", "war zone",
            "houthi", "military operation",
        ],
        "high": [
            "piracy", "security threat", "armed robbery",
            "military exercise", "exclusion zone", "threat advisory",
            "no-go zone",
        ],
        "medium": [
            "security alert", "suspicious vessel", "threat",
            "military", "patrol",
        ],
    },
    FrictionCategory.WEATHER_FORCE_MAJEURE: {
        "severe": [
            "hurricane", "typhoon", "cyclone", "tsunami",
            "force majeure", "catastrophic",
        ],
        "high": [
            "storm warning", "severe weather", "flooding",
            "monsoon disruption", "gale force", "high seas",
        ],
        "medium": [
            "weather warning", "rough seas", "fog delay",
            "wind advisory", "rain delay",
        ],
    },
    FrictionCategory.TRADE_POLICY: {
        "severe": [
            "trade war", "total ban",
        ],
        "high": [
            "trade policy change", "new tariff", "anti-dumping",
            "countervailing duty", "trade agreement", "brexit",
            "trade restriction",
        ],
        "medium": [
            "trade policy", "trade talks", "trade negotiation",
            "quota", "preferential",
        ],
    },
    FrictionCategory.LABOR_ACTION: {
        "severe": [
            "general strike", "nationwide strike", "indefinite strike",
        ],
        "high": [
            "strike", "walkout", "work stoppage",
            "labor dispute", "industrial action",
        ],
        "medium": [
            "labor", "union", "worker", "overtime ban",
            "go-slow",
        ],
    },
}

# Severity weights for scoring
SEVERITY_WEIGHTS = {
    "severe": 1.0,
    "high": 0.75,
    "medium": 0.5,
    "low": 0.25,
}


class FrictionClassifier:
    """Hybrid classifier: OpenAI for intelligent classification, rules as fallback."""

    def __init__(self):
        self._openai_client = None

    @property
    def openai_client(self):
        """Lazy-load OpenAI client."""
        if self._openai_client is None:
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self._openai_client = OpenAI(api_key=api_key)
            except ImportError:
                pass
        return self._openai_client

    def classify(self, text: str) -> FrictionSignal:
        """Classify text — tries OpenAI first, falls back to rules."""
        # Try OpenAI
        signal = self._classify_openai(text)
        if signal:
            return signal

        # Fallback to rules
        return self._classify_rules(text)

    def _classify_openai(self, text: str) -> Optional[FrictionSignal]:
        """Use OpenAI for intelligent classification."""
        if not self.openai_client:
            return None

        system_prompt = """You are a maritime trade friction analyst. Classify the following news text into exactly one category and severity.

CATEGORIES: customs_friction, port_disruption, sanctions_compliance, conflict_security, weather_force_majeure, trade_policy, labor_action, operational, none
SEVERITIES: severe, high, medium, low

Focus on impact to freight forwarders shipping from: India, Pakistan, Bangladesh, Vietnam, China, Brazil, Mexico, Caribbean, Africa (East/West/South), Turkey → to EU, UK, USA.

Respond ONLY with valid JSON:
{"category": "...", "severity": "...", "confidence": 0.0-1.0, "explanation": "one sentence"}"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text[:500]},  # Limit token usage
                ],
                temperature=0.1,
                max_tokens=100,
            )

            result = json.loads(response.choices[0].message.content)
            return FrictionSignal(
                category=result.get("category", "none"),
                severity=result.get("severity", "low"),
                confidence=float(result.get("confidence", 0.5)),
                explanation=result.get("explanation", ""),
                raw_text=text[:200],
            )
        except Exception as e:
            print(f"[FrictionClassifier] OpenAI error, falling back to rules: {e}")
            return None

    def _classify_rules(self, text: str) -> FrictionSignal:
        """Rule-based classification using weighted keyword matching."""
        text_lower = text.lower()

        best_category = FrictionCategory.NONE
        best_severity = "low"
        best_score = 0
        best_matches = []

        for category, severity_keywords in FRICTION_RULES.items():
            for severity, keywords in severity_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        weight = SEVERITY_WEIGHTS[severity]
                        # Severe matches get a 2x boost to always outrank lower severities
                        severity_boost = 2.0 if severity == "severe" else 1.0
                        score = weight * severity_boost * (1 + len(keyword) / 20)

                        if score > best_score:
                            best_score = score
                            best_category = category
                            best_severity = severity
                            best_matches.append(keyword)

        # Calculate confidence from match quality
        confidence = min(best_score, 1.0) if best_score > 0 else 0.1

        explanation = ""
        if best_matches:
            explanation = f"Matched keywords: {', '.join(best_matches[-3:])}"
        else:
            explanation = "No friction signals detected"

        return FrictionSignal(
            category=best_category.value if isinstance(best_category, FrictionCategory) else best_category,
            severity=best_severity,
            confidence=round(confidence, 2),
            explanation=explanation,
            raw_text=text[:200],
        )
