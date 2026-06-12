"""Source Pattern Miner — reads src/ corpus, finds code patterns via TF-IDF retrieval.

Uses lexical_retriever for deterministic chunk scoring.
AI layer (summarization role) adds interpretive summary — fixture OK if gateway unavailable.
Format namespace is enforced: fods query never returns fodt chunks.
src/ is NEVER modified.

authority_state: ai_draft on all outputs. non_authoritative: True.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _load_source_chunks(format_id: str) -> list[dict[str, str]]:
    """Load source files for the given format as text chunks."""
    chunks: list[dict[str, str]] = []
    for track_dir in [f"src/net/{format_id}", f"src/python/{format_id}"]:
        base = _REPO_ROOT / track_dir
        if not base.exists():
            continue
        for ext in ("*.cs", "*.py"):
            for p in base.rglob(ext):
                try:
                    text = p.read_text(encoding="utf-8", errors="replace")
                    chunks.append({
                        "id": str(p.relative_to(_REPO_ROOT)),
                        "text": text,
                        "format": format_id,
                    })
                except Exception:
                    pass
    return chunks


def _tfidf_score(query: str, text: str) -> float:
    """Simple TF-IDF-style relevance score."""
    q_tokens = set(re.findall(r"\w+", query.lower()))
    doc_tokens = re.findall(r"\w+", text.lower())
    if not doc_tokens or not q_tokens:
        return 0.0
    tf = sum(1 for t in doc_tokens if t in q_tokens) / len(doc_tokens)
    return tf


def mine_patterns(
    format_id: str,
    query: str,
    top_k: int = 5,
    output_dir: Path | None = None,
    sprint_id: str = "",
) -> dict[str, Any]:
    """Mine source patterns for a format using the given query."""
    chunks = _load_source_chunks(format_id)
    corpus_empty = len(chunks) == 0

    scored = []
    for chunk in chunks:
        score = _tfidf_score(query, chunk["text"])
        if score > 0:
            scored.append({"id": chunk["id"], "score": round(score, 6), "excerpt": chunk["text"][:300]})
    scored.sort(key=lambda x: x["score"], reverse=True)
    top_chunks = scored[:top_k]

    # AI summary via gateway (role=summarization, fixture OK)
    ai_summary = _gateway_summarize(format_id, query, top_chunks, sprint_id)

    result: dict[str, Any] = {
        "sprint_id": sprint_id,
        "format_id": format_id,
        "query": query,
        "corpus_empty": corpus_empty,
        "chunks_found": len(chunks),
        "top_k_returned": len(top_chunks),
        "lexical_patterns": top_chunks,
        "ai_pattern_summary": ai_summary,
        "authority_state": "ai_draft",
        "non_authoritative": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_file = output_dir / f"{format_id}-patterns.json"
        out_file.write_text(json.dumps(result, indent=2))

    return result


def _gateway_summarize(
    format_id: str, query: str, chunks: list[dict], sprint_id: str
) -> str:
    """Call gateway (summarization role) to summarize patterns. Fixture OK."""
    try:
        from tools.ai.control_plane.config import load_ai_config
        from tools.ai.control_plane.gateway import gateway_chat
        from tools.ai.control_plane.model_router import ModelRouter
        from tools.ai.schemas.models import AIRole, ModelSelectionRequest

        cfg = load_ai_config()
        if not cfg.is_configured:
            return f"[fixture] No live gateway for {format_id}. Top patterns: {[c['id'] for c in chunks[:3]]}"

        router = ModelRouter()
        decision = router.select(ModelSelectionRequest(role=AIRole.summarization))
        if decision.fail_closed or not decision.selected_model_id:
            return f"[fixture] No model for summarization. Top: {[c['id'] for c in chunks[:3]]}"

        prompt = (
            f"Summarize the key implementation patterns found in {format_id} source code "
            f"relevant to: '{query}'. Patterns found: {[c['id'] for c in chunks[:3]]}. "
            "Be brief and focus on what a Mainstream implementer needs to know."
        )
        messages = [{"role": "user", "content": prompt}]
        resp, record = gateway_chat(
            config=cfg,
            model=decision.selected_model_id,
            messages=messages,
            role="summarization",
            operation="source_pattern_summary",
            sprint_id=sprint_id,
            taskcard_id="TC-TOOL-006",
            gate_id="gate-5",
        )
        _append_ledger(record, sprint_id)
        return resp.get("content", "") or "[gateway_empty] No summary returned."
    except Exception as e:
        return f"[fixture_error] {type(e).__name__}: {e}"


def _append_ledger(record: Any, sprint_id: str) -> None:
    ledger = _REPO_ROOT / "reports/acceleration-product-first/ai-usage-ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sprint_id": sprint_id,
        "tool": "source_pattern_miner",
        "role": "summarization",
        "status": record.status.value if hasattr(record, "status") else str(record),
        "authority_state": "ai_draft",
        "live_ai_used": getattr(record, "status", None) is not None and record.status.value == "success",
    }
    with open(ledger, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Source Pattern Miner")
    parser.add_argument("--format", required=True, help="Format ID (fods, fodt, netpbm, sylk)")
    parser.add_argument("--query", required=True, help="Pattern query")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--sprint-id", default="")
    args = parser.parse_args()

    result = mine_patterns(
        format_id=args.format,
        query=args.query,
        top_k=args.top_k,
        output_dir=Path(args.output_dir),
        sprint_id=args.sprint_id,
    )
    print(f"corpus_empty={result['corpus_empty']} chunks={result['chunks_found']} top_k={result['top_k_returned']}")
    print(f"Output: {Path(args.output_dir) / (args.format + '-patterns.json')}")


if __name__ == "__main__":
    main()
