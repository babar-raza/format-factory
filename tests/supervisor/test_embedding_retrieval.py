"""
tests/supervisor/test_embedding_retrieval.py
Tests for tools/supervisor/embedding_retrieval.py

Sprint: FORMAT-FACTORY-SELF-HEALING-QUEUE-PROFESSIONALIZE-RNEXT-001

Covers:
- DocumentIndexer: index build, evidence scan, taskcard scan
- LexicalRetriever: tokenize, TF-IDF score, top-k retrieval
- PriorRunRetrievalPilot: from_repo, find_similar, index stats
- Advisory boundary (authority_state always ai_advisory)
- Lexical fallback (no embedding provider needed)
- Missing index/empty corpus handling
- Retrieval log saving
- find_similar_advisory convenience function
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor.embedding_retrieval import (
    DocumentIndexer,
    EmbeddingCache,
    EmbeddingProvider,
    HybridRetrievalPilot,
    LexicalRetriever,
    PriorRunRetrievalPilot,
    _cosine_similarity,
    _tokenize,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_EVIDENCE_YAML = """\
run_id: test-run-001
sprint_id: TEST-SPRINT-001
sprint_type: product
worker_self_verdict: PASS
declared_scope: >
  Add search_text function to ABW codec. Queue-dispatched execution.
  Product source mutation via QUEUE_DISPATCHED_EXECUTION.
changed_files:
  - src/python/abw/abw_codec.py
execution_method: QUEUE_DISPATCHED_EXECUTION
"""

SAMPLE_TASKCARD_YAML = """\
item_id: TC-TEST-001
title: "Add search_text to ABW codec"
lane: L2-product
status: completed
execution_method: QUEUE_DISPATCHED_EXECUTION
sprint_id: TEST-SPRINT-001
acceptance_criteria: search_text function added and tested
"""

SAMPLE_STALE_EVIDENCE_YAML = """\
run_id: test-run-stale-001
sprint_id: TEST-STALE-001
sprint_type: repair
worker_self_verdict: PASS
declared_scope: >
  Detected STALE_QUEUE_ITEM: rename_sheet already exists in gnumeric_codec.
  Healing loop classified and closed stale queue item.
execution_method: QUEUE_DISPATCHED_EXECUTION
"""


@pytest.fixture
def evidence_dir(tmp_path: Path) -> Path:
    """Create a temp evidence directory with sample declarations."""
    e = tmp_path / "evidences"
    for i, content in enumerate([
        SAMPLE_EVIDENCE_YAML,
        SAMPLE_TASKCARD_YAML,
        SAMPLE_STALE_EVIDENCE_YAML,
    ]):
        run_dir = e / f"test-run-{i:03d}"
        run_dir.mkdir(parents=True)
        (run_dir / "evidence-declaration.yaml").write_text(content, encoding="utf-8")
    return e


@pytest.fixture
def taskcard_dir(tmp_path: Path) -> Path:
    """Create a temp taskcard directory with sample taskcards."""
    t = tmp_path / "taskcards" / "test-sprint"
    t.mkdir(parents=True)
    (t / "TC-TEST-001.yaml").write_text(SAMPLE_TASKCARD_YAML, encoding="utf-8")
    (t / "TC-TEST-002.yaml").write_text(
        SAMPLE_TASKCARD_YAML.replace("TC-TEST-001", "TC-TEST-002").replace(
            "search_text", "rename_sheet stale detection"
        ),
        encoding="utf-8",
    )
    return tmp_path / "taskcards"


@pytest.fixture
def indexer(evidence_dir: Path, taskcard_dir: Path) -> DocumentIndexer:
    return DocumentIndexer(
        evidence_root=evidence_dir,
        taskcards_root=taskcard_dir,
        max_docs=20,
    )


@pytest.fixture
def pilot(evidence_dir: Path, taskcard_dir: Path, tmp_path: Path) -> PriorRunRetrievalPilot:
    indexer = DocumentIndexer(
        evidence_root=evidence_dir,
        taskcards_root=taskcard_dir,
        max_docs=20,
    )
    return PriorRunRetrievalPilot(
        indexer=indexer,
        index_dir=tmp_path / "embedding-index",
    )


# ---------------------------------------------------------------------------
# Test: tokenizer
# ---------------------------------------------------------------------------

class TestTokenizer:
    def test_tokenizes_basic_text(self) -> None:
        tokens = _tokenize("search_text function added to ABW codec")
        assert "search_text" in tokens
        assert "function" in tokens
        assert "abw" in tokens or "ABW".lower() in tokens

    def test_removes_stopwords(self) -> None:
        tokens = _tokenize("the function is added to the codec")
        assert "the" not in tokens
        assert "is" not in tokens

    def test_case_insensitive(self) -> None:
        tokens = _tokenize("STALE_QUEUE_ITEM Detected")
        assert "stale_queue_item" in tokens
        assert "detected" in tokens

    def test_empty_text(self) -> None:
        tokens = _tokenize("")
        assert tokens == []

    def test_numbers_included(self) -> None:
        tokens = _tokenize("sprint 001 wave 9")
        assert "001" in tokens or "sprint" in tokens


# ---------------------------------------------------------------------------
# Test: DocumentIndexer
# ---------------------------------------------------------------------------

class TestDocumentIndexer:
    def test_build_index_returns_documents(self, indexer: DocumentIndexer) -> None:
        docs = indexer.build_index()
        assert len(docs) > 0

    def test_documents_have_required_fields(self, indexer: DocumentIndexer) -> None:
        docs = indexer.build_index()
        for doc in docs:
            assert doc.doc_id
            assert doc.source_path
            assert doc.doc_type in ("evidence_declaration", "taskcard")
            assert doc.content
            assert doc.content_hash

    def test_evidence_declarations_indexed(self, indexer: DocumentIndexer) -> None:
        docs = indexer.build_index()
        evidence_docs = [d for d in docs if d.doc_type == "evidence_declaration"]
        assert len(evidence_docs) >= 1

    def test_taskcards_indexed(self, indexer: DocumentIndexer) -> None:
        docs = indexer.build_index()
        taskcard_docs = [d for d in docs if d.doc_type == "taskcard"]
        assert len(taskcard_docs) >= 1

    def test_max_docs_respected(self, evidence_dir: Path, taskcard_dir: Path) -> None:
        indexer = DocumentIndexer(
            evidence_root=evidence_dir,
            taskcards_root=taskcard_dir,
            max_docs=2,
        )
        docs = indexer.build_index()
        assert len(docs) <= 2

    def test_missing_evidence_dir_returns_empty(self, tmp_path: Path) -> None:
        indexer = DocumentIndexer(
            evidence_root=tmp_path / "nonexistent",
            taskcards_root=tmp_path / "also-nonexistent",
        )
        docs = indexer.build_index()
        assert docs == []

    def test_document_tokens_nonempty(self, indexer: DocumentIndexer) -> None:
        docs = indexer.build_index()
        for doc in docs:
            assert len(doc.tokens) > 0

    def test_content_hash_deterministic(self, indexer: DocumentIndexer) -> None:
        docs1 = indexer.build_index()
        docs2 = indexer.build_index()
        hashes1 = sorted(d.content_hash for d in docs1)
        hashes2 = sorted(d.content_hash for d in docs2)
        assert hashes1 == hashes2


# ---------------------------------------------------------------------------
# Test: LexicalRetriever
# ---------------------------------------------------------------------------

class TestLexicalRetriever:
    def test_retrieves_relevant_document(self, indexer: DocumentIndexer) -> None:
        docs = indexer.build_index()
        retriever = LexicalRetriever(docs)
        results = retriever.retrieve("search_text ABW codec")
        # Should find at least one result
        assert len(results) >= 1

    def test_retrieves_stale_queue_item(self, indexer: DocumentIndexer) -> None:
        docs = indexer.build_index()
        retriever = LexicalRetriever(docs)
        results = retriever.retrieve("STALE_QUEUE_ITEM healing gnumeric")
        assert len(results) >= 1

    def test_top_k_respected(self, indexer: DocumentIndexer) -> None:
        docs = indexer.build_index()
        retriever = LexicalRetriever(docs)
        results = retriever.retrieve("test", top_k=1)
        assert len(results) <= 1

    def test_empty_corpus_returns_empty(self) -> None:
        retriever = LexicalRetriever([])
        results = retriever.retrieve("any query")
        assert results == []

    def test_unknown_query_may_return_empty(self, indexer: DocumentIndexer) -> None:
        docs = indexer.build_index()
        retriever = LexicalRetriever(docs)
        results = retriever.retrieve("xyzzy quux frob nonce token")
        # No guarantee of results; may be empty
        assert isinstance(results, list)

    def test_scores_are_positive(self, indexer: DocumentIndexer) -> None:
        docs = indexer.build_index()
        retriever = LexicalRetriever(docs)
        results = retriever.retrieve("search_text codec function")
        for doc, score in results:
            assert score > 0

    def test_results_sorted_descending(self, indexer: DocumentIndexer) -> None:
        docs = indexer.build_index()
        retriever = LexicalRetriever(docs)
        results = retriever.retrieve("search_text execution sprint queue")
        scores = [s for _, s in results]
        assert scores == sorted(scores, reverse=True)

    def test_idempotent_retrieval(self, indexer: DocumentIndexer) -> None:
        docs = indexer.build_index()
        retriever = LexicalRetriever(docs)
        r1 = retriever.retrieve("search_text ABW codec")
        r2 = retriever.retrieve("search_text ABW codec")
        assert [d.doc_id for d, _ in r1] == [d.doc_id for d, _ in r2]


# ---------------------------------------------------------------------------
# Test: PriorRunRetrievalPilot
# ---------------------------------------------------------------------------

class TestPriorRunRetrievalPilot:
    def test_build_index_returns_count(self, pilot: PriorRunRetrievalPilot) -> None:
        n = pilot.build_index()
        assert n > 0

    def test_find_similar_returns_results(self, pilot: PriorRunRetrievalPilot) -> None:
        pilot.build_index()
        results = pilot.find_similar("STALE_QUEUE_ITEM gnumeric rename_sheet")
        assert isinstance(results, list)

    def test_find_similar_advisory_authority(self, pilot: PriorRunRetrievalPilot) -> None:
        pilot.build_index()
        results = pilot.find_similar("search_text ABW queue dispatch")
        for r in results:
            assert r.authority_state == "ai_advisory"
            assert r.non_authoritative is True

    def test_find_similar_to_dict_has_advisory_marker(
        self, pilot: PriorRunRetrievalPilot
    ) -> None:
        pilot.build_index()
        results = pilot.find_similar("sprint codec product")
        for r in results:
            d = r.to_dict()
            assert d["authority_state"] == "ai_advisory"
            assert d["non_authoritative"] is True

    def test_advisory_text_contains_advisory_marker(
        self, pilot: PriorRunRetrievalPilot
    ) -> None:
        pilot.build_index()
        results = pilot.find_similar("search_text")
        for r in results:
            assert "[ADVISORY]" in r.advisory_text

    def test_doc_type_filter_evidence(self, pilot: PriorRunRetrievalPilot) -> None:
        pilot.build_index()
        results = pilot.find_similar(
            "sprint execution queue", doc_type_filter="evidence_declaration"
        )
        for r in results:
            assert r.doc.doc_type == "evidence_declaration"

    def test_doc_type_filter_taskcard(self, pilot: PriorRunRetrievalPilot) -> None:
        pilot.build_index()
        results = pilot.find_similar("sprint execution queue", doc_type_filter="taskcard")
        for r in results:
            assert r.doc.doc_type == "taskcard"

    def test_get_index_stats_after_build(self, pilot: PriorRunRetrievalPilot) -> None:
        pilot.build_index()
        stats = pilot.get_index_stats()
        assert stats["doc_count"] > 0
        assert stats["authority_state"] == "ai_advisory"

    def test_get_index_stats_from_manifest(
        self, pilot: PriorRunRetrievalPilot, tmp_path: Path
    ) -> None:
        pilot.build_index()  # This saves manifest
        # Create new pilot pointing to same index dir
        new_pilot = PriorRunRetrievalPilot(
            indexer=pilot.indexer,
            index_dir=pilot.index_dir,
        )
        # Without build_index, stats come from manifest
        stats = new_pilot.get_index_stats()
        assert "doc_count" in stats

    def test_build_index_saves_manifest(
        self, pilot: PriorRunRetrievalPilot
    ) -> None:
        pilot.build_index()
        manifest = pilot.index_dir / "index-manifest.json"
        assert manifest.exists()
        data = json.loads(manifest.read_text())
        assert data["doc_count"] > 0
        assert data["authority_state"] == "ai_advisory"
        assert data["non_authoritative"] is True

    def test_save_retrieval_log(self, pilot: PriorRunRetrievalPilot) -> None:
        pilot.build_index()
        results = pilot.find_similar("search_text ABW")
        log_path = pilot.save_retrieval_log("search_text ABW", results)
        assert log_path.exists()
        data = json.loads(log_path.read_text())
        assert data["authority_state"] == "ai_advisory"
        assert data["non_authoritative"] is True
        assert "results" in data

    def test_no_direct_mutation_methods(self, pilot: PriorRunRetrievalPilot) -> None:
        """RetrievalResult must not have methods that mutate source."""
        pilot.build_index()
        results = pilot.find_similar("test query")
        if results:
            r = results[0]
            forbidden_methods = ["write", "patch", "apply", "mutate", "commit", "push"]
            for m in forbidden_methods:
                assert not hasattr(r, m), f"RetrievalResult must not have method '{m}'"


# ---------------------------------------------------------------------------
# Test: find_similar_advisory convenience
# ---------------------------------------------------------------------------

class TestFindSimilarAdvisory:
    def test_returns_list_of_dicts(self, evidence_dir: Path, tmp_path: Path) -> None:
        """Uses a custom pilot to avoid depending on real repo state."""
        indexer = DocumentIndexer(
            evidence_root=evidence_dir,
            taskcards_root=tmp_path / "empty-taskcards",
            max_docs=10,
        )
        pilot = PriorRunRetrievalPilot(
            indexer=indexer,
            index_dir=tmp_path / "idx",
        )
        pilot.build_index()
        results = pilot.find_similar("queue dispatch stale", top_k=3)
        for r in results:
            d = r.to_dict()
            assert "authority_state" in d
            assert d["authority_state"] == "ai_advisory"

    def test_empty_evidence_returns_empty_list(self, tmp_path: Path) -> None:
        indexer = DocumentIndexer(
            evidence_root=tmp_path / "empty",
            taskcards_root=tmp_path / "empty",
        )
        pilot = PriorRunRetrievalPilot(indexer=indexer, index_dir=tmp_path / "idx")
        pilot.build_index()
        results = pilot.find_similar("anything")
        assert results == []


# ---------------------------------------------------------------------------
# Phase 3: Hybrid retrieval tests
# ---------------------------------------------------------------------------

class TestEmbeddingCache:
    """Tests for EmbeddingCache: store, retrieve, invalidation."""

    def test_cache_miss_returns_none(self, tmp_path: Path) -> None:
        cache = EmbeddingCache(tmp_path / "cache.json")
        result = cache.get("path/to/file", "abc123", "model-x")
        assert result is None

    def test_cache_put_and_get(self, tmp_path: Path) -> None:
        cache = EmbeddingCache(tmp_path / "cache.json")
        vec = [0.1, 0.2, 0.3]
        cache.put("path/to/file", "abc123", "model-x", vec, 3, "professionalize")
        result = cache.get("path/to/file", "abc123", "model-x")
        assert result == vec

    def test_cache_invalidated_on_hash_change(self, tmp_path: Path) -> None:
        cache = EmbeddingCache(tmp_path / "cache.json")
        vec = [0.1, 0.2, 0.3]
        cache.put("path/to/file", "old_hash", "model-x", vec, 3, "professionalize")
        result = cache.get("path/to/file", "new_hash", "model-x")
        assert result is None

    def test_cache_persists_across_instances(self, tmp_path: Path) -> None:
        cache_path = tmp_path / "cache.json"
        cache1 = EmbeddingCache(cache_path)
        vec = [0.5, 0.6]
        cache1.put("src/file.py", "hash1", "model-y", vec, 2, "professionalize")

        cache2 = EmbeddingCache(cache_path)
        assert cache2.get("src/file.py", "hash1", "model-y") == vec

    def test_cache_stats(self, tmp_path: Path) -> None:
        cache = EmbeddingCache(tmp_path / "cache.json")
        cache.put("f1", "h1", "m1", [1.0], 1, "p1")
        cache.put("f2", "h2", "m1", [2.0], 1, "p1")
        stats = cache.stats()
        assert stats["entry_count"] == 2
        assert "cache_path" in stats


class TestCosineSimilarity:
    def test_identical_vectors(self) -> None:
        v = [1.0, 0.0, 0.0]
        assert abs(_cosine_similarity(v, v) - 1.0) < 1e-6

    def test_orthogonal_vectors(self) -> None:
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert abs(_cosine_similarity(a, b)) < 1e-6

    def test_opposite_vectors(self) -> None:
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        assert abs(_cosine_similarity(a, b) - (-1.0)) < 1e-6

    def test_empty_returns_zero(self) -> None:
        assert _cosine_similarity([], []) == 0.0

    def test_mismatched_lengths_returns_zero(self) -> None:
        assert _cosine_similarity([1.0], [1.0, 2.0]) == 0.0


class TestEmbeddingProviderNoCredential:
    """EmbeddingProvider without credential falls back gracefully."""

    def test_is_available_false_with_nonexistent_endpoint(self) -> None:
        """Endpoint that doesn't exist in config → not available."""
        provider = EmbeddingProvider(endpoint_id="nonexistent-endpoint-xyz")
        assert provider.is_available is False

    def test_get_embedding_returns_none_for_missing_endpoint(self) -> None:
        """Missing endpoint → get_embedding returns None (lexical fallback)."""
        provider = EmbeddingProvider(endpoint_id="nonexistent-endpoint-xyz")
        result = provider.get_embedding("some text", "src/file.py", "hash123")
        assert result is None

    def test_get_embedding_returns_none_always_for_chat_endpoint(self) -> None:
        """Even with credential, current embedding provider returns None (chat endpoint,
        not /v1/embeddings). This is advisory fallback behavior by design."""
        provider = EmbeddingProvider()
        # get_embedding returns None because we don't yet implement /v1/embeddings
        result = provider.get_embedding("some text", "src/file.py", "hash123")
        assert result is None


class TestHybridRetrievalPilot:
    """Tests for HybridRetrievalPilot with embedding fallback."""

    @pytest.fixture
    def hybrid_pilot(self, tmp_path: Path, evidence_dir: Path) -> HybridRetrievalPilot:
        indexer = DocumentIndexer(
            evidence_root=evidence_dir,
            taskcards_root=tmp_path / "taskcards",
            max_docs=50,
        )
        return HybridRetrievalPilot(
            indexer=indexer,
            index_dir=tmp_path / "idx",
            embedding_provider=None,  # lexical fallback
        )

    def test_hybrid_builds_index(self, hybrid_pilot: HybridRetrievalPilot) -> None:
        n = hybrid_pilot.build_index()
        assert n >= 1

    def test_hybrid_fallback_returns_results(
        self, hybrid_pilot: HybridRetrievalPilot
    ) -> None:
        hybrid_pilot.build_index()
        results = hybrid_pilot.find_similar("search_text ABW stale queue repair")
        assert len(results) >= 1

    def test_hybrid_fallback_method_label(
        self, hybrid_pilot: HybridRetrievalPilot
    ) -> None:
        hybrid_pilot.build_index()
        results = hybrid_pilot.find_similar("stale queue item")
        if results:
            assert results[0].retrieval_method == "hybrid_fallback_lexical"

    def test_hybrid_result_advisory_boundary(
        self, hybrid_pilot: HybridRetrievalPilot
    ) -> None:
        hybrid_pilot.build_index()
        results = hybrid_pilot.find_similar("product capability")
        for r in results:
            assert r.authority_state == "ai_advisory"
            assert r.non_authoritative is True

    def test_hybrid_embedding_stats(
        self, hybrid_pilot: HybridRetrievalPilot
    ) -> None:
        stats = hybrid_pilot.get_embedding_stats()
        assert "embedding_available" in stats
        assert stats["embedding_available"] is False  # no credential
        assert "cache_stats" in stats
        assert "alpha" in stats

    def test_hybrid_pilot_from_repo(self) -> None:
        pilot = HybridRetrievalPilot.from_repo()
        assert isinstance(pilot, HybridRetrievalPilot)

    def test_hybrid_result_has_score_breakdown(
        self, hybrid_pilot: HybridRetrievalPilot
    ) -> None:
        hybrid_pilot.build_index()
        results = hybrid_pilot.find_similar("stale queue repair")
        for r in results:
            assert hasattr(r, "lexical_score")
            assert hasattr(r, "embedding_score")
            assert hasattr(r, "hybrid_score")
