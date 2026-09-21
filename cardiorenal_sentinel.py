#!/usr/bin/env python3
"""Compatibility facade for earlier cardiorenal_sentinel imports."""

from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict, List

from cardiorenal_syndrome_agent.cli import main
from cardiorenal_syndrome_agent.engine import ClinicalDomainEngine
from cardiorenal_syndrome_agent.server import create_app


class Severity(str):
    INFO = "INFO"
    ADVISORY = "ADVISORY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL_ACTION_REQUIRED"


class DomainKnowledgeRegistry:
    SYSTEM_VERSION = "2.1.0"
    ZERO_PHI_COMPLIANCE = False
    IDENTIFIER_SCREENING_MODE = "heuristic"

    @staticmethod
    def audit_security_and_integrity(payload: Dict[str, Any]) -> List[str]:
        warnings = []
        for key in payload:
            if any(
                token in key.lower()
                for token in ("patient_name", "ssn", "mrn_raw", "dob_raw")
            ):
                warnings.append(
                    f"IDENTIFIER_PATTERN_WARNING: key '{key}' may contain a direct "
                    "identifier; do not submit identifiable data."
                )
        return warnings


class AgentAlert:
    def __init__(
        self,
        alert_id: str,
        agent_name: str,
        severity: str,
        title: str,
        details: str,
        recommendation: str,
    ):
        self.alert_id = alert_id
        self.agent_name = agent_name
        self.severity = severity
        self.title = title
        self.details = details
        self.recommendation = recommendation
        self.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "agent": self.agent_name,
            "severity": self.severity,
            "title": self.title,
            "details": self.details,
            "recommendation": self.recommendation,
            "timestamp": self.timestamp,
        }


class VenousCongestionScorerAgent:
    def evaluate(self, payload: Dict[str, Any]) -> List[AgentAlert]:
        result = ClinicalDomainEngine.evaluate_primary_index(
            float(payload.get("metric_primary", 15.0))
        )
        if not result:
            return []
        return [
            AgentAlert(
                str(uuid.uuid4())[:8],
                "VenousCongestionScorerAgent",
                Severity.WARNING,
                result["title"],
                result["finding"],
                result["recommendation"],
            )
        ]


class CRSClassificationAgent:
    def evaluate(self, payload: Dict[str, Any]) -> List[AgentAlert]:
        result = ClinicalDomainEngine.evaluate_secondary_kinetics(
            float(payload.get("metric_secondary", 5.0)),
            bool(payload.get("critical_flag", False)),
        )
        if not result:
            return []
        return [
            AgentAlert(
                str(uuid.uuid4())[:8],
                "CRSClassificationAgent",
                Severity.CRITICAL
                if bool(payload.get("critical_flag", False))
                else Severity.WARNING,
                result["title"],
                result["finding"],
                result["recommendation"],
            )
        ]


class DecongestionStrategyAgent:
    def evaluate(self, payload: Dict[str, Any]) -> List[AgentAlert]:
        result = ClinicalDomainEngine.evaluate_biomarker_concordance(
            str(payload.get("status_text", "NORMAL")), {}
        )
        if not result:
            return []
        return [
            AgentAlert(
                str(uuid.uuid4())[:8],
                "DecongestionStrategyAgent",
                Severity.ADVISORY,
                result["title"],
                result["finding"],
                result["recommendation"],
            )
        ]


class CardioRenalCoordinator:
    def __init__(self):
        self.sub_agent_1 = VenousCongestionScorerAgent()
        self.sub_agent_2 = CRSClassificationAgent()
        self.sub_agent_3 = DecongestionStrategyAgent()
        self.case_registry: Dict[str, Dict[str, Any]] = {}

    def audit_case(self, case_payload: Dict[str, Any]) -> Dict[str, Any]:
        case_id = str(
            case_payload.get("case_id", f"CASE-{uuid.uuid4().hex[:6].upper()}")
        )
        alerts = []
        alerts.extend(self.sub_agent_1.evaluate(case_payload))
        alerts.extend(self.sub_agent_2.evaluate(case_payload))
        alerts.extend(self.sub_agent_3.evaluate(case_payload))

        critical_count = sum(
            alert.severity == Severity.CRITICAL for alert in alerts
        )
        warning_count = sum(alert.severity == Severity.WARNING for alert in alerts)
        if critical_count:
            status = "CRITICAL_ACTION_REQUIRED"
        elif warning_count:
            status = "WARNING_ACTIVE"
        else:
            status = "CONCORDANT_NORMAL"

        dossier = {
            "system": "cardiorenal-syndrome-agent",
            "mode": "demonstration-threshold-audit",
            "case_id": case_id,
            "overall_status": status,
            "total_alerts": len(alerts),
            "critical_count": critical_count,
            "warning_count": warning_count,
            "alerts": [alert.to_dict() for alert in alerts],
            "consensus_summary": (
                f"Demonstration rules completed with status [{status}]."
            ),
            "timestamp": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
        }
        self.case_registry[case_id] = dossier
        return dossier

    def query_assistant(self, user_query: str) -> str:
        query = user_query.strip().lower()
        if "summary" in query or "status" in query:
            return (
                f"Local demonstration registry contains "
                f"{len(self.case_registry)} case record(s)."
            )
        if "guideline" in query or "protocol" in query:
            return (
                "No treatment guidelines are implemented. The reference "
                "classification follows ADQI CRS types and KDIGO GFR categories."
            )
        return (
            "Cardiorenal syndrome educational reference utilities are available; "
            "the retained threshold audit is demonstrative only."
        )


coordinator = CardioRenalCoordinator()
