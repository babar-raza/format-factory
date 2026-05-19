"""Deterministic lexical retrieval baseline — ranked, filtered, explainable.

Provides local retrieval that actually ranks and filters chunks using
TF-based lexical scoring. No vector DB required.

This replaces the return-all stub for pipeline use.
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass, field
from typing import Any

from tools.ai.normalization.adapter import NormalizedChunk


@dataclass
class ScoredChunk:
    """A chunk with its retrieval score and explanation."""
    chunk: NormalizedChunk
    score: float = 0.0
    matched_terms: list[str] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_hash": self.chunk.chunk_hash,
            "format_id": self.chunk.format_id,
            "section": self.chunk.section,
            "score": round(self.score, 4),
            "matched_terms": self.matched_terms,
            "explanation": self.explanation,
        }


@dataclass
class RetrievalResult:
    """Complete retrieval result with ranking metadata."""
    query: str
    query_hash: str
    format_id: str
    total_candidates: int
    returned: int
    top_k: int
    threshold: float
    scored_chunks: list[ScoredChunk] = field(default_factory=list)
    excluded_count: int = 0
    mode: str = "lexical"

    @property
    def has_results(self) -> bool:
        return len(self.scored_chunks) > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "query_hash": self.query_hash,
            "format_id": self.format_id,
            "total_candidates": self.total_candidates,
            "returned": self.returned,
            "top_k": self.top_k,
            "threshold": self.threshold,
            "excluded_count": self.excluded_count,
            "mode": self.mode,
            "chunks": [sc.to_dict() for sc in self.scored_chunks],
        }


_STOP_WORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "must", "to", "of",
    "in", "for", "on", "with", "at", "by", "from", "as", "into", "about",
    "and", "or", "not", "no", "but", "if", "then", "than", "that", "this",
    "it", "its", "which", "what", "when", "where", "how", "all", "each",
})

_TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase terms, filtering stop words."""
    return [
        t.lower()
        for t in _TOKEN_RE.findall(text)
        if t.lower() not in _STOP_WORDS and len(t) > 1
    ]


def compute_tf(tokens: list[str]) -> dict[str, float]:
    """Compute term frequency for a token list."""
    if not tokens:
        return {}
    counts: dict[str, int] = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    total = len(tokens)
    return {t: c / total for t, c in counts.items()}


def compute_idf(corpus_tokens: list[list[str]]) -> dict[str, float]:
    """Compute inverse document frequency across a corpus."""
    n = len(corpus_tokens)
    if n == 0:
        return {}
    doc_freq: dict[str, int] = {}
    for doc_tokens in corpus_tokens:
        seen = set(doc_tokens)
        for t in seen:
            doc_freq[t] = doc_freq.get(t, 0) + 1
    return {t: math.log((n + 1) / (df + 1)) + 1.0 for t, df in doc_freq.items()}


def score_chunk(
    query_tokens: list[str],
    chunk_tokens: list[str],
    idf: dict[str, float],
) -> tuple[float, list[str]]:
    """Score a chunk against a query using TF-IDF cosine-like scoring."""
    if not query_tokens or not chunk_tokens:
        return 0.0, []

    chunk_tf = compute_tf(chunk_tokens)
    query_tf = compute_tf(query_tokens)

    matched = []
    score = 0.0
    for term in set(query_tokens):
        if term in chunk_tf:
            matched.append(term)
            score += query_tf.get(term, 0) * chunk_tf[term] * idf.get(term, 1.0)

    return score, matched


def retrieve(
    query: str,
    chunks: list[NormalizedChunk],
    format_id: str,
    top_k: int = 5,
    threshold: float = 0.01,
    require_provenance: bool = True,
    current_source_hashes: dict[str, str] | None = None,
) -> RetrievalResult:
    """Retrieve top-k chunks ranked by lexical relevance.

    Args:
        query: The retrieval query text.
        chunks: All available normalized chunks.
        format_id: Required format namespace — chunks from other formats are rejected.
        top_k: Maximum number of chunks to return.
        threshold: Minimum score to include a chunk.
        require_provenance: If True, reject chunks with missing provenance.
        current_source_hashes: If provided, reject stale chunks whose source_hash doesn't match.

    Returns:
        RetrievalResult with ranked, filtered, scored chunks.
    """
    query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
    result = RetrievalResult(
        query=query,
        query_hash=query_hash,
        format_id=format_id,
        total_candidates=len(chunks),
        returned=0,
        top_k=top_k,
        threshold=threshold,
    )

    # Filter: namespace
    ns_filtered = []
    for c in chunks:
        if c.format_id != format_id:
            result.excluded_count += 1
            continue
        ns_filtered.append(c)

    # Filter: provenance
    prov_filtered = []
    for c in ns_filtered:
        if require_provenance and c.validate_provenance():
            result.excluded_count += 1
            continue
        prov_filtered.append(c)

    # Filter: staleness
    fresh_filtered = []
    for c in prov_filtered:
        if current_source_hashes and c.source_path in current_source_hashes:
            if c.source_hash != current_source_hashes[c.source_path]:
                result.excluded_count += 1
                continue
        fresh_filtered.append(c)

    # Tokenize
    query_tokens = tokenize(query)
    corpus_tokens = [tokenize(c.content) for c in fresh_filtered]
    idf = compute_idf(corpus_tokens)

    # Score
    scored: list[ScoredChunk] = []
    for i, chunk in enumerate(fresh_filtered):
        s, matched = score_chunk(query_tokens, corpus_tokens[i], idf)
        explanation = f"matched {len(matched)}/{len(set(query_tokens))} query terms"
        if s < threshold:
            explanation += f"; below threshold {threshold}"
            result.excluded_count += 1
            continue
        scored.append(ScoredChunk(
            chunk=chunk,
            score=s,
            matched_terms=matched,
            explanation=explanation,
        ))

    # Sort by score descending
    scored.sort(key=lambda x: x.score, reverse=True)

    # Top-k
    result.scored_chunks = scored[:top_k]
    result.returned = len(result.scored_chunks)

    return result
