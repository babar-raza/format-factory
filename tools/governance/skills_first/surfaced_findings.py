"""surfaced_findings.py — TC-STRUCT-001 (2026-07-17, FOUND-ISSUE-OWNERSHIP-ENFORCEMENT).

Ambient found-issue enforcement needs to know, at plan-closure time, which
HIGH/CRITICAL findings THIS agent's own audit invocations actually surfaced
this session — not "every finding anywhere in the repo" (unworkable and
philosophically wrong under ~40-50 concurrent agents; the found-issue-
ownership policy's trigger is *discovery*, not mere *coexistence*).

This module is the write side (called from audit.py's run_audit()) and the
read side (called from lifecycle_audit.py's new closure guard) of a single
append-only log, mirroring the existing advisory-log.jsonl convention
(tools/supervisor/coordination/hooks/gate.py's _advisory()) rather than
inventing a new logging primitive.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
SURFACED_FINDINGS_LOG = REPO_ROOT / ".local" / "supervisor" / "surfaced-findings.jsonl"

_BLOCKING_SEVERITIES = frozenset({"HIGH", "CRITICAL"})


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_agent_id() -> str:
    """Best-effort current-agent identity for attribution.

    Priority: (1) FF_AGENT_ID env var — explicit, set by the operator/session
    for every coordinated write this session; the reliable path. (2) the
    coordination plane's single-fresh-agent heuristic (same F1 mitigation
    pattern as continuation_identity.py's _resolve_via_coordination — reused,
    not reinvented). (3) "unknown" — never raises; attribution is best-effort,
    never a new point of fragility.
    """
    env_id = os.environ.get("FF_AGENT_ID")
    if env_id:
        return env_id
    try:
        import sys
        sup_dir = REPO_ROOT / "tools" / "supervisor"
        if str(sup_dir) not in sys.path:
            sys.path.insert(0, str(sup_dir))
        from coordination.db import connect  # noqa: PLC0415
        from coordination.root import resolve_coordination_root  # noqa: PLC0415

        root = resolve_coordination_root()
        conn = connect(root)
        try:
            rows = conn.execute(
                "SELECT agent_id FROM agents WHERE status='ACTIVE'"
            ).fetchall()
        finally:
            conn.close()
        fresh = {r["agent_id"] for r in rows}
        if len(fresh) == 1:
            return next(iter(fresh))
    except Exception:
        pass
    return "unknown"


def _fingerprint(finding: dict) -> str:
    """Stable identity for a finding, independent of *when* it was seen —
    used to dedupe repeated observations of the same underlying problem."""
    key = "|".join(str(finding.get(k, "")) for k in (
        "category", "command_file", "skill_id", "detail"))
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def record_surfaced_findings(findings: list[dict], agent_id: "str | None" = None) -> int:
    """Append each HIGH/CRITICAL finding to the surfaced-findings log.

    Never raises — a logging failure must not break the audit call that
    triggered it. Returns the number of entries written (0 on any failure).
    """
    blocking = [f for f in findings if f.get("severity") in _BLOCKING_SEVERITIES]
    if not blocking:
        return 0
    aid = agent_id or resolve_agent_id()
    try:
        SURFACED_FINDINGS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with SURFACED_FINDINGS_LOG.open("a", encoding="utf-8") as fh:
            for f in blocking:
                entry = {
                    "ts": _now_iso(),
                    "agent_id": aid,
                    "fingerprint": _fingerprint(f),
                    "severity": f.get("severity"),
                    "category": f.get("category"),
                    "command_file": f.get("command_file"),
                    "detail": f.get("detail"),
                }
                fh.write(json.dumps(entry, default=str) + "\n")
        return len(blocking)
    except Exception:
        return 0


def read_surfaced_findings(agent_id: "str | None" = None) -> list[dict]:
    """Return deduped surfaced-finding entries (one per fingerprint, earliest
    `ts` kept) — optionally filtered to a single agent_id. Never raises;
    returns [] on any read failure (missing file, malformed JSONL, etc.)."""
    if not SURFACED_FINDINGS_LOG.exists():
        return []
    by_fp: dict[str, dict] = {}
    try:
        for line in SURFACED_FINDINGS_LOG.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            fp = entry.get("fingerprint")
            if not fp:
                continue
            existing = by_fp.get(fp)
            if existing is None or entry.get("ts", "") < existing.get("ts", ""):
                by_fp[fp] = entry
    except Exception:
        return []
    entries = list(by_fp.values())
    if agent_id is not None:
        entries = [e for e in entries if e.get("agent_id") == agent_id]
    return entries
