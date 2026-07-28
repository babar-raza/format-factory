"""Atomic path ownership registry for concurrent workers.

Prevents two workers from simultaneously writing the same file by requiring
WRITE claims to be acquired atomically before any mutation.

Usage:
    from tools.supervisor.concurrency.worker_claim import WorkerClaims

    claims = WorkerClaims(db_path=db)
    with claims.claimed(worker_id, task_id, ["src/foo.py"], mission_id, lock_id):
        # exclusive write access to src/foo.py within this block
        do_mutation()

Mission: CONC-HARDENING-2026-07-02
"""
from __future__ import annotations

import json
import secrets
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

from .errors import PathOwnershipConflict

DEFAULT_LEASE_MINUTES: int = 30


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _iso_plus_minutes(minutes: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()


def _import_db_funcs():
    """Import db functions, supporting both repo-root and tools/supervisor sys.path contexts."""
    try:
        from control_index.db import ensure_db  # supervisor/ on sys.path
        return ensure_db
    except ImportError:
        pass
    import sys
    _repo = Path(__file__).resolve().parents[3]
    if str(_repo) not in sys.path:
        sys.path.insert(0, str(_repo))
    from tools.supervisor.control_index.db import ensure_db  # repo root on sys.path
    return ensure_db


def _get_db_connection(db_path: Path):
    return _import_db_funcs()(db_path)


def _paths_overlap(pattern_a: str, pattern_b: str) -> bool:
    """Return True if the two path patterns overlap.

    Overlap cases:
    - Exact match: 'src/foo.py' == 'src/foo.py'
    - B is under A: 'src/python/' is a prefix of 'src/python/ndjson/models.py'
    - A is under B: 'src/python/ndjson/models.py' starts with 'src/python/'
    """
    # Normalise: ensure directory patterns end with /
    a = pattern_a.rstrip("/")
    b = pattern_b.rstrip("/")
    if a == b:
        return True
    # Check if one is a directory prefix of the other
    if b.startswith(a + "/") or a.startswith(b + "/"):
        return True
    return False


class WorkerClaims:
    """Atomic path ownership registry backed by the SQLite control index.

    Parameters
    ----------
    db_path:
        Path to .local/supervisor/control-index.db
    lease_minutes:
        How long each claim is valid (default: 30 minutes)
    """

    def __init__(self, db_path: Path, lease_minutes: int | None = None) -> None:
        self.db_path = Path(db_path)
        self.lease_minutes = lease_minutes if lease_minutes is not None else DEFAULT_LEASE_MINUTES
        _import_db_funcs()(self.db_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @contextmanager
    def claimed(
        self,
        worker_id: str,
        task_id: str,
        paths: list[str],
        mission_id: str,
        lock_id: str,
        mode: str = "WRITE",
    ) -> Iterator[list[str]]:
        """Context manager: claim paths → yield claim_ids → release on exit."""
        claim_ids = self.claim(worker_id, task_id, paths, mission_id, lock_id, mode)
        try:
            yield claim_ids
        finally:
            self.release_all(worker_id)

    def claim(
        self,
        worker_id: str,
        task_id: str,
        paths: list[str],
        mission_id: str,
        lock_id: str,
        mode: str = "WRITE",
    ) -> list[str]:
        """Atomically claim paths for a worker.

        Uses BEGIN EXCLUSIVE transaction to prevent check-then-insert races.
        Raises PathOwnershipConflict if any path overlaps with an existing
        WRITE claim by a different worker.

        Returns list of claim_ids for the acquired claims.
        """
        if not paths:
            return []

        # TC-COORD-008: mirror into the coordination plane FIRST. Interactive
        # agents (hook auto-claims) live there; a foreign coordination lease
        # must block this legacy claim exactly like a legacy row would.
        from . import coordination_bridge as _bridge
        _lc_type = _bridge.lease_conflict_type()
        _mirror_leases: list[str] | None = None
        try:
            _mirror_leases = _bridge.mirror_claim(worker_id, task_id, paths,
                                                  mode)
        except Exception as _exc:
            if _lc_type is not None and isinstance(_exc, _lc_type):
                raise PathOwnershipConflict(
                    path=_exc.resource_key,
                    existing_worker_id=_bridge.resolve_owner_display(
                        _exc.holder_agent_id),
                    existing_task_id=_exc.holder_task_id or "unknown",
                    existing_claim_id=_exc.holder_lease_id,
                ) from _exc
            import warnings as _warnings
            _warnings.warn(f"[worker-claims] coordination mirror failed:"
                           f" {_exc}", stacklevel=2)

        now_str = _now_iso()
        expires = _iso_plus_minutes(self.lease_minutes)

        conn = _get_db_connection(self.db_path)
        try:
            # CRITICAL: BEGIN EXCLUSIVE ensures atomicity of check + insert
            conn.execute("BEGIN EXCLUSIVE")

            # First pass: check all paths for conflicts before inserting any
            if mode == "WRITE":
                for path in paths:
                    # Fetch all ACTIVE WRITE claims by other workers
                    rows = conn.execute(
                        """
                        SELECT claim_id, worker_id, task_id, resource_pattern
                        FROM worker_claims
                        WHERE status='ACTIVE' AND mode='WRITE' AND worker_id != ?
                        """,
                        (worker_id,),
                    ).fetchall()
                    for row in rows:
                        if _paths_overlap(path, row["resource_pattern"]):
                            conn.execute("ROLLBACK")
                            raise PathOwnershipConflict(
                                path=path,
                                existing_worker_id=row["worker_id"],
                                existing_task_id=row["task_id"],
                                existing_claim_id=row["claim_id"],
                            )

            # Second pass: insert all claims
            claim_ids: list[str] = []
            for path in paths:
                cid = f"claim-{worker_id[:16]}-{secrets.token_hex(4)}"
                conn.execute(
                    """
                    INSERT INTO worker_claims
                    (claim_id, mission_id, lock_id, worker_id, task_id,
                     resource_pattern, resource_type, mode,
                     acquired_at, lease_expires, status)
                    VALUES (?,?,?,?,?,?,'file',?,?,?,'ACTIVE')
                    """,
                    (
                        cid, mission_id, lock_id, worker_id, task_id,
                        path, mode, now_str, expires,
                    ),
                )
                claim_ids.append(cid)

            conn.commit()
            return claim_ids

        except PathOwnershipConflict:
            # Legacy-side conflict: roll the mirror back so the plane does
            # not carry a lease the caller never got.
            if _mirror_leases:
                _bridge.mirror_release(worker_id)
            raise
        except Exception:
            try:
                conn.execute("ROLLBACK")
            except Exception:
                pass
            if _mirror_leases:
                _bridge.mirror_release(worker_id)
            raise
        finally:
            conn.close()

    def release_all(self, worker_id: str) -> int:
        """Release all ACTIVE claims for this worker. Returns count released."""
        from . import coordination_bridge as _bridge
        _bridge.mirror_release(worker_id)
        conn = _get_db_connection(self.db_path)
        try:
            cursor = conn.execute(
                "UPDATE worker_claims SET status='RELEASED' "
                "WHERE worker_id=? AND status='ACTIVE'",
                (worker_id,),
            )
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def list_active(self, mission_id: str | None = None) -> list[dict]:
        """Return all ACTIVE claims, optionally filtered by mission."""
        conn = _get_db_connection(self.db_path)
        try:
            if mission_id:
                rows = conn.execute(
                    "SELECT * FROM worker_claims WHERE status='ACTIVE' AND mission_id=?",
                    (mission_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM worker_claims WHERE status='ACTIVE'"
                ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def check_overlap(
        self, paths: list[str], exclude_worker: str | None = None
    ) -> list[dict]:
        """Return list of conflicts for the given paths (non-atomic read-only check).

        Note: For atomic claim acquisition, use claim() which uses BEGIN EXCLUSIVE.
        This method is for diagnostic/advisory use only.
        """
        if not paths:
            return []
        conn = _get_db_connection(self.db_path)
        try:
            rows = conn.execute(
                "SELECT * FROM worker_claims WHERE status='ACTIVE' AND mode='WRITE'"
                + (" AND worker_id != ?" if exclude_worker else ""),
                (exclude_worker,) if exclude_worker else (),
            ).fetchall()

            conflicts = []
            for path in paths:
                for row in rows:
                    if _paths_overlap(path, row["resource_pattern"]):
                        conflicts.append({
                            "path": path,
                            "existing_claim_id": row["claim_id"],
                            "existing_worker_id": row["worker_id"],
                            "existing_task_id": row["task_id"],
                        })
            return conflicts
        finally:
            conn.close()
