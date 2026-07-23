from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


class ProducerStateError(RuntimeError):
    pass


def _digest(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_checkpoint(
    *,
    state_dir: Path,
    producer: str,
    plan_id: str,
    task_id: str | None,
    source_commit: str,
    evidence_path: Path | None = None,
    declared_verifier: str | None = None,
) -> dict[str, Any]:
    state_path = state_dir / "state.json"
    if not state_path.exists():
        raise ProducerStateError(f"missing producer state: {state_path}")
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProducerStateError(f"corrupt producer state: {exc}") from exc
    if not isinstance(state, dict) or not state.get("schema"):
        raise ProducerStateError("producer state must be an object with schema")
    gaps_path = state_dir / "current-gaps.json"
    journal_path = state_dir / "journal.jsonl"
    evidence_digest = _digest(evidence_path) if evidence_path else state.get("evidence_digest")
    if not isinstance(evidence_digest, str) or not re.fullmatch(
        r"[a-fA-F0-9]{64}", evidence_digest
    ):
        raise ProducerStateError(
            "producer checkpoint requires a SHA-256 evidence_digest or readable evidence_path"
        )
    if not declared_verifier:
        raise ProducerStateError("producer checkpoint requires a declared verifier")
    payload = {
        "producer": producer,
        "plan_id": plan_id,
        "task_id": task_id,
        "source_commit": source_commit,
        "producer_schema": state["schema"],
        "producer_state_digest": _digest(state_path),
        "producer_gap_digest": _digest(gaps_path),
        "producer_journal_digest": _digest(journal_path),
        "evidence_digest": evidence_digest,
        "declared_verifier": declared_verifier,
        "verified": False,
    }
    payload["checkpoint_id"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()[:24]
    return payload
