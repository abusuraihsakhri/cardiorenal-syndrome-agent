"""Pydantic models for the retained demonstration audit interface."""

import datetime
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field


DEMONSTRATION_STANDARD = "Demonstration rule set; not clinical guidance"


class UrgencyLevel(str, Enum):
    ROUTINE = "ROUTINE"
    ELEVATED = "ELEVATED_RISK"
    CRITICAL_STAT = "CRITICAL_STAT_PANIC"


class SystemIntegrityStatus(str, Enum):
    VALIDATED = "VALIDATED_OPTIMAL"
    DISCORDANT = "DISCORDANT_ANOMALY"
    RECALIBRATION_REQUIRED = "RECALIBRATION_REQUIRED"


class SystemTaskPayload(BaseModel):
    task_id: str = Field(..., description="Unique task/case identifier")
    target_identifier: str = Field(
        ..., description="Synthetic or non-identifying target label"
    )
    primary_metric: float = Field(..., description="Demonstration primary metric")
    secondary_metric: float = Field(
        default=0.0, description="Demonstration secondary metric"
    )
    status_descriptor: str = Field(default="NOMINAL", description="Status descriptor")
    is_critical_flag: bool = Field(
        default=False, description="Demonstration priority flag"
    )
    attributes: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat()
    )


class AgentAlert(BaseModel):
    alert_id: str
    origin_worker: str
    urgency: UrgencyLevel
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = DEMONSTRATION_STANDARD
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ConsensusDossier(BaseModel):
    dossier_id: str
    system_slug: str = "cardiorenal-syndrome-agent"
    domain: str = "Demonstration threshold audit"
    task_id: str
    target_identifier: str
    overall_urgency: UrgencyLevel
    integrity_status: SystemIntegrityStatus
    total_alerts: int
    critical_alerts_count: int
    alerts: List[AgentAlert]
    standard_reference: str = DEMONSTRATION_STANDARD
    consensus_summary: str
    audit_hash: str
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
