"""Secret redaction helper — ensures no secrets leak into logs/telemetry/evidence."""

from __future__ import annotations

import os
import re


# Patterns that look like secrets
_SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{10,}"),      # API keys starting with sk-
    re.compile(r"Bearer\s+[a-zA-Z0-9._-]+"),  # Bearer tokens
    re.compile(r"key=[a-zA-Z0-9]{8,}"),        # URL query params with keys
    re.compile(r"token=[a-zA-Z0-9]{8,}"),      # URL query params with tokens
]

# Env var names that hold secrets
_SECRET_ENV_VARS = [
    "GPT_OSS_API_KEY",
    "PROFESSIONALIZE_API_KEY",
    "AGENT_METRICS_API_KEY",
    "AGENT_METRICS_ENDPOINT",
]


def redact_text(text: str) -> str:
    """Redact potential secrets from a text string."""
    result = text
    for pattern in _SECRET_PATTERNS:
        result = pattern.sub("[REDACTED]", result)

    # Also redact known env var values if they appear
    for var_name in _SECRET_ENV_VARS:
        val = os.environ.get(var_name, "")
        if val and len(val) > 3 and val in result:
            result = result.replace(val, "[REDACTED]")

    return result


def contains_secret(text: str) -> bool:
    """Check if text appears to contain a secret."""
    for pattern in _SECRET_PATTERNS:
        if pattern.search(text):
            return True
    for var_name in _SECRET_ENV_VARS:
        val = os.environ.get(var_name, "")
        if val and len(val) > 3 and val in text:
            return True
    return False
