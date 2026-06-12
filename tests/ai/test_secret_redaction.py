"""Tests for secret redaction."""

import os
import sys
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.ai.validators.secret_redaction import redact_text, contains_secret


class TestSecretRedaction:
    def test_redact_api_key_pattern(self):
        text = "Authorization: Bearer sk-abc123def456ghi789"
        redacted = redact_text(text)
        assert "sk-abc123def456ghi789" not in redacted
        assert "[REDACTED]" in redacted

    def test_redact_url_key_param(self):
        text = "https://example.com?key=abcdef12345678"
        redacted = redact_text(text)
        assert "abcdef12345678" not in redacted

    def test_clean_text_unchanged(self):
        text = "This is a normal log line with no secrets."
        assert redact_text(text) == text

    def test_contains_secret_true(self):
        assert contains_secret("my key is sk-1234567890abcdef") is True

    def test_contains_secret_false(self):
        assert contains_secret("nothing secret here") is False

    def test_redact_env_var_value(self):
        env = {"GPT_OSS_API_KEY": "my-real-secret-key-here"}
        with patch.dict(os.environ, env, clear=True):
            text = "The key is my-real-secret-key-here in this text"
            redacted = redact_text(text)
            assert "my-real-secret-key-here" not in redacted
            assert "[REDACTED]" in redacted
