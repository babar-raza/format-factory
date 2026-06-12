"""Model discovery — enumerate available models at endpoint.

Uses httpx for /v1/models listing since LiteLLM doesn't natively support
model enumeration for custom OpenAI-compatible endpoints.
"""

from __future__ import annotations

import hashlib

import httpx

from tools.ai.control_plane.config import AIConfig, get_api_key
from tools.ai.schemas.models import AIRole, ModelCapability, ModelFingerprint


def guess_model_family(model_id: str) -> str:
    """Infer model family from model ID string. No hardcoded model names."""
    mid = model_id.lower()
    if "gpt" in mid:
        return "gpt"
    if "qwen" in mid:
        return "qwen"
    if "embed" in mid:
        return "embedding"
    if "llama" in mid:
        return "llama"
    if "mistral" in mid:
        return "mistral"
    return "unknown"


def infer_role_candidates(model_id: str) -> list[AIRole]:
    """Suggest role candidates based on model family. Not authoritative."""
    family = guess_model_family(model_id)
    if family == "gpt":
        return [AIRole.structured_extraction, AIRole.evidence_review, AIRole.summarization]
    if family == "qwen":
        return [AIRole.agentic_low_risk]
    if family == "embedding":
        return [AIRole.embedding_retrieval]
    return [AIRole.summarization]


def discover_models(config: AIConfig) -> list[ModelCapability]:
    """Discover available models at the configured endpoint.

    Returns a list of ModelCapability objects.
    Returns empty list if endpoint is unavailable or unconfigured.
    Never logs or returns the API key.
    """
    if not config.is_configured:
        return []

    api_key = get_api_key()
    if not api_key:
        return []

    url = config.endpoint.rstrip("/") + "/models"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return []

    models: list[ModelCapability] = []
    raw_models = data.get("data", [])
    if not isinstance(raw_models, list):
        return []

    for item in raw_models:
        model_id = item.get("id", "")
        if not model_id:
            continue
        mc = ModelCapability(
            model_id=model_id,
            provider=config.provider_name,
            supports_chat=True,
            supports_embedding="embed" in model_id.lower(),
            context_length=item.get("context_length"),
            model_family_guess=guess_model_family(model_id),
            role_candidates=infer_role_candidates(model_id),
            endpoint_identity_hash=hashlib.sha256(
                config.endpoint_identity.encode()
            ).hexdigest()[:12],
        )
        models.append(mc)

    return models


def fingerprint_models(models: list[ModelCapability]) -> list[ModelFingerprint]:
    """Create fingerprints for discovered models."""
    fps: list[ModelFingerprint] = []
    for m in models:
        fp = ModelFingerprint(model_id=m.model_id, provider=m.provider)
        fp.compute_hash()
        fps.append(fp)
    return fps
