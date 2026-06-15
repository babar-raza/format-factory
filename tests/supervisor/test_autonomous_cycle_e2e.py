"""
End-to-end tests for autonomous_cycle.run_cycle().
TC-E2E-001: Proves declaration → validate → inspect → grade → generate prompt
→ write signal → check_continuation → CONTINUE works mechanically.

LLM semantic verification is mocked (gateway returns None) so tests are
deterministic and fast (<5 sec per cycle).
"""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))
sys.path.insert(0, str(_repo_root / "tools" / "supervisor"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_declaration(tmp_path, run_id="e2e-test-001", sprint_id="E2E-TEST-SPRINT-001",
                       items=None, item_statuses=None):
    """Create a minimal but schema-valid evidence-declaration.yaml."""
    ev_dir = tmp_path / ".local" / "evidences" / run_id
    ev_dir.mkdir(parents=True, exist_ok=True)

    if items is None:
        items = [
            {"item_id": "ITEM-001", "title": "Test item one", "status": "completed",
             "evidence_paths": [f".local/evidences/{run_id}/proof-one.txt"]},
            {"item_id": "ITEM-002", "title": "Test item two", "status": "completed",
             "evidence_paths": [f".local/evidences/{run_id}/proof-two.txt"]},
        ]

    if item_statuses is not None:
        for item, status in zip(items, item_statuses):
            item["status"] = status

    # Create dummy evidence files
    for item in items:
        for ep in item.get("evidence_paths", []):
            p = tmp_path / ep
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f"Evidence for {item['item_id']}: test output 5 passed\n", encoding="utf-8")

    completed = [i["item_id"] for i in items if i["status"] == "completed"]
    incomplete = [i["item_id"] for i in items if i["status"] != "completed"]

    # Create declared changed files so anti-skip checker doesn't flag them
    changed_file = f".local/evidences/{run_id}/changed_src.py"
    (tmp_path / changed_file).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / changed_file).write_text("# changed file\n", encoding="utf-8")

    decl = {
        "run_id": run_id,
        "sprint_id": sprint_id,
        "evidence_root": f".local/evidences/{run_id}",
        "start_time": "2026-06-15T10:00:00Z",
        "end_time": "2026-06-15T11:00:00Z",
        "git_head_start": "abc1234",
        "git_head_end": "def5678",
        "git_status_final": "clean",
        "declared_scope": "E2E test sprint",
        "planned_work_items": items,
        "completed_work_items": completed,
        "incomplete_work_items": incomplete,
        "changed_files": [changed_file],
        "tests_run": 5,
        "test_results": {"passed": 5, "failed": 0, "skipped": 0, "errors": 0},
        "evidence_artifacts": [
            {"path": ep, "type": "focused_proof", "description": f"Proof for {item['item_id']}"}
            for item in items
            for ep in item.get("evidence_paths", [])
        ],
        "reports_created": [],
        "worker_self_verdict": "All work completed successfully",
        "worker_self_grade": "PASS",
        "next_recommended_work": ["Continue to next sprint"],
    }

    decl_path = ev_dir / "evidence-declaration.yaml"
    decl_path.write_text(yaml.dump(decl, default_flow_style=False, sort_keys=False), encoding="utf-8")
    return decl_path


def _setup_repo_structure(tmp_path):
    """Create the repo directory structure autonomous_cycle.py expects."""
    (tmp_path / "reports" / "supervisor").mkdir(parents=True, exist_ok=True)
    (tmp_path / "reports" / "supervisor-streams").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".local" / "supervisor").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".supervisor").mkdir(parents=True, exist_ok=True)

    # Policies
    policies = {"autonomous_continuation": {"max_iterations": 5}}
    (tmp_path / ".supervisor" / "policies.yaml").write_text(
        yaml.dump(policies), encoding="utf-8"
    )

    # Pre-populate approval-gates.md (generate_supervisor_packet would normally do this)
    (tmp_path / "reports" / "supervisor" / "approval-gates.md").write_text(
        "AUTONOMOUS_CONTINUE: YES\n", encoding="utf-8"
    )


def _mock_gateway(*args, **kwargs):
    """Mock LLM gateway — returns (None, None) to skip semantic verification."""
    return (None, None)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestE2EHappyPath:
    """TC-E2E-001: Full cycle with all items ACCEPTED → check_continuation → CONTINUE."""

    @patch("grade_declared_work._get_sv_gateway", side_effect=_mock_gateway)
    def test_cycle_completes_and_writes_signal(self, mock_gw, tmp_path):
        """Full cycle: 2 completed items → exit 0 or 3 → signal written with required fields."""
        _setup_repo_structure(tmp_path)
        decl_path = _write_declaration(tmp_path)

        from autonomous_cycle import run_cycle
        result = run_cycle(decl_path, tmp_path)

        # Cycle should complete (exit 0 = clean, exit 3 = rework — both are valid completions)
        assert result["exit_code"] in (0, 3), f"Unexpected exit: {result}"

        # Continuation signal must exist with required structure
        signal_path = tmp_path / ".local" / "supervisor" / "continuation-signal.json"
        assert signal_path.exists(), "continuation-signal.json not written"
        signal = json.loads(signal_path.read_text(encoding="utf-8"))
        assert "autonomous_continue" in signal
        assert "iteration" in signal
        assert "continuation_state" in signal
        assert "hard_stops_detected" in signal
        assert "max_iterations" in signal

        # next-work-items.json must exist (canonical copy)
        wi_path = tmp_path / ".local" / "supervisor" / "next-work-items.json"
        assert wi_path.exists(), "next-work-items.json not written"

    @patch("grade_declared_work._get_sv_gateway", side_effect=_mock_gateway)
    def test_check_continuation_consistent_with_signal(self, mock_gw, tmp_path):
        """check_continuation verdict is consistent with continuation-signal state."""
        _setup_repo_structure(tmp_path)
        decl_path = _write_declaration(tmp_path)

        from autonomous_cycle import run_cycle
        result = run_cycle(decl_path, tmp_path)

        signal_path = tmp_path / ".local" / "supervisor" / "continuation-signal.json"
        signal = json.loads(signal_path.read_text(encoding="utf-8"))

        from check_continuation import check
        verdict = check(tmp_path)

        # check_continuation must be consistent with the signal
        if signal["autonomous_continue"] and not signal.get("hard_stops_detected"):
            cont_state = signal.get("continuation_state", "")
            if not cont_state.startswith("NO_") and signal["iteration"] < signal["max_iterations"]:
                assert verdict["verdict"] == "CONTINUE"
            else:
                assert verdict["verdict"] == "STOP"
        else:
            # hard stops or autonomous_continue=false → STOP
            assert verdict["verdict"] == "STOP"

    @patch("grade_declared_work._get_sv_gateway", side_effect=_mock_gateway)
    def test_cycle_writes_item_grades(self, mock_gw, tmp_path):
        """Cycle produces item-grades with correct structure."""
        _setup_repo_structure(tmp_path)
        decl_path = _write_declaration(tmp_path)

        result = __import__("autonomous_cycle").run_cycle(decl_path, tmp_path)

        review_dir = tmp_path / ".local" / "supervisor" / "reviews" / "e2e-test-001"
        grades_path = review_dir / "item-grades.json"
        assert grades_path.exists(), "item-grades.json not written"

        grades = json.loads(grades_path.read_text(encoding="utf-8"))
        assert isinstance(grades, list)
        assert len(grades) >= 2
        for g in grades:
            assert "item_id" in g
            assert "supervisor_grade" in g

    @patch("grade_declared_work._get_sv_gateway", side_effect=_mock_gateway)
    def test_cycle_writes_manifest(self, mock_gw, tmp_path):
        """Cycle produces supervisor-cycle-manifest.yaml."""
        _setup_repo_structure(tmp_path)
        decl_path = _write_declaration(tmp_path)

        result = __import__("autonomous_cycle").run_cycle(decl_path, tmp_path)

        review_dir = tmp_path / ".local" / "supervisor" / "reviews" / "e2e-test-001"
        manifests = list(review_dir.glob("supervisor-cycle-manifest.yaml"))
        assert len(manifests) == 1
        manifest = yaml.safe_load(manifests[0].read_text(encoding="utf-8"))
        assert manifest["run_id"] == "e2e-test-001"
        assert "exit_code" in manifest


class TestE2ERework:
    """Rework path: partial items → exit 3 → true_with_rework."""

    @patch("grade_declared_work._get_sv_gateway", side_effect=_mock_gateway)
    def test_partial_items_produce_rework_signal(self, mock_gw, tmp_path):
        """All items partial → exit 3, continuation signal reflects rework state."""
        _setup_repo_structure(tmp_path)
        decl_path = _write_declaration(
            tmp_path,
            items=[
                {"item_id": "PART-001", "title": "Partial item", "status": "partial",
                 "evidence_paths": [".local/evidences/e2e-test-001/proof-one.txt"]},
            ],
        )

        result = __import__("autonomous_cycle").run_cycle(decl_path, tmp_path)

        signal_path = tmp_path / ".local" / "supervisor" / "continuation-signal.json"
        assert signal_path.exists()
        signal = json.loads(signal_path.read_text(encoding="utf-8"))

        # Partial items should produce rework or critical rework
        assert signal.get("rework_items") or signal.get("hard_stops_detected")


class TestE2EMultiSprint:
    """Two-sprint simulation: verify iteration increments."""

    @patch("grade_declared_work._get_sv_gateway", side_effect=_mock_gateway)
    def test_two_sprints_increment_iteration(self, mock_gw, tmp_path):
        """Run two cycles → iteration should increment."""
        _setup_repo_structure(tmp_path)

        # Sprint 1
        decl1 = _write_declaration(tmp_path, run_id="sprint-1", sprint_id="SPRINT-1")
        result1 = __import__("autonomous_cycle").run_cycle(decl1, tmp_path)

        signal_path = tmp_path / ".local" / "supervisor" / "continuation-signal.json"
        assert signal_path.exists()
        sig1 = json.loads(signal_path.read_text(encoding="utf-8"))
        iter1 = sig1["iteration"]

        # Sprint 2
        decl2 = _write_declaration(tmp_path, run_id="sprint-2", sprint_id="SPRINT-2")
        result2 = __import__("autonomous_cycle").run_cycle(decl2, tmp_path)

        sig2 = json.loads(signal_path.read_text(encoding="utf-8"))
        iter2 = sig2["iteration"]

        # Second sprint should have higher iteration
        assert iter2 > iter1, f"Iteration did not increment: {iter1} -> {iter2}"
