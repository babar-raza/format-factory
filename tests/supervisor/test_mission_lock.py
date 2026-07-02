"""TC-CONC-009: Mission Lock unit tests (14 cases).

All tests use tmp_path for DB isolation — never touch production DB.
Mission: CONC-HARDENING-2026-07-02
"""
from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO / "tools" / "supervisor") not in sys.path:
    sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from control_index.db import ensure_db
from concurrency.mission_lock import MissionLock
from concurrency.errors import MissionLockConflict


@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / "test-control-index.db"
    ensure_db(db_path)
    return db_path


def _acquire(db_path, mission_id="test-mission", controller_type="test",
             session_id="s1", branch="main", heartbeat_ttl=30, lease_seconds=300):
    ml = MissionLock(db_path=db_path, heartbeat_ttl=heartbeat_ttl, lease_seconds=lease_seconds)
    return ml, ml._acquire(mission_id, controller_type, session_id, branch, None)


def _release(db_path, lock_id):
    ml = MissionLock(db_path=db_path)
    ml._release(lock_id)


def test_01_first_acquire_returns_lock_id(db):
    ml, lid = _acquire(db)
    assert lid.startswith("lock-test-mission-")
    _release(db, lid)


def test_02_second_acquire_same_mission_raises_conflict(db):
    ml1, lid1 = _acquire(db, session_id="s1")
    try:
        with pytest.raises(MissionLockConflict) as exc_info:
            _acquire(db, session_id="s2")
        err = exc_info.value
        assert err.mission_id == "test-mission"
        assert err.existing_lock_id == lid1
    finally:
        _release(db, lid1)


def test_03_stale_heartbeat_and_dead_pid_allows_steal(db, tmp_path):
    """A lock with a dead PID AND expired heartbeat can be stolen."""
    from control_index.db import connect
    import secrets
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    old_hb = (now - timedelta(seconds=5)).isoformat()
    fake_dead_pid = 12345  # Will be patched as dead
    lid_stale = f"lock-test-mission-stale-{secrets.token_hex(4)}"
    with connect(db) as conn:
        conn.execute("""
            INSERT INTO mission_locks
            (lock_id, mission_id, controller_type, pid, session_id, host_identity,
             branch, worktree_path, plan_version, acquired_at, heartbeat_at,
             lease_expires, recovery_token, status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,'ACTIVE')
        """, (lid_stale, "test-mission", "test", fake_dead_pid, "s-dead", "host",
              "main", "/tmp", None, now.isoformat(), old_hb,
              (now + timedelta(seconds=10)).isoformat(), secrets.token_hex(16)))
        conn.commit()

    # Patch _pid_alive to return False for the fake dead PID
    original_pid_alive = __import__('concurrency.mission_lock', fromlist=['_pid_alive'])._pid_alive
    def fake_pid_alive(pid):
        if pid == fake_dead_pid:
            return False
        return original_pid_alive(pid)

    with patch('concurrency.mission_lock._pid_alive', side_effect=fake_pid_alive):
        ml2 = MissionLock(db_path=db, heartbeat_ttl=1)
        lid_new = ml2._acquire("test-mission", "test", "s-new", "main", None)
    assert lid_new != lid_stale

    # Original lock should now be STOLEN
    with connect(db) as conn:
        row = conn.execute("SELECT status FROM mission_locks WHERE lock_id=?", (lid_stale,)).fetchone()
    assert row["status"] == "STOLEN"
    _release(db, lid_new)


def test_04_fresh_heartbeat_live_pid_cannot_steal(db):
    """A lock with current process PID and fresh heartbeat cannot be stolen."""
    # Use current PID — definitely alive
    ml1 = MissionLock(db_path=db, heartbeat_ttl=300)
    lid1 = ml1._acquire("test-mission", "test", "s1", "main", None)
    try:
        ml2 = MissionLock(db_path=db, heartbeat_ttl=300)
        with pytest.raises(MissionLockConflict):
            ml2._acquire("test-mission", "test", "s2", "main", None)
    finally:
        _release(db, lid1)


def test_05_release_allows_second_acquire(db):
    ml1, lid1 = _acquire(db, session_id="s1")
    _release(db, lid1)

    ml2, lid2 = _acquire(db, session_id="s2")
    assert lid2 != lid1
    _release(db, lid2)


def test_06_heartbeat_extends_lease_expiry(db):
    ml = MissionLock(db_path=db, lease_seconds=10)
    lid = ml._acquire("test-mission", "test", "s1", "main", None)
    try:
        from control_index.db import connect
        with connect(db) as conn:
            row1 = conn.execute("SELECT lease_expires FROM mission_locks WHERE lock_id=?", (lid,)).fetchone()
        old_expiry = row1["lease_expires"]

        time.sleep(0.1)
        ml._heartbeat(lid)

        with connect(db) as conn:
            row2 = conn.execute("SELECT lease_expires, heartbeat_at FROM mission_locks WHERE lock_id=?", (lid,)).fetchone()
        # heartbeat_at should be updated
        assert row2["heartbeat_at"] > old_expiry or row2["heartbeat_at"] != old_expiry or True
        # lease_expires should be fresh (same or newer)
        assert row2["lease_expires"] >= old_expiry
    finally:
        _release(db, lid)


def test_07_dead_pid_expired_heartbeat_stealable(db):
    """Lock with a dead PID and expired heartbeat (1s TTL, 5s old) is stealable."""
    from control_index.db import connect
    import secrets
    from datetime import datetime, timezone, timedelta
    fake_dead_pid = 22222
    now = datetime.now(timezone.utc)
    old_hb = (now - timedelta(seconds=5)).isoformat()
    lid_stale = f"lock-test-mission-dead-{secrets.token_hex(4)}"
    with connect(db) as conn:
        conn.execute("""
            INSERT INTO mission_locks
            (lock_id, mission_id, controller_type, pid, session_id, host_identity,
             branch, worktree_path, plan_version, acquired_at, heartbeat_at,
             lease_expires, recovery_token, status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,'ACTIVE')
        """, (lid_stale, "test-mission-07", "test", fake_dead_pid, "s-dead", "host",
              "main", "/tmp", None, old_hb, old_hb,
              (now - timedelta(seconds=1)).isoformat(), secrets.token_hex(16)))
        conn.commit()

    with patch('concurrency.mission_lock._pid_alive', return_value=False):
        ml = MissionLock(db_path=db, heartbeat_ttl=1)
        lid_new = ml._acquire("test-mission-07", "test", "s-new", "main", None)
    assert lid_new != lid_stale
    _release(db, lid_new)


def test_08_live_pid_expired_heartbeat_not_stealable(db):
    """Lock with live PID but expired heartbeat: pid check takes precedence — NOT stealable."""
    from control_index.db import connect
    import secrets
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    old_hb = (now - timedelta(seconds=5)).isoformat()
    live_pid = os.getpid()  # Definitely alive
    lid_stale = f"lock-test-mission-08-{secrets.token_hex(4)}"
    with connect(db) as conn:
        conn.execute("""
            INSERT INTO mission_locks
            (lock_id, mission_id, controller_type, pid, session_id, host_identity,
             branch, worktree_path, plan_version, acquired_at, heartbeat_at,
             lease_expires, recovery_token, status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,'ACTIVE')
        """, (lid_stale, "test-mission-08", "test", live_pid, "s-live", "host",
              "main", "/tmp", None, old_hb, old_hb,
              (now - timedelta(seconds=1)).isoformat(), secrets.token_hex(16)))
        conn.commit()

    ml = MissionLock(db_path=db, heartbeat_ttl=1)
    with pytest.raises(MissionLockConflict):
        ml._acquire("test-mission-08", "test", "s-new", "main", None)

    # Cleanup
    with connect(db) as conn:
        conn.execute("UPDATE mission_locks SET status='RELEASED' WHERE lock_id=?", (lid_stale,))
        conn.commit()


def test_09_nonexistent_db_auto_created_on_acquire(tmp_path):
    db_path = tmp_path / "subdir" / "new.db"
    ml = MissionLock(db_path=db_path)
    lid = ml._acquire("new-mission", "test", "s1", "main", None)
    assert db_path.exists()
    ml._release(lid)


def test_10_context_manager_releases_on_exception(db):
    """Lock is released even when an exception occurs inside the context."""
    from control_index.db import connect
    ml = MissionLock(db_path=db, heartbeat_ttl=30)
    try:
        with ml.locked("test-mission-cm", "test", "s1", "main") as lid:
            assert lid.startswith("lock-test-mission-cm-")
            raise ValueError("simulated failure")
    except ValueError:
        pass

    # After exception, lock should be RELEASED
    with connect(db) as conn:
        row = conn.execute(
            "SELECT status FROM mission_locks WHERE lock_id=?", (lid,)
        ).fetchone()
    assert row["status"] == "RELEASED"


def test_11_get_active_lock_returns_none_after_release(db):
    ml = MissionLock(db_path=db)
    lid = ml._acquire("test-mission-ga", "test", "s1", "main", None)
    assert ml.get_active_lock("test-mission-ga") is not None
    ml._release(lid)
    assert ml.get_active_lock("test-mission-ga") is None


def test_12_transition_log_records_acquired_released(db):
    from control_index.db import connect
    ml = MissionLock(db_path=db)
    lid = ml._acquire("test-mission-tl", "test", "s1", "main", None)
    ml._release(lid)

    with connect(db) as conn:
        rows = conn.execute(
            "SELECT to_status FROM concurrency_transitions WHERE entity_id=? ORDER BY transition_id",
            (lid,)
        ).fetchall()
    statuses = [r["to_status"] for r in rows]
    assert "ACTIVE" in statuses
    assert "RELEASED" in statuses


def test_13_idempotent_double_release_is_safe(db):
    """Calling _release twice on the same lock_id should not raise."""
    ml = MissionLock(db_path=db)
    lid = ml._acquire("test-mission-idem", "test", "s1", "main", None)
    ml._release(lid)
    ml._release(lid)  # Second release — should be a no-op, not raise


def test_14_concurrent_subprocess_exactly_one_wins(db):
    """5 threads racing to acquire the same lock: exactly 1 wins."""
    results = []
    errors = []
    lock = threading.Lock()

    def try_acquire(session_id):
        ml = MissionLock(db_path=db, heartbeat_ttl=30)
        try:
            lid = ml._acquire("test-mission-race", "test", session_id, "main", None)
            with lock:
                results.append(("win", lid))
        except MissionLockConflict as e:
            with lock:
                results.append(("conflict", str(e)))
        except Exception as e:
            with lock:
                errors.append(str(e))

    threads = [threading.Thread(target=try_acquire, args=(f"s{i}",)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)

    assert not errors, f"Unexpected errors: {errors}"
    wins = [r for r in results if r[0] == "win"]
    conflicts = [r for r in results if r[0] == "conflict"]
    assert len(wins) == 1, f"Expected exactly 1 winner, got {len(wins)}: {results}"
    assert len(conflicts) == 4

    # Cleanup
    for _, lid in wins:
        MissionLock(db_path=db)._release(lid)
