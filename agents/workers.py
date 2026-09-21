"""Compatibility workers for the demonstration threshold audit.

The numeric thresholds in this module are retained for backwards compatibility
only; they are not validated clinical thresholds.
"""

import uuid
from typing import List

from .models import AgentAlert, SystemTaskPayload, UrgencyLevel


class InvariantQCWorker:
    @classmethod
    def evaluate(cls, payload: SystemTaskPayload) -> List[AgentAlert]:
        if payload.primary_metric <= 25.0:
            return []
        return [
            AgentAlert(
                alert_id=f"QC-{uuid.uuid4().hex[:6]}",
                origin_worker="InvariantQCWorker",
                urgency=UrgencyLevel.ELEVATED,
                summary="Configured Primary Threshold Exceeded",
                technical_details=(
                    f"Primary value ({payload.primary_metric:.2f}) exceeds the "
                    "legacy demonstration threshold (25.00)."
                ),
                actionable_remediation="Review the input and threshold configuration.",
            )
        ]


class SafetyEscalationWorker:
    @classmethod
    def evaluate(cls, payload: SystemTaskPayload) -> List[AgentAlert]:
        if not payload.is_critical_flag and payload.secondary_metric <= 12.0:
            return []
        return [
            AgentAlert(
                alert_id=f"SAFE-{uuid.uuid4().hex[:6]}",
                origin_worker="SafetyEscalationWorker",
                urgency=(
                    UrgencyLevel.CRITICAL_STAT
                    if payload.is_critical_flag
                    else UrgencyLevel.ELEVATED
                ),
                summary="Configured Priority Rule Triggered",
                technical_details=(
                    f"PriorityFlag={payload.is_critical_flag} with secondary "
                    f"value {payload.secondary_metric:.2f}."
                ),
                actionable_remediation="Review the input and configured rule.",
            )
        ]


class ProtocolConformanceWorker:
    @classmethod
    def evaluate(cls, payload: SystemTaskPayload) -> List[AgentAlert]:
        descriptor = str(payload.status_descriptor).upper()
        keywords = ("DISCORDANT", "ANOMALY", "VIOLATION", "FAIL", "REJECT")
        if not any(word in descriptor for word in keywords):
            return []
        return [
            AgentAlert(
                alert_id=f"CONF-{uuid.uuid4().hex[:6]}",
                origin_worker="ProtocolConformanceWorker",
                urgency=UrgencyLevel.ELEVATED,
                summary="Descriptor Flagged for Review",
                technical_details=(
                    f"Descriptor '{payload.status_descriptor}' matched a configured "
                    "review keyword."
                ),
                actionable_remediation="Review the source data and descriptor.",
            )
        ]
