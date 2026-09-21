"""Transparent rule utilities used by the package and browser reference app."""

from __future__ import annotations

import math
from typing import Any, Dict, Optional


CRS_TYPES: Dict[str, Dict[str, str]] = {
    "CRS_Type_1": {
        "label": "Type 1 — Acute cardiorenal syndrome",
        "primary_process": "Acute cardiac dysfunction",
        "secondary_process": "Acute kidney injury or dysfunction",
    },
    "CRS_Type_2": {
        "label": "Type 2 — Chronic cardiorenal syndrome",
        "primary_process": "Chronic cardiac dysfunction",
        "secondary_process": "Kidney injury or dysfunction",
    },
    "CRS_Type_3": {
        "label": "Type 3 — Acute renocardiac syndrome",
        "primary_process": "Acute kidney dysfunction",
        "secondary_process": "Acute cardiac injury or dysfunction",
    },
    "CRS_Type_4": {
        "label": "Type 4 — Chronic renocardiac syndrome",
        "primary_process": "Chronic kidney disease",
        "secondary_process": "Cardiac injury, disease, or dysfunction",
    },
    "CRS_Type_5": {
        "label": "Type 5 — Secondary cardiorenal syndrome",
        "primary_process": "Systemic disorder",
        "secondary_process": "Simultaneous cardiac and kidney injury or dysfunction",
    },
}

GFR_CATEGORIES = (
    ("G1", 90.0, None, "Normal or high"),
    ("G2", 60.0, 90.0, "Mildly decreased"),
    ("G3a", 45.0, 60.0, "Mildly to moderately decreased"),
    ("G3b", 30.0, 45.0, "Moderately to severely decreased"),
    ("G4", 15.0, 30.0, "Severely decreased"),
    ("G5", 0.0, 15.0, "Kidney failure"),
)


def _finite_number(value: float, name: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number")
    return number


def normalize_crs_type(value: str) -> str:
    raw = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "1": "CRS_Type_1",
        "type_1": "CRS_Type_1",
        "crs_1": "CRS_Type_1",
        "crs_type_1": "CRS_Type_1",
        "2": "CRS_Type_2",
        "type_2": "CRS_Type_2",
        "crs_2": "CRS_Type_2",
        "crs_type_2": "CRS_Type_2",
        "3": "CRS_Type_3",
        "type_3": "CRS_Type_3",
        "crs_3": "CRS_Type_3",
        "crs_type_3": "CRS_Type_3",
        "4": "CRS_Type_4",
        "type_4": "CRS_Type_4",
        "crs_4": "CRS_Type_4",
        "crs_type_4": "CRS_Type_4",
        "5": "CRS_Type_5",
        "type_5": "CRS_Type_5",
        "crs_5": "CRS_Type_5",
        "crs_type_5": "CRS_Type_5",
    }
    if raw not in aliases:
        raise ValueError("CRS type must be one of 1, 2, 3, 4, or 5")
    return aliases[raw]


def classify_crs_type(value: str) -> Dict[str, str]:
    key = normalize_crs_type(value)
    return {"crs_type": key, **CRS_TYPES[key]}


def kdigo_gfr_category(egfr: float) -> Dict[str, Any]:
    """Return the KDIGO GFR category for an eGFR value.

    A GFR category alone does not diagnose CKD. CKD requires chronicity and/or
    other markers of kidney damage.
    """

    value = _finite_number(egfr, "eGFR")
    if value < 0:
        raise ValueError("eGFR must be non-negative")

    for category, lower, upper, description in GFR_CATEGORIES:
        if value >= lower and (upper is None or value < upper):
            return {
                "category": category,
                "description": description,
                "egfr": value,
                "unit": "mL/min/1.73 m²",
                "ckd_note": (
                    "GFR category alone does not establish CKD; chronicity and "
                    "other markers of kidney damage must be considered."
                ),
            }
    raise RuntimeError("Unable to categorize eGFR")


def renal_perfusion_pressure(map_mm_hg: float, cvp_mm_hg: float) -> float:
    """Return the simple MAP - CVP pressure gradient approximation."""

    map_value = _finite_number(map_mm_hg, "MAP")
    cvp_value = _finite_number(cvp_mm_hg, "CVP")
    return round(map_value - cvp_value, 2)


class ClinicalDomainEngine:
    """Legacy threshold interface retained for compatibility.

    These thresholds are demonstration rules only. They are not validated
    diagnostic thresholds and must not be used to direct patient care.
    """

    PRIMARY_BASELINE_LIMIT = 20.0
    SECONDARY_ALERT_LIMIT = 10.0
    GUIDELINE = "Demonstration rule set; not clinical guidance"

    @classmethod
    def evaluate_primary_index(cls, value: float) -> Optional[Dict[str, Any]]:
        value = _finite_number(value, "primary metric")
        if value > cls.PRIMARY_BASELINE_LIMIT:
            return {
                "title": "Configured Primary Threshold Exceeded",
                "finding": (
                    f"Observed value ({value:.2f}) exceeds the demonstration "
                    f"threshold ({cls.PRIMARY_BASELINE_LIMIT:.1f})."
                ),
                "recommendation": "Review the input and configured threshold.",
            }
        return None

    @classmethod
    def evaluate_secondary_kinetics(
        cls, value: float, is_stat: bool
    ) -> Optional[Dict[str, Any]]:
        value = _finite_number(value, "secondary metric")
        if value > cls.SECONDARY_ALERT_LIMIT or bool(is_stat):
            return {
                "title": "Configured Secondary Rule Triggered",
                "finding": (
                    f"Secondary value ({value:.2f}) or priority flag triggered "
                    "the demonstration rule."
                ),
                "recommendation": "Review the input and configured rule.",
            }
        return None

    @classmethod
    def evaluate_biomarker_concordance(
        cls, status_flag: str, biomarkers: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        del biomarkers
        status_upper = str(status_flag).upper()
        if any(word in status_upper for word in ("DISCORDANT", "EQUIVOCAL")):
            return {
                "title": "Descriptor Flagged for Review",
                "finding": f"Status flag '{status_flag}' matched a review keyword.",
                "recommendation": "Review the source data and descriptor.",
            }
        return None
