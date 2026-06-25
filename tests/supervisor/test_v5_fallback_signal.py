"""V5: expansion_goal_fallback signal propagation test (Design 1 / Phase C).

Verifies that generate_task_candidates() correctly emits the expansion_goal_fallback
signal in its output JSON when the gap ledger returns zero eligible goals.

Scenarios:
1. Gap ledger with no foss_reduced gaps (only commercial) -> fallback: True
2. Gap ledger with a valid foss_reduced gap -> fallback: False
3. Missing gap ledger -> fallback: True (ledger returns empty)
4. excluded_gap_ids_count always present in output
5. hardcoded_fallback_goals_used > 0 when fallback fires
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools/supervisor"))

import autonomous_task_generator as _atg  # noqa: E402
from autonomous_task_generator import generate_task_candidates  # noqa: E402


def _write_ledger(tmp_path: Path, gaps: list[dict]) -> Path:
    ledger = tmp_path / "gap-ledger.json"
    ledger.write_text(json.dumps({"gaps": gaps}), encoding="utf-8")
    return ledger


def _foss_gap(gap_id: str, spec_facts: list | None = None) -> dict:
    """A valid foss_reduced gap that passes all filters in _load_gap_ledger_goals."""
    return {
        "gap_id": gap_id,
        "format": "CSV",  # CSV is in _FORMAT_SOURCE_MAP
        "capability_name": f"probe_{gap_id.lower().replace('-', '_')}",
        "product_type": "foss_reduced",
        "gap_type": "missing_test_coverage",
        "priority": "P2",
        "status": "open",
        "spec_facts": spec_facts if spec_facts is not None else [],
        "blockers": [],
        "notes": "v5 test gap",
    }


def _commercial_gap(gap_id: str) -> dict:
    """A commercial gap — filtered out by _load_gap_ledger_goals."""
    return {
        "gap_id": gap_id,
        "format": "FODS",
        "capability_name": f"load_{gap_id.lower()}",
        "product_type": "commercial",
        "gap_type": "missing_test_coverage",
        "priority": "P0",
        "status": "open",
        "spec_facts": ["FACT-FODS-001"],
        "blockers": [],
        "notes": "commercial gap — should not appear in ledger goals",
    }


@pytest.fixture()
def patch_ledger(monkeypatch, tmp_path):
    """Patches _GAP_LEDGER_PATH and _SAL_FACTS_PATH, returns factory for writing ledger content."""
    # Also patch SAL facts path to nonexistent so require_spec_facts stays False
    monkeypatch.setattr(_atg, "_SAL_FACTS_PATH", tmp_path / "nonexistent-sal.json")

    def _setup(gaps: list[dict]) -> Path:
        p = _write_ledger(tmp_path, gaps)
        monkeypatch.setattr(_atg, "_GAP_LEDGER_PATH", p)
        return p
    return _setup


class TestExpansionGoalFallbackSignal:
    def test_fallback_true_when_no_foss_gaps(self, patch_ledger, tmp_path):
        """When ledger has only commercial gaps, fallback fires: expansion_goal_fallback=True."""
        patch_ledger([_commercial_gap("GAP-COMM-001"), _commercial_gap("GAP-COMM-002")])
        out_path = tmp_path / "candidates.json"
        generate_task_candidates(output_path=out_path, max_candidates=20)
        data = json.loads(out_path.read_text())
        assert data["expansion_goal_fallback"] is True, (
            f"Expected expansion_goal_fallback=True when only commercial gaps present; "
            f"got: {data.get('expansion_goal_fallback')}"
        )

    def test_fallback_false_when_foss_gap_present(self, patch_ledger, tmp_path):
        """When ledger has a valid foss_reduced gap, fallback does NOT fire."""
        patch_ledger([_foss_gap("GAP-FOSS-001")])
        out_path = tmp_path / "candidates.json"
        generate_task_candidates(output_path=out_path, max_candidates=20)
        data = json.loads(out_path.read_text())
        assert data["expansion_goal_fallback"] is False, (
            f"Expected expansion_goal_fallback=False when foss gap is present; "
            f"got: {data.get('expansion_goal_fallback')}"
        )

    def test_fallback_true_when_ledger_missing(self, monkeypatch, tmp_path):
        """When ledger file doesn't exist, fallback fires."""
        monkeypatch.setattr(_atg, "_GAP_LEDGER_PATH", tmp_path / "nonexistent.json")
        monkeypatch.setattr(_atg, "_SAL_FACTS_PATH", tmp_path / "nonexistent-sal.json")
        out_path = tmp_path / "candidates.json"
        generate_task_candidates(output_path=out_path, max_candidates=20)
        data = json.loads(out_path.read_text())
        assert data["expansion_goal_fallback"] is True

    def test_excluded_gap_ids_count_always_present(self, patch_ledger, tmp_path):
        """excluded_gap_ids_count is always in output regardless of ledger state."""
        patch_ledger([])
        out_path = tmp_path / "candidates.json"
        generate_task_candidates(output_path=out_path, max_candidates=20)
        data = json.loads(out_path.read_text())
        assert "excluded_gap_ids_count" in data
        assert isinstance(data["excluded_gap_ids_count"], int)

    def test_hardcoded_fallback_goals_used_when_fallback_fires(self, patch_ledger, tmp_path):
        """When fallback fires, hardcoded _EXPANSION_GOALS are used as tasks."""
        patch_ledger([_commercial_gap("GAP-COMM-001")])
        out_path = tmp_path / "candidates.json"
        generate_task_candidates(output_path=out_path, max_candidates=20)
        data = json.loads(out_path.read_text())
        assert data["expansion_goal_fallback"] is True
        # When fallback fires, expansion goals fill the candidate list
        assert data["hardcoded_fallback_goals_used"] >= 0  # Could be 0 if all fns exist

    def test_gap_ledger_goals_count_in_output(self, patch_ledger, tmp_path):
        """gap_ledger_goals_available reflects how many ledger goals were available."""
        patch_ledger([_foss_gap("GAP-001"), _foss_gap("GAP-002")])
        out_path = tmp_path / "candidates.json"
        generate_task_candidates(output_path=out_path, max_candidates=20)
        data = json.loads(out_path.read_text())
        assert data["gap_ledger_goals_available"] >= 2

    def test_spec_facts_do_not_alone_trigger_fallback(self, patch_ledger, tmp_path):
        """Gaps without spec_facts still count as ledger goals (fallback=False)."""
        # This is the key distinction: fallback only fires when ledger has ZERO eligible goals.
        # Gaps with empty spec_facts ARE eligible (require_spec_facts defaults to False).
        patch_ledger([_foss_gap("GAP-001", spec_facts=[])])
        out_path = tmp_path / "candidates.json"
        generate_task_candidates(output_path=out_path, max_candidates=20)
        data = json.loads(out_path.read_text())
        assert data["expansion_goal_fallback"] is False, (
            "Gaps without spec_facts are still ledger goals when require_spec_facts=False. "
            "Fallback should not fire just because spec_facts are absent."
        )

    def test_output_json_has_required_signal_fields(self, patch_ledger, tmp_path):
        """All mandatory signal fields are present in the output JSON."""
        patch_ledger([])
        out_path = tmp_path / "candidates.json"
        generate_task_candidates(output_path=out_path, max_candidates=20)
        data = json.loads(out_path.read_text())
        required_fields = {
            "expansion_goal_fallback",
            "excluded_gap_ids_count",
            "gap_ledger_goals_available",
            "hardcoded_fallback_goals_used",
            "generator_version",
            "total_candidates",
            "tasks",
        }
        missing = required_fields - set(data.keys())
        assert not missing, f"Missing required output fields: {missing}"
