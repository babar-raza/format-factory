"""R169 — endpoint_client /v1/embeddings path tests (dry-run, advisory-only)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools" / "llm"))

from endpoint_client import EmbedResult, EndpointClient  # noqa: E402


class TestEmbedResult:
    def test_authority_state_always_advisory(self):
        r = EmbedResult(
            embeddings=[[0.1, 0.2]],
            endpoint_id="ep",
            model="m",
            input_hash="h",
            success=True,
        )
        assert r.authority_state == "ai_advisory"

    def test_non_authoritative_always_true(self):
        r = EmbedResult(
            embeddings=[],
            endpoint_id="ep",
            model=None,
            input_hash="h",
            success=False,
        )
        assert r.non_authoritative is True

    def test_to_dict_has_required_keys(self):
        r = EmbedResult(
            embeddings=[[0.1]], endpoint_id="e", model="m", input_hash="h", success=True
        )
        d = r.to_dict()
        assert "authority_state" in d
        assert "non_authoritative" in d
        assert "embeddings_count" in d
        assert "success" in d

    def test_embeddings_count_in_to_dict(self):
        r = EmbedResult(
            embeddings=[[0.1, 0.2], [0.3, 0.4]],
            endpoint_id="e",
            model="m",
            input_hash="h",
            success=True,
        )
        assert r.to_dict()["embeddings_count"] == 2

    def test_embedding_dim_in_to_dict(self):
        r = EmbedResult(
            embeddings=[[0.1, 0.2, 0.3]],
            endpoint_id="e",
            model="m",
            input_hash="h",
            success=True,
        )
        assert r.to_dict()["embedding_dim"] == 3

    def test_dry_run_field(self):
        r = EmbedResult(
            embeddings=[], endpoint_id="e", model="m", input_hash="h",
            success=True, dry_run=True,
        )
        assert r.dry_run is True
        assert r.to_dict()["dry_run"] is True

    def test_error_field(self):
        r = EmbedResult(
            embeddings=[], endpoint_id="e", model=None, input_hash="h",
            success=False, error="BLOCKED_NO_CREDENTIAL: X not set",
        )
        assert r.error.startswith("BLOCKED")
        assert r.success is False


class TestEndpointClientHasEmbed:
    def test_embed_method_exists(self):
        assert callable(getattr(EndpointClient, "embed", None))
