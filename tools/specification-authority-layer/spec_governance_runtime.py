"""
spec_governance_runtime.py — Anti-bypass enforcement runtime.

Enforces:
  1. No ad-hoc URL citation (source must be registered)
  2. No memory-only spec claim (source_refs required)
  3. No raw AI summary without source_refs
  4. No context pack use without manifest.sha256
  5. No stale context pack (source sha changed)

Also provides the usage ledger (append-only JSONL).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from .spec_source_registry import is_source_registered
    from .spec_digestor import check_staleness
    from .context_pack_builder import verify_context_pack
except ImportError:
    from spec_source_registry import is_source_registered
    from spec_digestor import check_staleness
    from context_pack_builder import verify_context_pack


USAGE_LEDGER_PATH = ".local/spec-usage-ledger/ledger.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class UsageLedgerEntry:
    entry_id: str
    action: str  # cite_source | use_context_pack | extract_requirements | register_source
    source_id: Optional[str]
    format_id: str
    actor: str
    outcome: str  # ALLOWED | REJECTED
    reason: str
    timestamp: str = field(default_factory=_now_iso)
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "action": self.action,
            "source_id": self.source_id,
            "format_id": self.format_id,
            "actor": self.actor,
            "outcome": self.outcome,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "extra": self.extra,
        }


def _append_ledger(entry: UsageLedgerEntry, ledger_path: Optional[str] = None) -> None:
    """Append an entry to the usage ledger (append-only)."""
    path = Path(ledger_path) if ledger_path else Path(USAGE_LEDGER_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry.to_dict()) + "\n")


import uuid


def check_citation_allowed(
    source_id: str,
    format_id: str,
    actor: str = "system",
    registry_dir: Optional[str] = None,
    ledger_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Anti-bypass check: is this source citation allowed?
    Logs to usage ledger.
    """
    if not source_id:
        outcome = "REJECTED"
        reason = "Empty source_id — memory-only citation not allowed."
    elif not is_source_registered(source_id, registry_dir):
        outcome = "REJECTED"
        reason = f"Source {source_id!r} not in registry — ad-hoc URL citation not allowed."
    else:
        outcome = "ALLOWED"
        reason = f"Source {source_id!r} is registered."

    entry = UsageLedgerEntry(
        entry_id=str(uuid.uuid4()),
        action="cite_source",
        source_id=source_id or None,
        format_id=format_id,
        actor=actor,
        outcome=outcome,
        reason=reason,
    )
    _append_ledger(entry, ledger_path)
    return {"allowed": outcome == "ALLOWED", "reason": reason}


def check_context_pack_use_allowed(
    pack_path: str,
    format_id: str,
    actor: str = "system",
    ledger_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Anti-bypass check: is this context pack valid and non-stale?
    """
    result = verify_context_pack(pack_path)
    if not result.get("valid"):
        outcome = "REJECTED"
        reason = result.get("reason", "Context pack invalid.")
    else:
        outcome = "ALLOWED"
        reason = f"Context pack {result.get('context_pack_id', '?')} verified."

    entry = UsageLedgerEntry(
        entry_id=str(uuid.uuid4()),
        action="use_context_pack",
        source_id=None,
        format_id=format_id,
        actor=actor,
        outcome=outcome,
        reason=reason,
        extra={"pack_path": pack_path},
    )
    _append_ledger(entry, ledger_path)
    return {"allowed": outcome == "ALLOWED", "reason": reason}


def check_memory_only_claim(
    claim: Dict[str, Any],
    format_id: str,
    actor: str = "system",
    registry_dir: Optional[str] = None,
    ledger_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Anti-bypass: reject claims with no source_refs or raw_ai_summary_only.
    """
    violations = []
    source_refs = claim.get("source_refs", [])
    if not source_refs:
        violations.append("No source_refs — memory-only claim not allowed.")

    if claim.get("raw_ai_summary_only", False):
        violations.append("raw_ai_summary_only=True not allowed.")

    for sr in source_refs:
        if registry_dir is not None:
            if not is_source_registered(sr, registry_dir):
                violations.append(f"source_ref {sr!r} not registered.")

    outcome = "REJECTED" if violations else "ALLOWED"
    reason = "; ".join(violations) if violations else "Claim has valid source_refs."

    entry = UsageLedgerEntry(
        entry_id=str(uuid.uuid4()),
        action="cite_source",
        source_id=None,
        format_id=format_id,
        actor=actor,
        outcome=outcome,
        reason=reason,
    )
    _append_ledger(entry, ledger_path)
    return {"allowed": outcome == "ALLOWED", "violations": violations, "reason": reason}


def load_usage_ledger(ledger_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load all entries from the usage ledger."""
    path = Path(ledger_path) if ledger_path else Path(USAGE_LEDGER_PATH)
    if not path.exists():
        return []
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    pass
    return entries
