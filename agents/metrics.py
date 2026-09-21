"""In-memory counters with Prometheus text exposition formatting."""

from typing import Dict


class SystemMetricsCollector:
    def __init__(self):
        self.system_name = "cardiorenal-syndrome-agent"
        self.tasks_total = 0
        self.critical_alerts_total = 0
        self.elevated_alerts_total = 0
        self.routine_tasks_total = 0
        self.identifier_blocks_total = 0
        self.audit_blocks_total = 0
        self.processing_latency_sum = 0.0

    def record_task(self, urgency: str, duration_sec: float):
        self.tasks_total += 1
        self.processing_latency_sum += max(0.0, float(duration_sec))
        self.audit_blocks_total += 1
        normalized = str(urgency).upper()
        if "CRITICAL" in normalized:
            self.critical_alerts_total += 1
        elif "ELEVATED" in normalized:
            self.elevated_alerts_total += 1
        else:
            self.routine_tasks_total += 1

    def record_phi_block(self):
        """Compatibility method name for an identifier-pattern block."""
        self.identifier_blocks_total += 1

    @property
    def phi_blocks_total(self) -> int:
        """Compatibility property for older callers."""
        return self.identifier_blocks_total

    def snapshot(self) -> Dict[str, float]:
        return {
            "tasks_total": self.tasks_total,
            "critical_alerts_total": self.critical_alerts_total,
            "elevated_alerts_total": self.elevated_alerts_total,
            "routine_tasks_total": self.routine_tasks_total,
            "identifier_blocks_total": self.identifier_blocks_total,
            "audit_blocks_total": self.audit_blocks_total,
            "processing_latency_avg_seconds": (
                self.processing_latency_sum / max(1, self.tasks_total)
            ),
        }

    def export_prometheus_text(self) -> str:
        values = self.snapshot()
        system = self.system_name
        lines = [
            "# HELP system_tasks_total Demonstration tasks processed",
            "# TYPE system_tasks_total counter",
            f'system_tasks_total{{system="{system}"}} {values["tasks_total"]}',
            "# HELP alerts_triggered_total Demonstration alerts by urgency",
            "# TYPE alerts_triggered_total counter",
            (
                f'alerts_triggered_total{{system="{system}",urgency="critical"}} '
                f'{values["critical_alerts_total"]}'
            ),
            (
                f'alerts_triggered_total{{system="{system}",urgency="elevated"}} '
                f'{values["elevated_alerts_total"]}'
            ),
            (
                f'alerts_triggered_total{{system="{system}",urgency="routine"}} '
                f'{values["routine_tasks_total"]}'
            ),
            "# HELP identifier_pattern_blocks_total Identifier-pattern screening blocks",
            "# TYPE identifier_pattern_blocks_total counter",
            (
                f'identifier_pattern_blocks_total{{system="{system}"}} '
                f'{values["identifier_blocks_total"]}'
            ),
            "# HELP audit_chain_blocks_total In-memory audit records created",
            "# TYPE audit_chain_blocks_total counter",
            (
                f'audit_chain_blocks_total{{system="{system}"}} '
                f'{values["audit_blocks_total"]}'
            ),
            "# HELP task_processing_duration_avg_seconds Average processing duration",
            "# TYPE task_processing_duration_avg_seconds gauge",
            (
                f'task_processing_duration_avg_seconds{{system="{system}"}} '
                f'{values["processing_latency_avg_seconds"]:.6f}'
            ),
            "",
        ]
        return "\n".join(lines)


GLOBAL_METRICS = SystemMetricsCollector()
