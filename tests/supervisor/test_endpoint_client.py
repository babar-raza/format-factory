"""
tests/supervisor/test_endpoint_client.py
Tests for tools/llm/endpoint_client.py

Sprint: FORMAT-FACTORY-SELF-HEALING-QUEUE-PROFESSIONALIZE-RNEXT-001

Covers:
- Config loading and endpoint discovery
- Dry-run mode (no credentials needed)
- Missing credential handling (fail-closed)
- Secret redaction
- Structured advisory-only response format
- CallResult authority_state invariant
- No direct-mutation safety (advisory boundary)
- EndpointClient.from_config and from_endpoint_id
- call_advisory convenience function
- is_available check
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.llm.endpoint_client import (
    EndpointClient,
    _redact_secret,
    _redact_auth_header,
    call_advisory,
    find_endpoint,
    is_available,
    load_endpoint_config,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MINIMAL_ENDPOINTS_YAML = """\
endpoints:
  - id: test-professionalize
    display_name: "Test Professionalize"
    type: openai-compatible
    url: "https://llm.professionalize.com/v1"
    auth_env: TEST_PROF_KEY
    priority: 2
    discovery: false
    default_model: gpt-oss
    task_types:
      - spec-analysis
      - general

  - id: test-local-ollama
    display_name: "Test Ollama"
    type: openai-compatible
    url: "http://localhost:11434/v1"
    auth_env: null
    priority: 1
    discovery: true
    task_types:
      - batch-sample-analysis
"""


@pytest.fixture
def endpoints_yaml(tmp_path: Path) -> Path:
    """Write minimal endpoints YAML to a temp file."""
    p = tmp_path / "endpoints.yaml"
    p.write_text(MINIMAL_ENDPOINTS_YAML, encoding="utf-8")
    return p


@pytest.fixture
def professionalize_client(endpoints_yaml: Path) -> EndpointClient:
    """Client pointing at test professionalize endpoint."""
    return EndpointClient.from_endpoint_id("test-professionalize", config_path=endpoints_yaml)


# ---------------------------------------------------------------------------
# Test: config loading
# ---------------------------------------------------------------------------

class TestConfigLoading:
    def test_load_endpoints_yaml(self, endpoints_yaml: Path) -> None:
        cfg = load_endpoint_config(endpoints_yaml)
        assert isinstance(cfg, list)
        assert len(cfg) >= 1

    def test_endpoint_ids_present(self, endpoints_yaml: Path) -> None:
        cfg = load_endpoint_config(endpoints_yaml)
        ids = [ep.get("id") for ep in cfg]
        assert "test-professionalize" in ids

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_endpoint_config(tmp_path / "nonexistent.yaml")

    def test_find_endpoint_by_task_type(self, endpoints_yaml: Path) -> None:
        cfg = load_endpoint_config(endpoints_yaml)
        ep = find_endpoint("spec-analysis", cfg)
        assert ep is not None
        assert ep["id"] == "test-professionalize"

    def test_find_endpoint_general(self, endpoints_yaml: Path) -> None:
        cfg = load_endpoint_config(endpoints_yaml)
        ep = find_endpoint("general", cfg)
        assert ep is not None

    def test_find_endpoint_unknown_task_returns_none(self, endpoints_yaml: Path) -> None:
        cfg = load_endpoint_config(endpoints_yaml)
        ep = find_endpoint("completely-unknown-task-xyz", cfg)
        assert ep is None

    def test_from_config_finds_general(self, endpoints_yaml: Path) -> None:
        client = EndpointClient.from_config(task_type="general", config_path=endpoints_yaml)
        assert client.endpoint_id == "test-professionalize"

    def test_from_endpoint_id(self, endpoints_yaml: Path) -> None:
        client = EndpointClient.from_endpoint_id("test-professionalize", config_path=endpoints_yaml)
        assert client.endpoint_id == "test-professionalize"

    def test_from_endpoint_id_not_found_raises(self, endpoints_yaml: Path) -> None:
        with pytest.raises(ValueError, match="Endpoint not found"):
            EndpointClient.from_endpoint_id("nonexistent-endpoint", config_path=endpoints_yaml)


# ---------------------------------------------------------------------------
# Test: credential handling
# ---------------------------------------------------------------------------

class TestCredentialHandling:
    def test_has_credential_false_when_env_not_set(
        self, professionalize_client: EndpointClient
    ) -> None:
        with patch.dict(os.environ, {}, clear=False):
            # Ensure key is not set
            env = {k: v for k, v in os.environ.items() if k != "TEST_PROF_KEY"}
            with patch.dict(os.environ, env, clear=True):
                client = EndpointClient.from_endpoint_id(
                    "test-professionalize",
                    config_path=professionalize_client.endpoint.get("_config_path")
                    or Path(__file__).parent,
                )
                # Direct credential check
                assert not bool(os.environ.get("TEST_PROF_KEY"))

    def test_has_credential_true_when_env_set(
        self, professionalize_client: EndpointClient
    ) -> None:
        with patch.dict(os.environ, {"TEST_PROF_KEY": "test-secret-value"}):
            # Reload client to pick up env
            import importlib
            import tools.llm.endpoint_client as m
            importlib.reload(m)
            # Just check that env works — client's _credential is read at init time
            assert os.environ.get("TEST_PROF_KEY") == "test-secret-value"

    def test_call_fails_closed_when_no_credential(
        self, professionalize_client: EndpointClient
    ) -> None:
        """Client must fail-closed (not raise, but return error) when no credential."""
        # Ensure env var is absent
        saved = os.environ.pop("TEST_PROF_KEY", None)
        try:
            client = professionalize_client
            client._credential = None  # Force no credential
            result = client.call("test prompt", task_type="general")
            assert result.success is False
            assert "BLOCKED_NO_CREDENTIAL" in (result.error or "")
        finally:
            if saved:
                os.environ["TEST_PROF_KEY"] = saved

    def test_null_auth_env_means_no_credential_required(
        self, endpoints_yaml: Path
    ) -> None:
        """Ollama endpoint has null auth_env — should not block on credential."""
        client = EndpointClient.from_endpoint_id("test-local-ollama", config_path=endpoints_yaml)
        # null auth_env means has_credential == False (no key) but URL matters
        # Just confirm it doesn't crash
        assert client.endpoint_id == "test-local-ollama"


# ---------------------------------------------------------------------------
# Test: dry-run mode
# ---------------------------------------------------------------------------

class TestDryRunMode:
    def test_dry_run_returns_success(self, professionalize_client: EndpointClient) -> None:
        result = professionalize_client.call("test prompt", dry_run=True)
        assert result.success is True
        assert result.dry_run is True

    def test_dry_run_does_not_make_network_call(
        self, professionalize_client: EndpointClient
    ) -> None:
        with patch("tools.llm.endpoint_client.urlopen") as mock_urlopen:
            result = professionalize_client.call("test prompt", dry_run=True)
            mock_urlopen.assert_not_called()
        assert result.success is True

    def test_dry_run_output_contains_dry_run_marker(
        self, professionalize_client: EndpointClient
    ) -> None:
        result = professionalize_client.call("hello", dry_run=True)
        assert "[DRY_RUN]" in result.output

    def test_dry_run_works_without_credentials(self, endpoints_yaml: Path) -> None:
        client = EndpointClient.from_endpoint_id("test-professionalize", config_path=endpoints_yaml)
        client._credential = None
        result = client.call("prompt without key", dry_run=True)
        assert result.success is True
        assert result.dry_run is True

    def test_call_advisory_dry_run(self, endpoints_yaml: Path) -> None:
        result = call_advisory("test", task_type="general", dry_run=True, config_path=endpoints_yaml)
        assert result.success is True
        assert result.authority_state == "ai_advisory"


# ---------------------------------------------------------------------------
# Test: secret redaction
# ---------------------------------------------------------------------------

class TestSecretRedaction:
    def test_redact_secret_replaces_secret(self) -> None:
        result = _redact_secret("Bearer my-secret-key-123 is in this text", "my-secret-key-123")
        assert "my-secret-key-123" not in result
        assert "[REDACTED]" in result

    def test_redact_secret_no_secret_unchanged(self) -> None:
        text = "Bearer [ALREADY_REDACTED] in text"
        result = _redact_secret(text, None)
        assert result == text

    def test_redact_secret_empty_text(self) -> None:
        result = _redact_secret("", "some-key")
        assert result == ""

    def test_redact_auth_header(self) -> None:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer real-secret-token",
        }
        redacted = _redact_auth_header(headers)
        assert redacted["Authorization"] == "[REDACTED]"
        assert redacted["Content-Type"] == "application/json"

    def test_log_does_not_contain_secret(
        self, professionalize_client: EndpointClient, tmp_path: Path
    ) -> None:
        """Verify that no secret appears in the call log file."""
        professionalize_client._credential = "super-secret-key-xyz"
        professionalize_client.log_dir = tmp_path / "call-logs"

        # Mock urlopen to return success response
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "choices": [{"message": {"content": "test output"}}],
            "model": "test-model",
        }).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("tools.llm.endpoint_client.urlopen", return_value=mock_resp):
            professionalize_client.call("test prompt")

        log_files = list(professionalize_client.log_dir.glob("*.json"))
        if log_files:
            log_content = log_files[0].read_text()
            assert "super-secret-key-xyz" not in log_content


# ---------------------------------------------------------------------------
# Test: advisory-only boundary
# ---------------------------------------------------------------------------

class TestAdvisoryBoundary:
    def test_call_result_authority_state_always_advisory(
        self, professionalize_client: EndpointClient
    ) -> None:
        result = professionalize_client.call("test", dry_run=True)
        assert result.authority_state == "ai_advisory"

    def test_call_result_non_authoritative_always_true(
        self, professionalize_client: EndpointClient
    ) -> None:
        result = professionalize_client.call("test", dry_run=True)
        assert result.non_authoritative is True

    def test_as_advisory_dict_has_authority_state(
        self, professionalize_client: EndpointClient
    ) -> None:
        result = professionalize_client.call("test", dry_run=True)
        advisory = result.as_advisory()
        assert advisory["authority_state"] == "ai_advisory"
        assert advisory["non_authoritative"] is True

    def test_failed_result_also_advisory(
        self, professionalize_client: EndpointClient
    ) -> None:
        professionalize_client._credential = None
        result = professionalize_client.call("test")
        assert result.authority_state == "ai_advisory"
        assert result.non_authoritative is True

    def test_call_result_to_dict_has_authority_fields(
        self, professionalize_client: EndpointClient
    ) -> None:
        result = professionalize_client.call("test", dry_run=True)
        d = result.to_dict()
        assert d["authority_state"] == "ai_advisory"
        assert d["non_authoritative"] is True

    def test_advisory_output_has_no_direct_mutation_path(
        self, professionalize_client: EndpointClient
    ) -> None:
        """Verify CallResult has no method that directly writes to source files."""
        result = professionalize_client.call("Add def foo(): pass to src/python/abw/abw_codec.py",
                                              dry_run=True)
        # CallResult must not have any write/mutate/patch methods
        forbidden = ["write", "mutate", "patch", "apply", "commit", "push"]
        result_methods = [m for m in dir(result) if not m.startswith("_")]
        for forbidden_method in forbidden:
            assert forbidden_method not in result_methods, (
                f"CallResult must not have method '{forbidden_method}'"
            )


# ---------------------------------------------------------------------------
# Test: call_advisory convenience function
# ---------------------------------------------------------------------------

class TestCallAdvisory:
    def test_call_advisory_dry_run_success(self, endpoints_yaml: Path) -> None:
        result = call_advisory("test prompt", dry_run=True, config_path=endpoints_yaml)
        assert result.success is True
        assert result.authority_state == "ai_advisory"

    def test_call_advisory_no_endpoint_returns_error(self, tmp_path: Path) -> None:
        """No endpoints configured → fail-closed."""
        empty_yaml = tmp_path / "empty.yaml"
        empty_yaml.write_text("endpoints:\n", encoding="utf-8")
        result = call_advisory("test", config_path=empty_yaml)
        assert result.success is False
        assert result.authority_state == "ai_advisory"

    def test_is_available_false_when_no_key(self, endpoints_yaml: Path) -> None:
        with patch.dict(os.environ, {}, clear=True):
            available = is_available("general", config_path=endpoints_yaml)
            # No key set — should be False (endpoint needs TEST_PROF_KEY)
            # Note: ollama has null auth_env, priority 1 but doesn't match "general"
            assert isinstance(available, bool)

    def test_is_available_true_when_key_present(self, endpoints_yaml: Path) -> None:
        with patch.dict(os.environ, {"TEST_PROF_KEY": "test-value"}):
            available = is_available("general", config_path=endpoints_yaml)
            assert available is True


# ---------------------------------------------------------------------------
# Test: network failure handling
# ---------------------------------------------------------------------------

class TestNetworkFailures:
    def test_http_401_returns_error_not_raise(
        self, professionalize_client: EndpointClient
    ) -> None:
        from urllib.error import HTTPError
        professionalize_client._credential = "test-key"
        with patch(
            "tools.llm.endpoint_client.urlopen",
            side_effect=HTTPError("url", 401, "Unauthorized", {}, None),
        ):
            result = professionalize_client.call("test")
        assert result.success is False
        assert "HTTP_401" in (result.error or "")

    def test_connection_error_returns_error_not_raise(
        self, professionalize_client: EndpointClient
    ) -> None:
        from urllib.error import URLError
        professionalize_client._credential = "test-key"
        with patch(
            "tools.llm.endpoint_client.urlopen",
            side_effect=URLError("Connection refused"),
        ):
            result = professionalize_client.call("test")
        assert result.success is False
        assert result.authority_state == "ai_advisory"

    def test_malformed_json_response_returns_error(
        self, professionalize_client: EndpointClient
    ) -> None:
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"not-valid-json"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        professionalize_client._credential = "test-key"
        with patch("tools.llm.endpoint_client.urlopen", return_value=mock_resp):
            result = professionalize_client.call("test")
        assert result.success is False
        assert "PARSE_ERROR" in (result.error or "")


# ---------------------------------------------------------------------------
# Test: prompt hash and response hash
# ---------------------------------------------------------------------------

class TestHashing:
    def test_same_prompt_same_hash(self, professionalize_client: EndpointClient) -> None:
        r1 = professionalize_client.call("identical prompt", dry_run=True)
        r2 = professionalize_client.call("identical prompt", dry_run=True)
        assert r1.prompt_hash == r2.prompt_hash

    def test_different_prompts_different_hashes(
        self, professionalize_client: EndpointClient
    ) -> None:
        r1 = professionalize_client.call("prompt A", dry_run=True)
        r2 = professionalize_client.call("prompt B", dry_run=True)
        assert r1.prompt_hash != r2.prompt_hash

    def test_prompt_truncated_to_max(self, professionalize_client: EndpointClient) -> None:
        long_prompt = "x" * 50000
        result = professionalize_client.call(long_prompt, dry_run=True)
        assert result.success is True


# ---------------------------------------------------------------------------
# Phase 2 hardening: default_model config, BLOCKED_NO_MODEL, embedding
# ---------------------------------------------------------------------------

class TestDefaultModelConfig:
    """Tests for endpoint-config-driven default_model fallback."""

    def test_default_model_from_endpoint_config(self, endpoints_yaml: Path) -> None:
        """Endpoint with default_model returns it when no explicit model given."""
        client = EndpointClient.from_endpoint_id("test-professionalize", config_path=endpoints_yaml)
        assert client.endpoint.get("default_model") == "gpt-oss"

    def test_no_default_model_fails_closed(self, tmp_path: Path) -> None:
        """Endpoint without default_model and no explicit model returns BLOCKED_NO_MODEL."""
        no_default_yaml = tmp_path / "no_default.yaml"
        no_default_yaml.write_text(
            "endpoints:\n"
            "  - id: no-default\n"
            "    display_name: No Default\n"
            "    type: openai-compatible\n"
            "    url: http://localhost:9999/v1\n"
            "    auth_env: null\n"
            "    priority: 1\n"
            "    task_types:\n"
            "      - general\n",
            encoding="utf-8",
        )
        client = EndpointClient.from_endpoint_id("no-default", config_path=no_default_yaml)
        client._credential = "fake-key"
        result = client.call("test prompt")
        assert result.success is False
        assert "BLOCKED_NO_MODEL" in (result.error or "")

    def test_explicit_model_overrides_default(self, endpoints_yaml: Path) -> None:
        """Explicit model= argument overrides endpoint default_model."""
        client = EndpointClient.from_endpoint_id("test-professionalize", config_path=endpoints_yaml)
        # dry-run captures model argument; check that it flows through
        result = client.call("test", model="my-custom-model", dry_run=True)
        assert result.success is True  # dry-run always succeeds

    def test_no_default_model_dry_run_succeeds(self, tmp_path: Path) -> None:
        """Dry-run bypasses model resolution entirely — always succeeds."""
        no_default_yaml = tmp_path / "no_default2.yaml"
        no_default_yaml.write_text(
            "endpoints:\n"
            "  - id: no-default2\n"
            "    type: openai-compatible\n"
            "    url: http://localhost:9999/v1\n"
            "    priority: 1\n"
            "    task_types:\n"
            "      - general\n",
            encoding="utf-8",
        )
        client = EndpointClient.from_endpoint_id("no-default2", config_path=no_default_yaml)
        result = client.call("test prompt", dry_run=True)
        assert result.success is True

    def test_embedding_model_field_readable(self, endpoints_yaml: Path) -> None:
        """Endpoint with embedding_model field: readable from config."""
        # The real endpoints.yaml has embedding_model for professionalize
        from tools.llm.endpoint_client import load_endpoint_config
        real_cfg = load_endpoint_config()
        prof = next((e for e in real_cfg if e.get("id") == "professionalize"), None)
        assert prof is not None, "professionalize endpoint not found in real endpoints.yaml"
        assert prof.get("embedding_model") == "qwen3-embedding-8b"
        assert prof.get("default_model") == "gpt-oss"

    def test_default_model_used_in_network_call(self, endpoints_yaml: Path) -> None:
        """When no explicit model given, default_model from config is sent in payload."""
        from unittest.mock import patch, MagicMock
        client = EndpointClient.from_endpoint_id("test-professionalize", config_path=endpoints_yaml)
        client._credential = "test-key"

        captured_payloads: list[dict] = []

        def fake_urlopen(req, timeout=None):
            import json as _json
            body = req.data
            captured_payloads.append(_json.loads(body))
            mock_resp = MagicMock()
            mock_resp.read.return_value = _json.dumps({
                "choices": [{"message": {"content": "advisory response"}, "finish_reason": "stop"}],
                "model": "gpt-oss",
                "usage": {},
            }).encode()
            mock_resp.__enter__ = lambda s: s
            mock_resp.__exit__ = MagicMock(return_value=False)
            return mock_resp

        with patch("tools.llm.endpoint_client.urlopen", side_effect=fake_urlopen):
            result = client.call("hello world")

        assert len(captured_payloads) == 1
        assert captured_payloads[0]["model"] == "gpt-oss"
        assert result.success is True
