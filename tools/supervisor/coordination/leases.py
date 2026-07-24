"""Atomic resource leases (TC-COORD-003).

Guarantees:
- claim() is all-or-nothing inside BEGIN IMMEDIATE; the partial unique index
  idx_lease_exclusive is the race-proof net under the overlap check pass.
- Parent/child overlap: a dir lease conflicts with a contained file lease and
  vice versa (ancestor/descendant key matching), unless the mode matrix says
  the modes are compatible.
- Expiry NEVER discards filesystem content. Lease expiry transitions through
  a recoverable STALE state; only an explicit governed takeover (with reason,
  audited) transfers ownership, and the successor must recapture baselines.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .db import (NowFn, connect, default_now, emit_event, expired_predicate,
                 immediate)
from .errors import LeaseConflict, LeaseStale, TakeoverDenied
from .ids import new_lease_id, pid_alive
from .registry import AgentRegistry
from .root import (ancestor_keys, canonical_resource, is_logical,
                   resolve_coordination_root, worktree_identity)

LIVE = ("ACTIVE", "STALE")
DEFAULT_TTL_EXPLICIT = 3600
DEFAULT_TTL_AUTO = 1800

# Mode compatibility: True = the pair CONFLICTS.
_WRITE_MODES = {"EXCLUSIVE_WRITE", "SRSW"}


def modes_conflict(a: str, b: str) -> bool:
    if a == "OBSERVE" or b == "OBSERVE":
        return False
    if a == "APPEND" and b == "APPEND":
        return False
    # APPEND vs write-modes, and write-modes vs anything non-OBSERVE conflict.
    return a in _WRITE_MODES or b in _WRITE_MODES


# Strength order for own-lease reuse: a lease covers a request only when its
# mode grants at least the requested access.
_MODE_RANK = {"OBSERVE": 0, "APPEND": 1, "SRSW": 2, "EXCLUSIVE_WRITE": 3}


def mode_covers(own_mode: str, requested: str) -> bool:
    return _MODE_RANK.get(own_mode, -1) >= _MODE_RANK.get(requested, 99)


def _resource_type(resource: str, key: str, worktree_path: str) -> str:
    if key.startswith("logical:"):
        return "logical"
    if key.startswith("cmd:"):
        return "command"
    if (Path(worktree_path) / key).is_dir():
        return "dir"
    return "file"


class LeaseManager:
    def __init__(self, root: Path | None = None, now_fn: NowFn = default_now,
                 start: str | Path | None = None):
        self.root = root or resolve_coordination_root(start)
        self.now_fn = now_fn
        self.start = start
        self.registry = AgentRegistry(self.root, now_fn=now_fn, start=start)

    # -- overlap query --------------------------------------------------------
    def _overlapping_live(self, conn: sqlite3.Connection, key: str,
                          worktree_id: str,
                          exclude_agent: str | None = None) -> list[sqlite3.Row]:
        """Live leases whose resource overlaps `key` in this worktree scope:
        exact match, ancestor dir lease, or descendant lease under a dir key."""
        ancestors = ancestor_keys(key) if not is_logical(key) else []
        placeholders = ",".join("?" for _ in ([key] + ancestors))
        sql = (
            "SELECT * FROM leases WHERE worktree_id=? AND status IN ('ACTIVE','STALE')"
            f" AND (resource_key IN ({placeholders})"
            "      OR resource_key LIKE ? ESCAPE '\\')"
        )
        like = _like_prefix(key) + "/%"
        params: list = [worktree_id, key, *ancestors, like]
        if exclude_agent:
            sql += " AND agent_id != ?"
            params.append(exclude_agent)
        return conn.execute(sql, params).fetchall()

    def find_covering(self, conn: sqlite3.Connection, agent_id: str, key: str,
                      worktree_id: str,
                      write_capable: bool = True) -> sqlite3.Row | None:
        """This agent's live lease covering `key` (exact or ancestor dir)."""
        ancestors = ancestor_keys(key) if not is_logical(key) else []
        placeholders = ",".join("?" for _ in ([key] + ancestors))
        sql = (
            "SELECT * FROM leases WHERE agent_id=? AND worktree_id=? AND "
            "status IN ('ACTIVE','STALE') AND resource_key IN "
            f"({placeholders})"
        )
        params: list = [agent_id, worktree_id, key, *ancestors]
        if write_capable:
            sql += " AND mode IN ('EXCLUSIVE_WRITE','SRSW','APPEND')"
        sql += " ORDER BY length(resource_key) DESC"
        return conn.execute(sql, params).fetchone()

    # -- claim ------------------------------------------------------------------
    def claim(self, agent_id: str, token: str, resources: list[str], *,
              mode: str = "EXCLUSIVE_WRITE", intended_ops: list[str] | None = None,
              ttl_seconds: int = DEFAULT_TTL_EXPLICIT, task_id: str | None = None,
              origin: str = "explicit",
              conn: sqlite3.Connection | None = None) -> list[dict]:
        """Atomically claim all resources or none. Raises LeaseConflict."""
        own_conn = conn is None
        if own_conn:
            conn = connect(self.root)
        try:
            ctx = immediate(conn) if own_conn else _null()
            with ctx:
                agent = self.registry.authenticate(conn, agent_id, token)
                return self._claim_locked(conn, agent, resources, mode,
                                          intended_ops or [], ttl_seconds,
                                          task_id, origin)
        finally:
            if own_conn:
                conn.close()

    def _claim_locked(self, conn, agent, resources, mode, intended_ops,
                      ttl_seconds, task_id, origin) -> list[dict]:
        import json as _json

        wt_id, wt_path = worktree_identity(self.start)
        now = self.now_fn()
        acquired: list[dict] = []
        for resource in resources:
            key, display = canonical_resource(resource, wt_path)
            scope = "global" if is_logical(key) else wt_id
            # Reuse an own covering lease of a compatible-or-stronger mode.
            own = self.find_covering(conn, agent["agent_id"], key, scope,
                                     write_capable=False)
            if own is not None and mode_covers(own["mode"], mode):
                conn.execute(
                    "UPDATE leases SET last_renewed_at=?, status='ACTIVE' "
                    "WHERE lease_id=?", (now, own["lease_id"]))
                acquired.append(dict(own) | {"reused": True})
                continue
            for other in self._overlapping_live(conn, key, scope,
                                                exclude_agent=agent["agent_id"]):
                if modes_conflict(other["mode"], mode):
                    raise LeaseConflict(
                        resource_key=key,
                        holder_agent_id=other["agent_id"],
                        holder_lease_id=other["lease_id"],
                        holder_task_id=other["task_id"],
                        holder_mode=other["mode"],
                        lease_expires_hint=other["last_renewed_at"],
                    )
            lease_id = new_lease_id()
            rtype = _resource_type(resource, key, wt_path)
            try:
                conn.execute(
                    "INSERT INTO leases(lease_id, agent_id, task_id,"
                    " resource_type, resource_key, resource_display,"
                    " worktree_id, mode, origin, intended_ops, acquired_at,"
                    " last_renewed_at, ttl_seconds, status)"
                    " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,'ACTIVE')",
                    (lease_id, agent["agent_id"],
                     task_id or agent["task_id"], rtype, key, display,
                     scope, mode, origin, _json.dumps(intended_ops),
                     now, now, ttl_seconds))
            except sqlite3.IntegrityError:
                holder = conn.execute(
                    "SELECT * FROM leases WHERE worktree_id=? AND"
                    " resource_key=? AND status IN ('ACTIVE','STALE')",
                    (scope, key)).fetchone()
                raise LeaseConflict(
                    resource_key=key,
                    holder_agent_id=holder["agent_id"] if holder else "unknown",
                    holder_lease_id=holder["lease_id"] if holder else "unknown",
                    holder_mode=holder["mode"] if holder else "EXCLUSIVE_WRITE",
                ) from None
            emit_event(conn, "lease", lease_id, "CLAIM", to_status="ACTIVE",
                       actor=agent["agent_id"],
                       detail={"resource": key, "mode": mode, "origin": origin},
                       now_fn=self.now_fn)
            row = conn.execute("SELECT * FROM leases WHERE lease_id=?",
                               (lease_id,)).fetchone()
            acquired.append(dict(row) | {"reused": False})
        return acquired

    def auto_claim(self, conn: sqlite3.Connection, agent: sqlite3.Row,
                   resource: str) -> dict:
        """Ambient single-file claim used by the hook preflight. Caller holds
        the immediate transaction."""
        return self._claim_locked(conn, agent, [resource], "EXCLUSIVE_WRITE",
                                  ["edit", "create"], DEFAULT_TTL_AUTO,
                                  agent["task_id"], "auto")[0]

    # -- read-only check --------------------------------------------------------
    def check(self, resources: list[str], mode: str = "EXCLUSIVE_WRITE",
              exclude_agent: str | None = None) -> list[dict]:
        conn = connect(self.root)
        try:
            wt_id, wt_path = worktree_identity(self.start)
            conflicts = []
            for resource in resources:
                key, _ = canonical_resource(resource, wt_path)
                scope = "global" if is_logical(key) else wt_id
                for other in self._overlapping_live(conn, key, scope,
                                                    exclude_agent=exclude_agent):
                    if modes_conflict(other["mode"], mode):
                        conflicts.append({"resource_key": key,
                                          "holder": dict(other)})
            return conflicts
        finally:
            conn.close()

    # -- renew / release ---------------------------------------------------------
    def renew(self, agent_id: str, token: str,
              lease_ids: list[str] | None = None) -> int:
        conn = connect(self.root)
        try:
            with immediate(conn):
                self.registry.authenticate(conn, agent_id, token)
                sql = ("SELECT lease_id, status FROM leases WHERE agent_id=?"
                       " AND status IN ('ACTIVE','STALE')")
                params: list = [agent_id]
                if lease_ids:
                    sql += f" AND lease_id IN ({','.join('?' * len(lease_ids))})"
                    params.extend(lease_ids)
                rows = conn.execute(sql, params).fetchall()
                now = self.now_fn()
                for r in rows:
                    conn.execute(
                        "UPDATE leases SET last_renewed_at=?, status='ACTIVE'"
                        " WHERE lease_id=?", (now, r["lease_id"]))
                    if r["status"] == "STALE":
                        emit_event(conn, "lease", r["lease_id"], "RECOVER",
                                   from_status="STALE", to_status="ACTIVE",
                                   actor=agent_id, now_fn=self.now_fn)
                return len(rows)
        finally:
            conn.close()

    def release(self, agent_id: str, token: str,
                lease_ids: list[str] | None = None,
                release_all: bool = False) -> int:
        """Release OWN leases only. Foreign release requires takeover()."""
        conn = connect(self.root)
        try:
            with immediate(conn):
                self.registry.authenticate(conn, agent_id, token)
                sql = ("SELECT lease_id FROM leases WHERE agent_id=? AND"
                       " status IN ('ACTIVE','STALE')")
                params: list = [agent_id]
                if not release_all:
                    if not lease_ids:
                        return 0
                    sql += f" AND lease_id IN ({','.join('?' * len(lease_ids))})"
                    params.extend(lease_ids)
                rows = conn.execute(sql, params).fetchall()
                if lease_ids and len(rows) != len(set(lease_ids)):
                    # At least one id is not ours / not live -- refuse the lot
                    # rather than silently partial-release.
                    raise LeaseStale(
                        ",".join(sorted(set(lease_ids)
                                        - {r["lease_id"] for r in rows})),
                        "lease not owned by caller or not live")
                for r in rows:
                    conn.execute(
                        "UPDATE leases SET status='RELEASED',"
                        " status_reason='released by owner' WHERE lease_id=?",
                        (r["lease_id"],))
                    emit_event(conn, "lease", r["lease_id"], "RELEASE",
                               to_status="RELEASED", actor=agent_id,
                               now_fn=self.now_fn)
                return len(rows)
        finally:
            conn.close()

    # -- reaper -------------------------------------------------------------------
    def reap(self, conn: sqlite3.Connection | None = None) -> dict:
        """Opportunistic, piggybacked on hook/CLI calls. Two phases:
        1. registry.reap(): heartbeat-expired agents -> STALE_SUSPECT.
        2. Expired ACTIVE leases of STALE_SUSPECT owners -> STALE when the
           owner is not provably live (dead PID) or 2x TTL has elapsed.
        Never touches files; never releases; STALE stays recoverable."""
        own_conn = conn is None
        if own_conn:
            conn = connect(self.root)
        try:
            ctx = immediate(conn) if own_conn else _null()
            with ctx:
                agents_marked = self.registry.reap(conn)
                now = self.now_fn()
                pred1 = expired_predicate("l.last_renewed_at", "l.ttl_seconds")
                pred2x = expired_predicate("l.last_renewed_at",
                                           "(l.ttl_seconds * 2)")
                candidates = conn.execute(
                    "SELECT l.lease_id, l.agent_id, a.pid, "
                    f"({pred2x}) AS twice_expired "
                    "FROM leases l JOIN agents a ON a.agent_id = l.agent_id "
                    "WHERE l.status='ACTIVE' AND a.status='STALE_SUSPECT' "
                    f"AND {pred1}", (now, now)).fetchall()
                leases_marked = 0
                for c in candidates:
                    if c["twice_expired"] or not pid_alive(c["pid"]):
                        conn.execute(
                            "UPDATE leases SET status='STALE',"
                            " status_reason='owner stale' WHERE lease_id=?",
                            (c["lease_id"],))
                        emit_event(conn, "lease", c["lease_id"], "STALE",
                                   from_status="ACTIVE", to_status="STALE",
                                   detail={"owner": c["agent_id"]},
                                   now_fn=self.now_fn)
                        leases_marked += 1
                return {"agents_marked": agents_marked,
                        "leases_marked": leases_marked}
        finally:
            if own_conn:
                conn.close()

    # -- governed takeover ----------------------------------------------------------
    def takeover(self, new_agent_id: str, token: str, stale_lease_id: str,
                 reason: str) -> dict:
        """Explicit governed transfer of a STALE lease. Records who/why.
        The successor MUST recapture baselines before writing (enforced by
        preflight: a takeover lease with no baselines refuses writes)."""
        if not reason or not reason.strip():
            raise TakeoverDenied(stale_lease_id, "a non-empty --reason is required")
        conn = connect(self.root)
        try:
            with immediate(conn):
                agent = self.registry.authenticate(conn, new_agent_id, token)
                self.reap(conn)  # give expiry a chance to surface first
                lease = conn.execute(
                    "SELECT * FROM leases WHERE lease_id=?",
                    (stale_lease_id,)).fetchone()
                if lease is None:
                    raise TakeoverDenied(stale_lease_id, "no such lease")
                if lease["status"] != "STALE":
                    raise TakeoverDenied(
                        stale_lease_id,
                        f"lease is {lease['status']}, not STALE")
                owner = conn.execute(
                    "SELECT * FROM agents WHERE agent_id=?",
                    (lease["agent_id"],)).fetchone()
                if owner is not None and owner["status"] == "ACTIVE":
                    raise TakeoverDenied(stale_lease_id, "owner is ACTIVE")
                if owner is not None and pid_alive(owner["pid"]):
                    # A live PID with a matching start time blocks takeover
                    # ONLY while the silence is short (< 2x heartbeat TTL).
                    # Beyond that the process is presumed hung: the lease is
                    # already STALE, takeover is explicit+audited, and the
                    # zombie stays contained (its lease becomes TAKEN_OVER so
                    # its preflights fail; raw writes classify as
                    # OTHER_AGENT/UNKNOWN on the successor side -> preserved).
                    from .ids import pid_start_time
                    pred2x = expired_predicate("last_heartbeat",
                                               "(heartbeat_ttl_s * 2)")
                    long_silent = conn.execute(
                        f"SELECT ({pred2x}) AS x FROM agents WHERE agent_id=?",
                        (self.now_fn(), owner["agent_id"])).fetchone()["x"]
                    current_start = pid_start_time(owner["pid"])
                    provably_same = (owner["pid_started_at"] is not None
                                     and current_start is not None
                                     and current_start == owner["pid_started_at"])
                    if provably_same and not long_silent:
                        raise TakeoverDenied(
                            stale_lease_id,
                            f"owner pid {owner['pid']} is provably live and "
                            "only recently silent")
                nid = new_lease_id()
                now = self.now_fn()
                conn.execute(
                    "UPDATE leases SET status='TAKEN_OVER', superseded_by=?,"
                    " status_reason=? WHERE lease_id=?",
                    (nid, f"takeover: {reason.strip()}", stale_lease_id))
                conn.execute(
                    "INSERT INTO leases(lease_id, agent_id, task_id,"
                    " resource_type, resource_key, resource_display,"
                    " worktree_id, mode, origin, intended_ops, acquired_at,"
                    " last_renewed_at, ttl_seconds, status, takeover_of)"
                    " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,'ACTIVE',?)",
                    (nid, new_agent_id, agent["task_id"],
                     lease["resource_type"], lease["resource_key"],
                     lease["resource_display"], lease["worktree_id"],
                     lease["mode"], "takeover", lease["intended_ops"],
                     now, now, DEFAULT_TTL_EXPLICIT, stale_lease_id))
                emit_event(conn, "takeover", nid, "TAKEOVER",
                           from_status="STALE", to_status="ACTIVE",
                           actor=new_agent_id,
                           detail={"of_lease": stale_lease_id,
                                   "previous_owner": lease["agent_id"],
                                   "reason": reason.strip()},
                           now_fn=self.now_fn)
                row = conn.execute("SELECT * FROM leases WHERE lease_id=?",
                                   (nid,)).fetchone()
                return dict(row)
        finally:
            conn.close()

    # -- queries for choke points -----------------------------------------------------
    def foreign_live_leases_for_keys(self, keys: list[str],
                                     exclude_agent: str | None) -> list[dict]:
        conn = connect(self.root)
        try:
            wt_id, _ = worktree_identity(self.start)
            hits: list[dict] = []
            for key in keys:
                for other in self._overlapping_live(conn, key, wt_id,
                                                    exclude_agent=exclude_agent):
                    if other["mode"] in _WRITE_MODES or other["mode"] == "APPEND":
                        hits.append({"resource_key": key, "holder": dict(other)})
            return hits
        finally:
            conn.close()


def _like_prefix(key: str) -> str:
    return key.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@contextmanager
def _null():
    yield
