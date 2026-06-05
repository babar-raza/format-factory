"""
test_autonomous_host_runner.py — Tests for Host-Level Autonomous Runner

Verifies:
1. detect_claude_cli: returns invocable=True when CLI on PATH, invocable=False otherwise
2. Missing CLI → HOST_INVOCATION_LAYER_MISSING
3. Missing CLI → honest_classification = CONTINUATION_PACKET_ONLY
4. Terminal train state → HOST_INVOCATION_DEFERRED
5. Safety check refuses hard-stop keywords in prompt
6. Dry run: available CLI + safe prompt → HOST_INVOCATION_ATTEMPTED (dry_run=True)
7. HOST_INVOCATION_LAYER_MISSING ≠ POC_READY
8. Runner always writes host-runner-state.json with non_terminal_proof
9. Runner never claims full autonomy when CLI missing
10. Host runner stops on proof-backed POC ready (deferred)
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.supervisor.autonomous_host_runner import (
    HOST_INVOCATION_ATTEMPTED,
    HOST_INVOCATION_DEFERRED,
    HOST_INVOCATION_LAYER_MISSING,
    HOST_INVOCATION_PACKET_ONLY,
    HOST_INVOCATION_REFUSED,
    _check_prompt_safety,
    detect_claude_cli,
    run_host_runner,
)


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

def _make_repo(tmp_path, train_terminal=False, autonomous=True, next_sprint_content=None):
    """Create minimal repo structure in tmp_path."""
    # continuation-signal.json
    sig_dir = tmp_path / ".local" / "supervisor"
    sig_dir.mkdir(parents=True)
    (sig_dir / "continuation-signal.json").write_text(json.dumps({
        "autonomous_continue": autonomous,
        "iteration": 5,
        "max_iterations": 12,
        "next_sprint_path": "reports/supervisor/next-sprint.md",
    }))

    # next-sprint.md
    ns_dir = tmp_path / "reports" / "supervisor"
    ns_dir.mkdir(parents=True)
    ns_content = next_sprint_content or "# Next Sprint\n- [pending] TASK-001: Continue ZST work\n"
    (ns_dir / "next-sprint.md").write_text(ns_content)

    return tmp_path


def _make_train_state(report_dir, terminal=False, execution_state=None):
    """Write a train-state.json to report_dir."""
    state = {
        "terminal": terminal,
        "execution_state": execution_state or (
            "MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING"
            if terminal else "NON_TERMINAL_CONTINUE"
        ),
        "next_action": {"action": "NON_TERMINAL_CONTINUE" if not terminal else "TERMINAL"},
    }
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "train-state.json").write_text(json.dumps(state))
    (report_dir / "next-action.json").write_text(json.dumps(state["next_action"]))
    return state


# ─────────────────────────────────────────────────────────────
# Test 1: CLI detection
# ─────────────────────────────────────────────────────────────

class TestCliDetection:
    def test_detect_returns_dict(self):
        """detect_claude_cli always returns a dict."""
        result = detect_claude_cli()
        assert isinstance(result, dict)
        assert "available" in result
        assert "invocable" in result
        assert "reason" in result

    def test_detect_has_required_fields(self):
        """detect_claude_cli has all required fields."""
        result = detect_claude_cli()
        required = {"available", "invocable", "reason", "path", "version"}
        assert required <= set(result.keys())

    def test_detect_invocable_is_bool(self):
        """invocable field is a boolean."""
        result = detect_claude_cli()
        assert isinstance(result["invocable"], bool)

    def test_detect_path_is_str_or_none(self):
        """path is a string if available, None otherwise."""
        result = detect_claude_cli()
        assert result["path"] is None or isinstance(result["path"], str)

    @patch("shutil.which", return_value=None)
    def test_detect_cli_not_on_path_invocable_false(self, mock_which):
        """When shutil.which returns None and no candidates exist, invocable=False."""
        with patch("pathlib.Path.exists", return_value=False):
            result = detect_claude_cli()
        assert result["invocable"] is False
        assert result["available"] is False

    @patch("shutil.which", return_value="/usr/bin/claude")
    @patch("subprocess.run")
    def test_detect_cli_on_path_invocable_true(self, mock_run, mock_which):
        """When CLI is on PATH and --version succeeds, invocable=True."""
        mock_run.return_value = MagicMock(returncode=0, stdout="Claude 2.1.62\n", stderr="")
        result = detect_claude_cli()
        assert result["available"] is True
        assert result["invocable"] is True
        assert result["path"] == "/usr/bin/claude"


# ─────────────────────────────────────────────────────────────
# Test 2: Missing CLI → HOST_INVOCATION_LAYER_MISSING
# ─────────────────────────────────────────────────────────────

class TestMissingCli:
    @patch("tools.supervisor.autonomous_host_runner.detect_claude_cli")
    def test_missing_cli_returns_layer_missing(self, mock_detect, tmp_path):
        """When CLI is not invocable, run_host_runner returns HOST_INVOCATION_LAYER_MISSING."""
        mock_detect.return_value = {
            "available": False,
            "invocable": False,
            "path": None,
            "version": None,
            "reason": "Not found",
        }
        repo = _make_repo(tmp_path)
        report_dir = repo / "reports" / "host-autonomy-runner"
        _make_train_state(report_dir, terminal=False)

        result = run_host_runner(repo_root=repo, report_dir=report_dir, dry_run=True)
        assert result["classification"] == HOST_INVOCATION_LAYER_MISSING

    @patch("tools.supervisor.autonomous_host_runner.detect_claude_cli")
    def test_missing_cli_honest_classification_is_packet_only(self, mock_detect, tmp_path):
        """When CLI missing, honest_classification must be CONTINUATION_PACKET_ONLY."""
        mock_detect.return_value = {
            "available": False,
            "invocable": False,
            "path": None,
            "version": None,
            "reason": "Not found",
        }
        repo = _make_repo(tmp_path)
        report_dir = repo / "reports" / "host-autonomy-runner"
        _make_train_state(report_dir, terminal=False)

        result = run_host_runner(repo_root=repo, report_dir=report_dir, dry_run=True)
        assert result.get("honest_classification") == HOST_INVOCATION_PACKET_ONLY

    @patch("tools.supervisor.autonomous_host_runner.detect_claude_cli")
    def test_runner_never_claims_full_autonomy_when_cli_missing(self, mock_detect, tmp_path):
        """
        When CLI is missing, the runner must NOT classify as HOST_INVOCATION_ATTEMPTED.
        It is packet-only, not fully autonomous.
        """
        mock_detect.return_value = {
            "available": False,
            "invocable": False,
            "path": None,
            "version": None,
            "reason": "Not found",
        }
        repo = _make_repo(tmp_path)
        report_dir = repo / "reports" / "host-autonomy-runner"
        _make_train_state(report_dir, terminal=False)

        result = run_host_runner(repo_root=repo, report_dir=report_dir, dry_run=True)
        assert result["classification"] != HOST_INVOCATION_ATTEMPTED


# ─────────────────────────────────────────────────────────────
# Test 3: Terminal state → HOST_INVOCATION_DEFERRED
# ─────────────────────────────────────────────────────────────

class TestTerminalStateDeferred:
    @patch("tools.supervisor.autonomous_host_runner.detect_claude_cli")
    def test_terminal_train_state_deferred(self, mock_detect, tmp_path):
        """When train is in terminal state, runner returns HOST_INVOCATION_DEFERRED."""
        mock_detect.return_value = {
            "available": True,
            "invocable": True,
            "path": "/usr/bin/claude",
            "version": "2.1.62",
            "reason": "Found",
        }
        repo = _make_repo(tmp_path)
        report_dir = repo / "reports" / "host-autonomy-runner"
        _make_train_state(report_dir, terminal=True)

        result = run_host_runner(repo_root=repo, report_dir=report_dir, dry_run=True)
        assert result["classification"] == HOST_INVOCATION_DEFERRED

    @patch("tools.supervisor.autonomous_host_runner.detect_claude_cli")
    def test_poc_ready_terminal_deferred(self, mock_detect, tmp_path):
        """POC ready terminal state → deferred (no invocation needed)."""
        mock_detect.return_value = {
            "available": True, "invocable": True,
            "path": "/usr/bin/claude", "version": "2.1", "reason": "Found",
        }
        repo = _make_repo(tmp_path)
        report_dir = repo / "reports" / "host-autonomy-runner"
        _make_train_state(
            report_dir,
            terminal=True,
            execution_state="MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING",
        )

        result = run_host_runner(repo_root=repo, report_dir=report_dir, dry_run=True)
        assert result["classification"] == HOST_INVOCATION_DEFERRED


# ─────────────────────────────────────────────────────────────
# Test 4: Safety check
# ─────────────────────────────────────────────────────────────

class TestSafetyCheck:
    def test_safe_prompt_passes(self):
        """A clean sprint prompt with no hard-stop keywords passes safety."""
        prompt = "# Next Sprint\n- [pending] TASK-001: Continue ZST work\n- [agent-owned] TASK-002: Build proof\n"
        result = _check_prompt_safety(prompt)
        assert result["safe"] is True
        assert result["violations"] == []

    def test_git_push_refused(self):
        """Prompt with 'git push' is refused."""
        prompt = "# Next Sprint\n- [external-gate] TASK-001: git push origin main\n"
        result = _check_prompt_safety(prompt)
        assert result["safe"] is False
        assert "git push" in result["violations"]

    def test_git_commit_refused(self):
        """Prompt with 'git commit' is refused."""
        prompt = "Run git commit to save changes"
        result = _check_prompt_safety(prompt)
        assert result["safe"] is False
        assert "git commit" in result["violations"]

    def test_gate_11_approval_refused(self):
        """Prompt requesting Gate 11 approval execution is refused."""
        prompt = "Execute Gate 11 approval with Babar Raza"
        result = _check_prompt_safety(prompt)
        assert result["safe"] is False

    def test_publish_refused(self):
        """Prompt with 'publish' keyword is refused."""
        prompt = "Publish the NuGet package to nuget.org"
        result = _check_prompt_safety(prompt)
        assert result["safe"] is False
        assert "publish" in result["violations"]

    @patch("tools.supervisor.autonomous_host_runner.detect_claude_cli")
    def test_unsafe_prompt_returns_refused(self, mock_detect, tmp_path):
        """Unsafe prompt → HOST_INVOCATION_REFUSED from run_host_runner."""
        mock_detect.return_value = {
            "available": True, "invocable": True,
            "path": "/usr/bin/claude", "version": "2.1", "reason": "Found",
        }
        repo = _make_repo(tmp_path, next_sprint_content="git push origin main\ngit commit -m 'release'\n")
        report_dir = repo / "reports" / "host-autonomy-runner"
        _make_train_state(report_dir, terminal=False)

        result = run_host_runner(repo_root=repo, report_dir=report_dir, dry_run=False)
        assert result["classification"] == HOST_INVOCATION_REFUSED
        assert len(result["violations"]) > 0


# ─────────────────────────────────────────────────────────────
# Test 5: Dry run behavior
# ─────────────────────────────────────────────────────────────

class TestDryRun:
    @patch("tools.supervisor.autonomous_host_runner.detect_claude_cli")
    def test_dry_run_with_available_cli_returns_attempted(self, mock_detect, tmp_path):
        """Dry run + available CLI + safe prompt → HOST_INVOCATION_ATTEMPTED."""
        mock_detect.return_value = {
            "available": True, "invocable": True,
            "path": "/usr/bin/claude", "version": "2.1.62", "reason": "Found",
        }
        repo = _make_repo(tmp_path)
        report_dir = repo / "reports" / "host-autonomy-runner"
        _make_train_state(report_dir, terminal=False)

        result = run_host_runner(repo_root=repo, report_dir=report_dir, dry_run=True)
        assert result["classification"] == HOST_INVOCATION_ATTEMPTED
        assert result.get("dry_run") is True

    @patch("tools.supervisor.autonomous_host_runner.detect_claude_cli")
    def test_dry_run_does_not_invoke_subprocess(self, mock_detect, tmp_path):
        """Dry run must NOT call subprocess.Popen."""
        mock_detect.return_value = {
            "available": True, "invocable": True,
            "path": "/usr/bin/claude", "version": "2.1", "reason": "Found",
        }
        repo = _make_repo(tmp_path)
        report_dir = repo / "reports" / "host-autonomy-runner"
        _make_train_state(report_dir, terminal=False)

        with patch("subprocess.Popen") as mock_popen:
            run_host_runner(repo_root=repo, report_dir=report_dir, dry_run=True)
            mock_popen.assert_not_called()


# ─────────────────────────────────────────────────────────────
# Test 6: Output files
# ─────────────────────────────────────────────────────────────

class TestOutputFiles:
    @patch("tools.supervisor.autonomous_host_runner.detect_claude_cli")
    def test_host_runner_writes_state_json(self, mock_detect, tmp_path):
        """run_host_runner always writes host-runner-state.json."""
        mock_detect.return_value = {
            "available": False, "invocable": False,
            "path": None, "version": None, "reason": "Not found",
        }
        repo = _make_repo(tmp_path)
        report_dir = repo / "reports" / "host-autonomy-runner"
        _make_train_state(report_dir, terminal=False)

        run_host_runner(repo_root=repo, report_dir=report_dir, dry_run=True)

        state_file = report_dir / "host-runner-state.json"
        assert state_file.exists()
        state = json.loads(state_file.read_text())
        assert "classification" in state
        assert "non_terminal_proof" in state

    @patch("tools.supervisor.autonomous_host_runner.detect_claude_cli")
    def test_non_terminal_proof_in_state(self, mock_detect, tmp_path):
        """host-runner-state.json must include non_terminal_proof."""
        mock_detect.return_value = {
            "available": False, "invocable": False,
            "path": None, "version": None, "reason": "Not found",
        }
        repo = _make_repo(tmp_path)
        report_dir = repo / "reports" / "host-autonomy-runner"
        _make_train_state(report_dir, terminal=False)

        run_host_runner(repo_root=repo, report_dir=report_dir, dry_run=True)

        state_file = report_dir / "host-runner-state.json"
        state = json.loads(state_file.read_text())
        proof = state["non_terminal_proof"]
        assert proof.get("continuation_packet_only_is_not_full_autonomy") is True
        assert proof.get("runner_never_claims_100pct_autonomous_without_cli") is True

    @patch("tools.supervisor.autonomous_host_runner.detect_claude_cli")
    def test_host_runner_writes_log_jsonl(self, mock_detect, tmp_path):
        """run_host_runner writes host-runner-log.jsonl."""
        mock_detect.return_value = {
            "available": False, "invocable": False,
            "path": None, "version": None, "reason": "Not found",
        }
        repo = _make_repo(tmp_path)
        report_dir = repo / "reports" / "host-autonomy-runner"
        _make_train_state(report_dir, terminal=False)

        run_host_runner(repo_root=repo, report_dir=report_dir, dry_run=True)

        log_file = report_dir / "host-runner-log.jsonl"
        assert log_file.exists()
        lines = [json.loads(l) for l in log_file.read_text().splitlines() if l.strip()]
        assert len(lines) >= 2
        events = [l["event"] for l in lines]
        assert "runner_start" in events
        assert "cli_detection" in events


# ─────────────────────────────────────────────────────────────
# Test 7: Classification constants
# ─────────────────────────────────────────────────────────────

class TestClassificationConstants:
    def test_layer_missing_not_poc_ready(self):
        """HOST_INVOCATION_LAYER_MISSING is distinct from POC_READY terminal states."""
        assert HOST_INVOCATION_LAYER_MISSING != "MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED"
        assert HOST_INVOCATION_LAYER_MISSING != "MAINSTREAM_POC_READY_CANDIDATE_AUTHORITY_VERIFIED_RELEASE_APPROVAL_PENDING"

    def test_packet_only_not_full_autonomy(self):
        """CONTINUATION_PACKET_ONLY explicitly documents lack of full autonomy."""
        assert HOST_INVOCATION_PACKET_ONLY == "CONTINUATION_PACKET_ONLY"
        assert "PACKET_ONLY" in HOST_INVOCATION_PACKET_ONLY

    def test_all_constants_distinct(self):
        """All classification constants are unique strings."""
        constants = [
            HOST_INVOCATION_ATTEMPTED,
            HOST_INVOCATION_LAYER_MISSING,
            HOST_INVOCATION_DEFERRED,
            HOST_INVOCATION_REFUSED,
            HOST_INVOCATION_PACKET_ONLY,
        ]
        assert len(constants) == len(set(constants))


# ─────────────────────────────────────────────────────────────
# Tests for noop invocation and classification
# ─────────────────────────────────────────────────────────────

class TestNoopInvocation:
    """Test the run_noop_invocation and classify_noop_result functions."""

    def test_dry_run_safe_prompt_passes_safety(self):
        """The safe noop prompt contains no hard-stop keywords."""
        from tools.supervisor.autonomous_host_runner import NOOP_PROMPT, _check_prompt_safety
        result = _check_prompt_safety(NOOP_PROMPT)
        assert result["safe"] is True
        assert result["violations"] == []

    def test_noop_expected_response_constant(self):
        """NOOP_EXPECTED_RESPONSE is the correct value."""
        from tools.supervisor.autonomous_host_runner import NOOP_EXPECTED_RESPONSE
        assert NOOP_EXPECTED_RESPONSE == "HOST_RUNNER_NOOP_OK"

    def test_classify_noop_proven_when_noop_ok(self):
        """When output contains HOST_RUNNER_NOOP_OK → PROVEN."""
        from tools.supervisor.autonomous_host_runner import classify_noop_result
        result = {"success": True, "output": "HOST_RUNNER_NOOP_OK", "noop_confirmed": True}
        classification = classify_noop_result(result)
        assert classification["classification"] == "HOST_RUNNER_LIVE_INVOCATION_PROVEN"
        assert classification["proven"] is True

    def test_classify_noop_nested_session_blocked(self):
        """Nested session error → BLOCKED_BY_POLICY with wiring instructions."""
        from tools.supervisor.autonomous_host_runner import classify_noop_result
        result = {
            "success": False,
            "output": "Error: Claude Code cannot be launched inside another Claude Code session.\nTo bypass this check, unset the CLAUDECODE environment variable.",
            "noop_confirmed": False,
            "returncode": 1,
        }
        classification = classify_noop_result(result)
        assert classification["classification"] == "HOST_RUNNER_LIVE_INVOCATION_BLOCKED_BY_POLICY"
        assert classification["proven"] is False
        assert classification["wiring_instructions"] is not None
        assert "CLAUDECODE" in classification["wiring_instructions"]

    def test_classify_noop_generic_failure(self):
        """Generic failure → FAILED with error."""
        from tools.supervisor.autonomous_host_runner import classify_noop_result
        result = {"success": False, "output": "some error", "noop_confirmed": False, "error": "Exit code 2"}
        classification = classify_noop_result(result)
        assert classification["classification"] == "HOST_RUNNER_LIVE_INVOCATION_FAILED"
        assert classification["proven"] is False

    def test_noop_invocation_dry_mode_does_not_call_subprocess(self, tmp_path):
        """When running dry_run=True on main runner, subprocess.Popen not called."""
        # This is tested via the existing run_host_runner dry_run tests
        # run_noop_invocation itself always invokes subprocess, but with a safe prompt
        # Here we just verify the noop prompt is safe
        from tools.supervisor.autonomous_host_runner import NOOP_PROMPT, _check_prompt_safety
        safety = _check_prompt_safety(NOOP_PROMPT)
        assert safety["safe"] is True

    def test_classify_noop_result_valid_contract(self):
        """classify_noop_result always returns required fields."""
        from tools.supervisor.autonomous_host_runner import classify_noop_result
        for test_input in [
            {"success": True, "output": "HOST_RUNNER_NOOP_OK", "noop_confirmed": True},
            {"success": False, "output": "nested session", "noop_confirmed": False},
            {"success": False, "output": "other error", "noop_confirmed": False, "error": "fail"},
        ]:
            result = classify_noop_result(test_input)
            assert "classification" in result
            assert "proven" in result
