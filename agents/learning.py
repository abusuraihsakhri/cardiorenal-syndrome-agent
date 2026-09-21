"""Small feedback-weight tracker retained for compatibility.

This module records explicit caller feedback. It does not train a model and does
not implement autonomous or Bayesian learning.
"""

from typing import Any, Dict, List

from pydantic import BaseModel


class WorkerPerformanceMetric(BaseModel):
    worker_name: str
    total_evaluations: int = 0
    concordant_decisions: int = 0
    dynamic_weight: float = 1.0


class ActiveLearningEngine:
    """Compatibility name for an explicit feedback-weight tracker."""

    def __init__(self, system_name: str = "Cardiorenal Syndrome Agent"):
        self.system_name = system_name
        self.worker_metrics: Dict[str, WorkerPerformanceMetric] = {
            name: WorkerPerformanceMetric(worker_name=name)
            for name in (
                "InvariantQCWorker",
                "SafetyEscalationWorker",
                "ProtocolConformanceWorker",
            )
        }
        self.uncertainty_buffer: List[Dict[str, Any]] = []

    def record_feedback(
        self, worker_name: str, was_concordant: bool, confidence_score: float
    ):
        if not 0.0 <= float(confidence_score) <= 1.0:
            raise ValueError("confidence_score must be between 0 and 1")
        metric = self.worker_metrics.setdefault(
            worker_name, WorkerPerformanceMetric(worker_name=worker_name)
        )
        metric.total_evaluations += 1
        if was_concordant:
            metric.concordant_decisions += 1

        observed_fraction = metric.concordant_decisions / metric.total_evaluations
        metric.dynamic_weight = round(
            max(0.2, min(1.5, observed_fraction * 1.5)), 3
        )

        if 0.45 <= confidence_score <= 0.65:
            self.uncertainty_buffer.append(
                {
                    "worker": worker_name,
                    "confidence": confidence_score,
                    "concordant": was_concordant,
                }
            )

    def get_calibrated_weights(self) -> Dict[str, float]:
        return {
            name: metric.dynamic_weight
            for name, metric in self.worker_metrics.items()
        }


GLOBAL_LEARNING_ENGINE = ActiveLearningEngine()
