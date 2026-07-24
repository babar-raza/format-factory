"""Bridge from the legacy concurrency package to the coordination plane.

Mission AGENT-COORD-2026-07-15 (TC-COORD-008), subsuming
CONC-HARDENING-2026-07-02.

Why a bridge and not a rewrite: the legacy WorkerClaims/MissionLock tables
and 42 tests are correct for headless-vs-headless arbitration, but they are
invisible to interactive agents. The coordination DB (see
tools/supervisor/coordination/) is the shared plane every population sees.
This bridge makes every legacy claim/lock ALSO exist as a coordination
lease, and makes legacy acquisition FAIL when an interactive agent already
holds an overlapping coordination lease. The legacy tables remain as a
projection for legacy callers; the coordination DB is the conflict
authority across populations. Full delegation (dropping the legacy tables)
is registered follow-up work, not silently pretended.

All infrastructure errors here are best-effort (warn, proceed) -- but
CONFLICTS always raise. Preservation-over-availability applies to files;
availability-over-perfection applies to bookkeeping.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

_MODE_MAP = {"WRITE": "EXCLUSIVE_WRITE", "READ": "OBSERVE",
             "INTEGRATE": "APPEND"}


def _coordination():
    """Lazy import of the coordination package in both sys.path contexts."""
    try:
        from coordination.errors import LeaseConflict
        from coordination.leases import LeaseManager
        from coordination.registry import AgentRegistry
        from coordination.root import resolve_coordination_root
        return AgentRegistry, LeaseManager, LeaseConflict, resolve_coordination_root
    except ImportError:
        supervisor_dir = Path(__file__).resolve().parents[1]
        if str(supervisor_dir) not in sys.path:
            sys.path.insert(0, str(supervisor_dir))
        try:
            from coordination.errors import LeaseConflict
            from coordination.leases import LeaseManager
            from coordination.registry import AgentRegistry
            from coordination.root import resolve_coordination_root
            return (AgentRegistry, LeaseManager, LeaseConflict,
                    resolve_coordination_root)
        except ImportError:
            return None


def _safe(worker_id: str) -> str:
    return "".join(c for c in worker_id if c.isalnum() or c in "-_")[:60]


def bridge_agent(worker_id: str):
    """(registry, lease_manager, agent_id, token, LeaseConflict) or None.
    Reuses a per-worker alias identity across processes via a runtime file."""
    import json

    coord = _coordination()
    if coord is None:
        return None
    AgentRegistry, LeaseManager, LeaseConflict, resolve_root = coord
    try:
        root = resolve_root()
        registry = AgentRegistry(root)
        lm = LeaseManager(root)
        alias_dir = root / "runtime" / "by-worker"
        alias_dir.mkdir(parents=True, exist_ok=True)
        alias_file = alias_dir / f"{_safe(worker_id)}.json"
        if alias_file.exists():
            try:
                data = json.loads(alias_file.read_text(encoding="utf-8"))
                from coordination.db import connect
                conn = connect(root)
                try:
                    registry.authenticate(conn, data["agent_id"],
                                          data["token"])
                    return registry, lm, data["agent_id"], data["token"], \
                        LeaseConflict
                finally:
                    conn.close()
            except Exception:
                pass  # stale/terminal alias: re-register below
        ra = registry.register("legacy-bridge", agent_type="headless",
                               execution_mode="headless",
                               task_id=f"worker:{worker_id}")
        alias_file.write_text(json.dumps(
            {"agent_id": ra.agent_id, "token": ra.token,
             "worker_id": worker_id}), encoding="utf-8")
        return registry, lm, ra.agent_id, ra.token, LeaseConflict
    except Exception as exc:
        warnings.warn(f"[coordination-bridge] unavailable: {exc}",
                      stacklevel=2)
        return None


def mirror_claim(worker_id: str, task_id: str, paths: list[str],
                 mode: str = "WRITE") -> list[str] | None:
    """Mirror a legacy claim into the coordination plane.

    Returns lease_ids, or None when the plane is unavailable (best-effort).
    Raises coordination LeaseConflict for the caller to translate.
    """
    bridge = bridge_agent(worker_id)
    if bridge is None:
        return None
    registry, lm, aid, tok, LeaseConflict = bridge
    lease_mode = _MODE_MAP.get(mode, "EXCLUSIVE_WRITE")
    acquired: list[str] = []
    from coordination.errors import ResourceEscape
    for path in paths:
        try:
            leases = lm.claim(aid, tok, [path], mode=lease_mode,
                              intended_ops=["edit"], task_id=task_id)
            acquired.extend(l["lease_id"] for l in leases)
        except ResourceEscape:
            warnings.warn(
                f"[coordination-bridge] path outside worktree not mirrored:"
                f" {path}", stacklevel=2)
        except LeaseConflict:
            if acquired:
                try:
                    lm.release(aid, tok, acquired)
                except Exception:
                    pass
            raise
    return acquired


def mirror_release(worker_id: str) -> None:
    bridge = bridge_agent(worker_id)
    if bridge is None:
        return
    _registry, lm, aid, tok, _LC = bridge
    try:
        lm.release(aid, tok, release_all=True)
    except Exception as exc:
        warnings.warn(f"[coordination-bridge] release failed: {exc}",
                      stacklevel=2)


def mirror_claim_logical(worker_id: str, task_id: str,
                         logical: str) -> list[str] | None:
    """Claim a logical resource (e.g. logical:mission:<id>) in the plane."""
    bridge = bridge_agent(worker_id)
    if bridge is None:
        return None
    _registry, lm, aid, tok, _LC = bridge
    leases = lm.claim(aid, tok, [logical], mode="EXCLUSIVE_WRITE",
                      intended_ops=["edit"], task_id=task_id)
    return [l["lease_id"] for l in leases]


def mirror_renew(worker_id: str) -> None:
    bridge = bridge_agent(worker_id)
    if bridge is None:
        return
    registry, lm, aid, tok, _LC = bridge
    try:
        registry.heartbeat(aid, tok)
        lm.renew(aid, tok)
    except Exception:
        pass


def lease_conflict_type():
    coord = _coordination()
    return coord[2] if coord else None


def resolve_owner_display(holder_agent_id: str) -> str:
    """Human-recognizable owner for conflict messages: legacy-bridge alias
    agents resolve back to their worker_id; everyone else keeps agent_id."""
    coord = _coordination()
    if coord is None:
        return holder_agent_id
    _AgentRegistry, _LM, _LC, resolve_root = coord
    try:
        from coordination.db import connect
        conn = connect(resolve_root())
        try:
            row = conn.execute(
                "SELECT provider, task_id FROM agents WHERE agent_id=?",
                (holder_agent_id,)).fetchone()
        finally:
            conn.close()
        if (row is not None and row["provider"] == "legacy-bridge"
                and (row["task_id"] or "").startswith("worker:")):
            return row["task_id"][len("worker:"):]
    except Exception:
        pass
    return holder_agent_id
