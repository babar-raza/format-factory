"""V1: Ledger-driven task selection tests (Design 1 / Phase C).

Verifies that _load_gap_ledger_goals() correctly:
1. Returns spec-grounded gaps when spec_facts present
2. Returns all eligible gaps when require_spec_facts=False (default)
3. Fires expansion_goal_fallback signal when ledger has zero eligible gaps
4. Excludes gaps in exclude_gap_ids
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools/supervisor"))

from autonomous_task_generator import _load_gap_ledger_goals  # noqa: E402


def _write_ledger(tmp_path: Path, gaps: list[dict]) -> Path:
    ledger = tmp_path / "gap-ledger.json"
    ledger.write_text(json.dumps({"gaps": gaps}), encoding="utf-8")
    return ledger


# Patch _GAP_LEDGER_PATH in the module
import autonomous_task_generator as _atg


@pytest.fixture()
def patch_ledger_path(monkeypatch, tmp_path):
    """Factory that writes a ledger to tmp_path and patches the module path."""
    def _patch(gaps):
        p = _write_ledger(tmp_path, gaps)
        monkeypatch.setattr(_atg, "_GAP_LEDGER_PATH", p)
        return p
    return _patch


def _base_gap(gap_id, spec_facts=None):
    return {
        "gap_id": gap_id,
        "format": "CSV",
        "capability_name": f"test_{gap_id.lower().replace('-', '_')}",
        "product_type": "foss_reduced",
        "gap_type": "missing_test_coverage",
        "priority": "P1",
        "status": "open",
        "spec_facts": spec_facts or [],
        "blockers": [],
        "notes": "test note",
    }


class TestLedgerSelection:
    def test_returns_all_eligible_by_default(self, patch_ledger_path):
        """Without require_spec_facts, all eligible gaps are returned."""
        patch_ledger_path([
            _base_gap("GAP-001", spec_facts=["FACT-CSV-001"]),
            _base_gap("GAP-002", spec_facts=[]),
        ])
        goals, spec_available = _load_gap_ledger_goals(require_spec_facts=False)
        gap_ids = {g["gap_id"] for g in goals}
        assert "GAP-001" in gap_ids
        assert "GAP-002" in gap_ids
        assert spec_available is True  # At least one has spec_facts

    def test_require_spec_facts_filters_ungrounded(self, patch_ledger_path):
        """With require_spec_facts=True, only spec-grounded gaps are returned."""
        patch_ledger_path([
            _base_gap("GAP-001", spec_facts=["FACT-CSV-001"]),
            _base_gap("GAP-002", spec_facts=[]),
        ])
        goals, spec_available = _load_gap_ledger_goals(require_spec_facts=True)
        gap_ids = {g["gap_id"] for g in goals}
        assert "GAP-001" in gap_ids
        assert "GAP-002" not in gap_ids
        assert spec_available is True

    def test_no_spec_facts_returns_empty_with_flag(self, patch_ledger_path):
        """When all gaps lack spec_facts and require_spec_facts=True, returns empty list."""
        patch_ledger_path([
            _base_gap("GAP-001", spec_facts=[]),
            _base_gap("GAP-002", spec_facts=[]),
        ])
        goals, spec_available = _load_gap_ledger_goals(require_spec_facts=True)
        assert goals == []
        assert spec_available is False

    def test_exclude_gap_ids_skips_listed(self, patch_ledger_path):
        """Gaps in exclude_gap_ids are not returned."""
        patch_ledger_path([
            _base_gap("GAP-001"),
            _base_gap("GAP-002"),
        ])
        goals, _ = _load_gap_ledger_goals(exclude_gap_ids={"GAP-001"})
        gap_ids = {g["gap_id"] for g in goals}
        assert "GAP-001" not in gap_ids
        assert "GAP-002" in gap_ids

    def test_empty_exclude_set_returns_all(self, patch_ledger_path):
        """Empty exclude set returns all eligible gaps."""
        patch_ledger_path([_base_gap("GAP-001"), _base_gap("GAP-002")])
        goals, _ = _load_gap_ledger_goals(exclude_gap_ids=set())
        assert len(goals) == 2

    def test_missing_ledger_returns_empty(self, monkeypatch, tmp_path):
        """Missing ledger returns ([], False)."""
        monkeypatch.setattr(_atg, "_GAP_LEDGER_PATH", tmp_path / "nonexistent.json")
        goals, spec_available = _load_gap_ledger_goals()
        assert goals == []
        assert spec_available is False

    def test_spec_facts_propagated_to_goal(self, patch_ledger_path):
        """spec_facts field is propagated into the returned goal dict."""
        patch_ledger_path([_base_gap("GAP-001", spec_facts=["FACT-CSV-001", "FACT-CSV-002"])])
        goals, _ = _load_gap_ledger_goals()
        assert goals[0]["spec_facts"] == ["FACT-CSV-001", "FACT-CSV-002"]

    def test_gap_source_is_gap_ledger(self, patch_ledger_path):
        """Returned goals have gap_source='gap_ledger'."""
        patch_ledger_path([_base_gap("GAP-001")])
        goals, _ = _load_gap_ledger_goals()
        assert goals[0]["gap_source"] == "gap_ledger"
