#!/usr/bin/env python3
"""
Cardiorenal Biomarker Integration for Cardiorenal Syndrome Agent.
Integrates cardiac and renal biomarkers for comprehensive CRS assessment.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CardiorenalBiomarkers:
    """Biomarkers for cardiorenal syndrome assessment."""
    bnp_pg_ml: float
    ntproBnp_pg_ml: float
    creatinine_mg_dl: float
    egfr: float
    cystatin_c_mg_l: float = 0.0
    troponin_ng_ml: float = 0.0
    galectin_3_ng_ml: float = 0.0
    sstd1_ng_ml: float = 0.0
    klotho_pg_ml: float = 0.0


def integrate_biomarkers(biomarkers: CardiorenalBiomarkers) -> Dict[str, Any]:
    """Integrate cardiac and renal biomarkers."""
    cardiac_stress = "normal"
    if biomarkers.ntproBnp_pg_ml > 5000:
        cardiac_stress = "severe"
    elif biomarkers.ntproBnp_pg_ml > 2000:
        cardiac_stress = "moderate"
    elif biomarkers.ntproBnp_pg_ml > 300:
        cardiac_stress = "mild"

    renal_function = "normal"
    if biomarkers.egfr < 15:
        renal_function = "kidney_failure"
    elif biomarkers.egfr < 30:
        renal_function = "severe_ckd"
    elif biomarkers.egfr < 60:
        renal_function = "moderate_ckd"
    elif biomarkers.egfr < 90:
        renal_function = "mild_ckd"

    fibrosis_risk = "low"
    if biomarkers.galectin_3_ng_ml > 17.8:
        fibrosis_risk = "high"
    elif biomarkers.galectin_3_ng_ml > 12.0:
        fibrosis_risk = "moderate"

    mortality_risk = "low"
    if biomarkers.sstd1_ng_ml > 35:
        mortality_risk = "high"
    elif biomarkers.sstd1_ng_ml > 14:
        mortality_risk = "moderate"

    overall_severity_score = 0
    if cardiac_stress in ("severe", "moderate"):
        overall_severity_score += 2 if cardiac_stress == "severe" else 1
    if renal_function in ("kidney_failure", "severe_ckd"):
        overall_severity_score += 2 if renal_function == "kidney_failure" else 1
    if fibrosis_risk == "high":
        overall_severity_score += 1
    if mortality_risk == "high":
        overall_severity_score += 1

    if overall_severity_score >= 5:
        crs_severity = "very_severe"
        recommendation = "Consider combined heart-kidney transplant evaluation. Palliative care discussion."
    elif overall_severity_score >= 3:
        crs_severity = "severe"
        recommendation = "Intensive diuresis. Consider ultrafiltration. Renal replacement therapy evaluation."
    elif overall_severity_score >= 2:
        crs_severity = "moderate"
        recommendation = "Optimize cardiac therapy. Avoid nephrotoxins. Close monitoring."
    else:
        crs_severity = "mild"
        recommendation = "Standard heart failure therapy. Monitor renal function."

    return {
        "cardiac_stress": cardiac_stress,
        "renal_function": renal_function,
        "fibrosis_risk": fibrosis_risk,
        "mortality_risk": mortality_risk,
        "overall_severity_score": overall_severity_score,
        "crs_severity": crs_severity,
        "recommendation": recommendation,
        "bnp": biomarkers.bnp_pg_ml,
        "egfr": biomarkers.egfr,
    }


class BiomarkerIntegrationAgent:
    """Sub-agent for biomarker integration."""

    def __init__(self):
        self.agent_name = "BiomarkerIntegrationAgent"

    def evaluate(self, biomarkers: CardiorenalBiomarkers) -> Dict[str, Any]:
        """Evaluate biomarker integration."""
        result = integrate_biomarkers(biomarkers)
        alerts = []

        if result["crs_severity"] in ("very_severe", "severe"):
            alerts.append({
                "type": "SEVERE_CRS", "severity": "CRITICAL",
                "message": f"Cardiorenal syndrome {result['crs_severity']} "
                           f"(score: {result['overall_severity_score']}).",
                "recommendation": result["recommendation"]
            })

        if biomarkers.troponin_ng_ml > 0.04:
            alerts.append({
                "type": "ELEVATED_TROPONIN", "severity": "WARNING",
                "message": f"Troponin {biomarkers.troponin_ng_ml:.2f}: myocardial injury.",
                "recommendation": "Assess for acute coronary syndrome or demand ischemia."
            })

        return {"biomarker_result": result, "alerts": alerts}
