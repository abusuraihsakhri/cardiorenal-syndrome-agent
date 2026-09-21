import math

import pytest

from biomarker_integration import CardiorenalBiomarkers, integrate_biomarkers
from cardiorenal_syndrome_agent.engine import (
    classify_crs_type,
    kdigo_gfr_category,
    renal_perfusion_pressure,
)
from crs_staging import classify_crs


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (90, "G1"),
        (89.9, "G2"),
        (60, "G2"),
        (59.9, "G3a"),
        (45, "G3a"),
        (44.9, "G3b"),
        (30, "G3b"),
        (29.9, "G4"),
        (15, "G4"),
        (14.9, "G5"),
    ],
)
def test_kdigo_gfr_boundaries(value, expected):
    assert kdigo_gfr_category(value)["category"] == expected


@pytest.mark.parametrize("value", ["1", "2", "3", "4", "5"])
def test_all_crs_types(value):
    result = classify_crs_type(value)
    assert result["crs_type"] == f"CRS_Type_{value}"


def test_invalid_reference_inputs():
    with pytest.raises(ValueError):
        classify_crs_type("9")
    with pytest.raises(ValueError):
        kdigo_gfr_category(-1)
    with pytest.raises(ValueError):
        kdigo_gfr_category(math.inf)


def test_map_minus_cvp_gradient():
    assert renal_perfusion_pressure(80, 15) == 65


def test_legacy_staging_no_longer_invents_prognosis_or_treatment():
    result = classify_crs("4", 44)
    assert result["gfr_category"] == "G3b"
    assert result["risk_score"] is None
    assert result["prognosis"] == "not_calculated"
    assert "No treatment recommendation" in result["management"]


def test_biomarker_context_does_not_create_mortality_score():
    biomarkers = CardiorenalBiomarkers(
        bnp_pg_ml=1200,
        ntproBnp_pg_ml=3000,
        creatinine_mg_dl=2.0,
        egfr=42,
        troponin_ng_ml=0.08,
    )
    result = integrate_biomarkers(biomarkers)
    assert result["renal_function"] == "G3b"
    assert result["mortality_risk"] == "not_calculated"
    assert result["overall_severity_score"] is None
    assert "No treatment recommendation" in result["recommendation"]
