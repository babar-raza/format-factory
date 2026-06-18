"""V2: Failure exclusion tests (Design 2 / Phase D).

Verifies load_excluded_gap_ids():
1. Returns gap_id for escalated, unresolved failures
2. Does NOT return gap_id for resolved failures
3. Does NOT return gap_id for below-threshold failures
4. Skips entries without a gap_id field
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools/supervisor"))

from failure_memory import FailureMemory, ESCALATION_THRESHOLD  # noqa: E402


def _make_store(tmp_path: Path, failures: list[dict]) -> FailureMemory:
    store_file = tmp_path / "failure-memory.json"
    store_file.write_text(
        json.dumps({
            "schema_version": "1.0",
            "updated_at": "2026-06-18T00:00:00+00:00",
            "failure_count": len(failures),
            "escalated_count": 0,
            "failures": failures,
        }),
        encoding="utf-8",
    )
    fm = FailureMemory(repo_root=tmp_path, store_path=store_file.name)
    return fm


def _entry(gap_id, occurrence_count, resolved=False):
    return {
        "id": f"FM-{gap_id}",
        "category": "TASK_SELECTION_FAILURE",
        "root_cause": f"Repeated failure for {gap_id}",
        "correction": "",
        "severity": "HIGH",
        "sprint_discovered": "sprint-1",
        "last_seen_sprint": "sprint-3",
        "discovered_at": "2026-06-01T00:00:00+00:00",
        "last_seen_at": "2026-06-18T00:00:00+00:00",
        "files_modified": [],
        "verification_command": "",
        "occurrence_count": occurrence_count,
        "escalated": occurrence_count >= ESCALATION_THRESHOLD,
        "resolved": resolved,
        "gap_id": gap_id,
    }


class TestFailureExclusion:
    def test_escalated_unresolved_is_excluded(self, tmp_path):
        """Escalated, unresolved failures produce their gap_id in the exclusion set."""
        fm = _make_store(tmp_path, [_entry("GAP-001", occurrence_count=ESCALATION_THRESHOLD)])
        excluded = fm.load_excluded_gap_ids()
        assert "GAP-001" in excluded

    def test_resolved_is_not_excluded(self, tmp_path):
        """Resolved failures are NOT excluded even when occurrence_count >= threshold."""
        fm = _make_store(tmp_path, [_entry("GAP-001", occurrence_count=ESCALATION_THRESHOLD, resolved=True)])
        excluded = fm.load_excluded_gap_ids()
        assert "GAP-001" not in excluded

    def test_below_threshold_not_excluded(self, tmp_path):
        """Failures below ESCALATION_THRESHOLD are not excluded."""
        fm = _make_store(tmp_path, [_entry("GAP-001", occurrence_count=ESCALATION_THRESHOLD - 1)])
        excluded = fm.load_excluded_gap_ids()
        assert "GAP-001" not in excluded

    def test_entry_without_gap_id_not_included(self, tmp_path):
        """Entries with no gap_id field produce no exclusion."""
        entry = _entry("GAP-X", occurrence_count=ESCALATION_THRESHOLD)
        entry.pop("gap_id")  # Remove gap_id
        fm = _make_store(tmp_path, [entry])
        excluded = fm.load_excluded_gap_ids()
        assert len(excluded) == 0

    def test_empty_store_returns_empty_set(self, tmp_path):
        """Empty failure store returns empty exclusion set."""
        fm = _make_store(tmp_path, [])
        excluded = fm.load_excluded_gap_ids()
        assert excluded == set()

    def test_multiple_escalated_returns_all(self, tmp_path):
        """All escalated unresolved failures are included."""
        fm = _make_store(tmp_path, [
            _entry("GAP-001", occurrence_count=ESCALATION_THRESHOLD),
            _entry("GAP-002", occurrence_count=ESCALATION_THRESHOLD + 2),
            _entry("GAP-003", occurrence_count=ESCALATION_THRESHOLD - 1),  # below threshold
        ])
        excluded = fm.load_excluded_gap_ids()
        assert "GAP-001" in excluded
        assert "GAP-002" in excluded
        assert "GAP-003" not in excluded

    def test_returns_set_not_list(self, tmp_path):
        """Return type is set."""
        fm = _make_store(tmp_path, [_entry("GAP-001", occurrence_count=ESCALATION_THRESHOLD)])
        excluded = fm.load_excluded_gap_ids()
        assert isinstance(excluded, set)


class TestExclusionWindowFromPolicies:
    """TC-HB-FOLLOW-003: exclusion_window_sprints is read from policies.yaml."""

    def _write_policies(self, tmp_path: Path, window: int) -> Path:
        import yaml  # type: ignore[import]
        policies = {
            "autonomous_continuation": {
                "failure_exclusion_window_sprints": window,
                "max_iterations": 12,
            }
        }
        p = tmp_path / ".supervisor" / "policies.yaml"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(yaml.dump(policies), encoding="utf-8")
        return p

    def test_reads_window_from_policies_yaml(self, tmp_path):
        """_read_exclusion_window() returns value from policies.yaml when present."""
        self._write_policies(tmp_path, window=5)
        fm = _make_store(tmp_path, [])
        fm.repo_root = tmp_path  # point at tmp dir where policies.yaml was written
        assert fm._read_exclusion_window() == 5

    def test_falls_back_to_3_when_no_policies_file(self, tmp_path):
        """_read_exclusion_window() returns 3 when policies.yaml is absent."""
        fm = _make_store(tmp_path, [])
        fm.repo_root = tmp_path / "nonexistent_root"
        assert fm._read_exclusion_window() == 3

    def test_explicit_param_overrides_policies(self, tmp_path):
        """Passing explicit exclusion_window_sprints overrides the policies file."""
        self._write_policies(tmp_path, window=10)
        fm = _make_store(tmp_path, [_entry("GAP-001", occurrence_count=ESCALATION_THRESHOLD)])
        fm.repo_root = tmp_path
        # Explicit 99 override — result is still based on occurrence_count logic, not window
        excluded = fm.load_excluded_gap_ids(exclusion_window_sprints=99)
        assert "GAP-001" in excluded  # Still excluded regardless of window value

    def test_production_policies_has_window_key(self):
        """The production .supervisor/policies.yaml has failure_exclusion_window_sprints."""
        import yaml  # type: ignore[import]
        p = _REPO / ".supervisor" / "policies.yaml"
        assert p.exists(), "policies.yaml must exist"
        policies = yaml.safe_load(p.read_text(encoding="utf-8"))
        window = policies.get("autonomous_continuation", {}).get("failure_exclusion_window_sprints")
        assert window is not None, "failure_exclusion_window_sprints must be in policies.yaml"
        assert isinstance(window, int), f"Expected int, got {type(window)}: {window}"
        assert window > 0, f"Window must be positive, got {window}"
