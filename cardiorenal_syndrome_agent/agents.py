"""Compatibility audit agents for the demonstration threshold interface."""

import uuid
from typing import Any, Dict, List

from .engine import ClinicalDomainEngine
from .models import (
    AgentAlert,
    ClinicalCasePayload,
    ClinicalIntegrityStatus,
    UrgencyLevel,
)


class VenousCongestionScorerAgent:
    def audit(self, case: ClinicalCasePayload) -> List[AgentAlert]:
        result = ClinicalDomainEngine.evaluate_primary_index(case.primary_metric)
        if not result:
            return []
        return [
            AgentAlert(
                alert_id=str(uuid.uuid4())[:8],
                sub_agent="VenousCongestionScorerAgent",
                urgency=UrgencyLevel.WARNING,
                title=result["title"],
                clinical_finding=result["finding"],
                actionable_recommendation=result["recommendation"],
            )
        ]


class CRSClassificationAgent:
    def audit(self, case: ClinicalCasePayload) -> List[AgentAlert]:
        result = ClinicalDomainEngine.evaluate_secondary_kinetics(
            case.secondary_metric, case.is_stat
        )
        if not result:
            return []
        return [
            AgentAlert(
                alert_id=str(uuid.uuid4())[:8],
                sub_agent="CRSClassificationAgent",
                urgency=(
                    UrgencyLevel.STAT_CRITICAL
                    if case.is_stat
                    else UrgencyLevel.WARNING
                ),
                title=result["title"],
                clinical_finding=result["finding"],
                actionable_recommendation=result["recommendation"],
            )
        ]


class DecongestionStrategyAgent:
    def audit(self, case: ClinicalCasePayload) -> List[AgentAlert]:
        result = ClinicalDomainEngine.evaluate_biomarker_concordance(
            case.status_flag, case.biomarkers
        )
        if not result:
            return []
        return [
            AgentAlert(
                alert_id=str(uuid.uuid4())[:8],
                sub_agent="DecongestionStrategyAgent",
                urgency=UrgencyLevel.ADVISORY,
                title=result["title"],
                clinical_finding=result["finding"],
                actionable_recommendation=result["recommendation"],
            )
        ]


class CardioRenalCoordinator:
    def __init__(self):
        self.agent_1 = VenousCongestionScorerAgent()
        self.agent_2 = CRSClassificationAgent()
        self.agent_3 = DecongestionStrategyAgent()
        self.case_registry: Dict[str, Dict[str, Any]] = {}

    def process_case(self, case: ClinicalCasePayload) -> Dict[str, Any]:
        all_alerts: List[AgentAlert] = []
        all_alerts.extend(self.agent_1.audit(case))
        all_alerts.extend(self.agent_2.audit(case))
        all_alerts.extend(self.agent_3.audit(case))

        stat_count = sum(
            alert.urgency == UrgencyLevel.STAT_CRITICAL for alert in all_alerts
        )
        warning_count = sum(
            alert.urgency == UrgencyLevel.WARNING for alert in all_alerts
        )

        if stat_count:
            status = ClinicalIntegrityStatus.CRITICAL_ACTION_REQUIRED
        elif all_alerts:
            status = ClinicalIntegrityStatus.DISCORDANCE_DETECTED
        else:
            status = ClinicalIntegrityStatus.CONCORDANT_NORMAL

        dossier = {
            "system": "cardiorenal-syndrome-agent",
            "mode": "demonstration-threshold-audit",
            "case_id": case.case_id,
            "patient_synthetic_id": case.patient_synthetic_id,
            "overall_status": status.value,
            "total_alerts": len(all_alerts),
            "stat_critical_alerts": stat_count,
            "warning_alerts": warning_count,
            "alerts": [alert.to_dict() for alert in all_alerts],
            "guideline_standard": ClinicalDomainEngine.GUIDELINE,
            "consensus_summary": (
                f"Demonstration audit completed across 3 rule modules with "
                f"status [{status.value}]."
            ),
        }
        self.case_registry[case.case_id] = dossier
        return dossier

    def query_supervisory_chat(self, user_query: str) -> str:
        query = user_query.strip().lower()
        if "status" in query or "summary" in query:
            return (
                f"The local demonstration registry contains "
                f"{len(self.case_registry)} case record(s)."
            )
        if "guideline" in query or "standard" in query:
            return (
                "The CRS type reference follows the ADQI five-type classification; "
                "GFR categories follow KDIGO. The legacy threshold audit is not "
                "clinical guidance."
            )
        return (
            "This repository provides educational CRS classification utilities and "
            "a legacy demonstration threshold audit."
        )
