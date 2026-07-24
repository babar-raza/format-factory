"""Agent identity and registration (TC-COORD-002).

Identity = (agent_id, secret token). Token hash is stored; the raw token
lives only in runtime token files under <root>/runtime/ so it survives
across tool calls without env-var ceremony (structural weakness W2 fix).
Interactive Claude agents are additionally bound to their harness
session_id, which the hook plane receives on stdin -- registration and
heartbeat then require zero agent discipline (design principle P1).
"""
from __future__ import annotations

import json
import os
import socket
import sqlite3
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from . import PROTOCOL_VERSION
from .db import (NowFn, connect, default_now, emit_event, ensure_db,
                 expired_predicate, immediate)
from .errors import NotRegistered
from .ids import new_agent_id, new_token, pid_start_time, token_hash
from .root import (repo_identity, resolve_coordination_root,
                   worktree_identity)

LIVE_STATUSES = ("ACTIVE", "IDLE", "STALE_SUSPECT")
DEFAULT_TTL = {"interactive": 1800, "headless": 90, "ci": 300}


@dataclass
class RegisteredAgent:
    agent_id: str
    token: str
    resumed: bool


def _atomic_write_json(path: Path, data: dict) -> None:
    """Same-dir temp + os.replace (NTFS-atomic). Local copy of the atomic_io
    pattern: this package is imported both as `coordination` (tests, via the
    tools/supervisor sys.path convention) and as `tools.supervisor.coordination`
    (CLI), so parent-relative imports of atomic_io are not reliable."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


class AgentRegistry:
    def __init__(self, root: Path | None = None, now_fn: NowFn = default_now,
                 start: str | Path | None = None):
        self.root = root or resolve_coordination_root(start)
        self.now_fn = now_fn
        self.start = start

    # -- runtime token files -------------------------------------------------
    def runtime_file(self, agent_id: str) -> Path:
        return self.root / "runtime" / f"{agent_id}.json"

    def session_file(self, session_id: str) -> Path:
        safe = "".join(c for c in session_id if c.isalnum() or c in "-_")[:80]
        return self.root / "runtime" / "by-session" / f"{safe}.json"

    def write_runtime_identity(self, agent_id: str, token: str,
                               session_id: str | None) -> None:
        payload = {"agent_id": agent_id, "token": token,
                   "protocol_version": PROTOCOL_VERSION,
                   "written_at": self.now_fn()}
        _atomic_write_json(self.runtime_file(agent_id), payload)
        if session_id:
            _atomic_write_json(self.session_file(session_id), payload)

    def read_runtime_identity(self, *, agent_id: str | None = None,
                              session_id: str | None = None) -> dict | None:
        path = None
        if agent_id:
            path = self.runtime_file(agent_id)
        elif session_id:
            path = self.session_file(session_id)
        if path is None or not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or "agent_id" not in data:
                return None
            return data
        except (OSError, ValueError):
            return None

    # -- registration --------------------------------------------------------
    def register(self, provider: str, *, agent_type: str = "interactive",
                 execution_mode: str = "interactive",
                 session_id: str | None = None, task_id: str | None = None,
                 plan_authority: str | None = None,
                 declared_scope: tuple[str, ...] | list[str] = (),
                 heartbeat_ttl_s: int | None = None) -> RegisteredAgent:
        ensure_db(self.root)
        ttl = heartbeat_ttl_s or DEFAULT_TTL.get(execution_mode, 1800)
        wt_id, wt_path = worktree_identity(self.start)
        now = self.now_fn()
        conn = connect(self.root)
        try:
            with immediate(conn):
                if session_id:
                    row = conn.execute(
                        "SELECT * FROM agents WHERE claude_session_id=? AND "
                        f"status IN {LIVE_STATUSES}", (session_id,)).fetchone()
                    if row is not None:
                        # Resume: rotate token (runtime file may be lost),
                        # refresh liveness fields.
                        token = new_token()
                        conn.execute(
                            "UPDATE agents SET agent_token_hash=?, pid=?, "
                            "last_heartbeat=?, status='ACTIVE', "
                            "status_reason='resumed' WHERE agent_id=?",
                            (token_hash(token), os.getpid(), now,
                             row["agent_id"]))
                        emit_event(conn, "agent", row["agent_id"], "RESUME",
                                   from_status=row["status"], to_status="ACTIVE",
                                   actor=row["agent_id"], now_fn=self.now_fn)
                        agent_id = row["agent_id"]
                        resumed = True
                    else:
                        agent_id, token = self._insert(
                            conn, provider, agent_type, execution_mode,
                            session_id, task_id, plan_authority,
                            declared_scope, ttl, wt_id, wt_path, now)
                        resumed = False
                else:
                    agent_id, token = self._insert(
                        conn, provider, agent_type, execution_mode,
                        None, task_id, plan_authority, declared_scope,
                        ttl, wt_id, wt_path, now)
                    resumed = False
        finally:
            conn.close()
        self.write_runtime_identity(agent_id, token, session_id)
        return RegisteredAgent(agent_id=agent_id, token=token, resumed=resumed)

    def _insert(self, conn, provider, agent_type, execution_mode, session_id,
                task_id, plan_authority, declared_scope, ttl, wt_id, wt_path,
                now) -> tuple[str, str]:
        agent_id = new_agent_id(provider)
        token = new_token()
        pid = os.getpid()
        conn.execute(
            "INSERT INTO agents(agent_id, agent_token_hash, provider,"
            " agent_type, execution_mode, claude_session_id, pid,"
            " pid_started_at, hostname, repo_identity, worktree_id,"
            " worktree_path, task_id, plan_authority, declared_scope,"
            " protocol_version, started_at, last_heartbeat, heartbeat_ttl_s,"
            " status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'ACTIVE')",
            (agent_id, token_hash(token), provider, agent_type,
             execution_mode, session_id, pid, pid_start_time(pid),
             socket.gethostname(), repo_identity(self.start), wt_id, wt_path,
             task_id, plan_authority, json.dumps(list(declared_scope)),
             PROTOCOL_VERSION, now, now, ttl))
        emit_event(conn, "agent", agent_id, "REGISTER", to_status="ACTIVE",
                   actor=agent_id,
                   detail={"provider": provider, "session_id": session_id,
                           "task_id": task_id},
                   now_fn=self.now_fn)
        return agent_id, token

    # -- authentication / heartbeat ------------------------------------------
    def authenticate(self, conn: sqlite3.Connection, agent_id: str,
                     token: str) -> sqlite3.Row:
        row = conn.execute(
            "SELECT * FROM agents WHERE agent_id=?", (agent_id,)).fetchone()
        if row is None:
            raise NotRegistered(f"unknown agent: {agent_id}")
        if row["agent_token_hash"] != token_hash(token):
            raise NotRegistered(f"bad token for agent: {agent_id}")
        if row["status"] not in LIVE_STATUSES:
            raise NotRegistered(
                f"agent {agent_id} is terminal ({row['status']})")
        return row

    def get_by_session(self, session_id: str) -> sqlite3.Row | None:
        conn = connect(self.root)
        try:
            return conn.execute(
                "SELECT * FROM agents WHERE claude_session_id=? AND "
                f"status IN {LIVE_STATUSES}", (session_id,)).fetchone()
        finally:
            conn.close()

    def heartbeat(self, agent_id: str, token: str) -> str:
        """Refresh liveness; resurrect STALE_SUSPECT. Returns new status."""
        conn = connect(self.root)
        try:
            with immediate(conn):
                row = self.authenticate(conn, agent_id, token)
                new_status = "ACTIVE"
                conn.execute(
                    "UPDATE agents SET last_heartbeat=?, status=? "
                    "WHERE agent_id=?", (self.now_fn(), new_status, agent_id))
                if row["status"] == "STALE_SUSPECT":
                    emit_event(conn, "agent", agent_id, "RESURRECT",
                               from_status="STALE_SUSPECT", to_status="ACTIVE",
                               actor=agent_id, now_fn=self.now_fn)
                return new_status
        finally:
            conn.close()

    def set_task(self, agent_id: str, token: str, task_id: str | None,
                 plan_authority: str | None = None) -> None:
        conn = connect(self.root)
        try:
            with immediate(conn):
                self.authenticate(conn, agent_id, token)
                conn.execute(
                    "UPDATE agents SET task_id=?, plan_authority="
                    "COALESCE(?, plan_authority) WHERE agent_id=?",
                    (task_id, plan_authority, agent_id))
        finally:
            conn.close()

    # -- lifecycle end -------------------------------------------------------
    def _finish(self, agent_id: str, token: str, terminal: str,
                reason: str | None, release_origin: str | None) -> int:
        """Common complete/abandon path. Returns released lease count."""
        conn = connect(self.root)
        try:
            with immediate(conn):
                row = self.authenticate(conn, agent_id, token)
                where = ("agent_id=? AND status IN ('ACTIVE','STALE')")
                params: list = [agent_id]
                if release_origin:
                    where += " AND origin=?"
                    params.append(release_origin)
                leases = conn.execute(
                    f"SELECT lease_id FROM leases WHERE {where}",
                    params).fetchall()
                now = self.now_fn()
                for lr in leases:
                    conn.execute(
                        "UPDATE leases SET status='RELEASED', status_reason=?"
                        " WHERE lease_id=?", (f"agent {terminal.lower()}",
                                              lr["lease_id"]))
                    emit_event(conn, "lease", lr["lease_id"], "RELEASE",
                               to_status="RELEASED", actor=agent_id,
                               detail={"cause": terminal}, now_fn=self.now_fn)
                conn.execute(
                    "UPDATE agents SET status=?, status_reason=?, "
                    "last_heartbeat=? WHERE agent_id=?",
                    (terminal, reason, now, agent_id))
                emit_event(conn, "agent", agent_id, terminal,
                           from_status=row["status"], to_status=terminal,
                           actor=agent_id, detail={"reason": reason},
                           now_fn=self.now_fn)
                return len(leases)
        finally:
            conn.close()

    def complete(self, agent_id: str, token: str,
                 reason: str | None = None) -> int:
        return self._finish(agent_id, token, "COMPLETED", reason, None)

    def abandon(self, agent_id: str, token: str, reason: str) -> int:
        return self._finish(agent_id, token, "ABANDONED", reason, None)

    def idle(self, agent_id: str, token: str) -> int:
        """Session ended normally: release AUTO leases, keep explicit ones,
        mark IDLE (recoverable; reaper handles the rest)."""
        conn = connect(self.root)
        try:
            with immediate(conn):
                self.authenticate(conn, agent_id, token)
                leases = conn.execute(
                    "SELECT lease_id FROM leases WHERE agent_id=? AND "
                    "origin='auto' AND status IN ('ACTIVE','STALE')",
                    (agent_id,)).fetchall()
                for lr in leases:
                    conn.execute(
                        "UPDATE leases SET status='RELEASED', "
                        "status_reason='session end' WHERE lease_id=?",
                        (lr["lease_id"],))
                    emit_event(conn, "lease", lr["lease_id"], "RELEASE",
                               to_status="RELEASED", actor=agent_id,
                               detail={"cause": "SESSION_END"},
                               now_fn=self.now_fn)
                conn.execute(
                    "UPDATE agents SET status='IDLE', last_heartbeat=? "
                    "WHERE agent_id=?", (self.now_fn(), agent_id))
                return len(leases)
        finally:
            conn.close()

    # -- reaper ---------------------------------------------------------------
    def reap(self, conn: sqlite3.Connection | None = None) -> int:
        """Heartbeat-expired live agents -> STALE_SUSPECT (recoverable)."""
        own = conn is None
        if own:
            conn = connect(self.root)
        try:
            pred = expired_predicate("last_heartbeat", "heartbeat_ttl_s")
            now = self.now_fn()
            ctx = immediate(conn) if own else _null_ctx()
            with ctx:
                rows = conn.execute(
                    "SELECT agent_id, status FROM agents WHERE status IN "
                    f"('ACTIVE','IDLE') AND {pred}", (now,)).fetchall()
                for r in rows:
                    conn.execute(
                        "UPDATE agents SET status='STALE_SUSPECT', "
                        "status_reason='heartbeat expired' WHERE agent_id=?",
                        (r["agent_id"],))
                    emit_event(conn, "agent", r["agent_id"], "STALE_SUSPECT",
                               from_status=r["status"],
                               to_status="STALE_SUSPECT",
                               detail={"as_of": now}, now_fn=self.now_fn)
                return len(rows)
        finally:
            if own:
                conn.close()


@contextmanager
def _null_ctx():
    yield
