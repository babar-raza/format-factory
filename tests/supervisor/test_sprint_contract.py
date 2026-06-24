"""Tests for sprint contract writer + compliance checker.

TC-FL-011: Phase 4 of the feedback loop redesign (pure-knitting-dusk plan).
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from sprint_executor_validate import check_contract_compliance


# ── Helpers ───────────────────────────────────────────────────────────────────

def _write_contract(tmp_path: Path, contracted_items: list[dict]) -> Path:
    contract = {
        "sprint_id": "test-sprint",
        "created_at": "2026-06-24T00:00:00Z",
        "contracted_items": contracted_items,
    }
    contract_dir = tmp_path / ".local" / "supervisor"
    contract_dir.mkdir(parents=True, exist_ok=True)
    contract_path = contract_dir / "sprint-contract.json"
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    return contract_path


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestContractCompliancePass:
    """Declaration has matching gap_ledger_ref -> no warnings."""

    def test_no_warnings(self, tmp_path):
        _write_contract(tmp_path, [
            {"item_id": "WI-GAP-1", "gap_ref": "GAP-CSV-001"},
        ])
        doc = {
            "planned_work_items": [{
                "item_id": "WI-GAP-1",
                "gap_ledger_ref": "GAP-CSV-001",
                "status": "completed",
            }],
        }
        warnings = check_contract_compliance(doc, tmp_path)
        assert len(warnings) == 0


class TestContractComplianceFail:
    """Declaration missing contracted gap_ref -> WARN(CONTRACT-001)."""

    def test_warning_produced(self, tmp_path):
        _write_contract(tmp_path, [
            {"item_id": "WI-GAP-MISSING", "gap_ref": "GAP-MISSING-001"},
        ])
        doc = {
            "planned_work_items": [{
                "item_id": "WI-OTHER",
                "status": "completed",
            }],
        }
        warnings = check_contract_compliance(doc, tmp_path)
        assert len(warnings) == 1
        assert "CONTRACT-001" in warnings[0]
        assert "GAP-MISSING-001" in warnings[0]


class TestNoContractFileNoWarnings:
    """Contract file missing -> graceful skip, no warnings."""

    def test_no_warnings(self, tmp_path):
        doc = {"planned_work_items": []}
        warnings = check_contract_compliance(doc, tmp_path)
        assert len(warnings) == 0


class TestCorruptContractNoCrash:
    """Invalid JSON in contract -> graceful skip."""

    def test_no_crash(self, tmp_path):
        contract_dir = tmp_path / ".local" / "supervisor"
        contract_dir.mkdir(parents=True, exist_ok=True)
        (contract_dir / "sprint-contract.json").write_text("NOT JSON", encoding="utf-8")
        doc = {"planned_work_items": []}
        warnings = check_contract_compliance(doc, tmp_path)
        assert len(warnings) == 0


class TestPartialCompliance:
    """2/3 contracted items addressed -> 1 warning."""

    def test_one_warning(self, tmp_path):
        _write_contract(tmp_path, [
            {"item_id": "WI-1", "gap_ref": "GAP-A"},
            {"item_id": "WI-2", "gap_ref": "GAP-B"},
            {"item_id": "WI-3", "gap_ref": "GAP-C"},
        ])
        doc = {
            "planned_work_items": [
                {"item_id": "WI-1", "gap_ledger_ref": "GAP-A"},
                {"item_id": "WI-2", "gap_ledger_ref": "GAP-B"},
            ],
        }
        warnings = check_contract_compliance(doc, tmp_path)
        assert len(warnings) == 1
        assert "GAP-C" in warnings[0]


class TestGapRefFallback:
    """Declaration uses gap_ref instead of gap_ledger_ref -> still matches."""

    def test_gap_ref_matches(self, tmp_path):
        _write_contract(tmp_path, [
            {"item_id": "WI-1", "gap_ref": "GAP-FALLBACK"},
        ])
        doc = {
            "planned_work_items": [{
                "item_id": "WI-1",
                "gap_ref": "GAP-FALLBACK",
            }],
        }
        warnings = check_contract_compliance(doc, tmp_path)
        assert len(warnings) == 0
