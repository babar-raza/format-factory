"""Lane E tests — spec normalization adapter.

Tests for chunk loading, provenance validation, stale hash detection,
and fail-closed behavior when no normalized artifacts exist.
"""

import json
import pytest
from pathlib import Path

from tools.ai.normalization.adapter import (
    NormalizedChunk,
    NormalizationNotAvailable,
    discover_normalized_artifacts,
    load_chunks_from_jsonl,
    load_normalized_chunks,
    validate_chunk_freshness,
)


def _make_chunk(**kwargs) -> NormalizedChunk:
    defaults = {
        "format_id": "fods",
        "source_path": "specs/fods/spec.md",
        "source_hash": "abc123",
        "extraction_method": "markdown_split",
        "normalization_version": "1.0",
        "content": "test content",
    }
    defaults.update(kwargs)
    chunk = NormalizedChunk(**defaults)
    chunk.compute_hash()
    return chunk


class TestChunkProvenance:
    def test_valid_provenance(self):
        chunk = _make_chunk()
        errors = chunk.validate_provenance()
        assert errors == []

    def test_missing_format_id(self):
        chunk = _make_chunk(format_id="")
        errors = chunk.validate_provenance()
        assert "missing format_id" in errors

    def test_missing_source_hash(self):
        chunk = _make_chunk(source_hash="")
        errors = chunk.validate_provenance()
        assert "missing source_hash" in errors

    def test_missing_extraction_method(self):
        chunk = _make_chunk(extraction_method="")
        errors = chunk.validate_provenance()
        assert "missing extraction_method" in errors


class TestChunkLoading:
    def test_load_from_jsonl(self, tmp_path):
        jsonl = tmp_path / "chunks.jsonl"
        chunk_data = {
            "format_id": "fods",
            "source_path": "specs/fods/spec.md",
            "source_hash": "abc123",
            "extraction_method": "markdown_split",
            "normalization_version": "1.0",
            "chunk_hash": "def456",
            "content": "test content",
        }
        jsonl.write_text(json.dumps(chunk_data) + "\n")
        chunks = load_chunks_from_jsonl(jsonl)
        assert len(chunks) == 1
        assert chunks[0].format_id == "fods"

    def test_empty_jsonl(self, tmp_path):
        jsonl = tmp_path / "empty.jsonl"
        jsonl.write_text("")
        chunks = load_chunks_from_jsonl(jsonl)
        assert chunks == []


class TestFailClosed:
    def test_no_artifacts_raises(self, tmp_path):
        with pytest.raises(NormalizationNotAvailable):
            load_normalized_chunks("nonexistent_format", tmp_path)

    def test_discover_empty_dir(self, tmp_path):
        artifacts = discover_normalized_artifacts("fods", tmp_path)
        assert artifacts == []


class TestStaleness:
    def test_fresh_chunk(self):
        chunk = _make_chunk(source_hash="abc123")
        assert validate_chunk_freshness(chunk, "abc123") is True

    def test_stale_chunk(self):
        chunk = _make_chunk(source_hash="abc123")
        assert validate_chunk_freshness(chunk, "xyz789") is False
