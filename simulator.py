"""Local stress test for the retained demonstration audit interface."""

import random
import sys
import time

from agents.base import AuditLogger, PHIGuard, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor


def run_simulation(iterations: int = 100, seed: int = 2026):
    if iterations <= 0:
        raise ValueError("iterations must be positive")

    rng = random.Random(seed)
    print(
        f"Starting local demonstration simulation "
        f"({iterations} tasks, seed={seed})..."
    )
    supervisor = SystemSupervisor(model_provider="mock")
    start_time = time.time()
    nominal_count = 0
    elevated_count = 0
    critical_count = 0
    identifier_blocks = 0

    for index in range(iterations):
        payload = SystemTaskPayload(
            task_id=f"SIM-{index + 1:04d}",
            target_identifier=f"SYNTH-{rng.randint(100, 999)}",
            primary_metric=round(rng.uniform(5.0, 40.0), 2),
            secondary_metric=round(rng.uniform(1.0, 20.0), 2),
            status_descriptor=rng.choice(
                ["NOMINAL", "DISCORDANT_ANOMALY", "REVIEW", "OPTIMAL"]
            ),
            is_critical_flag=rng.random() < 0.15,
        )

        dossier = supervisor.process_task(payload)
        if dossier.overall_urgency.value == "CRITICAL_STAT_PANIC":
            critical_count += 1
        elif dossier.overall_urgency.value == "ELEVATED_RISK":
            elevated_count += 1
        else:
            nominal_count += 1

        if (index + 1) % 25 == 0:
            try:
                PHIGuard.assert_no_phi(
                    f"Patient John Doe MRN-{rng.randint(100000, 999999)} test"
                )
            except SecurityException:
                identifier_blocks += 1

    elapsed = time.time() - start_time
    print("=" * 68)
    print(f"Tasks: {iterations}")
    print(f"Elapsed: {elapsed:.3f} s")
    print(f"Routine: {nominal_count}")
    print(f"Elevated: {elevated_count}")
    print(f"Critical-priority: {critical_count}")
    print(f"Identifier-pattern blocks in injected checks: {identifier_blocks}")
    print(f"Audit blocks: {len(AuditLogger.get_trail())}")
    print(f"Audit chain verifies: {AuditLogger.verify_integrity()}")
    print("=" * 68)


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    run_simulation(count)
