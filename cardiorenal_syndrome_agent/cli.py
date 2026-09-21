"""Command-line interface for the cardiorenal syndrome reference utilities."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from typing import Any

from .agents import CardioRenalCoordinator
from .engine import classify_crs_type, kdigo_gfr_category, renal_perfusion_pressure
from .models import ClinicalCasePayload


coordinator = CardioRenalCoordinator()


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "f", "no", "n", "off", ""}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")


def parse_float(value: Any, default: float, field: str) -> float:
    if value in (None, ""):
        return default
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field} must be finite")
    return result


def _unique_fields(existing: list[str], additions: list[str]) -> list[str]:
    result = list(existing)
    for field in additions:
        if field not in result:
            result.append(field)
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cardiorenal-syndrome-agent",
        description="Educational cardiorenal syndrome classification utilities.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    classify = subparsers.add_parser(
        "classify", help="Classify CRS type and add optional kidney/hemodynamic context"
    )
    classify.add_argument("--crs-type", required=True, help="CRS type: 1, 2, 3, 4, or 5")
    classify.add_argument("--egfr", type=float)
    classify.add_argument("--map", dest="map_mm_hg", type=float)
    classify.add_argument("--cvp", dest="cvp_mm_hg", type=float)

    audit = subparsers.add_parser(
        "audit", help="Run the retained demonstration threshold audit"
    )
    audit.add_argument("--case-id", "--task-id", dest="case_id", default="CASE-001")
    audit.add_argument(
        "--target", dest="synthetic_id", default="SYNTH-01",
        help="Synthetic/non-identifying target label",
    )
    audit.add_argument("--primary", type=float, default=10.0)
    audit.add_argument("--secondary", type=float, default=5.0)
    audit.add_argument("--stat", "--critical", dest="is_stat", action="store_true")
    audit.add_argument("--status", default="NORMAL")

    chat = subparsers.add_parser("chat", help="Show repository scope and references")
    chat.add_argument("query", nargs="+")

    batch = subparsers.add_parser("batch", help="Process demonstration CSV records")
    batch.add_argument("-i", "--input", required=True)
    batch.add_argument("-o", "--output", default="results.csv")

    subparsers.add_parser("verify-audit", help="Verify the in-process audit chain")

    serve = subparsers.add_parser("serve", help="Launch the optional FastAPI server")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

    return parser


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "classify":
        result: dict[str, Any] = {"classification": classify_crs_type(args.crs_type)}
        if args.egfr is not None:
            result["gfr"] = kdigo_gfr_category(args.egfr)
        if (args.map_mm_hg is None) != (args.cvp_mm_hg is None):
            parser.error("--map and --cvp must be provided together")
        if args.map_mm_hg is not None:
            result["map_minus_cvp_mm_hg"] = renal_perfusion_pressure(
                args.map_mm_hg, args.cvp_mm_hg
            )
        result["disclaimer"] = (
            "Educational reference only; not a diagnosis or treatment recommendation."
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    if args.command == "audit":
        case = ClinicalCasePayload(
            case_id=args.case_id,
            patient_synthetic_id=args.synthetic_id,
            primary_metric=args.primary,
            secondary_metric=args.secondary,
            status_flag=args.status,
            is_stat=args.is_stat,
        )
        print(json.dumps(coordinator.process_case(case), indent=2))
        return 0

    if args.command == "chat":
        print(coordinator.query_supervisory_chat(" ".join(args.query)))
        return 0

    if args.command == "verify-audit":
        from agents.base import AuditLogger

        valid = AuditLogger.verify_integrity()
        print(
            f"Audit Trail Blocks: {len(AuditLogger.get_trail())} | "
            f"Integrity Verified: {valid}"
        )
        return 0 if valid else 1

    if args.command == "batch":
        try:
            with open(args.input, mode="r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                fieldnames = list(reader.fieldnames or [])
                if not fieldnames:
                    raise ValueError("Input CSV has no header row")
                rows = list(reader)

            out_fields = _unique_fields(
                fieldnames,
                [
                    "overall_status",
                    "total_alerts",
                    "stat_critical_alerts",
                    "consensus_summary",
                ],
            )
            out_rows = []
            for row_number, row in enumerate(rows, start=2):
                try:
                    case = ClinicalCasePayload(
                        case_id=row.get("case_id") or row.get("task_id") or "CASE-01",
                        patient_synthetic_id=(
                            row.get("patient_synthetic_id")
                            or row.get("target_identifier")
                            or "SYNTH-01"
                        ),
                        primary_metric=parse_float(
                            row.get("metric_primary", row.get("primary_metric")),
                            15.0,
                            "primary metric",
                        ),
                        secondary_metric=parse_float(
                            row.get("metric_secondary", row.get("secondary_metric")),
                            5.0,
                            "secondary metric",
                        ),
                        status_flag=(
                            row.get("status_flag")
                            or row.get("status_text")
                            or row.get("status_descriptor")
                            or "NORMAL"
                        ),
                        is_stat=parse_bool(
                            row.get(
                                "is_stat",
                                row.get(
                                    "critical_flag",
                                    row.get("is_critical_flag", False),
                                ),
                            )
                        ),
                    )
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"Invalid CSV row {row_number}: {exc}") from exc

                dossier = coordinator.process_case(case)
                output = dict(row)
                output["overall_status"] = dossier["overall_status"]
                output["total_alerts"] = dossier["total_alerts"]
                output["stat_critical_alerts"] = dossier["stat_critical_alerts"]
                output["consensus_summary"] = dossier["consensus_summary"]
                out_rows.append(output)

            with open(args.output, mode="w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=out_fields)
                writer.writeheader()
                writer.writerows(out_rows)
            print(f"Processed {len(out_rows)} records -> {args.output}")
            return 0
        except (OSError, ValueError) as exc:
            print(f"Batch error: {exc}", file=sys.stderr)
            return 2

    if args.command == "serve":
        try:
            import uvicorn
        except ImportError:
            print(
                "Server extras are not installed. Run: "
                "pip install 'cardiorenal-syndrome-agent[server]'",
                file=sys.stderr,
            )
            return 1
        from .server import create_app

        uvicorn.run(create_app(), host=args.host, port=args.port)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
