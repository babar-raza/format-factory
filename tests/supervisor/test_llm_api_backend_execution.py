"""
Tests for LLM API backend H5 execution path.
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001
"""
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))

from tools.supervisor.backends.llm_api_backend import LlmApiBackend
from tools.supervisor.execution_backend import BackendStatus, BackendType


class TestLlmApiBackendDiscovery:
    def test_discover_returns_config_present_or_blocked(self):
        backend = LlmApiBackend()
        status = backend.discover()
        assert status in {BackendStatus.CONFIG_PRESENT, BackendStatus.BLOCKED_BY_CREDENTIALS}

    def test_backend_type_is_llm_api(self):
        assert LlmApiBackend().backend_type == BackendType.LLM_API

    def test_can_execute_only_llm_api_call(self):
        backend = LlmApiBackend()
        assert not backend.can_execute({"action_type": "RUN_JSON_VALIDATION"})
        assert not backend.can_execute({"action_type": "GIT_PUSH"})
        # LLM_API_CALL requires credentials; depends on env
        action = {"action_type": "LLM_API_CALL"}
        # can_execute returns True only if credentials present
        # Just verify it doesn't crash
        result = backend.can_execute(action)
        assert isinstance(result, bool)


class TestLlmApiBackendNoCredential:
    def test_execute_without_credential_returns_blocked(self, monkeypatch):
        monkeypatch.setenv("PROFESSIONALIZE_API_KEY", "")
        from tools.supervisor import llm_backend_config
        monkeypatch.setattr(llm_backend_config, "get_ready_endpoints", lambda: [])

        backend = LlmApiBackend()
        result = backend.execute({"action_id": "t1", "action_type": "LLM_API_CALL"}, [])
        assert result.status == "BLOCKED"
        assert result.exit_code == 3

    def test_execute_blocked_does_not_write_files(self, monkeypatch, tmp_path):
        monkeypatch.setattr(
            "tools.supervisor.backends.llm_api_backend.get_ready_endpoints", lambda: []
        )
        backend = LlmApiBackend()
        result_path = str(tmp_path / "out.json")
        result = backend.execute(
            {"action_id": "t1", "action_type": "LLM_API_CALL", "result_path": result_path}, []
        )
        assert result.status == "BLOCKED"
        assert not (tmp_path / "out.json").exists()


class TestLlmApiBackendBoundedCall:
    def test_professionalize_endpoint_classified(self):
        from tools.supervisor.llm_backend_config import classify_endpoint_availability
        status = classify_endpoint_availability("professionalize")
        # Should be CONFIG_PRESENT_CREDENTIAL_PRESENT or CONFIG_PRESENT_CREDENTIAL_ABSENT
        assert "CONFIG_PRESENT" in status or "BLOCKED" in status or "NOT_FOUND" in status

    def test_execute_fails_gracefully_on_network_error(self, monkeypatch, tmp_path):
        """Simulate network failure — backend returns FAILED, not crash."""

        fake_ep = [{"id": "test-ep", "priority": 0, "url": "http://localhost:1",
                    "auth_env": "PROFESSIONALIZE_API_KEY"}]
        monkeypatch.setattr(
            "tools.supervisor.backends.llm_api_backend.get_ready_endpoints", lambda: fake_ep
        )
        monkeypatch.setenv("PROFESSIONALIZE_API_KEY", "fake-key-for-test")

        backend = LlmApiBackend()
        result_path = str(tmp_path / "h5-result.json")
        result = backend.execute(
            {
                "action_id": "h5-test",
                "action_type": "LLM_API_CALL",
                "result_path": result_path,
                "model": "gpt-3.5-turbo",
            },
            [str(tmp_path)],
        )
        # Should return FAILED (network error) or BLOCKED, not crash
        assert result.status in {"FAILED", "BLOCKED"}
        assert result.exit_code != 0


class TestSessionSkillBackend:
    def test_session_skill_discover_returns_not_found(self):
        from tools.supervisor.backends.session_skill_backend import SessionSkillBackend
        backend = SessionSkillBackend()
        assert backend.discover() == BackendStatus.NOT_FOUND

    def test_session_skill_cannot_execute(self):
        from tools.supervisor.backends.session_skill_backend import SessionSkillBackend
        backend = SessionSkillBackend()
        assert not backend.can_execute({"action_type": "anything"})

    def test_session_skill_execute_returns_blocked_with_explanation(self):
        from tools.supervisor.backends.session_skill_backend import SessionSkillBackend
        backend = SessionSkillBackend()
        result = backend.execute({"action_id": "t1"}, [])
        assert result.status == "BLOCKED"
        assert any("SESSION_SKILL_TOOL" in e for e in result.errors)

    def test_session_skill_h5_claim_requires_runner_evidence(self):
        from tools.supervisor.backends.session_skill_backend import SessionSkillBackend
        backend = SessionSkillBackend()
        result = backend.execute({"action_id": "t1"}, [])
        # Proof level must NOT be H5 — cannot claim H5 without runner evidence
        assert result.proof_level is None
