#!/usr/bin/env python3
"""
CRS Staging and Classification for Cardiorenal Syndrome Agent.
Classifies CRS type and stage using Acqua-CRIS criteria.
"""

from typing import Dict, Any, Optional


CRS_TYPES = {
    "CRS_Type_1": {"name": "Acute Cardiorenal", "primary": "heart", "sequence": "heart->kidney"},
    "CRS_Type_2": {"name": "Chronic Cardiorenal", "primary": "heart", "sequence": "heart->kidney"},
    "CRS_Type_3": {"name": "Acute Renocardiac", "primary": "kidney", "sequence": "kidney->heart"},
    "CRS_Type_4": {"name": "Chronic Renocardiac", "primary": "kidney", "sequence": "kidney->heart"},
    "CRS_Type_5": {"name": "Systemic", "primary": "both", "sequence": "systemic"},
}

CRS_STAGES = {
    "A": {"description": "At risk", "egfr_range": ">=60", "biomarkers": "mildly_elevated"},
    "B": {"description": "Mildly decreased", "egfr_range": "60-89", "biomarkers": "moderately_elevated"},
    "C": {"description": "Moderately decreased", "egfr_range": "30-59", "biomarkers": "significantly_elevated"},
    "D": {"description": "Severely decreased", "egfr_range": "15-29", "biomarkers": "severely_elevated"},
    "E": {"description": "Kidney failure", "egfr_range": "<15", "biomarkers": "critically_elevated"},
}


def classify_crs(crs_type: str, egfr: float, bnp: float = 0.0,
                 creatinine: float = 0.0, age: float = 65.0,
                 diabetes: bool = False, hypertension: bool = False) -> Dict[str, Any]:
    """Classify cardiorenal syndrome type and stage."""
    type_info = CRS_TYPES.get(crs_type, CRS_TYPES["CRS_Type_1"])

    if egfr >= 90:
        stage = "A"
    elif egfr >= 60:
        stage = "B"
    elif egfr >= 30:
        stage = "C"
    elif egfr >= 15:
        stage = "D"
    else:
        stage = "E"

    stage_info = CRS_STAGES[stage]

    risk_score = 0
    risk_factors = []

    if egfr < 30:
        risk_score += 3
        risk_factors.append(f"eGFR {egfr:.0f}: severe renal dysfunction")
    elif egfr < 60:
        risk_score += 1
        risk_factors.append(f"eGFR {egfr:.0f}: moderate CKD")

    if bnp > 5000:
        risk_score += 2
        risk_factors.append(f"BNP {bnp:.0f}: severe cardiac stress")
    elif bnp > 1000:
        risk_score += 1
        risk_factors.append(f"BNP {bnp:.0f}: moderate cardiac stress")

    if diabetes:
        risk_score += 1
        risk_factors.append("Diabetes")
    if hypertension:
        risk_score += 1
        risk_factors.append("Hypertension")
    if age > 75:
        risk_score += 1
        risk_factors.append(f"Age {age:.0f}")

    if risk_score >= 5:
        prognosis = "very_poor"
    elif risk_score >= 3:
        prognosis = "poor"
    elif risk_score >= 1:
        prognosis = "guarded"
    else:
        prognosis = "fair"

    if stage in ("D", "E"):
        management = "Prepare for renal replacement therapy. Intensive cardiac management."
    elif stage == "C":
        management = "Aggressive diuresis. Avoid nephrotoxins. Consider specialist referral."
    elif stage == "B":
        management = "Optimize heart failure therapy. Monitor renal function closely."
    else:
        management = "Preventive strategies. Risk factor modification."

    return {
        "crs_type": crs_type,
        "type_name": type_info["name"],
        "stage": stage,
        "stage_description": stage_info["description"],
        "risk_score": risk_score,
        "risk_factors": risk_factors,
        "prognosis": prognosis,
        "management": management,
        "egfr": egfr,
    }


class CRSStagingAgent:
    """Sub-agent for CRS staging."""

    def __init__(self):
        self.agent_name = "CRSStagingAgent"

    def evaluate(self, crs_type: str, egfr: float, bnp: float = 0.0,
                 creatinine: float = 0.0, age: float = 65.0,
                 diabetes: bool = False, hypertension: bool = False) -> Dict[str, Any]:
        """Evaluate CRS staging."""
        result = classify_crs(crs_type, egfr, bnp, creatinine, age, diabetes, hypertension)
        alerts = []

        if result["stage"] in ("D", "E"):
            alerts.append({
                "type": "ADVANCED_CRS", "severity": "CRITICAL",
                "message": f"{result['type_name']} Stage {result['stage']} "
                           f"({result['stage_description']}).",
                "recommendation": result["management"]
            })
        elif result["stage"] == "C":
            alerts.append({
                "type": "MODERATE_CRS", "severity": "WARNING",
                "message": f"{result['type_name']} Stage {result['stage']}.",
                "recommendation": result["management"]
            })

        return {"staging_result": result, "alerts": alerts}
