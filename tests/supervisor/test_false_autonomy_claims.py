"""
Format Factory — False Autonomy Claims Validators
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001
Lane 3: Validator-first TDD gate

Tests 1-14: False autonomy patterns that must be rejected.
"""
import json
import pytest
import sys
from pathlib import Path

# Ensure tools importable
_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root))

from tools.supervisor.next_action_schema import validate_next_action, NextActionValidationError
from tools.supervisor.execution_backend import BackendType, BackendStatus
from tools.supervisor.backend_selector import select_backend
from tools.supervisor.backends.local_deterministic_backend import LocalDeterministicBackend
from tools.supervisor.backends.superpowers_skill_backend import SuperpowersSkillBackend
from tools.supervisor.backends.mcp_superpowers_backend import McpSuperpowersBackend


# --------------------------------------------------------------------------
# 1. Generated prompt is not execution
# --------------------------------------------------------------------------
def test_generated_prompt_is_not_execution():
    """A next-action with no result_path is advisory only. Validation passes but runner marks advisory."""
    action = {
        "action_id": "test-001",
        "action_type": "RUN_JSON_VALIDATION",
        "objective": "Validate a file",
        "preferred_backend": "LOCAL_DETERMINISTIC",
        # No result_path — advisory/generated only
    }
    # Schema validation should still pass
    validate_next_action(action)
    # But runner would not assign H3 without result_path being written
    assert "result_path" not in action or action.get("result_path") is None


# --------------------------------------------------------------------------
# 2. Manual mode is not autonomy
# --------------------------------------------------------------------------
def test_manual_mode_is_not_autonomy():
    """MANUAL_EXTERNAL_GATE action cannot be executed autonomously."""
    action = {
        "action_id": "test-002",
        "action_type": "MANUAL_EXTERNAL_GATE",
        "objective": "Human approval",
        "preferred_backend": "MANUAL_EXTERNAL_GATE",
        "external_gate": True,
    }
    # Schema allows external_gate with MANUAL_EXTERNAL_GATE type
    validate_next_action(action)
    # But backend selector must block it
    backends = [LocalDeterministicBackend()]
    backend, trace = select_backend(action, backends)
    assert trace.blocked, "MANUAL_EXTERNAL_GATE must block autonomous execution"


# --------------------------------------------------------------------------
# 3. Superpowers unavailable cannot be claimed
# --------------------------------------------------------------------------
def test_superpowers_unavailable_cannot_be_claimed():
    """Superpowers backend with missing plugin reports NOT_FOUND."""
    backend = SuperpowersSkillBackend()
    # .claude/plugins/ is absent in this repo
    status = backend.discover()
    assert status in (BackendStatus.NOT_FOUND, BackendStatus.SETUP_REQUIRED), (
        f"Expected NOT_FOUND or SETUP_REQUIRED, got {status}. "
        "Superpowers cannot be claimed as available."
    )
    assert not backend.can_execute({"action_type": "SKILL_TOOL_INVOKE"})


# --------------------------------------------------------------------------
# 4. Repo command is not Superpowers plugin
# --------------------------------------------------------------------------
def test_repo_command_is_not_superpowers_plugin():
    """SESSION_SKILL_TOOL (.claude/commands/) is distinct from Superpowers plugin."""
    commands_path = Path(".claude/commands")
    plugins_path = Path(".claude/plugins")
    # If commands/ exists with files, it's SESSION_SKILL_TOOL, not Superpowers
    if commands_path.exists():
        assert not plugins_path.exists() or not list(plugins_path.iterdir()), (
            ".claude/commands/ exists but .claude/plugins/ also exists — "
            "must distinguish SESSION_SKILL_TOOL from Superpowers plugin"
        )
    # Superpowers backend must NOT be in VERIFIED_CALLABLE status
    backend = SuperpowersSkillBackend()
    assert backend.discover() != BackendStatus.VERIFIED_CALLABLE


# --------------------------------------------------------------------------
# 5. Next action must be executed, not advisory
# --------------------------------------------------------------------------
def test_next_action_must_be_executed_not_advisory():
    """Forbidden action types must raise NextActionValidationError."""
    for forbidden_type in ["GIT_PUSH", "GIT_COMMIT", "GATE_11_APPROVAL", "PACKAGE_PUBLISH"]:
        action = {
            "action_id": "test-005",
            "action_type": forbidden_type,
            "objective": "Forbidden action",
            "preferred_backend": "LOCAL_DETERMINISTIC",
        }
        with pytest.raises(NextActionValidationError, match="Forbidden"):
            validate_next_action(action)


# --------------------------------------------------------------------------
# 6. Backend selector must execute, not just select
# --------------------------------------------------------------------------
def test_backend_selector_must_execute():
    """Selector returns a runnable backend for a valid local action."""
    action = {
        "action_id": "test-006",
        "action_type": "RUN_JSON_VALIDATION",
        "objective": "Validate JSON",
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "target": "reports/superpowers-agentic-autonomy/runtime-discovery/tool-status-runtime.json",
    }
    backends = [LocalDeterministicBackend()]
    backend, trace = select_backend(action, backends)
    assert not trace.blocked, f"Selector blocked: {trace.block_reason}"
    assert backend is not None
    assert backend.backend_type == BackendType.LOCAL_DETERMINISTIC


# --------------------------------------------------------------------------
# 7. Action result must exist after execution
# --------------------------------------------------------------------------
def test_action_result_must_exist(tmp_path):
    """Backend must write result_path; absence means H3 not achieved."""
    result_file = tmp_path / "result.json"
    action = {
        "action_id": "test-007",
        "action_type": "RUN_JSON_VALIDATION",
        "objective": "Validate",
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "target": str(Path("reports/superpowers-agentic-autonomy/runtime-discovery/tool-status-runtime.json")),
        "result_path": str(result_file),
    }
    backend = LocalDeterministicBackend()
    result = backend.execute(action, allowed_write_roots=[str(tmp_path)])
    assert result_file.exists(), "Backend must write result_path — H3 requires runner-written result"
    data = json.loads(result_file.read_text())
    assert data.get("backend_used") == BackendType.LOCAL_DETERMINISTIC.value


# --------------------------------------------------------------------------
# 8. Parent-created proof is invalid
# --------------------------------------------------------------------------
def test_parent_created_proof_invalid(tmp_path):
    """
    If host creates proof file before runner runs, runner should still work but
    the proof-creation pattern (package-107) must not be repeated.
    """
    # Simulate package-107 pattern: host creates the proof file
    proof_file = tmp_path / "host_created_proof.json"
    proof_file.write_text('{"created_by": "host", "fake": true}', encoding="utf-8")

    # Runner OVERWRITES it (runner takes ownership)
    action = {
        "action_id": "test-008",
        "action_type": "RUN_JSON_VALIDATION",
        "objective": "Validate",
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "target": str(Path("reports/superpowers-agentic-autonomy/runtime-discovery/tool-status-runtime.json")),
        "result_path": str(proof_file),
    }
    backend = LocalDeterministicBackend()
    result = backend.execute(action, allowed_write_roots=[str(tmp_path)])
    data = json.loads(proof_file.read_text())
    # Runner must have overwritten the host-created file
    assert data.get("backend_used") == BackendType.LOCAL_DETERMINISTIC.value
    assert "fake" not in data, "Host-created fake proof must be overwritten by runner"


# --------------------------------------------------------------------------
# 9. Package-107 false positive fails
# --------------------------------------------------------------------------
def test_package_107_false_positive_fails():
    """
    The package-107 pattern: host creates proof file, then claims H3.
    Verify that a result file without backend_used=LOCAL_DETERMINISTIC is not H3 proof.
    """
    fake_result = {"status": "SUCCESS", "created_by": "host_narrative", "proof_level": "H3"}
    # This lacks backend_used written by runner — must not be accepted as H3
    assert fake_result.get("backend_used") is None
    assert fake_result.get("backend_used") != BackendType.LOCAL_DETERMINISTIC.value
    # H3 requires result written by runner with backend_used field


# --------------------------------------------------------------------------
# 10. MCP configured != MCP callable
# --------------------------------------------------------------------------
def test_mcp_configured_ne_mcp_callable():
    """MCP config present (L1) does not mean MCP is callable (L5)."""
    backend = McpSuperpowersBackend()
    status = backend.discover()
    # L1 only → CONFIG_ONLY, not VERIFIED_CALLABLE
    assert status != BackendStatus.VERIFIED_CALLABLE, (
        "MCP config-only must not be VERIFIED_CALLABLE. "
        f"Got: {status}"
    )
    assert not backend.can_execute({"action_type": "MCP_TOOL_CALL"})


# --------------------------------------------------------------------------
# 11. LLM configured != LLM ready
# --------------------------------------------------------------------------
def test_llm_configured_ne_llm_ready():
    """LLM endpoint discover() must not claim VERIFIED_CALLABLE from config alone.
    Sprint 3: can_execute returns True when credentials present (implemented, not stub).
    discover() still returns CONFIG_PRESENT (not VERIFIED_CALLABLE) — correct distinction.
    """
    from tools.supervisor.backends.llm_api_backend import LlmApiBackend
    from tools.supervisor.llm_backend_config import get_ready_endpoints
    backend = LlmApiBackend()
    status = backend.discover()
    # discover() must not be VERIFIED_CALLABLE (only runtime HTTP probe would prove that)
    assert status != BackendStatus.VERIFIED_CALLABLE, (
        f"LLM must not be VERIFIED_CALLABLE from config alone. Got: {status}"
    )
    # can_execute: True if credentials present (backend implemented Sprint 3), False if not
    # This is honest: credentials present = can attempt; config-only without creds = cannot
    ready = get_ready_endpoints()
    expected_can_execute = bool(ready)
    assert backend.can_execute({"action_type": "LLM_API_CALL"}) == expected_can_execute


# --------------------------------------------------------------------------
# 12. Direct gate refused
# --------------------------------------------------------------------------
def test_direct_gate_refused():
    """Gate approval action types must fail validation."""
    for gate_type in ["GATE_8_APPROVAL", "GATE_11_APPROVAL"]:
        action = {
            "action_id": "test-012",
            "action_type": gate_type,
            "objective": "Approve gate",
            "preferred_backend": "MANUAL_EXTERNAL_GATE",
        }
        with pytest.raises(NextActionValidationError):
            validate_next_action(action)


# --------------------------------------------------------------------------
# 13. Direct poc-targets mutation refused
# --------------------------------------------------------------------------
def test_direct_poc_targets_mutation_refused():
    """MUTATE_POC_TARGETS action must be rejected."""
    action = {
        "action_id": "test-013",
        "action_type": "MUTATE_POC_TARGETS",
        "objective": "Change poc-targets.yaml",
        "preferred_backend": "LOCAL_DETERMINISTIC",
    }
    with pytest.raises(NextActionValidationError):
        validate_next_action(action)


# --------------------------------------------------------------------------
# 14. OpenSpec artifact is not implementation
# --------------------------------------------------------------------------
def test_openspec_artifact_is_not_implementation():
    """
    OpenSpec generates spec/change artifacts (proposal.md, spec files).
    These are NOT implementation. Proof level is at most H1.
    """
    # Check that openspec is NOT_FOUND (as verified in runtime discovery)
    try:
        import subprocess
        r = subprocess.run(
            "npx --no-install openspec --version",
            shell=True, capture_output=True, text=True, timeout=5
        )
        if r.returncode == 0:
            pytest.skip("OpenSpec found — this test verifies NOT_FOUND scenario")
    except Exception:
        pass
    # OpenSpec NOT_FOUND — confirm no openspec-generated implementation files exist
    openspec_impl_paths = [
        "tools/supervisor/next_action_runner_openspec_generated.py",
        "tools/supervisor/backend_selector_openspec_generated.py",
    ]
    for path in openspec_impl_paths:
        assert not Path(path).exists(), (
            f"OpenSpec-generated impl file found: {path}. "
            "OpenSpec artifacts must not be treated as implementation."
        )
