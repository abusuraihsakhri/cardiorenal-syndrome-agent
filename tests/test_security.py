from agents.base import AuditTrail


def test_audit_verification_recomputes_hmac():
    trail = AuditTrail(secret_key="unit-test-key")
    trail.log("tester", "test", "EVENT", {"value": 1})
    assert trail.verify_integrity() is True

    trail.logs[0]["event_type"] = "TAMPERED"
    assert trail.verify_integrity() is False


def test_get_trail_does_not_expose_internal_entries():
    trail = AuditTrail(secret_key="unit-test-key")
    trail.log("tester", "test", "EVENT", {"value": 1})
    copied = trail.get_trail()
    copied[0]["event_type"] = "TAMPERED"
    assert trail.verify_integrity() is True
