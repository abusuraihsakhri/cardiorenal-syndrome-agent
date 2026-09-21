"""Optional FastAPI application for the demonstration audit interface."""

from typing import Any, Dict

from .agents import CardioRenalCoordinator
from .models import ClinicalCasePayload


coordinator = CardioRenalCoordinator()


def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel, Field
    except ImportError as exc:
        raise RuntimeError(
            "FastAPI server dependencies are not installed. "
            "Install the 'server' optional dependency."
        ) from exc

    app = FastAPI(
        title="Cardiorenal Syndrome Agent",
        description=(
            "Educational CRS reference utilities plus a retained demonstration "
            "threshold-audit endpoint. Not clinical decision support."
        ),
        version="2.1.0",
    )

    class AuditRequest(BaseModel):
        case_id: str = "CASE-001"
        patient_synthetic_id: str = "SYNTH-01"
        primary_metric: float = 10.0
        secondary_metric: float = 5.0
        status_flag: str = "NORMAL"
        is_stat: bool = False
        clinical_notes: str = ""
        biomarkers: Dict[str, Any] = Field(default_factory=dict)

    class ChatRequest(BaseModel):
        query: str

    @app.get("/health")
    def health():
        return {
            "status": "HEALTHY",
            "service": "cardiorenal-syndrome-agent",
            "version": "2.1.0",
            "clinical_use": "not_for_clinical_decision_support",
        }

    @app.post("/api/audit")
    def api_audit(req: AuditRequest):
        return coordinator.process_case(
            ClinicalCasePayload(
                case_id=req.case_id,
                patient_synthetic_id=req.patient_synthetic_id,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_flag=req.status_flag,
                is_stat=req.is_stat,
                clinical_notes=req.clinical_notes,
                biomarkers=req.biomarkers,
            )
        )

    @app.post("/api/chat")
    def api_chat(req: ChatRequest):
        return {"response": coordinator.query_supervisory_chat(req.query)}

    return app
