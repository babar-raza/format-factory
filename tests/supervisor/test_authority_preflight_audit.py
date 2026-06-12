"""
test_authority_preflight_audit.py

Lane M: Verify that authority preflight writes machine-readable JSONL audit entries
for WARN_ALLOW decisions, and that BLOCK decisions do not write entries.

Sprint: FORMAT-FACTORY-SAL-INTEGRATION-HARDENING-SPRINT-2
Added: 2026-06-11
Gap closed: GAP-11 (exception audit trail)
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from product_source_executor import run_authority_preflight, _REPO_ROOT


def _mock_auth(level_int: int):
    return {
        "authority_level": f"P{level_int}",
        "authority_level_int": level_int,
        "product_expansion_allowed": level_int >= 4,
        "exception_allowed": None,
        "readiness_allowed": level_int >= 4,
    }


def _item(format_id: str, exception_classification: str = "") -> dict:
    return {
        "action_id": "AUDIT-TEST-001",
        "item_id": "AUDIT-ITEM-001",
        "item_type": "PRODUCT_SOURCE",
        "format_id": format_id,
        "target_path": f"src/python/{format_id}/{format_id}_codec.py",
        "exception_classification": exception_classification,
        "spec_fact_refs": [],
    }


class TestWarnAllowWritesAuditLog:
    """WARN_ALLOW decisions write a JSONL audit entry."""

    def test_warn_allow_writes_audit_log(self, tmp_path):
        """When WARN_ALLOW fires, an entry is written to authority-preflight-log.jsonl."""
        audit_log = tmp_path / "authority-preflight-log.jsonl"
        item = _item("abw", exception_classification="no_public_spec_available")

        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(1)), \
             patch("product_source_executor._REPO_ROOT", tmp_path):
            # Ensure .local/supervisor directory exists
            (tmp_path / ".local" / "supervisor").mkdir(parents=True, exist_ok=True)
            result = run_authority_preflight(item)

        # Sprint 2: WARN_ALLOW promoted to ALLOW for valid exceptions
        assert result["decision"] == "ALLOW", (
            f"Expected ALLOW (Sprint 2 — exceptions now return ALLOW), got {result['decision']}"
        )
        log_path = tmp_path / ".local" / "supervisor" / "authority-preflight-log.jsonl"
        assert log_path.exists(), f"Audit log should exist at {log_path}"
        lines = [l.strip() for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) >= 1, "At least one audit entry should be written"
        entry = json.loads(lines[-1])
        # Audit log records ALLOW_WITH_EXCEPTION to distinguish from unconditional ALLOW
        assert entry["decision"] == "ALLOW_WITH_EXCEPTION"
        assert entry["format_id"] == "abw"
        assert entry["exception"] == "no_public_spec_available"

    def test_audit_log_contains_format_and_exception(self, tmp_path):
        """Audit entry must contain format_id, exception, authority_level, item_id, ts."""
        item = _item("dif", exception_classification="empirical_authority_with_limits")
        item["item_id"] = "AUDIT-DIF-001"

        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(1)), \
             patch("product_source_executor._REPO_ROOT", tmp_path):
            (tmp_path / ".local" / "supervisor").mkdir(parents=True, exist_ok=True)
            result = run_authority_preflight(item)

        # Sprint 2: exception path returns ALLOW
        assert result["decision"] == "ALLOW"
        log_path = tmp_path / ".local" / "supervisor" / "authority-preflight-log.jsonl"
        assert log_path.exists()
        entry = json.loads(log_path.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert entry.get("format_id") == "dif"
        assert entry.get("exception") == "empirical_authority_with_limits"
        assert "authority_level" in entry
        assert "ts" in entry
        assert entry.get("item_id") == "AUDIT-DIF-001"

    def test_multiple_allow_with_exception_writes_multiple_entries(self, tmp_path):
        """Each ALLOW_WITH_EXCEPTION appends a new entry; log grows incrementally."""
        (tmp_path / ".local" / "supervisor").mkdir(parents=True, exist_ok=True)
        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(1)), \
             patch("product_source_executor._REPO_ROOT", tmp_path):
            for i in range(3):
                item = _item("tsv", exception_classification="no_public_spec_available")
                item["item_id"] = f"MULTI-{i}"
                run_authority_preflight(item)

        log_path = tmp_path / ".local" / "supervisor" / "authority-preflight-log.jsonl"
        lines = [l for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == 3, f"Expected 3 audit entries, got {len(lines)}"


class TestBlockDoesNotWriteAuditLog:
    """BLOCK decisions do not write audit entries (blocked before exception logic)."""

    def test_block_does_not_write_audit_log(self, tmp_path):
        """BLOCK (no exception) must not write to audit log."""
        (tmp_path / ".local" / "supervisor").mkdir(parents=True, exist_ok=True)
        item = _item("sylk")  # no exception_classification

        with patch("authority_gate_validation.validate_format_authority",
                   return_value=_mock_auth(1)), \
             patch("product_source_executor._REPO_ROOT", tmp_path):
            result = run_authority_preflight(item)

        assert result["decision"] == "BLOCK", (
            f"Expected BLOCK, got {result['decision']}"
        )
        log_path = tmp_path / ".local" / "supervisor" / "authority-preflight-log.jsonl"
        if log_path.exists():
            lines = [l for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
            exc_entries = [l for l in lines if json.loads(l).get("decision") == "ALLOW_WITH_EXCEPTION"]
            assert len(exc_entries) == 0, "BLOCK should not produce ALLOW_WITH_EXCEPTION audit entries"
        # Log may not exist at all — that's fine for BLOCK
