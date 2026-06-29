"""grading_retrieval_bridge.py — TC-LLM-WIRE-001: Bridges embedding retrieval into grading.

Provides:
  - retrieve_prior_context(): fetches similar prior items for LLM grading context
  - log_llm_call(): logs LLM call provenance to .local/llm-call-logs/
  - check_product_source_content(): deterministic content check (extracted for LOC cap)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def retrieve_prior_context(
    item_title: str,
    acceptance_criteria: str,
    repo_root: Path,
    top_k: int = 3,
) -> tuple[str, list[dict[str, Any]]]:
    """Retrieve similar prior evidence items as advisory grading context.

    Returns:
        (context_text, retrieval_results) — context_text is empty string if no results.
        retrieval_results is a list of dicts from find_similar_advisory().
    """
    try:
        from embedding_retrieval import find_similar_advisory
        query = f"{item_title} {acceptance_criteria}"
        results = find_similar_advisory(
            query, repo_root=repo_root, top_k=top_k,
            doc_type_filter="evidence_declaration",
        )
        if not results:
            return "", []
        snippets = []
        for rr in results[:top_k]:
            snippets.append(
                f"[Prior item: {rr.get('doc_id', '?')} "
                f"(score={rr.get('score', 0):.2f}, "
                f"method={rr.get('retrieval_method', '?')})]\n"
                f"{rr.get('advisory_text', '')[:300]}"
            )
        context = (
            "\n\nPrior similar items (advisory context, for comparison):\n"
            + "\n---\n".join(snippets)
        )
        return context, results
    except Exception:
        return "", []


def log_llm_call(
    item_id: str,
    ev_hash: str,
    result: dict,
    retrieval_results: list,
    repo_root: Path,
) -> None:
    """Log LLM call provenance to .local/llm-call-logs/. Best-effort."""
    try:
        log_dir = repo_root / ".local" / "llm-call-logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "item_id": item_id,
            "evidence_hash": ev_hash,
            "authority_state": "ai_advisory",
            "from_cache": False,
            "llm_used": result.get("llm_used", False),
            "adequate": result.get("adequate"),
            "confidence": result.get("confidence"),
            "retrieval_chunks": [
                {"doc_id": r.get("doc_id"), "score": r.get("score"),
                 "method": r.get("retrieval_method")}
                for r in (retrieval_results or [])[:3]
            ],
        }
        log_path = log_dir / f"grade-{ts}-{item_id[:20]}.json"
        log_path.write_text(json.dumps(log_entry, indent=2), encoding="utf-8")
    except Exception:
        pass


def check_product_source_content(
    found_paths: list[str],
    item_id: str,
    repo_root: "Path | None" = None,
) -> dict:
    """Deterministic content check for PRODUCT_SOURCE items (no LLM).

    Checks test files for def test_ + assert.
    Pure source-only items (no test file) are not penalized.

    Returns: {source_exists, test_content_valid, details}
    """
    _repo = Path(repo_root) if repo_root else Path(__file__).resolve().parent.parent.parent
    source_paths = [p for p in found_paths
                    if "test_" not in Path(p).name and p.endswith(".py")]
    test_paths = [p for p in found_paths
                  if "test_" in Path(p).name and p.endswith(".py")]

    source_exists = any((_repo / sp).exists() for sp in source_paths)

    test_content_valid = False
    details: list[str] = []
    for tp in test_paths:
        full = _repo / tp
        if not full.exists():
            details.append(f"test file missing: {tp}")
            continue
        try:
            content = full.read_text(encoding="utf-8", errors="replace")
            has_test_fn = "def test_" in content
            has_assert = "assert" in content
            if has_test_fn and has_assert:
                test_content_valid = True
                details.append(f"test content valid: {tp}")
            elif not has_test_fn:
                details.append(f"no def test_ in: {tp}")
            else:
                details.append(f"no assert in: {tp}")
        except Exception as _e:
            details.append(f"read error {tp}: {_e}")

    if not test_paths:
        test_content_valid = True  # Pure source items not penalized

    return {"source_exists": source_exists, "test_content_valid": test_content_valid,
            "details": details}
