"""Identifier screening and a small in-memory HMAC audit chain.

The identifier screen is a defensive heuristic, not a HIPAA compliance control.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


IDENTIFIER_PATTERNS = [
    re.compile(r"\b(?:MRN)[:#\s-]*\d{4,10}\b", re.IGNORECASE),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(
        r"\b(?:DOB|Date of Birth)[:\s]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:Patient\s+Name|Patient)[:\s]+[A-Z][a-z]+\s+[A-Z][a-z]+\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:John\s+Doe|Jane\s+Smith|Alice\s+Johnson)\b", re.IGNORECASE),
]


class SecurityException(Exception):
    """Raised when the heuristic identifier screen detects a sensitive pattern."""


class ResourceLimitExceededException(Exception):
    """Retained compatibility exception for callers that impose resource limits."""


def assert_no_phi(text: str) -> None:
    """Reject text matching common direct-identifier patterns.

    This is intentionally conservative and incomplete. It must not be described
    or relied upon as de-identification, Safe Harbor certification, or HIPAA
    compliance.
    """

    if not text:
        return
    for pattern in IDENTIFIER_PATTERNS:
        if pattern.search(str(text)):
            raise SecurityException(
                "Identifier screening blocked content matching a sensitive pattern"
            )


class PHIGuard:
    @staticmethod
    def assert_no_phi(text: str) -> None:
        assert_no_phi(text)

    @staticmethod
    def redact_phi(text: str) -> str:
        result = str(text)
        for pattern in IDENTIFIER_PATTERNS:
            result = pattern.sub("[REDACTED_IDENTIFIER]", result)
        return result


class AuditTrail:
    """In-memory chained HMAC-SHA256 log.

    A process-local random key is generated when no explicit key or
    AUDIT_SECRET_KEY is provided. Persisted verification across process restarts
    therefore requires a caller-supplied secret.
    """

    GENESIS_HASH = "GENESIS_BLOCK_0000000000000000"

    def __init__(self, secret_key: Optional[str] = None):
        configured = secret_key or os.getenv("AUDIT_SECRET_KEY")
        self.secret_key = (
            configured.encode("utf-8") if configured else secrets.token_bytes(32)
        )
        self.logs: List[Dict[str, Any]] = []

    def _signature_for(self, entry: Dict[str, Any]) -> str:
        sign_string = "|".join(
            [
                str(entry["audit_id"]),
                str(entry["timestamp"]),
                str(entry["actor"]),
                str(entry["actor_tier"]),
                str(entry["event_type"]),
                str(entry["payload_hash"]),
                str(entry["prev_hash"]),
            ]
        )
        return hmac.new(
            self.secret_key, sign_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def log(
        self,
        actor: str,
        actor_tier: str,
        event_type: str,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:
        payload_str = json.dumps(details, sort_keys=True, separators=(",", ":"))
        assert_no_phi(payload_str)
        payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        audit_id = f"AUDIT-{int(time.time() * 1000)}-{len(self.logs) + 1}"
        timestamp = datetime.now(timezone.utc).isoformat()
        prev_hash = (
            self.logs[-1]["current_hash"] if self.logs else self.GENESIS_HASH
        )
        entry = {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "actor": actor,
            "actor_tier": actor_tier,
            "event_type": event_type,
            "payload_hash": payload_hash,
            "prev_hash": prev_hash,
        }
        entry["current_hash"] = self._signature_for(entry)
        self.logs.append(entry)
        return dict(entry)

    def verify_integrity(self) -> bool:
        try:
            for index, entry in enumerate(self.logs):
                expected_prev = (
                    self.logs[index - 1]["current_hash"]
                    if index > 0
                    else self.GENESIS_HASH
                )
                if entry["prev_hash"] != expected_prev:
                    return False
                expected_signature = self._signature_for(entry)
                if not hmac.compare_digest(
                    expected_signature, str(entry["current_hash"])
                ):
                    return False
            return True
        except (KeyError, TypeError, ValueError):
            return False

    def get_trail(self) -> List[Dict[str, Any]]:
        return [dict(entry) for entry in self.logs]


GLOBAL_AUDIT = AuditTrail()


class AuditLogger:
    @staticmethod
    def log(
        actor: str,
        actor_tier: str,
        event_type: str,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:
        return GLOBAL_AUDIT.log(actor, actor_tier, event_type, details)

    @staticmethod
    def get_trail() -> List[Dict[str, Any]]:
        return GLOBAL_AUDIT.get_trail()

    @staticmethod
    def verify_integrity() -> bool:
        return GLOBAL_AUDIT.verify_integrity()


class ActionExecutor:
    @staticmethod
    def execute_with_audit(
        actor: str, actor_tier: str, action_type: str, fn, *args, **kwargs
    ):
        result = fn(*args, **kwargs)
        AuditLogger.log(actor, actor_tier, action_type, {"status": "SUCCESS"})
        return result
