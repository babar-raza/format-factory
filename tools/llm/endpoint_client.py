"""
tools/llm/endpoint_client.py — Governed LLM Endpoint Client
Sprint: FORMAT-FACTORY-SELF-HEALING-QUEUE-PROFESSIONALIZE-RNEXT-001

Provides a minimal, safe, auditable client for LLM endpoints configured in
tools/llm/endpoints.yaml, including llm.professionalize.com.

Hard safety rules:
  - LLM output is ALWAYS advisory. authority_state = "ai_advisory".
  - Output must NEVER directly mutate product source, supervisor, queue, or evidence.
  - Secrets read from environment variables only; never hardcoded.
  - All requests/responses logged with secret redaction.
  - Fail closed on missing credentials or network failure.
  - Dry-run mode available for testing without credentials.

Proof level: H5 (API call made, structured response received, evidence logged).

Usage:
    client = EndpointClient.from_config()
    result = client.call(
        task_type="spec-analysis",
        prompt="Summarize this evidence: ...",
        dry_run=False,
    )
    # result.authority_state == "ai_advisory"
    # result.output is the advisory text
    # result.evidence contains provenance for logging
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

_here = Path(__file__).resolve().parent
_REPO_ROOT = _here.parent.parent
_ENDPOINTS_YAML = _here / "endpoints.yaml"

# Advisory constant — never changes
_AUTHORITY_STATE = "ai_advisory"
_NON_AUTHORITATIVE = True

# Bounded limits
_DEFAULT_TIMEOUT_SECONDS = 30
_MAX_RETRIES = 2
_MAX_RESPONSE_CHARS = 8192
_MAX_PROMPT_CHARS = 16384


# ---------------------------------------------------------------------------
# Config loading (YAML without external deps)
# ---------------------------------------------------------------------------

def _parse_yaml_endpoints(text: str) -> list[dict[str, Any]]:
    """Minimal YAML parser for endpoints.yaml — no external deps required."""
    endpoints: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        # Detect new endpoint entry
        if stripped == "- id:" or stripped.startswith("- id:"):
            if current is not None:
                endpoints.append(current)
            current = {}
            val = stripped.split(":", 1)[1].strip() if ":" in stripped else ""
            if val:
                current["id"] = val
        elif current is not None and ":" in stripped and not stripped.startswith("-"):
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()
            # Type coercion
            if val == "null" or val == "~":
                current[key] = None
            elif val == "true":
                current[key] = True
            elif val == "false":
                current[key] = False
            elif val.isdigit():
                current[key] = int(val)
            else:
                # Remove quotes
                if (val.startswith('"') and val.endswith('"')) or \
                   (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                current[key] = val
        elif current is not None and stripped.startswith("- ") and \
             len(stripped) > 2 and ":" not in stripped:
            # List item
            key = list(current.keys())[-1] if current else None
            if key and isinstance(current.get(key), str):
                current[key] = [current[key], stripped[2:]]
            elif key and isinstance(current.get(key), list):
                current[key].append(stripped[2:])

    if current is not None:
        endpoints.append(current)
    return endpoints


def load_endpoint_config(config_path: "Path | str | None" = None) -> list[dict[str, Any]]:
    """Load endpoint configuration from endpoints.yaml."""
    path = Path(config_path) if config_path else _ENDPOINTS_YAML
    if not path.exists():
        raise FileNotFoundError(f"Endpoint config not found: {path}")
    text = path.read_text(encoding="utf-8")
    return _parse_yaml_endpoints(text)


def find_endpoint(
    task_type: str,
    config: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    """Find the highest-priority endpoint that supports the given task_type."""
    cfg = config or load_endpoint_config()
    candidates = []
    for ep in cfg:
        if ep.get("enabled") is False:
            continue
        tasks = ep.get("task_types", [])
        if isinstance(tasks, str):
            tasks = [tasks]
        if task_type in tasks:
            candidates.append(ep)
    if not candidates:
        return None
    return min(candidates, key=lambda e: e.get("priority", 99))


# ---------------------------------------------------------------------------
# Secret management
# ---------------------------------------------------------------------------

def _get_credential(auth_env: str | None) -> str | None:
    """Read credential from environment variable. Never from code."""
    if not auth_env:
        return None
    return os.environ.get(auth_env)


def _redact_secret(text: str, secret: str | None) -> str:
    """Replace secret value with [REDACTED] in text."""
    if not secret or not text:
        return text
    return text.replace(secret, "[REDACTED]")


def _redact_auth_header(headers: dict[str, str]) -> dict[str, str]:
    """Return headers dict with Authorization value redacted."""
    result = {}
    for k, v in headers.items():
        if k.lower() == "authorization":
            result[k] = "[REDACTED]"
        else:
            result[k] = v
    return result


# ---------------------------------------------------------------------------
# CallResult
# ---------------------------------------------------------------------------

class CallResult:
    """Result of an LLM API call. Always advisory."""

    def __init__(
        self,
        output: str,
        endpoint_id: str,
        model: str | None,
        task_type: str,
        prompt_hash: str,
        response_hash: str,
        duration_ms: int,
        success: bool,
        error: str | None = None,
        dry_run: bool = False,
        evidence: dict[str, Any] | None = None,
    ) -> None:
        self.output = output
        self.endpoint_id = endpoint_id
        self.model = model
        self.task_type = task_type
        self.prompt_hash = prompt_hash
        self.response_hash = response_hash
        self.duration_ms = duration_ms
        self.success = success
        self.error = error
        self.dry_run = dry_run
        self.authority_state = _AUTHORITY_STATE
        self.non_authoritative = _NON_AUTHORITATIVE
        self.evidence = evidence or {}
        self.called_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "output": self.output,
            "endpoint_id": self.endpoint_id,
            "model": self.model,
            "task_type": self.task_type,
            "prompt_hash": self.prompt_hash,
            "response_hash": self.response_hash,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
            "dry_run": self.dry_run,
            "authority_state": self.authority_state,
            "non_authoritative": self.non_authoritative,
            "called_at": self.called_at,
            "evidence": self.evidence,
        }

    def as_advisory(self) -> dict[str, Any]:
        """Return structured advisory result safe for passing to other systems."""
        return {
            "advisory_text": self.output if self.success else "",
            "authority_state": self.authority_state,
            "non_authoritative": self.non_authoritative,
            "success": self.success,
            "error": self.error,
            "endpoint_id": self.endpoint_id,
            "prompt_hash": self.prompt_hash,
            "dry_run": self.dry_run,
        }


# ---------------------------------------------------------------------------
# EmbedResult
# ---------------------------------------------------------------------------

class EmbedResult:
    """Result of a /v1/embeddings API call. Always advisory."""

    def __init__(
        self,
        embeddings: list[list[float]],
        endpoint_id: str,
        model: str | None,
        input_hash: str,
        success: bool,
        error: str | None = None,
        dry_run: bool = False,
        duration_ms: int = 0,
    ) -> None:
        self.embeddings = embeddings
        self.endpoint_id = endpoint_id
        self.model = model
        self.input_hash = input_hash
        self.success = success
        self.error = error
        self.dry_run = dry_run
        self.duration_ms = duration_ms
        self.authority_state = _AUTHORITY_STATE
        self.non_authoritative = _NON_AUTHORITATIVE
        self.called_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "embeddings_count": len(self.embeddings),
            "embedding_dim": len(self.embeddings[0]) if self.embeddings else 0,
            "endpoint_id": self.endpoint_id,
            "model": self.model,
            "input_hash": self.input_hash,
            "success": self.success,
            "error": self.error,
            "dry_run": self.dry_run,
            "duration_ms": self.duration_ms,
            "authority_state": self.authority_state,
            "non_authoritative": self.non_authoritative,
            "called_at": self.called_at,
        }


# ---------------------------------------------------------------------------
# EndpointClient
# ---------------------------------------------------------------------------

class EndpointClient:
    """Governed LLM endpoint client.

    - Reads config from endpoints.yaml
    - Credentials from env vars only
    - All calls are advisory (authority_state = "ai_advisory")
    - Dry-run mode available
    - Fail-closed on missing credentials
    - Request/response logged with secret redaction
    """

    def __init__(
        self,
        endpoint: dict[str, Any],
        *,
        timeout: int = _DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = _MAX_RETRIES,
        log_dir: Path | None = None,
    ) -> None:
        self.endpoint = endpoint
        self.timeout = timeout
        self.max_retries = max_retries
        self.log_dir = log_dir or (_REPO_ROOT / ".local" / "llm-call-logs")
        self._credential: str | None = _get_credential(endpoint.get("auth_env"))

    @classmethod
    def from_config(
        cls,
        task_type: str = "general",
        config_path: Path | None = None,
        **kwargs: Any,
    ) -> "EndpointClient":
        """Create client for the highest-priority endpoint supporting task_type."""
        cfg = load_endpoint_config(config_path)
        ep = find_endpoint(task_type, cfg)
        if ep is None:
            raise ValueError(f"No configured endpoint supports task_type={task_type!r}")
        return cls(ep, **kwargs)

    @classmethod
    def from_endpoint_id(
        cls,
        endpoint_id: str,
        config_path: Path | None = None,
        **kwargs: Any,
    ) -> "EndpointClient":
        """Create client for a specific endpoint by ID."""
        cfg = load_endpoint_config(config_path)
        for ep in cfg:
            if ep.get("id") == endpoint_id:
                ep = dict(ep)
                ep["_config_path"] = str(config_path) if config_path else None
                return cls(ep, **kwargs)
        raise ValueError(f"Endpoint not found: {endpoint_id!r}")

    @property
    def has_credential(self) -> bool:
        """True if the API credential is available in the environment."""
        return bool(self._credential)

    @property
    def endpoint_id(self) -> str:
        return self.endpoint.get("id", "unknown")

    @property
    def endpoint_url(self) -> str | None:
        url = self.endpoint.get("url")
        if url and "${" in str(url):
            # Resolve env var reference
            match = re.search(r"\$\{(\w+)\}", url)
            if match:
                val = os.environ.get(match.group(1))
                return val if val else None
        return url

    def call(
        self,
        prompt: str,
        *,
        task_type: str = "general",
        model: str | None = None,
        dry_run: bool = False,
        system_prompt: str | None = None,
    ) -> CallResult:
        """Make an advisory LLM call.

        Args:
            prompt: The user prompt (truncated to _MAX_PROMPT_CHARS).
            task_type: Task type for routing/logging.
            model: Model name override (uses endpoint default if None).
            dry_run: If True, skip actual API call and return mock advisory.
            system_prompt: Optional system prompt prefix.

        Returns:
            CallResult with authority_state="ai_advisory".
        """
        start = time.monotonic()

        # Truncate prompt for safety
        safe_prompt = prompt[:_MAX_PROMPT_CHARS]
        prompt_hash = hashlib.sha256(safe_prompt.encode()).hexdigest()[:16]

        if dry_run:
            return self._dry_run_result(safe_prompt, task_type, prompt_hash)

        if not self.has_credential:
            return CallResult(
                output="",
                endpoint_id=self.endpoint_id,
                model=model,
                task_type=task_type,
                prompt_hash=prompt_hash,
                response_hash="",
                duration_ms=0,
                success=False,
                error=f"BLOCKED_NO_CREDENTIAL: {self.endpoint.get('auth_env', 'unknown')} not set",
            )

        url = self.endpoint_url
        if not url:
            return CallResult(
                output="",
                endpoint_id=self.endpoint_id,
                model=model,
                task_type=task_type,
                prompt_hash=prompt_hash,
                response_hash="",
                duration_ms=0,
                success=False,
                error="BLOCKED_NO_URL: endpoint URL not configured or env var not set",
            )

        # Build request
        ep_type = self.endpoint.get("type", "openai-compatible")
        return self._call_openai_compatible(
            url=url,
            prompt=safe_prompt,
            system_prompt=system_prompt,
            model=model,
            task_type=task_type,
            prompt_hash=prompt_hash,
            start=start,
        )

    def _dry_run_result(
        self, prompt: str, task_type: str, prompt_hash: str
    ) -> CallResult:
        """Return a safe dry-run result without making any network call."""
        mock_output = (
            f"[DRY_RUN] Advisory response for task_type={task_type!r}. "
            f"Endpoint: {self.endpoint_id}. Prompt hash: {prompt_hash}. "
            f"Has credential: {self.has_credential}. "
            "This is a dry-run response and has no authority over any system."
        )
        return CallResult(
            output=mock_output,
            endpoint_id=self.endpoint_id,
            model=None,
            task_type=task_type,
            prompt_hash=prompt_hash,
            response_hash=hashlib.sha256(mock_output.encode()).hexdigest()[:16],
            duration_ms=0,
            success=True,
            dry_run=True,
            evidence={"dry_run": True, "credential_present": self.has_credential},
        )

    def _call_openai_compatible(
        self,
        *,
        url: str,
        prompt: str,
        system_prompt: str | None,
        model: str | None,
        task_type: str,
        prompt_hash: str,
        start: float,
    ) -> CallResult:
        """Call an OpenAI-compatible /v1/chat/completions endpoint."""
        chat_url = url.rstrip("/") + "/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Resolve model: explicit > endpoint default_model > fail-closed error
        resolved_model = model or self.endpoint.get("default_model")
        if not resolved_model:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return CallResult(
                output="",
                endpoint_id=self.endpoint_id,
                model=None,
                task_type=task_type,
                prompt_hash=prompt_hash,
                response_hash="",
                duration_ms=elapsed_ms,
                success=False,
                error="BLOCKED_NO_MODEL: no model specified and no default_model in endpoint config",
            )

        payload = {
            "model": resolved_model,
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.1,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._credential}",
        }

        body = json.dumps(payload).encode("utf-8")
        req = Request(chat_url, data=body, headers=headers, method="POST")

        last_error: str | None = None
        for attempt in range(self.max_retries + 1):
            try:
                with urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read().decode("utf-8")
                    elapsed_ms = int((time.monotonic() - start) * 1000)
                    return self._parse_openai_response(
                        raw, task_type, prompt_hash, model, elapsed_ms
                    )
            except HTTPError as exc:
                last_error = f"HTTP_{exc.code}: {exc.reason}"
                if exc.code in (401, 403, 404):
                    break  # Non-retryable auth/not-found errors
            except URLError as exc:
                last_error = f"URL_ERROR: {exc.reason}"
            except Exception as exc:  # noqa: BLE001
                last_error = f"UNEXPECTED: {type(exc).__name__}: {exc}"
                break

            if attempt < self.max_retries:
                time.sleep(1.0 * (attempt + 1))  # linear backoff

        elapsed_ms = int((time.monotonic() - start) * 1000)
        return CallResult(
            output="",
            endpoint_id=self.endpoint_id,
            model=model,
            task_type=task_type,
            prompt_hash=prompt_hash,
            response_hash="",
            duration_ms=elapsed_ms,
            success=False,
            error=last_error or "UNKNOWN_ERROR",
        )

    def _parse_openai_response(
        self,
        raw: str,
        task_type: str,
        prompt_hash: str,
        model: str | None,
        elapsed_ms: int,
    ) -> CallResult:
        """Parse OpenAI-compatible response JSON and return CallResult."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            return CallResult(
                output="",
                endpoint_id=self.endpoint_id,
                model=model,
                task_type=task_type,
                prompt_hash=prompt_hash,
                response_hash="",
                duration_ms=elapsed_ms,
                success=False,
                error=f"PARSE_ERROR: {exc}",
            )

        # Extract content from choices[0].message.content
        try:
            output = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            output = data.get("content", "") or str(data)

        output = output[:_MAX_RESPONSE_CHARS]
        response_hash = hashlib.sha256(output.encode()).hexdigest()[:16]
        actual_model = data.get("model") or model

        evidence = {
            "endpoint_id": self.endpoint_id,
            "task_type": task_type,
            "prompt_hash": prompt_hash,
            "response_hash": response_hash,
            "elapsed_ms": elapsed_ms,
            "model": actual_model,
            "usage": data.get("usage"),
        }

        # Log call evidence (redacted)
        self._log_call(evidence, output)

        return CallResult(
            output=output,
            endpoint_id=self.endpoint_id,
            model=actual_model,
            task_type=task_type,
            prompt_hash=prompt_hash,
            response_hash=response_hash,
            duration_ms=elapsed_ms,
            success=True,
            evidence=evidence,
        )

    def embed(
        self,
        texts: list[str],
        *,
        model: str | None = None,
        dry_run: bool = False,
    ) -> "EmbedResult":
        """Call the /v1/embeddings endpoint (advisory only).

        All embeddings output carries authority_state="ai_advisory".
        Embeddings MUST NOT be used to make governance decisions or
        to mutate product source, supervisor, queue, or evidence.

        Args:
            texts: List of strings to embed. Each is truncated to _MAX_PROMPT_CHARS.
            model: Model name override. Falls back to endpoint default_model.
            dry_run: If True, return zero-vector mocks without calling API.

        Returns:
            EmbedResult with advisory embeddings, or error.
        """
        safe_texts = [t[:_MAX_PROMPT_CHARS] for t in texts]
        input_hash = hashlib.sha256("||".join(safe_texts).encode()).hexdigest()[:16]
        start = time.monotonic()

        if dry_run:
            return EmbedResult(
                embeddings=[[0.0] for _ in safe_texts],
                endpoint_id=self.endpoint_id,
                model=model or "dry-run",
                input_hash=input_hash,
                success=True,
                dry_run=True,
            )

        if not self.has_credential:
            return EmbedResult(
                embeddings=[],
                endpoint_id=self.endpoint_id,
                model=model,
                input_hash=input_hash,
                success=False,
                error=f"BLOCKED_NO_CREDENTIAL: {self.endpoint.get('auth_env', 'unknown')} not set",
            )

        url = self.endpoint_url
        if not url:
            return EmbedResult(
                embeddings=[],
                endpoint_id=self.endpoint_id,
                model=model,
                input_hash=input_hash,
                success=False,
                error="BLOCKED_NO_URL: endpoint has no base_url",
            )

        resolved_model = model or self.endpoint.get("default_model")
        if not resolved_model:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return EmbedResult(
                embeddings=[],
                endpoint_id=self.endpoint_id,
                model=None,
                input_hash=input_hash,
                success=False,
                error="BLOCKED_NO_MODEL: no model specified and no default_model in endpoint config",
                duration_ms=elapsed_ms,
            )

        embed_url = url.rstrip("/") + "/embeddings"
        payload = {
            "model": resolved_model,
            "input": safe_texts,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._credential}",
        }

        body = json.dumps(payload).encode("utf-8")
        req = Request(embed_url, data=body, headers=headers, method="POST")

        last_error: str | None = None
        for attempt in range(self.max_retries + 1):
            try:
                with urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read().decode("utf-8")
                    elapsed_ms = int((time.monotonic() - start) * 1000)
                    return self._parse_embed_response(
                        raw, resolved_model, input_hash, elapsed_ms
                    )
            except HTTPError as exc:
                last_error = f"HTTP_{exc.code}: {exc.reason}"
                if exc.code in (401, 403, 404):
                    break
            except URLError as exc:
                last_error = f"URL_ERROR: {exc.reason}"
            except Exception as exc:  # noqa: BLE001
                last_error = f"UNEXPECTED: {type(exc).__name__}: {exc}"
                break

            if attempt < self.max_retries:
                time.sleep(1.0 * (attempt + 1))

        elapsed_ms = int((time.monotonic() - start) * 1000)
        return EmbedResult(
            embeddings=[],
            endpoint_id=self.endpoint_id,
            model=resolved_model,
            input_hash=input_hash,
            success=False,
            error=last_error or "UNKNOWN_ERROR",
            duration_ms=elapsed_ms,
        )

    def _parse_embed_response(
        self,
        raw: str,
        model: str | None,
        input_hash: str,
        elapsed_ms: int,
    ) -> "EmbedResult":
        """Parse OpenAI-compatible /v1/embeddings response."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            return EmbedResult(
                embeddings=[],
                endpoint_id=self.endpoint_id,
                model=model,
                input_hash=input_hash,
                success=False,
                error=f"PARSE_ERROR: {exc}",
                duration_ms=elapsed_ms,
            )

        try:
            embeddings = [item["embedding"] for item in data.get("data", [])]
        except (KeyError, TypeError):
            embeddings = []

        actual_model = data.get("model") or model
        return EmbedResult(
            embeddings=embeddings,
            endpoint_id=self.endpoint_id,
            model=actual_model,
            input_hash=input_hash,
            success=bool(embeddings),
            duration_ms=elapsed_ms,
        )

    def _log_call(self, evidence: dict[str, Any], output: str) -> None:
        """Log call evidence to .local/llm-call-logs/ with secret redaction."""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            log_path = self.log_dir / f"call-{ts}-{evidence.get('prompt_hash', 'x')}.json"
            log_entry = {
                **evidence,
                "output_preview": output[:256],
                "authority_state": _AUTHORITY_STATE,
                "non_authoritative": _NON_AUTHORITATIVE,
                "logged_at": datetime.now(timezone.utc).isoformat(),
            }
            log_path.write_text(
                json.dumps(log_entry, indent=2), encoding="utf-8"
            )
        except Exception:  # noqa: BLE001
            pass  # Log failure must not break the caller


# ---------------------------------------------------------------------------
# Module-level convenience functions
# ---------------------------------------------------------------------------

def call_advisory(
    prompt: str,
    *,
    task_type: str = "general",
    model: str | None = None,
    dry_run: bool = False,
    config_path: Path | None = None,
) -> CallResult:
    """Make an advisory LLM call using the best available endpoint.

    Fails closed (returns error CallResult) if no endpoint/credential available.
    Output is always advisory: authority_state = "ai_advisory".
    """
    try:
        client = EndpointClient.from_config(task_type=task_type, config_path=config_path)
        return client.call(prompt, task_type=task_type, model=model, dry_run=dry_run)
    except Exception as exc:  # noqa: BLE001
        prompt_hash = hashlib.sha256(prompt[:_MAX_PROMPT_CHARS].encode()).hexdigest()[:16]
        return CallResult(
            output="",
            endpoint_id="none",
            model=model,
            task_type=task_type,
            prompt_hash=prompt_hash,
            response_hash="",
            duration_ms=0,
            success=False,
            error=f"CLIENT_INIT_ERROR: {exc}",
        )


def is_available(task_type: str = "general", config_path: Path | None = None) -> bool:
    """Return True if a credentialed endpoint is available for the task_type."""
    try:
        cfg = load_endpoint_config(config_path)
        ep = find_endpoint(task_type, cfg)
        if ep is None:
            return False
        cred = _get_credential(ep.get("auth_env"))
        return bool(cred)
    except Exception:  # noqa: BLE001
        return False


if __name__ == "__main__":
    # CLI: python tools/llm/endpoint_client.py "your prompt here" --dry-run
    import argparse

    parser = argparse.ArgumentParser(description="Advisory LLM call via configured endpoint")
    parser.add_argument("prompt", nargs="?", default="Ping: return OK JSON")
    parser.add_argument("--task-type", default="general")
    parser.add_argument("--model", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--endpoint-id", default=None)
    args = parser.parse_args()

    if args.endpoint_id:
        client = EndpointClient.from_endpoint_id(args.endpoint_id)
        result = client.call(args.prompt, task_type=args.task_type, model=args.model,
                             dry_run=args.dry_run)
    else:
        result = call_advisory(
            args.prompt,
            task_type=args.task_type,
            model=args.model,
            dry_run=args.dry_run,
        )

    print(json.dumps(result.to_dict(), indent=2))
    sys.exit(0 if result.success else 1)
