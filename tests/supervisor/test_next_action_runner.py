"""
Format Factory — Next Action Runner Tests
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001
Lane 3: Runner validators
"""
import json
import pytest
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root))

from tools.supervisor.next_action_schema import NextActionValidationError, validate_next_action
from tools.supervisor.next_action_runner import run_action
from tools.supervisor.execution_backend import BackendType, ProofLevel


def _make_action(tmp_path, action_type="RUN_JSON_VALIDATION", target=None):
    if target is None:
        # Create a valid JSON file to validate
        target_file = tmp_path / "input.json"
        target_file.write_text('{"test": true}', encoding="utf-8")
        target = str(target_file)
    result_path = str(tmp_path / "result.json")
    return {
        "action_id": "test-runner-001",
        "action_type": action_type,
        "objective": "Test runner dispatch",
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "target": target,
        "result_path": result_path,
    }, result_path


def test_runner_validates_invalid_action(tmp_path):
    """Runner rejects actions with missing required fields."""
    action_file = tmp_path / "bad-action.json"
    action_file.write_text('{"action_type": "RUN_JSON_VALIDATION"}', encoding="utf-8")
    result = run_action(str(action_file))
    assert result["status"] == "INVALID_ACTION"


def test_runner_rejects_forbidden_action(tmp_path):
    """Runner rejects forbidden action types."""
    action_file = tmp_path / "forbidden.json"
    action_file.write_text(json.dumps({
        "action_id": "bad",
        "action_type": "GIT_PUSH",
        "objective": "Push code",
        "preferred_backend": "LOCAL_DETERMINISTIC",
    }), encoding="utf-8")
    result = run_action(str(action_file))
    assert result["status"] == "INVALID_ACTION"


def test_runner_dispatches_local_deterministic(tmp_path):
    """Runner dispatches RUN_JSON_VALIDATION to LOCAL_DETERMINISTIC backend."""
    action, result_path = _make_action(tmp_path)
    action_file = tmp_path / "action.json"
    action_file.write_text(json.dumps(action), encoding="utf-8")

    result = run_action(str(action_file), allowed_write_roots=[str(tmp_path)])

    assert result["status"] == "SUCCESS"
    assert result["backend_used"] == BackendType.LOCAL_DETERMINISTIC.value
    assert result["proof_level"] == ProofLevel.H3.value
    assert Path(result_path).exists(), "Runner must write result_path"


def test_runner_writes_result_not_caller(tmp_path):
    """Verify the runner (not the caller) writes the result file."""
    action, result_path = _make_action(tmp_path)
    action_file = tmp_path / "action.json"
    action_file.write_text(json.dumps(action), encoding="utf-8")

    # Result file does not exist before running
    assert not Path(result_path).exists()

    run_action(str(action_file), allowed_write_roots=[str(tmp_path)])

    # Runner created it
    assert Path(result_path).exists()
    data = json.loads(Path(result_path).read_text())
    assert data["backend_used"] == BackendType.LOCAL_DETERMINISTIC.value


def test_runner_handles_nonexistent_action_file():
    """Runner returns INVALID_ACTION for missing file."""
    result = run_action("/nonexistent/path/action.json")
    assert result["status"] == "INVALID_ACTION"


def test_runner_dry_run(tmp_path):
    """Dry-run returns selected backend without executing."""
    action, result_path = _make_action(tmp_path)
    action_file = tmp_path / "action.json"
    action_file.write_text(json.dumps(action), encoding="utf-8")

    result = run_action(str(action_file), dry_run=True)

    assert result["status"] == "DRY_RUN"
    assert result["selected_backend"] == BackendType.LOCAL_DETERMINISTIC.value
    assert not Path(result_path).exists(), "Dry-run must not write result file"


def test_runner_proof_level_h3(tmp_path):
    """Successful execution returns proof_level H3."""
    action, result_path = _make_action(tmp_path)
    action_file = tmp_path / "action.json"
    action_file.write_text(json.dumps(action), encoding="utf-8")

    result = run_action(str(action_file), allowed_write_roots=[str(tmp_path)])
    assert result["proof_level"] == "H3"


def test_runner_md_nonempty_check(tmp_path):
    """Runner can execute RUN_MD_NONEMPTY_CHECK."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Title\n\nSome content.", encoding="utf-8")
    result_path = tmp_path / "md-result.json"

    action = {
        "action_id": "test-md-001",
        "action_type": "RUN_MD_NONEMPTY_CHECK",
        "objective": "Check MD file",
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "target": str(md_file),
        "result_path": str(result_path),
    }
    action_file = tmp_path / "action.json"
    action_file.write_text(json.dumps(action), encoding="utf-8")

    result = run_action(str(action_file), allowed_write_roots=[str(tmp_path)])
    assert result["status"] == "SUCCESS"
    assert result_path.exists()


def test_runner_selection_trace_included(tmp_path):
    """Runner result includes backend selection trace."""
    action, result_path = _make_action(tmp_path)
    action_file = tmp_path / "action.json"
    action_file.write_text(json.dumps(action), encoding="utf-8")

    result = run_action(str(action_file), allowed_write_roots=[str(tmp_path)])
    assert "selection_trace" in result
    trace = result["selection_trace"]
    assert "selected" in trace
    assert trace["selected"] == BackendType.LOCAL_DETERMINISTIC.value
