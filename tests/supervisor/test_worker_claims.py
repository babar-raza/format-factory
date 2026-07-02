"""TC-CONC-009: Worker Claims unit tests (10 cases).

All tests use tmp_path for DB isolation.
Mission: CONC-HARDENING-2026-07-02
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO / "tools" / "supervisor") not in sys.path:
    sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from control_index.db import ensure_db
from concurrency.worker_claim import WorkerClaims
from concurrency.errors import PathOwnershipConflict


@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / "test-control-index.db"
    ensure_db(db_path)
    return db_path


@pytest.fixture
def lock_id(db):
    """Insert a dummy ACTIVE mission lock row; return its lock_id so FK constraints pass."""
    from control_index.db import connect
    import secrets
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    lid = f"lock-test-{secrets.token_hex(4)}"
    with connect(db) as conn:
        conn.execute("""
            INSERT INTO mission_locks
            (lock_id, mission_id, controller_type, pid, session_id, host_identity,
             branch, worktree_path, plan_version, acquired_at, heartbeat_at,
             lease_expires, recovery_token, status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,'ACTIVE')
        """, (lid, "format-factory-main", "test", 1, "s-test", "host",
              "main", "/tmp", None, now.isoformat(), now.isoformat(),
              (now + timedelta(hours=1)).isoformat(), secrets.token_hex(16)))
        conn.commit()
    yield lid
    # Release it after test
    with connect(db) as conn:
        conn.execute("UPDATE mission_locks SET status='RELEASED' WHERE lock_id=?", (lid,))
        conn.commit()


@pytest.fixture
def wc(db):
    return WorkerClaims(db_path=db, lease_minutes=60)


def test_01_claim_returns_claim_ids(wc, lock_id):
    cids = wc.claim("worker-A", "task-1", ["src/python/csv/models.py"],
                    "format-factory-main", lock_id)
    assert len(cids) == 1
    assert cids[0].startswith("claim-worker-A-")
    wc.release_all("worker-A")


def test_02_disjoint_paths_both_workers_succeed(wc, lock_id):
    cids_a = wc.claim("worker-A", "task-A", ["src/python/ndjson/models.py"],
                      "format-factory-main", lock_id)
    cids_b = wc.claim("worker-B", "task-B", ["src/python/csv/models.py"],
                      "format-factory-main", lock_id)
    assert len(cids_a) == 1
    assert len(cids_b) == 1

    active = wc.list_active(mission_id="format-factory-main")
    assert len(active) == 2
    wc.release_all("worker-A")
    wc.release_all("worker-B")


def test_03_same_file_write_write_raises_conflict(wc, lock_id):
    path = "src/python/tsv/models.py"
    wc.claim("worker-A", "task-A", [path], "format-factory-main", lock_id)
    with pytest.raises(PathOwnershipConflict) as exc_info:
        wc.claim("worker-B", "task-B", [path], "format-factory-main", lock_id)
    err = exc_info.value
    assert err.path == path
    assert err.existing_worker_id == "worker-A"
    wc.release_all("worker-A")


def test_04_read_read_no_conflict(wc, lock_id):
    """Two READ claims on the same path should not conflict."""
    path = "src/python/csv/models.py"
    cids_a = wc.claim("worker-A", "task-A", [path], "format-factory-main", lock_id, mode="READ")
    cids_b = wc.claim("worker-B", "task-B", [path], "format-factory-main", lock_id, mode="READ")
    assert len(cids_a) == 1
    assert len(cids_b) == 1
    wc.release_all("worker-A")
    wc.release_all("worker-B")


def test_05_expired_claim_does_not_block_new(db, lock_id):
    """An EXPIRED claim (past lease_expires) must not block new claims."""
    from control_index.db import connect
    import secrets
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    past = (now - timedelta(hours=1)).isoformat()
    path = "src/python/gnumeric/models.py"

    # Insert a synthetic expired claim (status=EXPIRED means it must not block)
    expired_claim_id = f"claim-expired-{secrets.token_hex(4)}"
    with connect(db) as conn:
        conn.execute("""
            INSERT INTO worker_claims
            (claim_id, mission_id, lock_id, worker_id, task_id, resource_pattern,
             resource_type, mode, acquired_at, lease_expires, status)
            VALUES (?,?,?,?,?,?,'file','WRITE',?,?,'EXPIRED')
        """, (expired_claim_id, "format-factory-main", lock_id,
              "worker-dead", "task-old", path, past, past))
        conn.commit()

    wc = WorkerClaims(db_path=db)
    # Should succeed — EXPIRED claim must not block
    cids = wc.claim("worker-new", "task-new", [path], "format-factory-main", lock_id)
    assert len(cids) == 1
    wc.release_all("worker-new")


def test_06_release_all_removes_worker_claims(wc, lock_id):
    wc.claim("worker-A", "task-1", ["src/a.py", "src/b.py"], "format-factory-main", lock_id)
    active_before = wc.list_active(mission_id="format-factory-main")
    assert len(active_before) == 2

    released = wc.release_all("worker-A")
    assert released == 2

    active_after = wc.list_active(mission_id="format-factory-main")
    assert len(active_after) == 0


def test_07_directory_prefix_overlap_detected(wc, lock_id):
    """Worker A claims a directory prefix; Worker B claims a file inside it — conflict."""
    dir_path = "src/python/ndjson/"
    file_path = "src/python/ndjson/models.py"

    wc.claim("worker-A", "task-A", [dir_path], "format-factory-main", lock_id)
    with pytest.raises(PathOwnershipConflict) as exc_info:
        wc.claim("worker-B", "task-B", [file_path], "format-factory-main", lock_id)
    assert exc_info.value.existing_worker_id == "worker-A"
    wc.release_all("worker-A")


def test_08_context_manager_releases_on_exception(wc, lock_id):
    """claimed() context manager releases paths even when an exception is raised."""
    path = "src/python/dif/models.py"
    try:
        with wc.claimed("worker-ctx", "task-ctx", [path], "format-factory-main", lock_id) as cids:
            assert len(cids) == 1
            raise RuntimeError("simulated")
    except RuntimeError:
        pass

    # Claims must be released
    active = wc.list_active(mission_id="format-factory-main")
    assert all(c["worker_id"] != "worker-ctx" for c in active)


def test_09_list_active_returns_only_active(wc, lock_id):
    wc.claim("worker-A", "task-A", ["src/p1.py"], "format-factory-main", lock_id)
    wc.claim("worker-B", "task-B", ["src/p2.py"], "format-factory-main", lock_id)
    wc.release_all("worker-B")

    active = wc.list_active(mission_id="format-factory-main")
    assert len(active) == 1
    assert active[0]["worker_id"] == "worker-A"
    wc.release_all("worker-A")


def test_10_check_overlap_returns_empty_when_none(wc):
    """check_overlap() with no active claims returns empty list."""
    overlaps = wc.check_overlap(["src/python/pbm/models.py"])
    assert overlaps == []
