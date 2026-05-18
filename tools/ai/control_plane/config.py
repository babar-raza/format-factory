"""AI Control Plane configuration — loads from environment variables only.

Never prints, logs, or returns actual secret values.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class AIConfig:
    """Immutable AI configuration loaded from environment."""
    endpoint: str
    api_key_present: bool
    provider_name: str = "openai"
    endpoint_env_var: str = "GPT_OSS_ENDPOINT"
    api_key_env_var: str = "GPT_OSS_API_KEY"

    @property
    def endpoint_identity(self) -> str:
        """Return hostname only — no path, no query, no secrets."""
        try:
            parsed = urlparse(self.endpoint)
            return parsed.hostname or "unknown"
        except Exception:
            return "unknown"

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoint) and self.api_key_present


# Alias env var names to check
_ENDPOINT_VARS = ["GPT_OSS_ENDPOINT", "PROFESSIONALIZE_BASE_URL"]
_API_KEY_VARS = ["GPT_OSS_API_KEY", "PROFESSIONALIZE_API_KEY"]


def load_ai_config() -> AIConfig:
    """Load AI configuration from system environment variables.

    Checks primary env vars first, then optional aliases.
    Never returns the API key value itself.
    """
    endpoint = ""
    for var in _ENDPOINT_VARS:
        val = os.environ.get(var, "").strip()
        if val:
            endpoint = val
            break

    api_key_present = False
    for var in _API_KEY_VARS:
        val = os.environ.get(var, "").strip()
        if val:
            api_key_present = True
            break

    return AIConfig(
        endpoint=endpoint,
        api_key_present=api_key_present,
    )


def get_api_key() -> str | None:
    """Return the API key for internal gateway use only.

    This must NEVER be logged, printed, or included in telemetry/evidence.
    Returns None if not configured.
    """
    for var in _API_KEY_VARS:
        val = os.environ.get(var, "").strip()
        if val:
            return val
    return None
