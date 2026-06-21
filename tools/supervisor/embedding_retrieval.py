"""
tools/supervisor/embedding_retrieval.py — Minimal Embedding/Prior-Run Retrieval Pilot
Sprint: FORMAT-FACTORY-SELF-HEALING-QUEUE-PROFESSIONALIZE-RNEXT-001

Provides a minimal, governed, advisory-only retrieval system over prior
evidence declarations, taskcards, and defect records.

Design constraints:
  - Output is ALWAYS advisory (authority_state = "ai_advisory")
  - Retrieval results must NEVER directly drive source mutations
  - Lexical fallback available when embedding provider is unavailable
  - Index stored locally under .local/embedding-index/ (read/write)
  - No external dependencies beyond stdlib

Architecture:
  1. DocumentIndexer — builds an index from evidence/taskcard YAML files
  2. LexicalRetriever — scores documents by keyword frequency (fallback, always available)
  3. EmbeddingRetriever — uses endpoint_client to get embeddings (optional, advisory)
  4. PriorRunRetrievalPilot — main entry point combining indexer + retrieval

Proof level: H3 (lexical fallback) / H5 (embedding via LLM endpoint, if available)

Usage (healing loop):
    pilot = PriorRunRetrievalPilot.from_repo(repo_root)
    results = pilot.find_similar("STALE_QUEUE_ITEM defect in gnumeric rename_sheet")
    # results[0].advisory_text = "Similar issue seen in sprint X..."
    # results are advisory only — no direct action authority
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

_here = Path(__file__).resolve().parent
_REPO_ROOT = _here.parent.parent
_INDEX_DIR = _REPO_ROOT / ".local" / "embedding-index"
_EVIDENCE_ROOT = _REPO_ROOT / ".local" / "evidences"
_TASKCARDS_ROOT = _REPO_ROOT / "taskcards"

# Advisory constant
_AUTHORITY_STATE = "ai_advisory"
_NON_AUTHORITATIVE = True

# Index limits for pilot
_MAX_INDEX_DOCS = 50
_MAX_RETRIEVAL_RESULTS = 5
_MIN_SCORE = 0.01


# ---------------------------------------------------------------------------
# Document record
# ---------------------------------------------------------------------------

class IndexedDocument:
    """A document indexed for retrieval."""

    def __init__(
        self,
        doc_id: str,
        source_path: str,
        doc_type: str,
        content: str,
        content_hash: str,
        metadata: dict[str, Any],
        tokens: list[str] | None = None,
    ) -> None:
        self.doc_id = doc_id
        self.source_path = source_path
        self.doc_type = doc_type  # evidence_declaration | taskcard | defect_log
        self.content = content
        self.content_hash = content_hash
        self.metadata = metadata
        self.tokens = tokens or _tokenize(content)
        self.indexed_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "source_path": self.source_path,
            "doc_type": self.doc_type,
            "content_hash": self.content_hash,
            "metadata": self.metadata,
            "token_count": len(self.tokens),
            "indexed_at": self.indexed_at,
        }


# ---------------------------------------------------------------------------
# Retrieval result
# ---------------------------------------------------------------------------

class RetrievalResult:
    """Advisory retrieval result. Always non-authoritative."""

    def __init__(
        self,
        doc: IndexedDocument,
        score: float,
        retrieval_method: str,
        query_hash: str,
    ) -> None:
        self.doc = doc
        self.score = score
        self.retrieval_method = retrieval_method  # lexical | embedding
        self.query_hash = query_hash
        self.authority_state = _AUTHORITY_STATE
        self.non_authoritative = _NON_AUTHORITATIVE

    @property
    def advisory_text(self) -> str:
        """Human-readable advisory snippet."""
        snippet = self.doc.content[:512].replace("\n", " ").strip()
        return (
            f"[ADVISORY] Similar {self.doc.doc_type} found at {self.doc.source_path} "
            f"(score={self.score:.3f}, method={self.retrieval_method}): {snippet}..."
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc.doc_id,
            "source_path": self.doc.source_path,
            "doc_type": self.doc.doc_type,
            "score": self.score,
            "retrieval_method": self.retrieval_method,
            "query_hash": self.query_hash,
            "authority_state": self.authority_state,
            "non_authoritative": self.non_authoritative,
            "advisory_text": self.advisory_text,
            "metadata": self.doc.metadata,
        }


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    """Simple tokenizer: lowercase, split on non-alphanumeric, remove stopwords."""
    _STOPWORDS = frozenset({
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "have", "has", "had", "do", "does", "did", "will", "would",
        "shall", "should", "may", "might", "must", "can", "could",
        "and", "or", "but", "if", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "up", "about", "into", "through",
        "not", "this", "that", "it", "its", "we", "our", "you", "they",
        "their", "i", "my", "me", "he", "she", "his", "her", "as", "so",
    })
    tokens = re.findall(r"[a-z0-9_]+", text.lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


# ---------------------------------------------------------------------------
# TF-IDF lexical retriever
# ---------------------------------------------------------------------------

class LexicalRetriever:
    """TF-IDF retriever over a list of IndexedDocument objects.

    Always available (no external dependencies).
    """

    def __init__(self, documents: list[IndexedDocument]) -> None:
        self.documents = documents
        self._idf: dict[str, float] = self._compute_idf()

    def _compute_idf(self) -> dict[str, float]:
        """Compute inverse document frequency for all terms."""
        n = len(self.documents)
        if n == 0:
            return {}
        df: Counter[str] = Counter()
        for doc in self.documents:
            for term in set(doc.tokens):
                df[term] += 1
        return {
            term: math.log((n + 1) / (count + 1)) + 1.0
            for term, count in df.items()
        }

    def retrieve(
        self,
        query: str,
        top_k: int = _MAX_RETRIEVAL_RESULTS,
    ) -> list[tuple[IndexedDocument, float]]:
        """Return top-k documents by TF-IDF score."""
        query_tokens = _tokenize(query)
        if not query_tokens or not self.documents:
            return []

        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
        scores: list[tuple[IndexedDocument, float]] = []

        for doc in self.documents:
            tf_counts = Counter(doc.tokens)
            n_tokens = len(doc.tokens) or 1
            score = 0.0
            for qt in query_tokens:
                tf = tf_counts.get(qt, 0) / n_tokens
                idf = self._idf.get(qt, 0.0)
                score += tf * idf
            if score > _MIN_SCORE:
                scores.append((doc, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


# ---------------------------------------------------------------------------
# Document indexer
# ---------------------------------------------------------------------------

class DocumentIndexer:
    """Scans evidence and taskcard files and builds IndexedDocument list."""

    def __init__(
        self,
        evidence_root: Path | None = None,
        taskcards_root: Path | None = None,
        max_docs: int = _MAX_INDEX_DOCS,
    ) -> None:
        self.evidence_root = evidence_root or _EVIDENCE_ROOT
        self.taskcards_root = taskcards_root or _TASKCARDS_ROOT
        self.max_docs = max_docs

    def build_index(self) -> list[IndexedDocument]:
        """Scan evidence declarations and taskcards; return IndexedDocument list."""
        docs: list[IndexedDocument] = []
        for doc in self._iter_evidence_declarations():
            if len(docs) >= self.max_docs:
                break
            docs.append(doc)
        for doc in self._iter_taskcards():
            if len(docs) >= self.max_docs:
                break
            docs.append(doc)
        return docs

    def _iter_evidence_declarations(self) -> Iterator[IndexedDocument]:
        """Yield IndexedDocument for each evidence-declaration.yaml found."""
        if not self.evidence_root.exists():
            return
        # Sort by modification time (newest first)
        run_dirs = sorted(
            [d for d in self.evidence_root.iterdir() if d.is_dir()],
            key=lambda d: d.stat().st_mtime,
            reverse=True,
        )
        for run_dir in run_dirs:
            decl = run_dir / "evidence-declaration.yaml"
            if not decl.exists():
                continue
            try:
                content = decl.read_text(encoding="utf-8", errors="replace")
                content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
                metadata = self._extract_yaml_metadata(content)
                try:
                    src_path = str(decl.relative_to(_REPO_ROOT))
                except ValueError:
                    src_path = str(decl)
                yield IndexedDocument(
                    doc_id=f"evidence:{run_dir.name}",
                    source_path=src_path,
                    doc_type="evidence_declaration",
                    content=content,
                    content_hash=content_hash,
                    metadata=metadata,
                )
            except Exception:  # noqa: BLE001
                continue

    def _iter_taskcards(self) -> Iterator[IndexedDocument]:
        """Yield IndexedDocument for each taskcard YAML found."""
        if not self.taskcards_root.exists():
            return
        for yaml_file in sorted(self.taskcards_root.rglob("*.yaml")):
            try:
                content = yaml_file.read_text(encoding="utf-8", errors="replace")
                content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
                metadata = self._extract_yaml_metadata(content)
                try:
                    src_path = str(yaml_file.relative_to(_REPO_ROOT))
                except ValueError:
                    src_path = str(yaml_file)
                yield IndexedDocument(
                    doc_id=f"taskcard:{yaml_file.stem}",
                    source_path=src_path,
                    doc_type="taskcard",
                    content=content,
                    content_hash=content_hash,
                    metadata=metadata,
                )
            except Exception:  # noqa: BLE001
                continue

    def _extract_yaml_metadata(self, content: str) -> dict[str, Any]:
        """Extract key metadata fields from YAML text (no external YAML parser)."""
        metadata: dict[str, Any] = {}
        for line in content.splitlines()[:30]:
            stripped = line.strip()
            if ":" in stripped and not stripped.startswith("#"):
                key, _, val = stripped.partition(":")
                key = key.strip().lstrip("- ")
                val = val.strip().strip('"').strip("'")
                if key in (
                    "run_id", "sprint_id", "worker_self_verdict", "item_id",
                    "title", "status", "supervisor_grade", "lane", "sprint_type",
                    "execution_method", "doc_type",
                ):
                    metadata[key] = val
        return metadata


# ---------------------------------------------------------------------------
# Pilot index persistence
# ---------------------------------------------------------------------------

def _save_index(documents: list[IndexedDocument], index_dir: Path) -> None:
    """Save index manifest to disk for reuse."""
    index_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "indexed_at": datetime.now(timezone.utc).isoformat(),
        "doc_count": len(documents),
        "documents": [d.to_dict() for d in documents],
        "authority_state": _AUTHORITY_STATE,
        "non_authoritative": _NON_AUTHORITATIVE,
    }
    (index_dir / "index-manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


def _load_index_manifest(index_dir: Path) -> dict[str, Any] | None:
    """Load index manifest if it exists."""
    manifest_path = index_dir / "index-manifest.json"
    if not manifest_path.exists():
        return None
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------------------
# Main pilot entry point
# ---------------------------------------------------------------------------

class PriorRunRetrievalPilot:
    """Advisory retrieval over prior evidence runs.

    Given a defect description (rework reason, failure message, stale item),
    returns similar prior evidence and taskcards as advisory suggestions.

    Output is ALWAYS advisory. Results must NEVER drive direct source mutations.
    """

    def __init__(
        self,
        indexer: DocumentIndexer | None = None,
        index_dir: Path | None = None,
        max_results: int = _MAX_RETRIEVAL_RESULTS,
    ) -> None:
        self.indexer = indexer or DocumentIndexer()
        self.index_dir = index_dir or _INDEX_DIR
        self.max_results = max_results
        self._documents: list[IndexedDocument] = []
        self._retriever: LexicalRetriever | None = None

    @classmethod
    def from_repo(
        cls,
        repo_root: Path | None = None,
        max_docs: int = _MAX_INDEX_DOCS,
    ) -> "PriorRunRetrievalPilot":
        """Create pilot from standard repo paths."""
        root = repo_root or _REPO_ROOT
        indexer = DocumentIndexer(
            evidence_root=root / ".local" / "evidences",
            taskcards_root=root / "taskcards",
            max_docs=max_docs,
        )
        index_dir = root / ".local" / "embedding-index"
        return cls(indexer=indexer, index_dir=index_dir)

    def build_index(self) -> int:
        """Build/rebuild the document index. Returns document count."""
        self._documents = self.indexer.build_index()
        self._retriever = LexicalRetriever(self._documents)
        _save_index(self._documents, self.index_dir)
        return len(self._documents)

    def find_similar(
        self,
        query: str,
        top_k: int | None = None,
        doc_type_filter: str | None = None,
    ) -> list[RetrievalResult]:
        """Find similar prior evidence/taskcards for advisory guidance.

        Args:
            query: Defect description or rework reason.
            top_k: Maximum results (default: self.max_results).
            doc_type_filter: Filter by doc_type ('evidence_declaration' or 'taskcard').

        Returns:
            List of RetrievalResult, sorted by score descending. Always advisory.
        """
        if self._retriever is None:
            self.build_index()

        k = top_k or self.max_results
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]

        raw_results = self._retriever.retrieve(query, top_k=k * 2)  # type: ignore[union-attr]

        results: list[RetrievalResult] = []
        for doc, score in raw_results:
            if doc_type_filter and doc.doc_type != doc_type_filter:
                continue
            results.append(
                RetrievalResult(
                    doc=doc,
                    score=score,
                    retrieval_method="lexical_tfidf",
                    query_hash=query_hash,
                )
            )
            if len(results) >= k:
                break

        return results

    def get_index_stats(self) -> dict[str, Any]:
        """Return stats about the current index."""
        if not self._documents:
            manifest = _load_index_manifest(self.index_dir)
            if manifest:
                return {
                    "doc_count": manifest.get("doc_count", 0),
                    "indexed_at": manifest.get("indexed_at"),
                    "source": "manifest",
                    "authority_state": _AUTHORITY_STATE,
                }
            return {"doc_count": 0, "source": "empty"}

        by_type: Counter[str] = Counter(d.doc_type for d in self._documents)
        return {
            "doc_count": len(self._documents),
            "by_type": dict(by_type),
            "source": "in_memory",
            "authority_state": _AUTHORITY_STATE,
            "non_authoritative": _NON_AUTHORITATIVE,
        }

    def save_retrieval_log(
        self,
        query: str,
        results: list[RetrievalResult],
        log_dir: Path | None = None,
    ) -> Path:
        """Save a retrieval log entry for evidence/auditability."""
        log_root = log_dir or (self.index_dir / "retrieval-logs")
        log_root.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        log_path = log_root / f"retrieval-{ts}.json"
        entry = {
            "query": query[:256],
            "query_hash": hashlib.sha256(query.encode()).hexdigest()[:16],
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "result_count": len(results),
            "results": [r.to_dict() for r in results],
            "authority_state": _AUTHORITY_STATE,
            "non_authoritative": _NON_AUTHORITATIVE,
        }
        log_path.write_text(json.dumps(entry, indent=2), encoding="utf-8")
        return log_path


# ---------------------------------------------------------------------------
# Hybrid retrieval: lexical + optional embedding
# Phase 3 addition — Sprint: FORMAT-FACTORY-BROAD-SELF-HEALING-PRODUCT-ACCELERATION-RNEXT
# ---------------------------------------------------------------------------

_EMBEDDING_CACHE_VERSION = 1


class EmbeddingCache:
    """Persistent cache for document embedding vectors.

    Stores embeddings keyed by (source_path, content_hash, model_id).
    Invalidates entries when content_hash changes.
    All cached data is advisory only — non_authoritative=True.
    """

    def __init__(self, cache_path: Path) -> None:
        self.cache_path = cache_path
        self._data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if self.cache_path.exists():
            try:
                return json.loads(self.cache_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                pass
        return {
            "version": _EMBEDDING_CACHE_VERSION,
            "entries": {},
            "authority_state": _AUTHORITY_STATE,
            "non_authoritative": _NON_AUTHORITATIVE,
        }

    def _save(self) -> None:
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass

    def _key(self, source_path: str, content_hash: str, model_id: str) -> str:
        return hashlib.sha256(f"{source_path}|{content_hash}|{model_id}".encode()).hexdigest()[:32]

    def get(
        self, source_path: str, content_hash: str, model_id: str
    ) -> list[float] | None:
        key = self._key(source_path, content_hash, model_id)
        entry = self._data.get("entries", {}).get(key)
        if entry is None:
            return None
        # Invalidate if content_hash changed
        if entry.get("content_hash") != content_hash:
            return None
        return entry.get("embedding")

    def put(
        self,
        source_path: str,
        content_hash: str,
        model_id: str,
        embedding: list[float],
        dimension: int,
        provider_id: str,
    ) -> None:
        key = self._key(source_path, content_hash, model_id)
        self._data.setdefault("entries", {})[key] = {
            "source_path": source_path,
            "content_hash": content_hash,
            "model_id": model_id,
            "embedding_dimension": dimension,
            "provider_id": provider_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "authority_state": _AUTHORITY_STATE,
            "non_authoritative": _NON_AUTHORITATIVE,
            "advisory_only": True,
            "embedding": embedding,
        }
        self._save()

    def stats(self) -> dict[str, Any]:
        entries = self._data.get("entries", {})
        return {
            "entry_count": len(entries),
            "cache_path": str(self.cache_path),
            "authority_state": _AUTHORITY_STATE,
        }


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors (stdlib only)."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a < 1e-10 or mag_b < 1e-10:
        return 0.0
    return dot / (mag_a * mag_b)


class EmbeddingProvider:
    """Optional embedding provider via endpoint_client.

    Advisory only. Falls back gracefully if endpoint is unavailable.
    Uses simple text snippet as embedding input (first 512 chars of content).

    NOTE: Because the embedding API requires an HTTP call returning a float vector,
    and without live credentials this returns None (fallback to lexical).
    When credentials are available, embeddings are fetched and cached.
    """

    def __init__(
        self,
        endpoint_id: str = "professionalize",
        model_id: str = "qwen3-embedding-8b",
        cache: EmbeddingCache | None = None,
    ) -> None:
        self.endpoint_id = endpoint_id
        self.model_id = model_id
        self.cache = cache
        self._client: Any | None = None
        self._available: bool | None = None

    def _get_client(self) -> Any | None:
        """Lazily import and create the endpoint client."""
        if self._client is not None:
            return self._client
        try:
            _tools = str(Path(__file__).parent.parent / "llm")
            if _tools not in sys.path:
                sys.path.insert(0, _tools)
            from endpoint_client import EndpointClient  # type: ignore[import]
            client = EndpointClient.from_endpoint_id(self.endpoint_id)
            if not client.has_credential:
                self._available = False
                return None
            self._client = client
            self._available = True
            return self._client
        except Exception:  # noqa: BLE001
            self._available = False
            return None

    @property
    def is_available(self) -> bool:
        if self._available is None:
            self._get_client()
        return bool(self._available)

    def get_embedding(
        self, text: str, source_path: str, content_hash: str
    ) -> list[float] | None:
        """Get embedding for text. Returns None if unavailable (fallback)."""
        # Check cache first
        if self.cache:
            cached = self.cache.get(source_path, content_hash, self.model_id)
            if cached is not None:
                return cached

        client = self._get_client()
        if client is None:
            return None

        # TC-EMBED-001: Call /v1/embeddings endpoint via EndpointClient.embed().
        # Returns list[float] on success; None on failure (triggers lexical fallback).
        # All embeddings are advisory-only (authority_state="ai_advisory").
        truncated = text[:512]
        try:
            result = client.embed([truncated], model=self.model_id)
            if result.success and result.embeddings:
                vector = result.embeddings[0]
                if self.cache:
                    self.cache.set(source_path, content_hash, self.model_id, vector)
                return vector
        except Exception:
            pass
        return None  # Lexical fallback if embedding call fails


class HybridRetrievalPilot(PriorRunRetrievalPilot):
    """Hybrid retrieval pilot: lexical TF-IDF + optional embedding scoring.

    Extends PriorRunRetrievalPilot with:
    - Optional embedding provider (falls back to lexical if unavailable)
    - Hybrid score = alpha * lexical_score + (1 - alpha) * embedding_score
    - Embedding cache for reuse and invalidation on content_hash change
    - All results remain advisory-only (non_authoritative=True)

    Fallback behavior:
    - If embedding is unavailable: hybrid degrades to lexical only (alpha=1.0)
    - Results are labeled 'hybrid_fallback_lexical' to indicate embedding was unavailable
    """

    def __init__(
        self,
        indexer: DocumentIndexer | None = None,
        index_dir: Path | None = None,
        max_results: int = _MAX_RETRIEVAL_RESULTS,
        embedding_provider: EmbeddingProvider | None = None,
        alpha: float = 0.5,
    ) -> None:
        super().__init__(indexer=indexer, index_dir=index_dir, max_results=max_results)
        self._embedding_provider = embedding_provider
        self.alpha = alpha  # weight for lexical score in hybrid
        cache_path = (index_dir or _INDEX_DIR) / "embedding-cache.json"
        self._embedding_cache = EmbeddingCache(cache_path)
        if self._embedding_provider and self._embedding_provider.cache is None:
            self._embedding_provider.cache = self._embedding_cache

    @classmethod
    def from_repo(
        cls,
        repo_root: Path | None = None,
        max_docs: int = _MAX_INDEX_DOCS,
        use_embedding: bool = True,
    ) -> "HybridRetrievalPilot":
        root = repo_root or _REPO_ROOT
        indexer = DocumentIndexer(
            evidence_root=root / ".local" / "evidences",
            taskcards_root=root / "taskcards",
            max_docs=max_docs,
        )
        index_dir = root / ".local" / "embedding-index"
        provider = EmbeddingProvider() if use_embedding else None
        return cls(indexer=indexer, index_dir=index_dir, embedding_provider=provider)

    def find_similar(
        self,
        query: str,
        top_k: int | None = None,
        doc_type_filter: str | None = None,
    ) -> list[RetrievalResult]:
        """Hybrid retrieval: lexical + optional embedding.

        Returns RetrievalResult objects with extended to_dict() that includes
        lexical_score, embedding_score, hybrid_score, and retrieval_method.
        """
        if self._retriever is None:
            self.build_index()

        k = top_k or self.max_results
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]

        # Get lexical candidates (wider net for hybrid re-ranking)
        raw_lexical = self._retriever.retrieve(query, top_k=k * 3)  # type: ignore[union-attr]

        embedding_available = (
            self._embedding_provider is not None and self._embedding_provider.is_available
        )
        method = "hybrid" if embedding_available else "hybrid_fallback_lexical"

        # Normalize lexical scores to [0, 1]
        lex_scores = {doc.doc_id: score for doc, score in raw_lexical}
        max_lex = max(lex_scores.values(), default=1.0) or 1.0
        norm_lex = {did: s / max_lex for did, s in lex_scores.items()}

        results: list[RetrievalResult] = []
        for doc, raw_lex in raw_lexical:
            lex_s = norm_lex.get(doc.doc_id, 0.0)
            emb_s = 0.0
            if embedding_available and self._embedding_provider:
                vec = self._embedding_provider.get_embedding(
                    doc.content[:512], doc.source_path, doc.content_hash
                )
                if vec is not None:
                    query_vec = self._embedding_provider.get_embedding(
                        query, "_query_", hashlib.sha256(query.encode()).hexdigest()[:16]
                    )
                    if query_vec is not None:
                        emb_s = max(0.0, _cosine_similarity(vec, query_vec))

            hybrid_s = self.alpha * lex_s + (1 - self.alpha) * emb_s
            if hybrid_s < _MIN_SCORE and not embedding_available:
                continue

            if doc_type_filter and doc.doc_type != doc_type_filter:
                continue

            result = RetrievalResult(
                doc=doc,
                score=hybrid_s,
                retrieval_method=method,
                query_hash=query_hash,
            )
            # Augment result with score breakdown
            result.lexical_score = lex_s  # type: ignore[attr-defined]
            result.embedding_score = emb_s  # type: ignore[attr-defined]
            result.hybrid_score = hybrid_s  # type: ignore[attr-defined]
            results.append(result)

            if len(results) >= k:
                break

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:k]

    def get_embedding_stats(self) -> dict[str, Any]:
        return {
            "embedding_available": (
                self._embedding_provider.is_available if self._embedding_provider else False
            ),
            "cache_stats": self._embedding_cache.stats(),
            "alpha": self.alpha,
            "authority_state": _AUTHORITY_STATE,
            "non_authoritative": _NON_AUTHORITATIVE,
        }


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def find_similar_advisory(
    query: str,
    *,
    repo_root: Path | None = None,
    top_k: int = _MAX_RETRIEVAL_RESULTS,
    doc_type_filter: str | None = None,
) -> list[dict[str, Any]]:
    """Advisory retrieval wrapper. Returns list of advisory result dicts.

    Builds index on first call. Always advisory — results must not drive mutations.
    """
    pilot = PriorRunRetrievalPilot.from_repo(repo_root)
    pilot.build_index()
    results = pilot.find_similar(query, top_k=top_k, doc_type_filter=doc_type_filter)
    return [r.to_dict() for r in results]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Advisory prior-run retrieval")
    parser.add_argument("query", nargs="?", default="STALE_QUEUE_ITEM defect")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--doc-type", default=None)
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()

    pilot = PriorRunRetrievalPilot.from_repo()
    n = pilot.build_index()
    print(f"Index built: {n} documents")

    if args.stats:
        print(json.dumps(pilot.get_index_stats(), indent=2))
        sys.exit(0)

    results = pilot.find_similar(args.query, top_k=args.top_k, doc_type_filter=args.doc_type)
    print(f"Query: {args.query!r}")
    print(f"Results: {len(results)}")
    for r in results:
        print(f"  [{r.score:.3f}] {r.doc.doc_type}: {r.doc.source_path}")
        print(f"         {r.advisory_text[:120]}")
