"""
Format Factory — Execution Backend Tests
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001
"""
import json
import pytest
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root))

from tools.supervisor.execution_backend import BackendStatus, BackendType, ProofLevel
from tools.supervisor.backends.local_deterministic_backend import LocalDeterministicBackend


def test_local_backend_always_available():
    """LOCAL_DETERMINISTIC backend is always VERIFIED_CALLABLE."""
    backend = LocalDeterministicBackend()
    assert backend.discover() == BackendStatus.VERIFIED_CALLABLE


def test_local_backend_supports_json_validation():
    assert LocalDeterministicBackend().can_execute({"action_type": "RUN_JSON_VALIDATION"})


def test_local_backend_supports_yaml_validation():
    assert LocalDeterministicBackend().can_execute({"action_type": "RUN_YAML_VALIDATION"})


def test_local_backend_supports_md_nonempty():
    assert LocalDeterministicBackend().can_execute({"action_type": "RUN_MD_NONEMPTY_CHECK"})


def test_local_backend_does_not_support_llm_call():
    assert not LocalDeterministicBackend().can_execute({"action_type": "LLM_API_CALL"})


def test_local_backend_json_validation_success(tmp_path):
    """Local backend validates a valid JSON file."""
    target = tmp_path / "valid.json"
    target.write_text('{"key": "value"}', encoding="utf-8")
    result_path = tmp_path / "result.json"

    action = {
        "action_id": "be-001",
        "action_type": "RUN_JSON_VALIDATION",
        "objective": "test",
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "target": str(target),
        "result_path": str(result_path),
    }
    backend = LocalDeterministicBackend()
    result = backend.execute(action, [str(tmp_path)])

    assert result.status == "SUCCESS"
    assert result.exit_code == 0
    assert result.backend_used == BackendType.LOCAL_DETERMINISTIC
    assert result.proof_level == ProofLevel.H3
    assert result_path.exists()


def test_local_backend_json_validation_failure(tmp_path):
    """Local backend fails on invalid JSON."""
    target = tmp_path / "bad.json"
    target.write_text('not valid json {', encoding="utf-8")
    result_path = tmp_path / "result.json"

    action = {
        "action_id": "be-002",
        "action_type": "RUN_JSON_VALIDATION",
        "objective": "test bad",
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "target": str(target),
        "result_path": str(result_path),
    }
    backend = LocalDeterministicBackend()
    result = backend.execute(action, [str(tmp_path)])

    assert result.status == "FAILED"
    assert result.errors


def test_local_backend_md_nonempty_success(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text("# Title\n\nContent here.", encoding="utf-8")
    result_path = tmp_path / "result.json"

    action = {
        "action_id": "be-003",
        "action_type": "RUN_MD_NONEMPTY_CHECK",
        "objective": "test md",
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "target": str(md),
        "result_path": str(result_path),
    }
    result = LocalDeterministicBackend().execute(action, [str(tmp_path)])
    assert result.status == "SUCCESS"


def test_local_backend_md_nonempty_failure(tmp_path):
    md = tmp_path / "empty.md"
    md.write_text("   \n   ", encoding="utf-8")
    result_path = tmp_path / "result.json"

    action = {
        "action_id": "be-004",
        "action_type": "RUN_MD_NONEMPTY_CHECK",
        "objective": "test empty md",
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "target": str(md),
        "result_path": str(result_path),
    }
    result = LocalDeterministicBackend().execute(action, [str(tmp_path)])
    assert result.status == "FAILED"


def test_local_backend_result_includes_backend_used(tmp_path):
    target = tmp_path / "v.json"
    target.write_text('{}', encoding="utf-8")
    result_path = tmp_path / "result.json"

    action = {"action_id": "be-005", "action_type": "RUN_JSON_VALIDATION",
              "objective": "t", "preferred_backend": "LOCAL_DETERMINISTIC",
              "target": str(target), "result_path": str(result_path)}
    LocalDeterministicBackend().execute(action, [str(tmp_path)])
    data = json.loads(result_path.read_text())
    assert data["backend_used"] == BackendType.LOCAL_DETERMINISTIC.value


def test_local_backend_enforce_write_root(tmp_path):
    """Backend enforces allowed_write_roots."""
    target = tmp_path / "v.json"
    target.write_text('{}', encoding="utf-8")
    result_path = tmp_path / "outside" / "result.json"  # outside write root

    action = {"action_id": "be-006", "action_type": "RUN_JSON_VALIDATION",
              "objective": "t", "preferred_backend": "LOCAL_DETERMINISTIC",
              "target": str(target), "result_path": str(result_path)}
    backend = LocalDeterministicBackend()
    # Restrict write root to a subdirectory that doesn't contain result_path
    restricted_root = str(tmp_path / "allowed")
    Path(restricted_root).mkdir()
    with pytest.raises(PermissionError):
        backend.execute(action, [restricted_root])
