"""
tools/llm/prompt_cache.py — LLM Prompt/Response Cache Writer
TC-0005 (Phase 1, 2026-06-18)

Writes prompt-response pairs to .local/llm-cache/<format-id>/<task-id>.jsonl
and optionally stores full text in .local/llm-cache/full/<task-id>.jsonl.

Safety invariants:
- Full text is NEVER stored without explicit store_full_text=True
- Hashes are always written for integrity; full text is optional
- Cache files are gitignored; do NOT commit them
- Cached responses are advisory only (authority_state="ai_advisory")
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_LOCAL_DIR = Path(__file__).parents[2] / ".local" / "llm-cache"


def _cache_path(format_id: str | None, task_id: str) -> Path:
    subdir = format_id if format_id else "_global"
    p = _LOCAL_DIR / subdir
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{task_id}.jsonl"


def _full_cache_path(task_id: str) -> Path:
    p = _LOCAL_DIR / "full"
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{task_id}.jsonl"


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_cache_entry(
    task_id: str,
    task_type: str,
    prompt_hash: str,
    response_hash: str,
    model_id: str,
    endpoint_id: str,
    format_id: str | None = None,
    store_full_text: bool = False,
    prompt_text: str | None = None,
    response_text: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Path:
    """
    Write a prompt-response cache entry as a JSONL line.

    If store_full_text=True AND prompt_text/response_text are provided,
    the full text is written to .local/llm-cache/full/<task-id>.jsonl.
    Otherwise only hashes are stored.

    Returns the path to the summary cache file.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_id": task_id,
        "task_type": task_type,
        "format_id": format_id,
        "model_id": model_id,
        "endpoint_id": endpoint_id,
        "prompt_hash": prompt_hash,
        "response_hash": response_hash,
        "has_full_text": store_full_text and prompt_text is not None,
        "authority_state": "ai_advisory",
        "metadata": metadata or {},
    }

    cache_file = _cache_path(format_id, task_id)
    with cache_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    if store_full_text and prompt_text is not None and response_text is not None:
        full_entry = {
            **entry,
            "prompt_text": prompt_text,
            "response_text": response_text,
        }
        full_file = _full_cache_path(task_id)
        with full_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(full_entry) + "\n")

    return cache_file


def lookup_cached_response(
    task_id: str,
    prompt_hash: str,
    format_id: str | None = None,
) -> dict[str, Any] | None:
    """
    Look up a cached response by prompt_hash. Returns the most recent matching entry,
    or None if not found.
    """
    cache_file = _cache_path(format_id, task_id)
    if not cache_file.exists():
        return None
    matches = []
    with cache_file.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    if entry.get("prompt_hash") == prompt_hash:
                        matches.append(entry)
                except json.JSONDecodeError:
                    pass
    return matches[-1] if matches else None
