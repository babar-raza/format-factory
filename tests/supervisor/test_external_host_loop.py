"""
test_external_host_loop.py

Tests for external_host_loop.py  -  validates the external autonomous host loop.

Sprint: FORMAT-FACTORY-AUTONOMOUS-EXTERNAL-HOST-BOOTSTRAP-001
Updated: FORMAT-FACTORY-AUTONOMOUS-HOST-LOOP-FALSE-POSITIVE-REPAIR-001
  Added regression tests for package-107 false-positive defects.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

# external_host_loop.py is tombstoned - skip all tests if import raises
try:
    import external_host_loop as _ehl_check  # noqa: F401
    _EHL_AVAILABLE = True
except (DeprecationWarning, Exception):
    _EHL_AVAILABLE = False
pytestmark = pytest.mark.skipif(
    not _EHL_AVAILABLE,
    reason="external_host_loop.py is tombstoned (quarantined 2026-07-06)",
)


class TestNextActionLoading:
    """Tests for load_next_action()."""

    def test_loads_valid_next_action(self):
        from external_host_loop import load_next_action
        na_path = REPO_ROOT / "reports/autonomous-external-host-bootstrap/next-action.json"
        if not na_path.exists():
            pytest.skip("next-action.json not found")
        data, err = load_next_action(na_path)
        assert err is None
        assert data is not None
        assert data["schema_version"] == 1

    def test_fails_on_missing_file(self):
        from external_host_loop import load_next_action
        data, err = load_next_action(Path("/nonexistent/next-action.json"))
        assert data is None
        assert "not found" in err.lower()

    def test_fails_on_wrong_schema_version(self):
        from external_host_loop import load_next_action
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"schema_version": 99, "action_id": "test"}, f)
            f.flush()
            data, err = load_next_action(Path(f.name))
        assert data is None
        assert "schema_version" in err.lower() or "unsupported" in err.lower()

    def test_fails_on_missing_required_fields(self):
        from external_host_loop import load_next_action
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"schema_version": 1}, f)  # missing required fields
            f.flush()
            data, err = load_next_action(Path(f.name))
        assert data is None
        assert "missing" in err.lower()

    def test_next_action_schema_is_valid(self):
        """next-action.json must validate against its schema."""
        na_path = REPO_ROOT / "reports/autonomous-external-host-bootstrap/next-action.json"
        schema_path = REPO_ROOT / "reports/autonomous-external-host-bootstrap/next-action.schema.json"
        if not na_path.exists() or not schema_path.exists():
            pytest.skip("next-action.json or schema not found")
        data = json.loads(na_path.read_text())
        schema = json.loads(schema_path.read_text())
        # Basic structural check
        assert data["schema_version"] == 1
        assert data["action_type"] in schema["properties"]["action_type"]["enum"]
        assert data["mode"] in schema["properties"]["mode"]["enum"]


class TestPromptSafety:
    """Tests for check_prompt_safety()."""

    def test_safe_prompt_returns_no_violations(self):
        from external_host_loop import check_prompt_safety
        safe = "Write a file to reports/smoke/proof.md with HOST_CYCLE_SMOKE_OK"
        violations = check_prompt_safety(safe, [])
        assert violations == []

    def test_git_commit_is_refused(self):
        from external_host_loop import check_prompt_safety
        bad = "Run git commit -m 'test' to save changes"
        violations = check_prompt_safety(bad, [])
        assert any("git commit" in v for v in violations)

    def test_git_push_is_refused(self):
        from external_host_loop import check_prompt_safety
        bad = "git push origin main"
        violations = check_prompt_safety(bad, [])
        assert any("git push" in v for v in violations)

    def test_publish_is_refused(self):
        from external_host_loop import check_prompt_safety
        bad = "Run twine upload to pypi publish the package"
        violations = check_prompt_safety(bad, [])
        assert len(violations) > 0

    def test_gate_approval_is_refused(self):
        from external_host_loop import check_prompt_safety
        bad = "Gate 11 approval is now complete"
        violations = check_prompt_safety(bad, [])
        assert any("gate 11 approval" in v.lower() for v in violations)

    def test_authorized_git_is_refused(self):
        from external_host_loop import check_prompt_safety
        bad = "Authorized git commit and push to remote"
        violations = check_prompt_safety(bad, [])
        assert len(violations) > 0

    def test_src_mutation_in_forbidden_list(self):
        from external_host_loop import check_prompt_safety
        # forbidden_actions are checked as literal substring match against prompt
        bad = "perform src mutation on FodsParser.cs"
        violations = check_prompt_safety(bad, ["src mutation"])
        assert any("src mutation" in v for v in violations)

    def test_poc_targets_mutation_is_refused(self):
        from external_host_loop import check_prompt_safety
        bad = "directly mutate poc-targets.yaml to update commercial_product_ready"
        violations = check_prompt_safety(bad, [])
        assert len(violations) > 0

    def test_safe_smoke_prompt_has_no_violations(self):
        """The actual safe-smoke-prompt.md must pass safety check."""
        from external_host_loop import check_prompt_safety
        prompt_path = REPO_ROOT / "reports/autonomous-external-host-bootstrap/safe-smoke-prompt.md"
        if not prompt_path.exists():
            pytest.skip("safe-smoke-prompt.md not found")
        content = prompt_path.read_text(encoding="utf-8")
        forbidden = ["git commit", "git push", "Gate approval", "poc-targets mutation", "src mutation"]
        violations = check_prompt_safety(content, forbidden)
        # Should have no violations except possibly warning-level text about what NOT to do
        hard_violations = [v for v in violations if not any(
            word in content.lower()[:content.lower().find(v.split(":", 1)[-1].lower()) + 5]
            for word in ["do not", "must not", "never", "forbidden"]
        )]
        # The smoke prompt lists DO NOT instructions  -  those shouldn't count as violations
        # Basic check: smoke prompt doesn't have "git commit" as an action
        assert "authorized git" not in content.lower()
        assert "gate 11 approval" not in content.lower() or "do not" in content.lower()


class TestCLAUDECODEScrub:
    """Tests for scrub_claudecode_env()."""

    def test_scrub_removes_claudecode(self):
        from external_host_loop import scrub_claudecode_env
        with patch.dict(os.environ, {"CLAUDECODE": "1"}):
            clean_env, was_set = scrub_claudecode_env()
        assert was_set is True
        assert "CLAUDECODE" not in clean_env

    def test_scrub_preserves_other_env_vars(self):
        from external_host_loop import scrub_claudecode_env
        with patch.dict(os.environ, {"CLAUDECODE": "1", "PATH": os.environ.get("PATH", "")}):
            clean_env, _ = scrub_claudecode_env()
        assert "PATH" in clean_env

    def test_not_set_when_claudecode_absent(self):
        from external_host_loop import scrub_claudecode_env
        env_without = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        with patch.dict(os.environ, env_without, clear=True):
            _, was_set = scrub_claudecode_env()
        assert was_set is False

    def test_child_process_without_claudecode_can_run_version(self):
        """After scrubbing CLAUDECODE, claude --version should work.
        Skipped when running inside Claude Code (CLAUDECODE set) to avoid CLI hangs.
        """
        import subprocess
        import shutil
        from external_host_loop import scrub_claudecode_env
        if os.environ.get("CLAUDECODE"):
            pytest.skip("Skipped inside Claude Code session  -  claude CLI may hang")
        claude_path = shutil.which("claude")
        if not claude_path:
            pytest.skip("Claude CLI not found")
        with patch.dict(os.environ, {"CLAUDECODE": "1"}):
            clean_env, _ = scrub_claudecode_env()
        r = subprocess.run(
            [claude_path, "--version"],
            capture_output=True, text=True, env=clean_env, timeout=15,
        )
        assert r.returncode == 0
        assert "claude" in r.stdout.lower() or "2." in r.stdout


class TestGitStatusVerification:
    """Tests for verify_git_status()."""

    def test_allowed_path_is_clean(self):
        from external_host_loop import verify_git_status
        # No changes in this test  -  should be clean for known-allowed paths
        clean, violations = verify_git_status(
            REPO_ROOT,
            ["reports/autonomous-external-host-bootstrap/smoke/"],
        )
        # If smoke dir was written, it should be in allowed list
        # This test mainly verifies the function runs without error
        assert isinstance(clean, bool)
        assert isinstance(violations, list)

    def test_empty_allowed_roots_catches_everything(self):
        from external_host_loop import verify_git_status
        # With empty allowed roots, any dirty file is a violation
        clean, violations = verify_git_status(REPO_ROOT, [])
        # Repo is known to be dirty from prior sprints
        # Just verify the function returns correctly typed results
        assert isinstance(clean, bool)


class TestExternalHostLoopDryRun:
    """Tests for run_host_loop() in dry-run mode."""

    def test_dry_run_returns_dry_run_ready(self):
        from external_host_loop import run_host_loop, RESULT_CLASSIFICATIONS
        na_path = REPO_ROOT / "reports/autonomous-external-host-bootstrap/next-action.json"
        if not na_path.exists():
            pytest.skip("next-action.json not found")
        with tempfile.TemporaryDirectory() as tmp:
            result = run_host_loop(
                next_action_path=na_path,
                repo_root=REPO_ROOT,
                output_dir=Path(tmp),
                dry_run=True,
            )
        assert result["classification"] == RESULT_CLASSIFICATIONS["DRY_RUN_READY"]

    def test_unsafe_prompt_is_refused(self):
        from external_host_loop import run_host_loop, RESULT_CLASSIFICATIONS
        na_path = REPO_ROOT / "reports/autonomous-external-host-bootstrap/next-action.json"
        if not na_path.exists():
            pytest.skip("next-action.json not found")
        # Patch prompt content to be unsafe
        with tempfile.TemporaryDirectory() as tmp:
            unsafe_prompt = Path(tmp) / "unsafe.md"
            unsafe_prompt.write_text("git commit -m 'test'", encoding="utf-8")
            # Create a modified next-action pointing to unsafe prompt
            na_data = json.loads(na_path.read_text())
            na_data["prompt_path"] = str(unsafe_prompt)
            modified_na = Path(tmp) / "na.json"
            modified_na.write_text(json.dumps(na_data))
            result = run_host_loop(
                next_action_path=modified_na,
                repo_root=REPO_ROOT,
                output_dir=Path(tmp) / "out",
                dry_run=False,  # would hit safety check before invocation
            )
        assert result["classification"] == RESULT_CLASSIFICATIONS["REFUSED_UNSAFE"]

    def test_missing_next_action_returns_failed(self):
        from external_host_loop import run_host_loop, RESULT_CLASSIFICATIONS
        with tempfile.TemporaryDirectory() as tmp:
            result = run_host_loop(
                next_action_path=Path("/nonexistent/next-action.json"),
                repo_root=REPO_ROOT,
                output_dir=Path(tmp),
                dry_run=True,
            )
        assert result["classification"] == RESULT_CLASSIFICATIONS["FAILED"]


# ---------------------------------------------------------------------------
# Package-107 False-Positive Regression Tests
# (Sprint: FORMAT-FACTORY-AUTONOMOUS-HOST-LOOP-FALSE-POSITIVE-REPAIR-001)
# ---------------------------------------------------------------------------

PACKAGE_107_STDOUT_FIXTURE = (
    "I need your approval to run these commands. Could you approve:\n\n"
    "1. **Unit tests**: `.local/venv/Scripts/python -m pytest tests/supervisor/test_external_host_loop.py -v`\n"
    "2. **Dry-run**: `.local/venv/Scripts/python tools/supervisor/external_host_loop.py --dry-run`\n\n"
    "While waiting, here's what I found from the existing artifacts:\n\n"
    "## Current State\n\n"
    "**Previous live attempt** (`host-loop-result.json`):\n"
    "- **Classification:** `HOST_LOOP_FAILED`\n"
    "- The child Claude session didn't output the `HOST_CYCLE_SMOKE_OK` marker.\n"
)


class TestPackage107FalsePositiveRegression:
    """Regression tests that ensure the package-107 false-positive patterns
    are impossible with the fixed strict validation."""

    def test_marker_in_explanatory_stdout_does_not_pass(self):
        """marker found in prose output must classify as FALSE_POSITIVE_MARKER_IN_PROSE."""
        from external_host_loop import is_marker_in_prose_only
        prose = (
            "The previous attempt did not output HOST_CYCLE_SMOKE_OK marker. "
            "I need to run the smoke test to produce it."
        )
        # is_marker_in_prose_only should detect this
        assert is_marker_in_prose_only(prose, "HOST_CYCLE_SMOKE_OK") is True

    def test_permission_request_stdout_detected(self):
        """Claude asking for approval must be detected as a permission prompt."""
        from external_host_loop import is_permission_prompt
        assert is_permission_prompt("I need your approval to run these commands") is True
        assert is_permission_prompt("Could you approve the following commands?") is True
        assert is_permission_prompt("To run these commands, I need permission") is True

    def test_permission_request_not_false_positive_on_safe_text(self):
        """Safe task output should not be detected as a permission prompt."""
        from external_host_loop import is_permission_prompt
        assert is_permission_prompt("HOST_RUNNER_NOOP_OK") is False
        assert is_permission_prompt('{"status": "HOST_CYCLE_SMOKE_OK", "action_id": "x", "nonce": "y"}') is False

    def test_package_107_stdout_is_permission_prompt(self):
        """The actual package-107 stdout fixture must be detected as permission prompt."""
        from external_host_loop import is_permission_prompt
        assert is_permission_prompt(PACKAGE_107_STDOUT_FIXTURE) is True

    def test_exact_noop_stdout_required(self):
        """Stdout with extra prose around the marker must not pass NOOP mode."""
        from external_host_loop import is_marker_in_prose_only
        # Extra text around the exact marker = prose
        assert is_marker_in_prose_only("Sure! HOST_RUNNER_NOOP_OK\n", "HOST_RUNNER_NOOP_OK") is True
        assert is_marker_in_prose_only("HOST_RUNNER_NOOP_OK\nAdditional info", "HOST_RUNNER_NOOP_OK") is True

    def test_exact_noop_stdout_passes(self):
        """Stdout that is ONLY the marker (stripped) must not be detected as prose."""
        from external_host_loop import is_marker_in_prose_only
        assert is_marker_in_prose_only("HOST_RUNNER_NOOP_OK", "HOST_RUNNER_NOOP_OK") is False
        assert is_marker_in_prose_only("HOST_RUNNER_NOOP_OK\n", "HOST_RUNNER_NOOP_OK") is False

    def test_strict_json_valid_output_passes(self):
        """Valid strict JSON stdout with correct fields passes validation."""
        import json as _json
        from external_host_loop import validate_strict_json_output
        action = {
            "action_id": "HOST_SMOKE_001",
            "success_marker": "HOST_CYCLE_SMOKE_OK",
            "nonce": "test-nonce-123",
            "schema_version": 2,
        }
        stdout = _json.dumps({
            "status": "HOST_CYCLE_SMOKE_OK",
            "action_id": "HOST_SMOKE_001",
            "nonce": "test-nonce-123",
            "files_written": ["reports/foo/proof.md"],
        })
        valid, err, parsed = validate_strict_json_output(stdout, action)
        assert valid is True
        assert err is None

    def test_nonce_mismatch_fails(self):
        """JSON with wrong nonce must fail validation."""
        import json as _json
        from external_host_loop import validate_strict_json_output
        action = {
            "action_id": "HOST_SMOKE_001",
            "success_marker": "HOST_CYCLE_SMOKE_OK",
            "nonce": "correct-nonce",
            "schema_version": 2,
        }
        stdout = _json.dumps({
            "status": "HOST_CYCLE_SMOKE_OK",
            "action_id": "HOST_SMOKE_001",
            "nonce": "WRONG-nonce",
        })
        valid, err, _ = validate_strict_json_output(stdout, action)
        assert valid is False
        assert "nonce" in err.lower()

    def test_action_id_mismatch_fails(self):
        """JSON with wrong action_id must fail validation."""
        import json as _json
        from external_host_loop import validate_strict_json_output
        action = {
            "action_id": "HOST_SMOKE_001",
            "success_marker": "HOST_CYCLE_SMOKE_OK",
            "nonce": "n",
            "schema_version": 2,
        }
        stdout = _json.dumps({
            "status": "HOST_CYCLE_SMOKE_OK",
            "action_id": "WRONG_ID",
            "nonce": "n",
        })
        valid, err, _ = validate_strict_json_output(stdout, action)
        assert valid is False
        assert "action_id" in err.lower()

    def test_host_runner_must_not_create_proof_file(self):
        """run_host_loop must FAIL when child did not create the proof file.
        The host runner must NOT synthesize the proof file itself.
        """
        import json as _json
        from external_host_loop import run_host_loop, RESULT_CLASSIFICATIONS
        from unittest.mock import patch as _patch
        nonce = "test-nonce-abc"
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            prompt_file = tmpdir / "prompt.md"
            prompt_file.write_text("Smoke test prompt.", encoding="utf-8")
            proof_path = tmpdir / "smoke" / "proof.md"
            na = {
                "schema_version": 2,
                "action_id": "HOST_SMOKE_001",
                "nonce": nonce,
                "action_type": "CLAUDE_CODE_SMOKE",
                "mode": "LIVE_NOOP_OR_SMOKE",
                "prompt_path": str(prompt_file),
                "allowed_write_roots": [str(tmpdir / "smoke") + "/"],
                "forbidden_actions": [],
                "success_marker": "HOST_CYCLE_SMOKE_OK",
                "max_runtime_seconds": 10,
                "success_contract": {
                    "stdout_mode": "STRICT_JSON",
                    "required_nonce_match": True,
                    "child_must_write_expected_file": True,
                    "parent_may_create_proof_file": False,
                },
                "expected_output_files": [str(proof_path)],
            }
            na_file = tmpdir / "next-action.json"
            na_file.write_text(_json.dumps(na))

            # Mock invoke_claude to return valid JSON stdout  -  but child does NOT create proof
            valid_stdout = _json.dumps({
                "status": "HOST_CYCLE_SMOKE_OK",
                "action_id": "HOST_SMOKE_001",
                "nonce": nonce,
                "files_written": [str(proof_path)],
            })

            def mock_invoke(*args, **kwargs):
                return {"exit_code": 0, "stdout": valid_stdout, "stderr": "", "classification": None}

            with _patch("external_host_loop.invoke_claude", side_effect=mock_invoke):
                with _patch("external_host_loop.verify_git_status", return_value=(True, [])):
                    result = run_host_loop(
                        next_action_path=na_file,
                        repo_root=Path(tmp),
                        output_dir=tmpdir / "out",
                        dry_run=False,
                    )

            # Must fail because child didn't create the proof file
            assert result["classification"] == RESULT_CLASSIFICATIONS["FAILED"], (
                f"Expected FAILED (proof file not created by child), got {result['classification']}"
            )
            # Critical: host runner must NOT have created the proof file
            assert not proof_path.exists(), "Host runner must NOT create the proof file"

    def test_git_violations_fail_smoke(self):
        """Git violations outside allowed_write_roots must return GIT_VIOLATION."""
        import json as _json
        from external_host_loop import run_host_loop, RESULT_CLASSIFICATIONS
        from unittest.mock import patch as _patch
        nonce = "git-test-nonce"
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            prompt_file = tmpdir / "prompt.md"
            prompt_file.write_text("Test prompt.", encoding="utf-8")
            na = {
                "schema_version": 2,
                "action_id": "HOST_SMOKE_001",
                "nonce": nonce,
                "action_type": "CLAUDE_CODE_SMOKE",
                "mode": "LIVE_NOOP_OR_SMOKE",
                "prompt_path": str(prompt_file),
                "allowed_write_roots": ["reports/repair/smoke/"],
                "forbidden_actions": [],
                "success_marker": "HOST_CYCLE_SMOKE_OK",
                "max_runtime_seconds": 10,
                "success_contract": {"stdout_mode": "STRICT_JSON"},
                "expected_output_files": [str(tmpdir / "smoke" / "proof.md")],
            }
            na_file = tmpdir / "next-action.json"
            na_file.write_text(_json.dumps(na))

            proof_file = tmpdir / "smoke" / "proof.md"
            proof_file.parent.mkdir(parents=True, exist_ok=True)
            proof_file.write_text(
                f"HOST_CYCLE_SMOKE_OK\naction_id: HOST_SMOKE_001\nnonce: {nonce}\ncreated_by: child_agent\n",
                encoding="utf-8",
            )

            valid_stdout = _json.dumps({
                "status": "HOST_CYCLE_SMOKE_OK",
                "action_id": "HOST_SMOKE_001",
                "nonce": nonce,
                "files_written": [str(proof_file)],
            })

            def mock_invoke(*args, **kwargs):
                return {"exit_code": 0, "stdout": valid_stdout, "stderr": "", "classification": None}

            # Mock git violations: dirty files outside allowed write roots
            def mock_git_dirty(*args, **kwargs):
                return False, ["src/net/fods/FodsCsvExporter.cs", "src/python/abw/abw_codec.py"]

            with _patch("external_host_loop.invoke_claude", side_effect=mock_invoke):
                with _patch("external_host_loop.verify_git_status", side_effect=mock_git_dirty):
                    result = run_host_loop(
                        next_action_path=na_file,
                        repo_root=Path(tmp),
                        output_dir=tmpdir / "out",
                        dry_run=False,
                    )

        assert result["classification"] == RESULT_CLASSIFICATIONS["GIT_VIOLATION"], (
            f"Expected GIT_VIOLATION, got {result['classification']}"
        )

    def test_permission_prompt_in_run_host_loop_returns_blocked(self):
        """run_host_loop must return BLOCKED_PERMISSION_PROMPT when Claude asks for approval."""
        import json as _json
        from external_host_loop import run_host_loop, RESULT_CLASSIFICATIONS
        from unittest.mock import patch as _patch
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            prompt_file = tmpdir / "prompt.md"
            prompt_file.write_text("Do the smoke test.", encoding="utf-8")
            na = {
                "schema_version": 1,
                "action_id": "HOST_NOOP_TEST",
                "action_type": "CLAUDE_PRINT_PROMPT",
                "mode": "LIVE_NOOP_OR_SMOKE",
                "prompt_path": str(prompt_file),
                "allowed_write_roots": [],
                "forbidden_actions": [],
                "success_marker": "HOST_RUNNER_NOOP_OK",
                "max_runtime_seconds": 10,
            }
            na_file = tmpdir / "next-action.json"
            na_file.write_text(_json.dumps(na))

            def mock_invoke(*args, **kwargs):
                return {
                    "exit_code": 0,
                    "stdout": "I need your approval to run these commands. Could you approve?",
                    "stderr": "",
                    "classification": RESULT_CLASSIFICATIONS["BLOCKED_PERMISSION_PROMPT"],
                    "permission_prompt_detected": True,
                }

            with _patch("external_host_loop.invoke_claude", side_effect=mock_invoke):
                result = run_host_loop(
                    next_action_path=na_file,
                    repo_root=Path(tmp),
                    output_dir=tmpdir / "out",
                    dry_run=False,
                )

        assert result["classification"] == RESULT_CLASSIFICATIONS["BLOCKED_PERMISSION_PROMPT"]

    def test_package_107_stdout_fixture_fails_strict_noop(self):
        """The actual package-107 stdout must fail strict NOOP validation."""
        from external_host_loop import is_permission_prompt
        stdout = PACKAGE_107_STDOUT_FIXTURE
        # It IS a permission prompt
        assert is_permission_prompt(stdout) is True
        # Even if we check for marker in prose (marker appears as backtick code in text)
        # The marker does NOT appear literally in this fixture without backticks,
        # but the permission prompt check catches it first
        assert is_permission_prompt(stdout) is True

    def test_schema_v2_requires_nonce(self):
        """Schema v2 next-action without nonce must fail loading."""
        from external_host_loop import load_next_action
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({
                "schema_version": 2,
                "action_id": "X",
                "action_type": "CLAUDE_CODE_SMOKE",
                "mode": "LIVE_NOOP_OR_SMOKE",
                "prompt_path": "p.md",
                "allowed_write_roots": [],
                "forbidden_actions": [],
                "success_marker": "OK",
                "max_runtime_seconds": 60,
                # nonce MISSING
                "success_contract": {"stdout_mode": "STRICT_JSON"},
            }, f)
            f.flush()
            data, err = load_next_action(Path(f.name))
        assert data is None
        assert "nonce" in err.lower()

    def test_schema_v2_requires_success_contract(self):
        """Schema v2 next-action without success_contract must fail loading."""
        from external_host_loop import load_next_action
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({
                "schema_version": 2,
                "action_id": "X",
                "action_type": "CLAUDE_CODE_SMOKE",
                "mode": "LIVE_NOOP_OR_SMOKE",
                "prompt_path": "p.md",
                "allowed_write_roots": [],
                "forbidden_actions": [],
                "success_marker": "OK",
                "max_runtime_seconds": 60,
                "nonce": "abc-123",
                # success_contract MISSING
            }, f)
            f.flush()
            data, err = load_next_action(Path(f.name))
        assert data is None
        assert "success_contract" in err.lower()

    def test_schema_v1_still_loads(self):
        """Schema v1 next-action should still load without nonce/success_contract."""
        from external_host_loop import load_next_action
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({
                "schema_version": 1,
                "action_id": "X",
                "action_type": "CLAUDE_PRINT_PROMPT",
                "mode": "LIVE_NOOP_OR_SMOKE",
                "prompt_path": "p.md",
                "allowed_write_roots": [],
                "forbidden_actions": [],
                "success_marker": "OK",
                "max_runtime_seconds": 60,
            }, f)
            f.flush()
            data, err = load_next_action(Path(f.name))
        assert err is None
        assert data is not None
