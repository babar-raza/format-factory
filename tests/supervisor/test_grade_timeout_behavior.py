"""Behavioral tests for TC-GRADE-002: timeout=30 in _sv_sdk_fallback().

These tests verify that:
1. The timeout parameter is passed to client.chat.completions.create()
2. TimeoutError (or any Exception) triggers the retry loop
3. All 3 retries exhausted → returns None (not an exception)
4. Partial timeout (2 fails, 1 success) → returns result

Tests use sys.modules injection to mock the 'openai' import inside _sv_sdk_fallback().
(TC-POSTSPRINT-003)
"""
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, call, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))


def _make_cfg(endpoint="http://test-endpoint/v1"):
    """Build a minimal cfg object matching what _sv_sdk_fallback expects."""
    cfg = MagicMock()
    cfg.endpoint = endpoint
    return cfg


def _call_sdk_fallback_with_mock_openai(mock_create_side_effect, api_key="test-api-key"):
    """Run _sv_sdk_fallback() with a mocked openai module.

    Injects a fake 'openai' module into sys.modules so the __import__("openai")
    inside _sv_sdk_fallback() receives our mock without touching the real openai package.
    """
    from grade_declared_work import _sv_sdk_fallback

    messages = [{"role": "user", "content": "test evidence review"}]
    cfg = _make_cfg()

    # Build mock openai module
    mock_openai = types.ModuleType("openai")
    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create.side_effect = mock_create_side_effect
    mock_openai.OpenAI = MagicMock(return_value=mock_client_instance)

    with patch.dict(sys.modules, {"openai": mock_openai}):
        with patch.dict("os.environ", {"GPT_OSS_API_KEY": api_key}):
            # Patch time.sleep to avoid actual delays during retry backoff
            with patch("time.sleep"):
                result = _sv_sdk_fallback(messages, cfg)

    return result, mock_client_instance


class TestSdkFallbackTimeoutBehavior:
    """Verify timeout=30 and retry behavior in _sv_sdk_fallback()."""

    def test_timeout_parameter_passed_to_create(self):
        """TIMEOUT-001: OpenAI client must be constructed with a timeout parameter.

        TC-GRADE-002 originally verified `timeout=30` on create(). In the hardened path
        (LLM-GRADER-TIMEOUT-001), the timeout is now applied at the client constructor level
        via httpx.Timeout (separate connect + read bounds) rather than on each create() call.
        This test verifies that the OpenAI() client is constructed with some `timeout=` value
        (scalar or httpx.Timeout), proving the per-attempt bound is enforced.
        """
        from grade_declared_work import _sv_sdk_fallback
        import os

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "ADEQUATE"

        mock_openai = types.ModuleType("openai")
        mock_client_instance = MagicMock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI = MagicMock(return_value=mock_client_instance)

        cfg = _make_cfg()
        messages = [{"role": "user", "content": "test evidence review"}]

        with patch.dict(sys.modules, {"openai": mock_openai}):
            with patch.dict("os.environ", {"GPT_OSS_API_KEY": "test-api-key"}):
                with patch("time.sleep"):
                    result = _sv_sdk_fallback(messages, cfg)

        assert result == "ADEQUATE"

        # Verify timeout was set on the OpenAI client constructor (LLM-GRADER-TIMEOUT-001)
        openai_constructor_calls = mock_openai.OpenAI.call_args_list
        assert len(openai_constructor_calls) >= 1, "OpenAI() must be called to create client"
        constructor_kwargs = openai_constructor_calls[0].kwargs
        assert "timeout" in constructor_kwargs, (
            "timeout= must be passed to OpenAI() constructor for bounded per-attempt timeouts. "
            "This is the hardened version of TC-GRADE-002 (LLM-GRADER-TIMEOUT-001)."
        )

    def test_timeout_error_triggers_retry_loop(self):
        """TIMEOUT-002: Exception on first 2 calls → retried; success on 3rd → result returned.

        Proves the `except Exception` catch triggers the retry loop, not a hard failure.
        Simulates a timeout (or any transient error) on attempts 1 and 2, success on 3.
        """
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "ADEQUATE_AFTER_RETRY"

        # First 2 raise TimeoutError-like exception, 3rd succeeds
        class MockTimeoutError(Exception):
            pass

        result, mock_client = _call_sdk_fallback_with_mock_openai(
            mock_create_side_effect=[
                MockTimeoutError("timeout on attempt 1"),
                MockTimeoutError("timeout on attempt 2"),
                mock_response,
            ]
        )

        assert result == "ADEQUATE_AFTER_RETRY", (
            "Should return result after retrying past transient timeouts"
        )
        assert mock_client.chat.completions.create.call_count == 3, (
            f"Expected 3 total attempts (2 failed + 1 success), got {mock_client.chat.completions.create.call_count}"
        )

    def test_all_retries_exhausted_returns_none(self):
        """TIMEOUT-003: Exception on all 3 retries → _sv_sdk_fallback returns None (not raised).

        Critical safety check: when all 3 attempts time out, the function must return None
        gracefully rather than propagating the exception to the caller.
        """
        class MockTimeoutError(Exception):
            pass

        result, mock_client = _call_sdk_fallback_with_mock_openai(
            mock_create_side_effect=[
                MockTimeoutError("attempt 1"),
                MockTimeoutError("attempt 2"),
                MockTimeoutError("attempt 3"),
            ]
        )

        assert result is None, (
            "_sv_sdk_fallback must return None (not raise) when all 3 retries fail"
        )
        assert mock_client.chat.completions.create.call_count == 3, (
            f"Expected exactly 3 attempts before giving up, got {mock_client.chat.completions.create.call_count}"
        )

    def test_no_api_key_returns_none_immediately(self):
        """TIMEOUT-004: Missing API key → returns None immediately without calling create().

        Negative control: _sv_sdk_fallback must short-circuit when GPT_OSS_API_KEY is absent,
        never reaching the create() call (which would block anyway).
        """
        from grade_declared_work import _sv_sdk_fallback

        messages = [{"role": "user", "content": "test"}]
        cfg = _make_cfg()

        mock_openai = types.ModuleType("openai")
        mock_client_instance = MagicMock()
        mock_openai.OpenAI = MagicMock(return_value=mock_client_instance)

        with patch.dict(sys.modules, {"openai": mock_openai}):
            with patch.dict("os.environ", {}, clear=False):
                # Ensure GPT_OSS_API_KEY is not set
                import os
                env_backup = os.environ.pop("GPT_OSS_API_KEY", None)
                try:
                    result = _sv_sdk_fallback(messages, cfg)
                finally:
                    if env_backup is not None:
                        os.environ["GPT_OSS_API_KEY"] = env_backup

        assert result is None, "Must return None immediately when API key is missing"
        mock_client_instance.chat.completions.create.assert_not_called()
