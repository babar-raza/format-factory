"""
Tests for H6 external host activation — no false success claims.
Sprint: FORMAT-FACTORY-H6-EXTERNAL-HOST-ACTIVATION-AND-PROOF-001
"""
import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
H6_REPORT_DIR = REPO_ROOT / "reports" / "h6-external-host-activation"
STATE_DIR = REPO_ROOT / ".local" / "supervisor"


# ── H6 cannot be claimed on external_run_confirmed=false alone ─────────────

def test_h6_proof_requires_cycle_results():
    """H6 proven requires cycle result files from external process."""
    cycle_results = list((REPO_ROOT / "reports" / "autonomous-orchestrator" / "proof-run").glob("cycle-*.json"))
    assert len(cycle_results) >= 3, f"H6 requires >=3 cycle result files, found {len(cycle_results)}"


def test_h6_proof_requires_heartbeat():
    """H6 proven requires heartbeat file."""
    heartbeat = STATE_DIR / "orchestrator-heartbeat.json"
    assert heartbeat.exists(), "orchestrator-heartbeat.json must exist for H6 proof"
    data = json.loads(heartbeat.read_text())
    assert "heartbeat_at" in data


def test_h6_proof_requires_orchestrator_state():
    """H6 proven requires orchestrator-state.json with updated cycle_index."""
    state = STATE_DIR / "orchestrator-state.json"
    assert state.exists(), "orchestrator-state.json must exist for H6 proof"
    data = json.loads(state.read_text())
    assert data.get("cycle_index", 0) >= 3, f"cycle_index must be >=3, got {data.get('cycle_index')}"


def test_h6_proof_requires_stop_reason():
    """H6 proven requires stop-reason.json."""
    stop = STATE_DIR / "stop-reason.json"
    assert stop.exists(), "stop-reason.json must exist"
    data = json.loads(stop.read_text())
    assert data.get("stop_code") in (
        "MAX_CYCLES_REACHED",
        "MAX_CYCLES_REACHED_RESUMABLE",
        "WATCH_IDLE",
        "TRUE_EXTERNAL_GATE",
        "QUEUE_EMPTY_NO_PENDING",
        "USER_STOPPED",
    ), f"stop_code {data.get('stop_code')} not acceptable for H6 proof"


def test_h6_proof_stop_reason_acceptable_not_error():
    """H6 proof requires stop reason is not an error condition."""
    stop = STATE_DIR / "stop-reason.json"
    if not stop.exists():
        pytest.skip("stop-reason.json not present")
    data = json.loads(stop.read_text())
    error_codes = {"REPEATED_FAILURE", "ORCHESTRATOR_ERROR", "EVIDENCE_PACKAGE_FAILED"}
    assert data.get("stop_code") not in error_codes


def test_h6_launch_attempts_documented():
    """Launch attempts must be documented in launch-attempts.json."""
    attempts_file = H6_REPORT_DIR / "host-launch" / "launch-attempts.json"
    assert attempts_file.exists(), "launch-attempts.json must document actual attempts"
    data = json.loads(attempts_file.read_text())
    attempts = data.get("attempts", [])
    assert len(attempts) >= 2, "At least 2 launch attempts must be documented"


def test_h6_launch_attempt_b_succeeded():
    """Attempt B (real local backend) must have succeeded."""
    attempts_file = H6_REPORT_DIR / "host-launch" / "launch-attempts.json"
    if not attempts_file.exists():
        pytest.skip("launch-attempts.json not present")
    data = json.loads(attempts_file.read_text())
    attempt_b = next((a for a in data.get("attempts", []) if a.get("id") == "ATTEMPT_B"), None)
    assert attempt_b is not None, "ATTEMPT_B must be documented"
    assert attempt_b.get("result") == "SUCCESS", f"ATTEMPT_B result must be SUCCESS, got {attempt_b.get('result')}"
    assert attempt_b.get("cycles", 0) >= 3


def test_h6_claudecode_cleared_during_runs():
    """CLAUDECODE must have been cleared during external host runs."""
    attempts_file = H6_REPORT_DIR / "host-launch" / "launch-attempts.json"
    if not attempts_file.exists():
        pytest.skip("launch-attempts.json not present")
    data = json.loads(attempts_file.read_text())
    evidence = data.get("h6_evidence", {})
    assert evidence.get("claudecode_cleared_during_runs") is True


def test_h6_at_least_3_actions_executed():
    """At least 3 actions must have been executed."""
    attempts_file = H6_REPORT_DIR / "host-launch" / "launch-attempts.json"
    if not attempts_file.exists():
        pytest.skip("launch-attempts.json not present")
    data = json.loads(attempts_file.read_text())
    evidence = data.get("h6_evidence", {})
    assert evidence.get("total_cycles_executed", 0) >= 3


def test_no_advisory_prompt_executed():
    """No advisory prompt (next-sprint.md) must have been executed."""
    attempts_file = H6_REPORT_DIR / "host-launch" / "launch-attempts.json"
    if not attempts_file.exists():
        pytest.skip("launch-attempts.json not present")
    data = json.loads(attempts_file.read_text())
    evidence = data.get("h6_evidence", {})
    assert evidence.get("no_advisory_prompt_executed") is True


def test_no_forbidden_action_executed():
    """No forbidden action types must have been executed."""
    cycle_results = list((REPO_ROOT / "reports" / "autonomous-orchestrator" / "proof-run").glob("cycle-*.json"))
    forbidden = {"GIT_PUSH", "GIT_COMMIT", "GATE_8_APPROVAL", "GATE_11_APPROVAL", "PACKAGE_PUBLISH", "MCP_ACTIVATE"}
    for result_file in cycle_results:
        data = json.loads(result_file.read_text(encoding="utf-8"))
        action_type = data.get("action_type", "")
        assert action_type not in forbidden, f"Forbidden action {action_type} found in {result_file.name}"
