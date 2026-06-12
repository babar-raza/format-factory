"""Lane F tests — embedding and vector-store foundation.

Tests for namespace isolation, stale index detection, cross-namespace rejection,
embedding model fingerprint change, and missing model fail-closed.
"""

import pytest

from tools.ai.retrieval.namespace_manager import (
    CrossNamespaceError,
    IndexManifest,
    MissingEmbeddingModelError,
    NamespaceManager,
)


class TestNamespaceIsolation:
    def test_create_namespace(self, tmp_path):
        mgr = NamespaceManager(store_root=tmp_path)
        manifest = IndexManifest(
            format_id="fods",
            embedding_model_id="qwen3-embedding-8b",
            embedding_model_fingerprint="fp123",
            chunk_count=5,
            chunk_hashes=["h1", "h2", "h3", "h4", "h5"],
        )
        ns_path = mgr.create_namespace("fods", manifest)
        assert ns_path.exists()
        assert (ns_path / "manifest.json").exists()

    def test_per_format_isolation(self, tmp_path):
        mgr = NamespaceManager(store_root=tmp_path)
        m1 = IndexManifest(format_id="fods", embedding_model_id="m1", embedding_model_fingerprint="fp1")
        m2 = IndexManifest(format_id="fodt", embedding_model_id="m1", embedding_model_fingerprint="fp1")
        mgr.create_namespace("fods", m1)
        mgr.create_namespace("fodt", m2)
        assert mgr.namespace_exists("fods")
        assert mgr.namespace_exists("fodt")
        assert mgr.get_namespace_path("fods") != mgr.get_namespace_path("fodt")

    def test_cross_namespace_rejected(self, tmp_path):
        mgr = NamespaceManager(store_root=tmp_path)
        with pytest.raises(CrossNamespaceError):
            mgr.reject_cross_namespace_query("fods", "fodt")


class TestStaleIndexDetection:
    def test_stale_when_chunks_change(self, tmp_path):
        mgr = NamespaceManager(store_root=tmp_path)
        manifest = IndexManifest(
            format_id="fods",
            embedding_model_fingerprint="fp1",
            chunk_hashes=["h1", "h2"],
        )
        mgr.create_namespace("fods", manifest)
        is_stale, reason = mgr.detect_stale_index("fods", ["h1", "h3"], "fp1")
        assert is_stale is True
        assert reason == "chunk_hashes_changed"

    def test_stale_when_model_changes(self, tmp_path):
        mgr = NamespaceManager(store_root=tmp_path)
        manifest = IndexManifest(
            format_id="fods",
            embedding_model_fingerprint="fp1",
            chunk_hashes=["h1"],
        )
        mgr.create_namespace("fods", manifest)
        is_stale, reason = mgr.detect_stale_index("fods", ["h1"], "fp2")
        assert is_stale is True
        assert reason == "embedding_model_changed"

    def test_up_to_date(self, tmp_path):
        mgr = NamespaceManager(store_root=tmp_path)
        manifest = IndexManifest(
            format_id="fods",
            embedding_model_fingerprint="fp1",
            chunk_hashes=["h1", "h2"],
        )
        mgr.create_namespace("fods", manifest)
        is_stale, reason = mgr.detect_stale_index("fods", ["h1", "h2"], "fp1")
        assert is_stale is False
        assert reason == "up_to_date"


class TestMissingEmbeddingModel:
    def test_query_nonexistent_namespace(self, tmp_path):
        mgr = NamespaceManager(store_root=tmp_path)
        with pytest.raises(MissingEmbeddingModelError):
            mgr.query("nonexistent", "test query")


class TestManifestPersistence:
    def test_load_manifest(self, tmp_path):
        mgr = NamespaceManager(store_root=tmp_path)
        manifest = IndexManifest(
            format_id="fods",
            embedding_model_id="m1",
            embedding_model_fingerprint="fp1",
            chunk_hashes=["h1"],
        )
        mgr.create_namespace("fods", manifest)
        mgr2 = NamespaceManager(store_root=tmp_path)
        loaded = mgr2.load_manifest("fods")
        assert loaded is not None
        assert loaded.format_id == "fods"
        assert loaded.embedding_model_fingerprint == "fp1"
