"""One-shot preflight: the per-edit hot path (TC-COORD-005).

Called by the PreToolUse hook before every file mutation and available as a
CLI verb for headless/adapter agents. One BEGIN IMMEDIATE transaction plus
at most one file hash; ambient behavior:
- no covering lease + resource free  -> auto-claim + baseline capture -> allow
- no covering lease + foreign holder -> conflict record -> deny (exit 2)
- covering lease + attributable state -> allow (heartbeat + renew piggyback)
- covering lease + drift             -> conflict record -> deny (exit 5)
"""
from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from .baselines import (NO_BASELINE, WRITE_OK, BaselineTracker, sha256_file)
from .conflicts import ConflictLog
from .db import NowFn, connect, default_now, emit_event, immediate
from .errors import NotRegistered, ResourceEscape
from .leases import LeaseManager
from .registry import AgentRegistry
from .root import canonical_resource, is_logical, resolve_coordination_root, worktree_identity

ENV_AGENT = "FF_AGENT_ID"
ENV_TOKEN = "FF_AGENT_TOKEN"


@dataclass
class PreflightResult:
    decision: str                 # 'allow' | 'deny'
    exit_code: int                # 0 allow; 2/3/4/5 deny reasons
    reason: str
    agent_id: str | None = None
    lease_id: str | None = None
    classification: str | None = None
    conflict_id: str | None = None
    auto_claimed: bool = False
    detail: dict = field(default_factory=dict)

    @property
    def allowed(self) -> bool:
        return self.decision == "allow"


def resolve_identity(registry: AgentRegistry, *, agent_id: str | None = None,
                     token: str | None = None,
                     session_id: str | None = None) -> tuple[str, str] | None:
    """(agent_id, token) from explicit args, runtime files, or env."""
    if agent_id and token:
        return agent_id, token
    if agent_id:
        data = registry.read_runtime_identity(agent_id=agent_id)
        if data:
            return data["agent_id"], data["token"]
        return None
    if session_id:
        data = registry.read_runtime_identity(session_id=session_id)
        if data:
            return data["agent_id"], data["token"]
        return None
    env_agent, env_token = os.environ.get(ENV_AGENT), os.environ.get(ENV_TOKEN)
    if env_agent and env_token:
        return env_agent, env_token
    if env_agent:
        data = registry.read_runtime_identity(agent_id=env_agent)
        if data:
            return data["agent_id"], data["token"]
    return None


def preflight(resource: str, op: str = "edit", *, root: Path | None = None,
              start: str | Path | None = None, agent_id: str | None = None,
              token: str | None = None, session_id: str | None = None,
              now_fn: NowFn = default_now, reap: bool = True) -> PreflightResult:
    root = root or resolve_coordination_root(start)
    registry = AgentRegistry(root, now_fn=now_fn, start=start)
    lm = LeaseManager(root, now_fn=now_fn, start=start)
    tracker = BaselineTracker(now_fn=now_fn)
    clog = ConflictLog(root, now_fn=now_fn)

    ident = resolve_identity(registry, agent_id=agent_id, token=token,
                             session_id=session_id)
    if ident is None:
        return PreflightResult(
            "deny", NotRegistered.exit_code,
            "no registered agent identity; run: "
            "python -m tools.supervisor.coordination register --provider <p>")
    aid, tok = ident

    wt_id, wt_path = worktree_identity(start)
    try:
        key, display = canonical_resource(resource, wt_path)
    except ResourceEscape as exc:
        return PreflightResult("deny", exc.exit_code, str(exc), agent_id=aid)

    conn = connect(root)
    try:
        with immediate(conn):
            try:
                agent = registry.authenticate(conn, aid, tok)
            except NotRegistered as exc:
                return PreflightResult("deny", exc.exit_code, str(exc),
                                       agent_id=aid)
            now = now_fn()
            conn.execute(
                "UPDATE agents SET last_heartbeat=?, status='ACTIVE'"
                " WHERE agent_id=?", (now, aid))
            if reap:
                lm.reap(conn)

            scope = "global" if is_logical(key) else wt_id
            own = lm.find_covering(conn, aid, key, scope, write_capable=True)

            if own is None:
                foreign = [o for o in lm._overlapping_live(
                    conn, key, scope, exclude_agent=aid)
                    if o["mode"] in ("EXCLUSIVE_WRITE", "SRSW", "APPEND")]
                if foreign:
                    holder = foreign[0]
                    cid = clog.record(
                        conn, resource_key=key, resource_display=display,
                        detected_by=aid, conflict_type="lease-denied",
                        apparent_owner=holder["agent_id"],
                        related_tasks=[t for t in (agent["task_id"],
                                                   holder["task_id"]) if t],
                        attempted_op=op,
                        safe_action="wait-for-release-or-takeover")
                    return PreflightResult(
                        "deny", 2,
                        f"'{display}' is held by {holder['agent_id']}"
                        f" (lease {holder['lease_id']}, task"
                        f" {holder['task_id'] or '-'}); wait for release or"
                        " use a governed takeover if it goes stale",
                        agent_id=aid, lease_id=holder["lease_id"],
                        conflict_id=cid)
                lease = lm.auto_claim(conn, agent, resource)
                tracker.capture(conn, lease["lease_id"], [(key, display)],
                                wt_path)
                return PreflightResult(
                    "allow", 0, "auto-claimed", agent_id=aid,
                    lease_id=lease["lease_id"], auto_claimed=True,
                    classification=NO_BASELINE)

            # Own covering lease: recover STALE, renew, then attribute.
            conn.execute(
                "UPDATE leases SET last_renewed_at=?, status='ACTIVE'"
                " WHERE lease_id=?", (now, own["lease_id"]))
            classification, detail = tracker.classify_change(
                conn, aid, own["lease_id"], key, wt_path)
            if classification == NO_BASELINE:
                tracker.capture(conn, own["lease_id"], [(key, display)],
                                wt_path)
                return PreflightResult(
                    "allow", 0, "baseline captured on first touch",
                    agent_id=aid, lease_id=own["lease_id"],
                    classification=classification, detail=detail)
            if classification in WRITE_OK:
                return PreflightResult(
                    "allow", 0, classification.lower(), agent_id=aid,
                    lease_id=own["lease_id"], classification=classification,
                    detail=detail)

            ctype = ("unknown-change" if classification == "UNKNOWN"
                     else "baseline-drift")
            cid = clog.record(
                conn, resource_key=key, resource_display=display,
                detected_by=aid, conflict_type=ctype,
                apparent_owner=detail.get("apparent_owner"),
                related_tasks=[t for t in (agent["task_id"],) if t],
                baseline_sha256=detail.get("baseline_sha256"),
                current_sha256=detail.get("current_sha256"),
                attempted_op=op, classification=classification,
                safe_action="preserve-and-rebaseline")
            emit_event(conn, "lease", own["lease_id"], "WRITE_REFUSED",
                       actor=aid, detail={"file": key,
                                          "classification": classification},
                       now_fn=now_fn)
            return PreflightResult(
                "deny", 5,
                f"'{display}' changed underneath the lease"
                f" ({classification}); refusing to overwrite. Review the"
                " current content, then 'conflicts resolve' and"
                " 'renew --rebaseline' to proceed deliberately",
                agent_id=aid, lease_id=own["lease_id"],
                classification=classification, conflict_id=cid,
                detail=detail)
    finally:
        conn.close()


def record_write(resource: str, op: str = "edit", *, root: Path | None = None,
                 start: str | Path | None = None, agent_id: str | None = None,
                 token: str | None = None, session_id: str | None = None,
                 source: str = "cli",
                 now_fn: NowFn = default_now) -> dict | None:
    """Journal a completed write (PostToolUse hook / adapter step).
    Returns the journal payload or None when identity/lease is unavailable
    (never raises on the post-write path -- attribution then degrades to
    UNKNOWN->preserve, the safe direction)."""
    root = root or resolve_coordination_root(start)
    registry = AgentRegistry(root, now_fn=now_fn, start=start)
    ident = resolve_identity(registry, agent_id=agent_id, token=token,
                             session_id=session_id)
    if ident is None:
        return None
    aid, tok = ident
    wt_id, wt_path = worktree_identity(start)
    try:
        key, display = canonical_resource(resource, wt_path)
    except ResourceEscape:
        return None
    lm = LeaseManager(root, now_fn=now_fn, start=start)
    tracker = BaselineTracker(now_fn=now_fn)
    conn = connect(root)
    try:
        with immediate(conn):
            try:
                registry.authenticate(conn, aid, tok)
            except NotRegistered:
                return None
            scope = "global" if is_logical(key) else wt_id
            own = lm.find_covering(conn, aid, key, scope, write_capable=True)
            post = sha256_file(Path(wt_path) / display)
            base = None
            if own is not None:
                b = tracker.get_baseline(conn, own["lease_id"], key)
                base = b["baseline_sha256"] if b is not None else None
            tracker.journal(conn, aid, own["lease_id"] if own else None,
                            key, op, base, post, source=source)
            return {"agent_id": aid, "file_key": key, "post_sha256": post,
                    "lease_id": own["lease_id"] if own else None}
    finally:
        conn.close()
