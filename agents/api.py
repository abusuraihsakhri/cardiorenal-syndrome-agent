"""Optional FastAPI interface for the legacy demonstration audit."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .base import AuditLogger, SecurityException
from .models import SystemTaskPayload
from .supervisor import SystemSupervisor


supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Cardiorenal Syndrome Agent",
    description=(
        "Legacy demonstration threshold audit. "
        "Not a clinical decision-support service."
    ),
    version="2.1.0",
)


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


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    return supervisor.process_task(payload).to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        return {"response": supervisor.query_supervisory_chat(req.query)}
    except (SecurityException, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/audit/logs")
def api_audit_logs():
    return {
        "audit_trail": AuditLogger.get_trail(),
        "verified": AuditLogger.verify_integrity(),
    }
