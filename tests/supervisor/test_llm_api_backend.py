"""
Format Factory — LLM API Backend Tests
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001
"""
import pytest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.supervisor.execution_backend import BackendStatus, BackendType
from tools.supervisor.backends.llm_api_backend import LlmApiBackend
from tools.supervisor.llm_backend_config import load_endpoints, classify_endpoint_availability


def test_llm_not_verified_callable():
    backend = LlmApiBackend()
    status = backend.discover()
    assert status != BackendStatus.VERIFIED_CALLABLE


def test_llm_cannot_execute():
    # Sprint 3: LLM backend now executes LLM_API_CALL when credentials present.
    # can_execute returns True if ready endpoints exist, False otherwise.
    # This replaces the old stub assertion (can_execute always False).
    from tools.supervisor.llm_backend_config import get_ready_endpoints
    backend = LlmApiBackend()
    ready = get_ready_endpoints()
    expected = bool(ready)
    assert backend.can_execute({"action_type": "LLM_API_CALL"}) == expected


def test_llm_execute_returns_blocked():
    backend = LlmApiBackend()
    result = backend.execute({"action_id": "t", "action_type": "LLM_API_CALL"}, [])
    assert result.status == "BLOCKED"


def test_endpoints_file_readable():
    endpoints = load_endpoints()
    assert isinstance(endpoints, list)
    assert len(endpoints) >= 1


def test_professionalize_endpoint_has_credential():
    status = classify_endpoint_availability("professionalize")
    assert status == "CONFIG_PRESENT_CREDENTIAL_PRESENT"


def test_anthropic_endpoint_absent():
    status = classify_endpoint_availability("claude-native")
    assert status == "CONFIG_PRESENT_CREDENTIAL_ABSENT"
