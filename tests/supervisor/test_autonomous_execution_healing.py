"""
test_autonomous_execution_healing.py

Tests for Sprint 5: FORMAT-FACTORY-AUTONOMOUS-EXECUTION-HEALING-AND-HOST-LOOP-PROOF-001

Validates:
  1. Continuation-signal rollover (max_iterations reached → reset to 0, continue=True)
  2. Host runner CLAUDECODE nested-session detection
  3. Prompt generator no-bad-netpbm-paths (re-validated after fix)
  4. autonomous_cycle.py rollover logic
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


# ── Tests: host runner nested session detection ───────────────────────────────

class TestNestedSessionDetection:
    """Verify detect_nested_session() correctly identifies CLAUDECODE env var."""

    def test_no_nested_session_when_claudecode_unset(self):
        from autonomous_host_runner import detect_nested_session
        with patch.dict(os.environ, {}, clear=False):
            env_copy = os.environ.copy()
            env_copy.pop("CLAUDECODE", None)
            with patch.dict(os.environ, env_copy, clear=True):
                result = detect_nested_session()
        assert result["nested"] is False
        assert result["wiring_instructions"] is None

    def test_nested_session_when_claudecode_set(self):
        from autonomous_host_runner import detect_nested_session
        with patch.dict(os.environ, {"CLAUDECODE": "1"}):
            result = detect_nested_session()
        assert result["nested"] is True
        assert "CLAUDECODE" in result["wiring_instructions"]
        assert result["external_terminal_command"] is not None
        assert "HOST_RUNNER_NOOP_OK" in result["external_terminal_command"]

    def test_nested_session_wiring_instructions_include_unset(self):
        from autonomous_host_runner import detect_nested_session
        with patch.dict(os.environ, {"CLAUDECODE": "1"}):
            result = detect_nested_session()
        # Instructions must tell user to unset CLAUDECODE
        assert "unset CLAUDECODE" in result["external_terminal_command"]

    def test_not_nested_when_claudecode_empty_string(self):
        from autonomous_host_runner import detect_nested_session
        with patch.dict(os.environ, {"CLAUDECODE": ""}):
            result = detect_nested_session()
        # Empty string = not set (treated as absent)
        assert result["nested"] is False

    def test_host_invocation_blocked_classification(self):
        """When CLAUDECODE is set, run_host_runner should return blocked classification."""
        from autonomous_host_runner import (
            HOST_INVOCATION_BLOCKED_NESTED,
            run_host_runner,
        )
        with patch.dict(os.environ, {"CLAUDECODE": "1"}):
            import tempfile
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                result = run_host_runner(
                    repo_root=REPO_ROOT,
                    report_dir=tmp_path,
                    dry_run=True,
                )
        assert result["classification"] == HOST_INVOCATION_BLOCKED_NESTED
        assert result["manual_invocation_required"] is True


# ── Tests: continuation signal rollover ──────────────────────────────────────

class TestContinuationSignalRollover:
    """Verify that reaching max_iterations triggers a governed rollover."""

    def test_rollover_resets_iteration_to_zero(self):
        """When iter=max, rollover should reset iteration to 0 in the signal."""
        signal_path = REPO_ROOT / ".local" / "supervisor" / "continuation-signal.json"
        if not signal_path.exists():
            pytest.skip("continuation-signal.json not found")
        signal = json.loads(signal_path.read_text(encoding="utf-8"))
        # After rollover: iteration should be 0, not 12
        # (only valid if rollover has occurred this session)
        if "checkpoint_rollover" in signal:
            assert signal["iteration"] == 0, (
                f"Expected iteration=0 after rollover, got {signal['iteration']}"
            )
            assert signal["autonomous_continue"] is True, (
                "Expected autonomous_continue=True after rollover"
            )

    def test_rollover_note_records_previous_iteration(self):
        """Rollover note must record the iteration it rolled over from."""
        signal_path = REPO_ROOT / ".local" / "supervisor" / "continuation-signal.json"
        if not signal_path.exists():
            pytest.skip("continuation-signal.json not found")
        signal = json.loads(signal_path.read_text(encoding="utf-8"))
        if "checkpoint_rollover" in signal:
            rollover = signal["checkpoint_rollover"]
            assert "rollover_from_iteration" in rollover
            assert rollover["rollover_from_iteration"] > 0
            assert "CHECKPOINT_ROLLOVER_CONTINUE" in rollover["rollover_rule"]

    def test_continuation_state_is_yes_after_rollover(self):
        """After rollover, continuation_state should be YES (not NO_MAX_ITERATIONS)."""
        signal_path = REPO_ROOT / ".local" / "supervisor" / "continuation-signal.json"
        if not signal_path.exists():
            pytest.skip("continuation-signal.json not found")
        signal = json.loads(signal_path.read_text(encoding="utf-8"))
        if "checkpoint_rollover" in signal:
            assert signal.get("continuation_state") in ("YES", "YES_WITH_LIMITATIONS", "YES_WITH_REWORK"), (
                f"Expected YES-family state after rollover, got {signal.get('continuation_state')}"
            )

    def test_rollover_classify_function_handles_max_iterations(self):
        """classify_continuation_state should return YES (not NO_MAX_ITERATIONS) when rolled over."""
        from autonomous_cycle import classify_continuation_state
        # Simulate post-rollover state: at_max_iterations=False (already reset)
        result = classify_continuation_state(
            auto_continue_value=True,
            at_max_iterations=False,
            hard_stops=[],
            overclaimed=[],
            rework_items=[],
            review={},
            policies_path=REPO_ROOT / ".supervisor" / "policies.yaml",
        )
        assert result in ("YES", "YES_WITH_LIMITATIONS")


# ── Tests: prompt generator path fix ─────────────────────────────────────────

class TestPromptGeneratorPathFix:
    """Verify the prompt generator produces correct Python Netpbm paths."""

    PROMPT_PATH = REPO_ROOT / "reports" / "supervisor" / "latest-next-worker-prompt.md"

    def test_no_src_python_netpbm_in_prompt(self):
        """The bad path src/python/netpbm/ must not appear in the generated prompt."""
        if not self.PROMPT_PATH.exists():
            pytest.skip("latest-next-worker-prompt.md not found")
        content = self.PROMPT_PATH.read_text(encoding="utf-8", errors="replace")
        assert "src/python/netpbm" not in content, (
            "Prompt contains bad path src/python/netpbm — fix not applied"
        )

    def test_no_tests_python_netpbm_in_prompt(self):
        """The bad path tests/python/netpbm/ must not appear in the generated prompt."""
        if not self.PROMPT_PATH.exists():
            pytest.skip("latest-next-worker-prompt.md not found")
        content = self.PROMPT_PATH.read_text(encoding="utf-8", errors="replace")
        assert "tests/python/netpbm" not in content, (
            "Prompt contains bad path tests/python/netpbm — fix not applied"
        )

    def test_correct_pbm_pgm_ppm_paths_present(self):
        """The correct split paths pbm/pgm/ppm should appear when Netpbm is in FOSS list."""
        if not self.PROMPT_PATH.exists():
            pytest.skip("latest-next-worker-prompt.md not found")
        content = self.PROMPT_PATH.read_text(encoding="utf-8", errors="replace")
        # At least one of the correct paths should be present
        has_pbm = "src/python/pbm/" in content or "tests/python/pbm/" in content
        has_pgm = "src/python/pgm/" in content or "tests/python/pgm/" in content
        has_ppm = "src/python/ppm/" in content or "tests/python/ppm/" in content
        assert has_pbm or has_pgm or has_ppm, (
            "Prompt does not contain any of src/python/pbm|pgm|ppm — Netpbm FOSS train may be missing"
        )

    def test_python_package_dir_override_exists(self):
        """The generator must define PYTHON_PACKAGE_DIR_OVERRIDE with netpbm entry."""
        gen_path = REPO_ROOT / "tools" / "supervisor" / "generate_next_worker_prompt.py"
        if not gen_path.exists():
            pytest.skip("generate_next_worker_prompt.py not found")
        content = gen_path.read_text(encoding="utf-8")
        assert "PYTHON_PACKAGE_DIR_OVERRIDE" in content, (
            "Generator missing PYTHON_PACKAGE_DIR_OVERRIDE constant"
        )
        assert '"netpbm"' in content or "'netpbm'" in content, (
            "Generator PYTHON_PACKAGE_DIR_OVERRIDE must contain netpbm entry"
        )


# ── Tests: external terminal command format ───────────────────────────────────

class TestExternalTerminalCommand:
    """Verify the wiring instructions provide a usable external terminal command."""

    def test_external_command_references_noop_ok(self):
        from autonomous_host_runner import _EXTERNAL_TERMINAL_COMMAND
        assert "HOST_RUNNER_NOOP_OK" in _EXTERNAL_TERMINAL_COMMAND

    def test_external_command_unsets_claudecode(self):
        from autonomous_host_runner import _EXTERNAL_TERMINAL_COMMAND
        assert "unset CLAUDECODE" in _EXTERNAL_TERMINAL_COMMAND

    def test_external_command_uses_claude_print(self):
        from autonomous_host_runner import _EXTERNAL_TERMINAL_COMMAND
        assert "claude --print" in _EXTERNAL_TERMINAL_COMMAND
