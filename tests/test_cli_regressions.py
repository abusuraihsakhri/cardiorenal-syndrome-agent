import csv

import pytest

from cardiorenal_syndrome_agent.cli import main, parse_bool


@pytest.mark.parametrize("value", ["False", "false", "0", "no", "off", ""])
def test_false_csv_values_are_false(value):
    assert parse_bool(value) is False


@pytest.mark.parametrize("value", ["True", "true", "1", "yes", "on"])
def test_true_csv_values_are_true(value):
    assert parse_bool(value) is True


def test_invalid_boolean_is_rejected():
    with pytest.raises(ValueError):
        parse_bool("maybe")


def test_batch_false_string_does_not_trigger_priority(tmp_path):
    source = tmp_path / "source.csv"
    target = tmp_path / "result.csv"
    source.write_text(
        "case_id,patient_synthetic_id,metric_primary,metric_secondary,is_stat,status_flag\n"
        "CASE-1,SYNTH-1,10,5,False,NORMAL\n",
        encoding="utf-8",
    )

    assert main(["batch", "-i", str(source), "-o", str(target)]) == 0

    with target.open(encoding="utf-8", newline="") as handle:
        row = next(csv.DictReader(handle))
    assert row["overall_status"] == "CONCORDANT_NORMAL"
    assert row["stat_critical_alerts"] == "0"


def test_classify_cli_smoke(capsys):
    assert main(["classify", "--crs-type", "1", "--egfr", "55"]) == 0
    output = capsys.readouterr().out
    assert '"crs_type": "CRS_Type_1"' in output
    assert '"category": "G3a"' in output
