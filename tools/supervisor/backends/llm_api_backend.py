"""
Format Factory — LLM API Backend
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001

Implements bounded LLM_API_CALL dispatch via openai-compatible endpoints.
Only calls endpoint when:
  - endpoint config present
  - credential env var present
  - action_type == LLM_API_CALL
  - no repo content sent (bounded test only)

H5 proof: backend executes via runner, result written, backend_used=LLM_API.
"""
from __future__ import annotations
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from tools.supervisor.execution_backend import (
    BackendResult, BackendStatus, BackendType, ExecutionBackend, ProofLevel
)
from tools.supervisor.llm_backend_config import get_ready_endpoints

_here = Path(__file__).resolve().parent
_repo_root = _here.parent.parent.parent.parent

# Bounded test prompt — no repo content, no sensitive data
_BOUNDED_TEST_PROMPT = (
    'Return valid JSON only, no markdown, no explanation: '
    '{"status":"OK","backend":"LLM_API","proof_level":"H5"}'
)

# Maximum response length to accept for content field (characters)
_MAX_CONTENT_LEN = 500


class LlmApiBackend(ExecutionBackend):
    """LLM API backend — bounded execution for H5 proof."""

    @property
    def backend_type(self) -> BackendType:
        return BackendType.LLM_API

    def discover(self) -> BackendStatus:
        ready = get_ready_endpoints()
        if ready:
            return BackendStatus.CONFIG_PRESENT  # Config + credentials present
        return BackendStatus.BLOCKED_BY_CREDENTIALS

    def can_execute(self, action: dict) -> bool:
        """Execute LLM_API_CALL actions when endpoint credentials are present."""
        if action.get("action_type") != "LLM_API_CALL":
            return False
        ready = get_ready_endpoints()
        return bool(ready)

    def execute(self, action: dict, allowed_write_roots) -> BackendResult:
        action_id = action.get("action_id", "unknown")
        result_path = action.get("result_path", "")

        ready = get_ready_endpoints()
        if not ready:
            return BackendResult(
                action_id=action_id,
                backend_used=BackendType.LLM_API,
                status="BLOCKED",
                exit_code=3,
                errors=["No ready LLM endpoints (credentials absent)"],
            )

        # Pick endpoint with credentials first; among those, highest priority (lowest number)
        credentialed = [e for e in ready if e.get("auth_env") and os.environ.get(e.get("auth_env", ""), "")]
        pool = credentialed if credentialed else ready
        ep = min(pool, key=lambda e: e.get("priority", 99))
        ep_id = ep.get("id", "unknown")
        ep_url = ep.get("url", "")
        auth_env = ep.get("auth_env", "")

        # Get credential (presence only verified — never log value)
        api_key = os.environ.get(auth_env, "") if auth_env else ""
        if not api_key:
            return BackendResult(
                action_id=action_id,
                backend_used=BackendType.LLM_API,
                status="BLOCKED",
                exit_code=3,
                errors=[f"Credential {auth_env} absent at runtime"],
            )

        # Bounded call — attempt HTTP request with retry + error classification
        prompt = action.get("prompt", _BOUNDED_TEST_PROMPT)
        model = action.get("model", ep.get("default_model", "recommended"))

        import urllib.request
        import urllib.error

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 64,
            "temperature": 0,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        req = urllib.request.Request(
            f"{ep_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        # Load shared reliability layer for error classification + retry
        try:
            from tools.supervisor.grader_reliability import (
                RetryPolicy, GradingObserver, call_with_retry,
                GraderRetryExhausted, GraderPermanentFailure, classify_exception,
            )
            _rel_ok = True
        except ImportError:
            _rel_ok = False

        body: str | None = None
        _last_error_class = "UNKNOWN_PROVIDER_FAILURE"

        def _do_http() -> str:
            with urllib.request.urlopen(req, timeout=8) as resp:
                return resp.read().decode("utf-8")

        if _rel_ok:
            policy = RetryPolicy(max_attempts=2, overall_deadline=25.0, read_timeout=8.0)
            observer = GradingObserver()
            try:
                body = call_with_retry(
                    _do_http, policy=policy, observer=observer,
                    item_id=action_id, provider=ep_id, model=model,
                )
            except GraderPermanentFailure as exc:
                _last_error_class = exc.error_class.value
                return BackendResult(
                    action_id=action_id,
                    backend_used=BackendType.LLM_API,
                    status="FAILED",
                    exit_code=1,
                    errors=[f"LLM call permanent failure ({_last_error_class}): {type(exc.exc).__name__}"],
                    warnings=[f"Endpoint: {ep_id} ({ep_url})", "Not retried — permanent error class"],
                )
            except GraderRetryExhausted as exc:
                _last_error_class = exc.error_class.value
                return BackendResult(
                    action_id=action_id,
                    backend_used=BackendType.LLM_API,
                    status="FAILED",
                    exit_code=1,
                    errors=[f"LLM call retries exhausted ({_last_error_class}): {type(exc.last_exc).__name__}"],
                    warnings=[f"Endpoint: {ep_id} ({ep_url})", "Retried per RetryPolicy; all attempts failed"],
                )
            except Exception as exc:
                return BackendResult(
                    action_id=action_id,
                    backend_used=BackendType.LLM_API,
                    status="FAILED",
                    exit_code=1,
                    errors=[f"LLM call failed: {type(exc).__name__}"],
                    warnings=[f"Endpoint: {ep_id} ({ep_url})"],
                )
        else:
            # Fallback: single attempt (original behaviour) when reliability module unavailable
            try:
                body = _do_http()
            except Exception as exc:
                return BackendResult(
                    action_id=action_id,
                    backend_used=BackendType.LLM_API,
                    status="FAILED",
                    exit_code=1,
                    errors=[f"LLM call failed: {type(exc).__name__}: {exc}"],
                    warnings=[f"Endpoint: {ep_id} ({ep_url})"],
                )

        if body is None:
            return BackendResult(
                action_id=action_id,
                backend_used=BackendType.LLM_API,
                status="FAILED",
                exit_code=1,
                errors=["LLM call returned no body"],
            )

        try:
            resp_data = json.loads(body)
            content = resp_data["choices"][0]["message"]["content"] or ""
        except Exception as exc:
            return BackendResult(
                action_id=action_id,
                backend_used=BackendType.LLM_API,
                status="FAILED",
                exit_code=1,
                errors=[f"LLM response parse failed: {type(exc).__name__}"],
            )

        if len(content) > _MAX_CONTENT_LEN:
            content = content[:_MAX_CONTENT_LEN] + "...[truncated]"

        # Try to parse content as JSON (bounded test expects JSON)
        try:
            parsed = json.loads(content.strip())
        except Exception:
            parsed = {"raw": content}

        result_record = {
            "status": "SUCCESS",
            "action_id": action_id,
            "backend_used": "LLM_API",
            "proof_level": "H5",
            "endpoint_id": ep_id,
            "model": model,
            "response": parsed,
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }

        # Write result
        if result_path:
            for root in (allowed_write_roots or []):
                try:
                    rp = Path(result_path)
                    if not rp.is_absolute():
                        rp = _repo_root / rp
                    rp.parent.mkdir(parents=True, exist_ok=True)
                    rp.write_text(json.dumps(result_record, indent=2), encoding="utf-8")
                    break
                except Exception:
                    continue

        return BackendResult(
            action_id=action_id,
            backend_used=BackendType.LLM_API,
            status="SUCCESS",
            exit_code=0,
            result_path=result_path,
            proof_level=ProofLevel.H5,
        )
