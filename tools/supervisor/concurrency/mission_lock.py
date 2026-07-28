"""SQLite-backed mission controller lock with heartbeat and PID liveness.

Provides machine-enforced enforcement of the One-Mechanism Lock rule:
only one controller (headless or interactive) may operate on a given
mission at a time.

Usage:
    from tools.supervisor.concurrency.mission_lock import MissionLock

    db = Path(".local/supervisor/control-index.db")
    lock = MissionLock(db_path=db)

    with lock.locked("format-factory-main", "headless", session_id, branch) as lock_id:
        # only one process reaches here per mission
        do_work()

Mission: CONC-HARDENING-2026-07-02
"""
from __future__ import annotations

import os
import secrets
import socket
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

from .errors import LockNotHeld, MissionLockConflict

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_LEASE_SECONDS: int = 300        # 5 minutes
DEFAULT_HEARTBEAT_INTERVAL: int = 10    # seconds between heartbeat updates
DEFAULT_HEARTBEAT_TTL: int = 30         # seconds before heartbeat considered stale


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _iso_plus(seconds: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()


def _pid_alive(pid: int) -> bool:
    """Check if a process with the given PID is running."""
    try:
        import psutil  # type: ignore[import]
        return psutil.pid_exists(pid)
    except ImportError:
        pass
    # Fallback: send signal 0 (no-op signal, just checks existence)
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError, PermissionError):
        # OSError(ESRCH) = no such process
        # PermissionError = process exists but not owned (treat as alive)
        import errno
        try:
            os.kill(pid, 0)
        except PermissionError:
            return True  # Process exists, different user
        except OSError as e:
            return e.errno != getattr(__import__('errno'), 'ESRCH', 3)
        return False


def _log_transition(
    conn,
    entity_type: str,
    entity_id: str,
    from_status: str | None,
    to_status: str,
    actor: str,
    reason: str | None = None,
) -> None:
    """Append an immutable row to concurrency_transitions."""
    conn.execute(
        """
        INSERT INTO concurrency_transitions
        (entity_type, entity_id, from_status, to_status, actor, reason, occurred_at)
        VALUES (?,?,?,?,?,?,?)
        """,
        (entity_type, entity_id, from_status, to_status, actor, reason, _now_iso()),
    )


def _import_db_funcs():
    """Import db functions, supporting both repo-root and tools/supervisor sys.path contexts."""
    try:
        from control_index.db import ensure_db, connect  # supervisor/ on sys.path
        return ensure_db, connect
    except ImportError:
        pass
    import sys
    _repo = Path(__file__).resolve().parents[3]
    if str(_repo) not in sys.path:
        sys.path.insert(0, str(_repo))
    from tools.supervisor.control_index.db import ensure_db, connect  # repo root on sys.path
    return ensure_db, connect


def _get_db_connection(db_path: Path):
    """Return a live connection using the control_index db module."""
    ensure_db, _ = _import_db_funcs()
    return ensure_db(db_path)


# ---------------------------------------------------------------------------
# MissionLock
# ---------------------------------------------------------------------------

class MissionLock:
    """SQLite-backed mission controller lock with heartbeat and PID liveness.

    Parameters
    ----------
    db_path:
        Path to .local/supervisor/control-index.db
    lease_seconds:
        How long each heartbeat extends the lease (default: 300s)
    heartbeat_ttl:
        Seconds before a missing heartbeat marks the lock stealable (default: 30s)
    """

    def __init__(
        self,
        db_path: Path,
        *,
        lease_seconds: int | None = None,
        heartbeat_ttl: int | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.lease_seconds = lease_seconds if lease_seconds is not None else DEFAULT_LEASE_SECONDS
        self.heartbeat_ttl = heartbeat_ttl if heartbeat_ttl is not None else DEFAULT_HEARTBEAT_TTL
        # Ensure DB + schema exists (idempotent)
        ensure_db, _ = _import_db_funcs()
        ensure_db(self.db_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @contextmanager
    def locked(
        self,
        mission_id: str,
        controller_type: str,
        session_id: str,
        branch: str,
        plan_version: str | None = None,
    ) -> Iterator[str]:
        """Context manager: acquire lock → yield lock_id → release on exit.

        Raises MissionLockConflict if another live controller holds the lock.

        Usage:
            with MissionLock(db).locked("format-factory-main", "headless",
                                        session_id, branch) as lock_id:
                ...
        """
        # TC-COORD-008: mirror the mission lock into the coordination plane
        # FIRST so interactive agents can see (and be blocked by) the
        # controller, and so a coordination-side holder blocks this one.
        from . import coordination_bridge as _bridge
        _bridge_worker = f"mission-{controller_type}-{session_id}"
        _lc_type = _bridge.lease_conflict_type()
        _mirrored = False
        try:
            _mirrored = _bridge.mirror_claim_logical(
                _bridge_worker, mission_id,
                f"logical:mission:{mission_id}") is not None
        except Exception as _exc:
            if _lc_type is not None and isinstance(_exc, _lc_type):
                raise MissionLockConflict(
                    mission_id=mission_id,
                    existing_lock_id=_exc.holder_lease_id,
                    existing_controller=_bridge.resolve_owner_display(
                        _exc.holder_agent_id),
                    existing_pid=0,
                    heartbeat_at=_exc.lease_expires_hint or "unknown",
                ) from _exc
            import warnings as _warnings
            _warnings.warn(f"[mission-lock] coordination mirror failed:"
                           f" {_exc}", stacklevel=2)

        try:
            lock_id = self._acquire(
                mission_id=mission_id,
                controller_type=controller_type,
                session_id=session_id,
                branch=branch,
                plan_version=plan_version,
            )
        except Exception:
            if _mirrored:
                _bridge.mirror_release(_bridge_worker)
            raise
        self._bridge_worker = _bridge_worker
        hb_stop = threading.Event()
        hb_thread = self._start_heartbeat_thread(lock_id, hb_stop)
        hb_thread.start()
        try:
            yield lock_id
        finally:
            hb_stop.set()
            hb_thread.join(timeout=5)
            self._release(lock_id)
            if _mirrored:
                _bridge.mirror_release(_bridge_worker)
            self._bridge_worker = None

    def get_active_lock(self, mission_id: str) -> dict | None:
        """Return the current ACTIVE lock for a mission, or None."""
        conn = _get_db_connection(self.db_path)
        try:
            row = conn.execute(
                "SELECT * FROM mission_locks WHERE mission_id=? AND status='ACTIVE'",
                (mission_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def is_owner_alive(self, lock_id: str) -> bool:
        """True if the lock owner's PID is running AND heartbeat is fresh."""
        conn = _get_db_connection(self.db_path)
        try:
            row = conn.execute(
                "SELECT * FROM mission_locks WHERE lock_id=?",
                (lock_id,),
            ).fetchone()
            if not row:
                return False
            return self._check_owner_alive(dict(row))
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Private implementation
    # ------------------------------------------------------------------

    def _acquire(
        self,
        mission_id: str,
        controller_type: str,
        session_id: str,
        branch: str,
        plan_version: str | None,
    ) -> str:
        """Atomic acquire. Steals lock only if PID is dead AND heartbeat expired."""
        now_str = _now_iso()
        lock_id = (
            f"lock-{mission_id}-"
            f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}-"
            f"{secrets.token_hex(4)}"
        )
        lease_expires = _iso_plus(self.lease_seconds)
        recovery_token = secrets.token_hex(16)
        host = socket.gethostname()
        worktree = str(Path.cwd())
        pid = os.getpid()

        conn = _get_db_connection(self.db_path)
        try:
            # Check for existing ACTIVE lock
            row = conn.execute(
                "SELECT * FROM mission_locks WHERE mission_id=? AND status='ACTIVE'",
                (mission_id,),
            ).fetchone()

            if row:
                row_dict = dict(row)
                if self._check_owner_alive(row_dict):
                    raise MissionLockConflict(
                        mission_id=mission_id,
                        existing_lock_id=row_dict["lock_id"],
                        existing_controller=row_dict["controller_type"],
                        existing_pid=row_dict["pid"],
                        heartbeat_at=row_dict["heartbeat_at"],
                    )
                # Owner is dead — steal the lock
                conn.execute(
                    "UPDATE mission_locks SET status='STOLEN' WHERE lock_id=?",
                    (row_dict["lock_id"],),
                )
                _log_transition(
                    conn, "mission_lock", row_dict["lock_id"],
                    "ACTIVE", "STOLEN", lock_id, "owner_dead_lock_stolen",
                )

            # Insert new ACTIVE lock
            conn.execute(
                """
                INSERT INTO mission_locks
                (lock_id, mission_id, controller_type, pid, session_id,
                 host_identity, branch, worktree_path, plan_version,
                 acquired_at, heartbeat_at, lease_expires, recovery_token, status)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,'ACTIVE')
                """,
                (
                    lock_id, mission_id, controller_type, pid, session_id,
                    host, branch, worktree, plan_version,
                    now_str, now_str, lease_expires, recovery_token,
                ),
            )
            _log_transition(conn, "mission_lock", lock_id, None, "ACTIVE", lock_id, "acquired")
            conn.commit()
            return lock_id
        except MissionLockConflict:
            raise
        except Exception as _exc:
            import sqlite3 as _sqlite3
            if isinstance(_exc, _sqlite3.IntegrityError) and "mission_lock" in str(_exc).lower():
                # Partial unique index rejected concurrent INSERT — convert to MissionLockConflict
                try:
                    _row = conn.execute(
                        "SELECT * FROM mission_locks WHERE mission_id=? AND status='ACTIVE'",
                        (mission_id,),
                    ).fetchone()
                    if _row:
                        raise MissionLockConflict(
                            mission_id=mission_id,
                            existing_lock_id=_row["lock_id"],
                            existing_controller=_row["controller_type"],
                            existing_pid=_row["pid"],
                            heartbeat_at=_row["heartbeat_at"],
                        ) from _exc
                except MissionLockConflict:
                    raise
                except Exception:
                    pass
            raise
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _release(self, lock_id: str) -> None:
        """Release a lock by setting status to RELEASED."""
        conn = _get_db_connection(self.db_path)
        try:
            updated = conn.execute(
                "UPDATE mission_locks SET status='RELEASED' "
                "WHERE lock_id=? AND status='ACTIVE'",
                (lock_id,),
            ).rowcount
            if updated:
                _log_transition(
                    conn, "mission_lock", lock_id, "ACTIVE", "RELEASED", lock_id, "released"
                )
            conn.commit()
        finally:
            conn.close()

    def _heartbeat(self, lock_id: str) -> None:
        """Refresh heartbeat_at and extend lease_expires."""
        # Keep the coordination-plane mirror fresh too (TC-COORD-008).
        bridge_worker = getattr(self, "_bridge_worker", None)
        if bridge_worker:
            try:
                from . import coordination_bridge as _bridge
                _bridge.mirror_renew(bridge_worker)
            except Exception:
                pass
        new_expiry = _iso_plus(self.lease_seconds)
        conn = _get_db_connection(self.db_path)
        try:
            conn.execute(
                "UPDATE mission_locks SET heartbeat_at=?, lease_expires=? "
                "WHERE lock_id=? AND status='ACTIVE'",
                (_now_iso(), new_expiry, lock_id),
            )
            conn.commit()
        except Exception:
            pass  # Heartbeat failure is non-fatal; lease expiry handles recovery
        finally:
            conn.close()

    def _start_heartbeat_thread(self, lock_id: str, stop_event: threading.Event) -> threading.Thread:
        """Return a daemon thread that heartbeats every interval seconds until stop_event."""
        interval = DEFAULT_HEARTBEAT_INTERVAL

        def _beat() -> None:
            while not stop_event.wait(timeout=interval):
                try:
                    self._heartbeat(lock_id)
                except Exception:
                    pass  # Non-fatal

        t = threading.Thread(target=_beat, daemon=True, name=f"heartbeat-{lock_id}")
        return t

    def _check_owner_alive(self, row: dict) -> bool:
        """True if owner should be considered alive (must not steal lock).

        PID check takes precedence: a running PID means alive regardless of
        heartbeat age. A dead PID falls back to heartbeat freshness.
        Steal only when BOTH fail: dead PID AND expired heartbeat.
        """
        try:
            pid_alive = _pid_alive(row["pid"])
        except Exception:
            pid_alive = False

        if pid_alive:
            return True  # Running PID → never steal

        try:
            hb = datetime.fromisoformat(row["heartbeat_at"])
            if hb.tzinfo is None:
                hb = hb.replace(tzinfo=timezone.utc)
            hb_age = (datetime.now(timezone.utc) - hb).total_seconds()
            hb_fresh = hb_age < self.heartbeat_ttl
        except Exception:
            hb_fresh = False

        return hb_fresh  # PID dead; use heartbeat as liveness signal
