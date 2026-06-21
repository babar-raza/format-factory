"""tests/supervisor/test_machinery_audit.py

Tests for tools/supervisor/machinery_audit.py

TC-MACH-WF-001: post-execution audit produces PASS/FAIL_WITH_GAPS verdict
TC-MACH-WF-003: mission completion gate returns MISSION_COMPLETE / MISSION_INCOMPLETE
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from machinery_audit import run_audit, check_mission_complete  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ledger(tmp_path: Path, closed_gaps: list, open_gaps: list,
                 completion_audit_pending: bool = True) -> Path:
    ledger_dir = tmp_path / ".local" / "supervisor" / "machinery"
    ledger_dir.mkdir(parents=True)
    ledger = {
        "mission_id": "test-mission-001",
        "current_iteration": 1,
        "closed_gaps": closed_gaps,
        "open_gaps": open_gaps,
        "completion_audit_pending": completion_audit_pending,
    }
    p = ledger_dir / "mission-ledger.json"
    p.write_text(json.dumps(ledger), encoding="utf-8")
    return tmp_path


def _make_evidence_file(tmp_path: Path, rel_path: str) -> None:
    """Create a dummy evidence file at tmp_path / rel_path."""
    target = tmp_path / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("evidence", encoding="utf-8")


# ===========================================================================
# TC-MACH-WF-001: run_audit()
# ===========================================================================

class TestRunAuditPass:
    """A closed gap with verified evidence produces PASS verdict."""

    def test_closed_gap_with_evidence_passes(self, tmp_path):
        _make_ledger(tmp_path, closed_gaps=["GAP-WF-001"], open_gaps=[])
        # GAP-WF-001 maps to tools/supervisor/machinery_audit.py
        _make_evidence_file(tmp_path, "tools/supervisor/machinery_audit.py")

        result = run_audit(tmp_path, iteration=1)

        assert result["verdict"] == "PASS"
        assert "GAP-WF-001" in result["verified_gaps"]
        assert result["unverified_gaps"] == []

    def test_gap_with_empty_evidence_map_passes(self, tmp_path):
        """GAP-ARCH-013 has no evidence path — treated as verified (unknown gap)."""
        _make_ledger(tmp_path, closed_gaps=["GAP-ARCH-013"], open_gaps=[])

        result = run_audit(tmp_path, iteration=1)

        assert result["verdict"] == "PASS"
        assert "GAP-ARCH-013" in result["verified_gaps"]

    def test_multiple_verified_gaps(self, tmp_path):
        _make_ledger(tmp_path, closed_gaps=["GAP-WF-001", "GAP-WF-003"], open_gaps=[])
        _make_evidence_file(tmp_path, "tools/supervisor/machinery_audit.py")

        result = run_audit(tmp_path, iteration=1)

        assert result["verdict"] == "PASS"
        assert set(result["verified_gaps"]) == {"GAP-WF-001", "GAP-WF-003"}
        assert result["verified_count"] == 2
        assert result["unverified_count"] == 0


class TestRunAuditFailWithGaps:
    """A closed gap whose evidence file is missing produces FAIL_WITH_GAPS."""

    def test_missing_evidence_produces_fail(self, tmp_path):
        _make_ledger(tmp_path, closed_gaps=["GAP-WF-004"], open_gaps=[])
        # Do NOT create the evidence file for GAP-WF-004

        result = run_audit(tmp_path, iteration=1)

        assert result["verdict"] == "FAIL_WITH_GAPS"
        assert "GAP-WF-004" in result["unverified_gaps"]
        assert result["unverified_count"] == 1

    def test_partial_evidence_fail(self, tmp_path):
        """One verified, one not — verdict is FAIL_WITH_GAPS."""
        _make_ledger(tmp_path, closed_gaps=["GAP-WF-001", "GAP-WF-004"], open_gaps=[])
        # Only create evidence for GAP-WF-001
        _make_evidence_file(tmp_path, "tools/supervisor/machinery_audit.py")

        result = run_audit(tmp_path, iteration=1)

        assert result["verdict"] == "FAIL_WITH_GAPS"
        assert "GAP-WF-001" in result["verified_gaps"]
        assert "GAP-WF-004" in result["unverified_gaps"]


class TestRunAuditError:
    """Missing or malformed ledger produces ERROR verdict."""

    def test_missing_ledger_returns_error(self, tmp_path):
        result = run_audit(tmp_path, iteration=1)
        assert result["verdict"] == "ERROR"
        assert "error" in result

    def test_malformed_ledger_returns_error(self, tmp_path):
        ledger_dir = tmp_path / ".local" / "supervisor" / "machinery"
        ledger_dir.mkdir(parents=True)
        (ledger_dir / "mission-ledger.json").write_text("{not valid json{{", encoding="utf-8")

        result = run_audit(tmp_path, iteration=1)
        assert result["verdict"] == "ERROR"


# ===========================================================================
# TC-MACH-WF-003: check_mission_complete()
# ===========================================================================

class TestMissionCompleteGate:

    def test_no_open_gaps_and_no_pending_returns_complete(self, tmp_path):
        _make_ledger(tmp_path, closed_gaps=["GAP-WF-001"], open_gaps=[],
                     completion_audit_pending=False)

        result = check_mission_complete(tmp_path)

        assert result["verdict"] == "MISSION_COMPLETE"
        assert result["open_gaps"] == []

    def test_open_gaps_remain_returns_incomplete(self, tmp_path):
        _make_ledger(tmp_path, closed_gaps=[], open_gaps=["GAP-ARCH-004"],
                     completion_audit_pending=False)

        result = check_mission_complete(tmp_path)

        assert result["verdict"] == "MISSION_INCOMPLETE"
        assert "GAP-ARCH-004" in result["open_gaps"]

    def test_completion_audit_pending_returns_incomplete(self, tmp_path):
        """Even with no open gaps, pending audit means INCOMPLETE."""
        _make_ledger(tmp_path, closed_gaps=["GAP-WF-001"], open_gaps=[],
                     completion_audit_pending=True)

        result = check_mission_complete(tmp_path)

        assert result["verdict"] == "MISSION_INCOMPLETE"

    def test_missing_ledger_returns_incomplete(self, tmp_path):
        result = check_mission_complete(tmp_path)
        assert result["verdict"] == "MISSION_INCOMPLETE"
        assert "ledger missing" in result["reason"]
