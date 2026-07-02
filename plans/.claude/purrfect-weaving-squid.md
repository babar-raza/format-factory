# Plan: Concurrent Agent Execution Hardening
plan_id: purrfect-weaving-squid
type: machinery_hardening
mission_id: CONC-HARDENING-2026-07-02
status: COMPLETE
track_type: machinery

---

## Forensic Audit Record (2026-07-02)

This plan was forensically audited after initial creation. The following critical
defects were found and corrected in this version:

| ID | Severity | Finding | Resolution |
|----|----------|---------|-----------|
| C-1 | CRITICAL | `UNIQUE(mission_id, status)` prevents multiple RELEASED rows | Changed to partial index `WHERE status='ACTIVE'` |
| C-2 | CRITICAL | `_git("string")` passed string not list | Fixed to `_git(["rev-parse", "--abbrev-ref", "HEAD"])` |
| C-3 | CRITICAL | `_db_path()` and `_get_session_id()` not defined in sprint_executor.py | Added helper definitions to TC-CONC-007 |
| C-4 | CRITICAL | MissionLock API inconsistent (two styles) | Canonicalized to `MissionLock(db_path).locked(...)` context manager |
| C-5 | CRITICAL | Path claim `check_overlap()` + `INSERT` not atomic | Mandated `BEGIN EXCLUSIVE` transaction in TC-CONC-005 |
| H-1 | HIGH | No dependency ordering between taskcards | Added prerequisites fields to all taskcards |
| H-2 | HIGH | Interactive `/autonomous-loop` guard absent | Added TC-CONC-007b for autonomous-loop skill preflight |
| H-3 | HIGH | Unit tests would use production DB | Added `tmp_path` isolation requirement to TC-CONC-009 |
| H-4 | HIGH | `_extract_declared_paths()` underspecified | Added full specification in TC-CONC-008 |
| H-5 | HIGH | Pilot 4 waits 35s — CI unusable | Added configurable `heartbeat_ttl_seconds` parameter |
| H-6 | HIGH | `SCHEMA_VERSION` in `__init__.py` not mentioned | Added step to TC-CONC-003 to bump `SCHEMA_VERSION = 2` |
| H-7 | HIGH | TC-CONC-001 fabricates unknown git operation | Changed to evidence-based description only |
| M-4 | MEDIUM | ATTEMPT events in Pilot 9 not defined | Removed ATTEMPT events; changed to attempt_count counter |
| M-5 | MEDIUM | Pilot evidence outputs not specified | Added `evidence_output:` for each pilot |
| L-1 | LOW | .gitignore update unnecessary | Removed — `.local/` already covered |
| L-3 | LOW | SCHEMA_VERSION location not identified | Identified: `tools/supervisor/control_index/__init__.py` line 13 |

---

## Context

**Incident:** A headless `sprint_executor.py run-loop` executed concurrently with an
interactive VSCode session. Both operated on the same working tree (One-Mechanism Lock
violation). The 18-line R1227 NDJSON patch was lost mid-session (documented in
GAP-MA-006). Work was manually reapplied and committed in `41ff66b1`.

**First failed control boundary:** No machine-enforced mission lock exists in
`sprint_executor.py run-loop` startup. The `autonomous_orchestrator.py` has a
PID-based `orchestrator.lock` at `.local/supervisor/orchestrator.lock`, but
`sprint_executor.py` bypasses it — it does not import or check that lock. As a
result, two controllers can operate simultaneously with no technical barrier.

**Goal:** Implement production-grade multi-agent coordination:
- Machine-enforced mission lock (SQLite-backed, atomic, heartbeat-aware)
- Worker path-ownership registry (blocks concurrent overlapping write claims)
- Git-backed checkpoint system (saves uncommitted diffs before risky ops)
- Controller startup guards in both headless and interactive entry points
- Full test suite (42 unit tests) + 10 concurrency pilots

**R1227 recovery status:** COMPLETE — `src/python/ndjson/models.py` with
`is_small`, `is_large`, `min_keys` is committed at HEAD in `41ff66b1`.

---

## Current Architecture (What Exists)

| Component | Location | Coverage |
|-----------|----------|----------|
| Atomic writes (temp+replace) | `tools/supervisor/atomic_io.py` | All state files |
| PID-based orchestrator lock | `tools/supervisor/autonomous_orchestrator.py` | Orchestrator only — sprint_executor bypasses |
| Plan lock (session-keyed) | `tools/supervisor/write_plan_lock.py` | Plan lifecycle only |
| Session isolation (CCI-MVP) | `tools/supervisor/check_continuation.py` | Chat isolation only |
| SQLite control index (SCHEMA_VERSION=1) | `tools/supervisor/control_index/__init__.py` | Analytics overlay — no concurrency tables |
| One-Mechanism Lock | CLAUDE.md (text) | **Documentation only — zero machine enforcement** |

**Critical gaps:**
- No machine lock prevents two controllers starting on the same mission/working tree
- No path ownership registry blocks concurrent file mutations
- No pre-operation checkpoint of uncommitted working-tree diffs before risky ops
- SQLite schema v1 has no tables for locks/leases/claims/heartbeats/checkpoints

**DB reality:** `tools/supervisor/control_index/db.py:ensure_db()` calls `init_db()`
when `get_schema_version(db_path) < SCHEMA_VERSION`. Bumping `SCHEMA_VERSION` from 1
to 2 in `tools/supervisor/control_index/__init__.py` is sufficient to trigger
schema upgrade on next `ensure_db()` call — no separate migration runner needed.

---

## Taskcard Execution Order (dependencies enforced)

```
TC-CONC-001 (no deps)  ─┐
TC-CONC-002 (no deps)  ─┤─→ TC-CONC-003 ─→ TC-CONC-004 ─┐
                                                            ├─→ TC-CONC-007
                                            TC-CONC-005 ───┤
                                            TC-CONC-006 ───┤─→ TC-CONC-008
                                                            │
                         All above ────────────────────────┴─→ TC-CONC-009 ─→ TC-CONC-010 ─→ TC-CONC-011
```

---

## Implementation Taskcards

### TC-CONC-001: Incident Bind + Root Cause Report
**Status:** CLOSED
**Prerequisites:** None
**Rollback:** None needed (report files only)

**Deliverables:**
- `reports/concurrency/incident-root-cause.yaml`
- `reports/concurrency/lost-work-reconciliation.yaml`

**What to produce in `incident-root-cause.yaml`** (evidence-based only — do NOT
fabricate the specific git command that caused the loss):
```yaml
concurrency_incident:
  incident_id: CONC-INC-2026-07-02-R1227
  repository: format-factory
  affected_task: R1227
  affected_paths:
    - src/python/ndjson/models.py
  lost_change_description: "18-line addition: is_small, is_large, min_keys properties in NdjsonDocument"
  interactive_actor: "VSCode /autonomous-loop interactive session"
  headless_actor: "sprint_executor.py run-loop (background process)"
  active_mechanisms:
    - "One-Mechanism Lock (CLAUDE.md text only — zero machine enforcement)"
    - "autonomous_orchestrator.py orchestrator.lock (PID-based, bypassed by sprint_executor)"
  first_failed_control_boundary: >
    sprint_executor.py cmd_run_loop() has no lock acquisition before
    entering its work loop. It does not check orchestrator.lock and has
    no concurrency guard of any kind. Any number of instances can start
    simultaneously.
  recovery_path: "Manual reapplication; committed in 41ff66b1"
  evidence_refs:
    - reports/machinery-assurance/gap-ledger.yaml  # GAP-MA-006
    - reports/machinery-assurance/final-report.md
  verification_at_head: "git show HEAD:src/python/ndjson/models.py | grep is_small"
```

**`lost-work-reconciliation.yaml` must confirm:**
- `UNRECONCILED_LOST_OR_ORPHANED_WORK: 0`
- R1227 verification: run `python -c "from ndjson.models import NdjsonDocument; print('ok')"`
  in `.venv` to confirm is_small/is_large/min_keys accessible

**Completion criteria:** Both YAML files exist and are schema-valid.

---

### TC-CONC-002: Mutator Inventory
**Status:** CLOSED
**Prerequisites:** TC-CONC-001
**Rollback:** None needed (report file only)

**Deliverable:** `reports/concurrency/mutator-inventory.yaml`

**Required structure for each entry:**
```yaml
- mutator_id: M01
  entry_point: tools/supervisor/sprint_executor.py
  mechanism: headless subprocess (claude --print)
  files_or_state_owned:
    - .local/evidences/{run_id}/
    - .local/supervisor/continuation-signal.json
  lock_behavior: NONE (no lock acquired today)
  workspace_behavior: SHARED (operates on main working tree)
  conflict_behavior: NONE (no conflict detection)
  recovery_behavior: NONE
  bypasses:
    - autonomous_orchestrator.py orchestrator.lock
  findings: UNGOVERNED
```

**Known mutators (minimum 15):**
1. M01: `sprint_executor.py run-loop` — evidence injection, continuation-signal writes
2. M02: `autonomous_cycle.py` — reports/supervisor/, continuation-signal.json
3. M03: `write_plan_lock.py` — .local/supervisor/*.json + plan file HTML comment
4. M04: `autonomous_orchestrator.py` — orchestrator.lock, dispatch
5. M05: Interactive `/autonomous-loop` VSCode skill (invokes claude interactively)
6. M06: `lifecycle_audit.py` — lifecycle-audit-results.json
7. M07: `check_continuation.py` — READ-ONLY (no mutation)
8. M08: Git SCM Agent (AG4) — git commit/push on working tree
9. M09: Governance validators — READ-ONLY (no mutation)
10. M10: Evidence ingestors — .local/evidences/ WRITE
11. M11: `tools/capability_layer/capability_pipeline.py` — reports/ WRITE
12. M12: `tools/supervisor/build_declaration_review_package.py` — review ZIPs WRITE
13. M13: `tools/supervisor/grader_reliability.py` — grade artifact WRITE
14. M14: Source/test authoring tools (add-python-api, add-dotnet-api, etc.) — src/ + tests/ WRITE
15. M15: File watcher (`.supervisor/state/watcher.json` trigger scripts) — state WRITE

**Required counters at report close:**
- `UNINVENTORIED_MUTATORS: 0`
- `UNGOVERNED_MUTATION_PATHS: 0`

**Completion criteria:** `mutator-inventory.yaml` exists with all 15+ entries, each
with lock_behavior, workspace_behavior, conflict_behavior, bypasses fields populated.

---

### TC-CONC-003: SQLite Concurrency Schema + Version Bump
**Status:** CLOSED
**Prerequisites:** None (parallel with TC-CONC-001, TC-CONC-002)
**Rollback:** If migration fails, revert schema.sql and __init__.py; existing tables use `IF NOT EXISTS` so partial upgrade only adds rows to schema_meta

**Files modified:**
- `tools/supervisor/control_index/schema.sql` — add 4 tables + partial index
- `tools/supervisor/control_index/__init__.py` — bump `SCHEMA_VERSION = 1` → `SCHEMA_VERSION = 2`

**Do NOT create a separate migrate.py** — `db.py:ensure_db()` already calls
`init_db()` when `get_schema_version < SCHEMA_VERSION`. Bumping the constant is
sufficient; `IF NOT EXISTS` makes it idempotent.

**Add to end of `schema.sql`:**

```sql
-- ============================================================
-- CONCURRENCY CONTROL TABLES (schema v2)
-- ============================================================

-- T11: Mission-level controller lock
-- CRITICAL: partial index (not UNIQUE column constraint) to allow
-- unlimited RELEASED/EXPIRED rows while enforcing ONE ACTIVE per mission
CREATE TABLE IF NOT EXISTS mission_locks (
    lock_id         TEXT PRIMARY KEY,
    mission_id      TEXT NOT NULL,
    controller_type TEXT NOT NULL,     -- 'interactive' | 'headless'
    pid             INTEGER NOT NULL,
    session_id      TEXT NOT NULL,
    host_identity   TEXT NOT NULL,
    branch          TEXT NOT NULL,
    worktree_path   TEXT NOT NULL,
    plan_version    TEXT,
    acquired_at     TEXT NOT NULL,
    heartbeat_at    TEXT NOT NULL,
    lease_expires   TEXT NOT NULL,     -- ISO8601; refreshed by heartbeat
    recovery_token  TEXT NOT NULL,     -- secrets.token_hex(16)
    status          TEXT NOT NULL DEFAULT 'ACTIVE'
                    CHECK(status IN ('ACTIVE','RELEASED','EXPIRED','STOLEN'))
);
-- CRITICAL: partial unique index — only one ACTIVE row per mission
-- Multiple RELEASED/EXPIRED rows are allowed (history)
CREATE UNIQUE INDEX IF NOT EXISTS idx_mission_lock_active
    ON mission_locks(mission_id)
    WHERE status = 'ACTIVE';

-- T12: Worker path ownership claims
CREATE TABLE IF NOT EXISTS worker_claims (
    claim_id        TEXT PRIMARY KEY,
    mission_id      TEXT NOT NULL,
    lock_id         TEXT NOT NULL
                    REFERENCES mission_locks(lock_id) ON DELETE CASCADE,
    worker_id       TEXT NOT NULL,
    task_id         TEXT NOT NULL,
    resource_pattern TEXT NOT NULL,
    resource_type   TEXT NOT NULL DEFAULT 'file',
    mode            TEXT NOT NULL DEFAULT 'WRITE'
                    CHECK(mode IN ('READ','WRITE','INTEGRATE')),
    acquired_at     TEXT NOT NULL,
    lease_expires   TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'ACTIVE'
                    CHECK(status IN ('ACTIVE','RELEASED','EXPIRED'))
);
CREATE INDEX IF NOT EXISTS idx_worker_claims_active
    ON worker_claims(mission_id, status)
    WHERE status = 'ACTIVE';

-- T13: Immutable concurrency transition audit log
CREATE TABLE IF NOT EXISTS concurrency_transitions (
    transition_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type     TEXT NOT NULL
                    CHECK(entity_type IN ('mission_lock','worker_claim','checkpoint')),
    entity_id       TEXT NOT NULL,
    from_status     TEXT,
    to_status       TEXT NOT NULL,
    actor           TEXT NOT NULL,
    reason          TEXT,
    occurred_at     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ct_entity ON concurrency_transitions(entity_type, entity_id);

-- T14: Task checkpoints (patch file references — no blobs in DB)
CREATE TABLE IF NOT EXISTS concurrency_checkpoints (
    checkpoint_id   TEXT PRIMARY KEY,
    task_id         TEXT NOT NULL,
    worker_id       TEXT NOT NULL,
    description     TEXT,
    base_sha        TEXT NOT NULL,     -- git rev-parse HEAD at checkpoint time
    patch_path      TEXT NOT NULL,     -- absolute path to .patch file
    changed_files   TEXT NOT NULL,     -- JSON array of relative paths
    created_at      TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'VALID'
                    CHECK(status IN ('VALID','APPLIED','SUPERSEDED'))
);
CREATE INDEX IF NOT EXISTS idx_checkpoints_task ON concurrency_checkpoints(task_id, created_at);
```

**In `tools/supervisor/control_index/__init__.py`, line 13:**
Change `SCHEMA_VERSION = 1` → `SCHEMA_VERSION = 2`

**Verification after implementation:**
```bash
python -m tools.supervisor.control_index init
python -m tools.supervisor.control_index status
# Must show: schema_version: 2 and row_counts for mission_locks, worker_claims,
# concurrency_transitions, concurrency_checkpoints
```

**Completion criteria:**
- `schema.sql` contains all 4 new tables + partial index
- `__init__.py` has `SCHEMA_VERSION = 2`
- `python -m tools.supervisor.control_index status` shows schema_version: 2

---

### TC-CONC-004: Mission Lock Module
**Status:** CLOSED
**Prerequisites:** TC-CONC-003 (schema must exist before module can be written/tested)

**New files:**
- `tools/supervisor/concurrency/__init__.py` — empty package init
- `tools/supervisor/concurrency/errors.py` — all exception classes
- `tools/supervisor/concurrency/mission_lock.py` — `MissionLock` class

**`errors.py` — all exceptions for the concurrency package:**
```python
class MissionLockConflict(RuntimeError):
    def __init__(self, mission_id, existing_lock_id, existing_controller, existing_pid, heartbeat_at):
        self.mission_id = mission_id
        self.existing_lock_id = existing_lock_id
        self.existing_controller = existing_controller
        self.existing_pid = existing_pid
        self.heartbeat_at = heartbeat_at
        super().__init__(
            f"Mission '{mission_id}' is locked by {existing_controller} "
            f"(PID {existing_pid}, heartbeat {heartbeat_at})"
        )

class PathOwnershipConflict(RuntimeError):
    def __init__(self, path, existing_worker_id, existing_task_id, existing_claim_id):
        self.path = path
        self.existing_worker_id = existing_worker_id
        self.existing_task_id = existing_task_id
        self.existing_claim_id = existing_claim_id
        super().__init__(
            f"Path '{path}' is owned by worker '{existing_worker_id}' "
            f"(task '{existing_task_id}', claim '{existing_claim_id}')"
        )

class StaleBaseRevision(RuntimeError):
    def __init__(self, checkpoint_base_sha, current_sha):
        self.checkpoint_base_sha = checkpoint_base_sha
        self.current_sha = current_sha
        super().__init__(
            f"Checkpoint base {checkpoint_base_sha[:8]} != current HEAD {current_sha[:8]}"
        )

class CheckpointError(RuntimeError): ...
class LockNotHeld(RuntimeError): ...
```

**`mission_lock.py` — canonical API:**

```python
class MissionLock:
    """SQLite-backed mission controller lock with heartbeat and PID liveness."""

    DEFAULT_LEASE_SECONDS = 300      # 5 minutes (production)
    DEFAULT_HEARTBEAT_INTERVAL = 10  # seconds between heartbeat updates
    DEFAULT_HEARTBEAT_TTL = 30       # seconds before heartbeat considered stale
    BUSY_RETRIES = 5
    BUSY_SLEEP = 0.1

    def __init__(self, db_path: Path, *,
                 lease_seconds: int | None = None,
                 heartbeat_ttl: int | None = None):
        self.db_path = db_path
        self.lease_seconds = lease_seconds or self.DEFAULT_LEASE_SECONDS
        self.heartbeat_ttl = heartbeat_ttl or self.DEFAULT_HEARTBEAT_TTL
        # Ensure DB + schema exists
        from tools.supervisor.control_index.db import ensure_db
        ensure_db(db_path)

    @contextmanager
    def locked(self, mission_id: str, controller_type: str,
               session_id: str, branch: str,
               plan_version: str | None = None) -> Iterator[str]:
        """Context manager: acquire lock, yield lock_id, release on exit.

        Usage:
            with MissionLock(db_path).locked("format-factory-main", "headless",
                                             session_id, branch) as lock_id:
                ...
        Raises MissionLockConflict if another live controller holds the lock.
        """
        lock_id = self._acquire(mission_id, controller_type, session_id, branch, plan_version)
        hb_thread = self._start_heartbeat(lock_id)
        try:
            yield lock_id
        finally:
            hb_thread.cancel()
            self._release(lock_id)

    def _acquire(self, mission_id, controller_type, session_id, branch, plan_version) -> str:
        """Atomic acquire. Steals lock only if PID is dead AND heartbeat expired."""
        import os, secrets, socket
        from datetime import datetime, timezone, timedelta

        now = datetime.now(timezone.utc)
        lock_id = f"lock-{mission_id}-{now.strftime('%Y%m%dT%H%M%S')}-{secrets.token_hex(4)}"
        lease_expires = (now + timedelta(seconds=self.lease_seconds)).isoformat()
        recovery_token = secrets.token_hex(16)

        with _connect(self.db_path) as conn:
            # Try to find an existing ACTIVE lock
            row = conn.execute(
                "SELECT * FROM mission_locks WHERE mission_id=? AND status='ACTIVE'",
                (mission_id,)
            ).fetchone()

            if row:
                if self._is_owner_alive(dict(row)):
                    raise MissionLockConflict(
                        mission_id=mission_id,
                        existing_lock_id=row["lock_id"],
                        existing_controller=row["controller_type"],
                        existing_pid=row["pid"],
                        heartbeat_at=row["heartbeat_at"],
                    )
                # Owner is dead — steal the lock
                conn.execute(
                    "UPDATE mission_locks SET status='STOLEN' WHERE lock_id=?",
                    (row["lock_id"],)
                )
                _log_transition(conn, "mission_lock", row["lock_id"],
                                "ACTIVE", "STOLEN", lock_id, "owner_dead")

            # INSERT new ACTIVE lock
            conn.execute("""
                INSERT INTO mission_locks
                (lock_id, mission_id, controller_type, pid, session_id, host_identity,
                 branch, worktree_path, plan_version, acquired_at, heartbeat_at,
                 lease_expires, recovery_token, status)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,'ACTIVE')
            """, (lock_id, mission_id, controller_type, os.getpid(), session_id,
                  socket.gethostname(), branch, str(Path.cwd()),
                  plan_version, now.isoformat(), now.isoformat(),
                  lease_expires, recovery_token))
            _log_transition(conn, "mission_lock", lock_id, None, "ACTIVE", lock_id, "acquired")
            conn.commit()
        return lock_id

    def _release(self, lock_id: str) -> None:
        with _connect(self.db_path) as conn:
            conn.execute(
                "UPDATE mission_locks SET status='RELEASED' WHERE lock_id=? AND status='ACTIVE'",
                (lock_id,)
            )
            _log_transition(conn, "mission_lock", lock_id, "ACTIVE", "RELEASED", lock_id, "released")
            conn.commit()

    def _heartbeat(self, lock_id: str) -> None:
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        new_expiry = (now + timedelta(seconds=self.lease_seconds)).isoformat()
        with _connect(self.db_path) as conn:
            conn.execute(
                "UPDATE mission_locks SET heartbeat_at=?, lease_expires=? WHERE lock_id=?",
                (now.isoformat(), new_expiry, lock_id)
            )
            conn.commit()

    def _start_heartbeat(self, lock_id: str) -> threading.Timer:
        """Start a repeating daemon timer that heartbeats every interval seconds."""
        interval = self.DEFAULT_HEARTBEAT_INTERVAL

        def _beat():
            try:
                self._heartbeat(lock_id)
            except Exception:
                pass  # Non-fatal; lease will expire if missed long enough
            # Re-schedule
            t = threading.Timer(interval, _beat)
            t.daemon = True
            t.start()
            # Store reference for cancellation via the original Timer
        t = threading.Timer(interval, _beat)
        t.daemon = True
        return t  # Caller calls t.start() and t.cancel()

    def _is_owner_alive(self, row: dict) -> bool:
        """True if owner process is running AND heartbeat is recent."""
        import psutil
        from datetime import datetime, timezone, timedelta
        try:
            pid_alive = psutil.pid_exists(row["pid"])
        except Exception:
            pid_alive = False
        try:
            hb = datetime.fromisoformat(row["heartbeat_at"])
            hb_fresh = (datetime.now(timezone.utc) - hb) < timedelta(seconds=self.heartbeat_ttl)
        except Exception:
            hb_fresh = False
        return pid_alive and hb_fresh

    def get_active_lock(self, mission_id: str) -> dict | None:
        with _connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM mission_locks WHERE mission_id=? AND status='ACTIVE'",
                (mission_id,)
            ).fetchone()
            return dict(row) if row else None
```

**Helper functions (module-level in mission_lock.py):**
```python
def _connect(db_path: Path):
    from tools.supervisor.control_index.db import connect
    return connect(db_path)

def _log_transition(conn, entity_type, entity_id, from_status, to_status, actor, reason):
    from datetime import datetime, timezone
    conn.execute("""
        INSERT INTO concurrency_transitions
        (entity_type, entity_id, from_status, to_status, actor, reason, occurred_at)
        VALUES (?,?,?,?,?,?,?)
    """, (entity_type, entity_id, from_status, to_status, actor, reason,
          datetime.now(timezone.utc).isoformat()))
```

**Note on `psutil`:** If not installed, fall back to `os.kill(pid, 0)` pattern:
```python
try:
    import psutil
    pid_alive = psutil.pid_exists(row["pid"])
except ImportError:
    try:
        os.kill(row["pid"], 0)
        pid_alive = True
    except (OSError, ProcessLookupError):
        pid_alive = False
```

**Completion criteria:**
- `tools/supervisor/concurrency/mission_lock.py` exists
- `MissionLock(tmp_db).locked(...)` context manager acquires and releases
- Transition log populated after each acquire/release

---

### TC-CONC-005: Worker Path Claim Module
**Status:** CLOSED
**Prerequisites:** TC-CONC-003, TC-CONC-004 (errors.py)

**New file:** `tools/supervisor/concurrency/worker_claim.py`

**Critical requirement:** Path claim must be atomic. The check-then-insert must use
`BEGIN EXCLUSIVE` (or `BEGIN IMMEDIATE`) to prevent two concurrent callers from both
reading "no conflict" and both inserting.

```python
class WorkerClaims:
    DEFAULT_LEASE_MINUTES = 30

    def __init__(self, db_path: Path, lease_minutes: int | None = None):
        self.db_path = db_path
        self.lease_minutes = lease_minutes or self.DEFAULT_LEASE_MINUTES
        from tools.supervisor.control_index.db import ensure_db
        ensure_db(db_path)

    @contextmanager
    def claimed(self, worker_id: str, task_id: str,
                paths: list[str], mission_id: str,
                lock_id: str, mode: str = 'WRITE') -> Iterator[list[str]]:
        """Context manager: claim paths, yield claim_ids, release on exit."""
        claim_ids = self.claim(worker_id, task_id, paths, mission_id, lock_id, mode)
        try:
            yield claim_ids
        finally:
            self.release_all(worker_id)

    def claim(self, worker_id: str, task_id: str, paths: list[str],
              mission_id: str, lock_id: str, mode: str = 'WRITE') -> list[str]:
        """Atomically claim paths. Raises PathOwnershipConflict if overlap exists."""
        import secrets
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        expires = (now + timedelta(minutes=self.lease_minutes)).isoformat()

        # CRITICAL: BEGIN EXCLUSIVE to prevent concurrent check+insert race
        with _connect(self.db_path) as conn:
            conn.execute("BEGIN EXCLUSIVE")
            try:
                # Check all paths for overlap before inserting any
                for path in paths:
                    if mode == 'WRITE':
                        conflict = conn.execute("""
                            SELECT claim_id, worker_id, task_id FROM worker_claims
                            WHERE status='ACTIVE' AND mode='WRITE'
                              AND worker_id != ?
                              AND (resource_pattern = ?
                                   OR ? LIKE resource_pattern || '%'
                                   OR resource_pattern LIKE ? || '%')
                        """, (worker_id, path, path, path)).fetchone()
                        if conflict:
                            conn.execute("ROLLBACK")
                            raise PathOwnershipConflict(
                                path=path,
                                existing_worker_id=conflict["worker_id"],
                                existing_task_id=conflict["task_id"],
                                existing_claim_id=conflict["claim_id"],
                            )

                # All checks passed — insert all claims
                claim_ids = []
                for path in paths:
                    cid = f"claim-{worker_id}-{secrets.token_hex(4)}"
                    conn.execute("""
                        INSERT INTO worker_claims
                        (claim_id, mission_id, lock_id, worker_id, task_id,
                         resource_pattern, resource_type, mode,
                         acquired_at, lease_expires, status)
                        VALUES (?,?,?,?,?,?,'file',?,?,?,'ACTIVE')
                    """, (cid, mission_id, lock_id, worker_id, task_id,
                          path, mode, now.isoformat(), expires))
                    claim_ids.append(cid)
                conn.commit()
                return claim_ids
            except PathOwnershipConflict:
                raise
            except Exception:
                conn.execute("ROLLBACK")
                raise

    def release_all(self, worker_id: str) -> int:
        """Release all ACTIVE claims for this worker. Returns count released."""
        with _connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE worker_claims SET status='RELEASED' WHERE worker_id=? AND status='ACTIVE'",
                (worker_id,)
            )
            conn.commit()
            return cursor.rowcount

    def list_active(self, mission_id: str | None = None) -> list[dict]:
        with _connect(self.db_path) as conn:
            if mission_id:
                rows = conn.execute(
                    "SELECT * FROM worker_claims WHERE status='ACTIVE' AND mission_id=?",
                    (mission_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM worker_claims WHERE status='ACTIVE'"
                ).fetchall()
            return [dict(r) for r in rows]
```

**Completion criteria:**
- Two workers claiming same path raises `PathOwnershipConflict`
- Two workers claiming disjoint paths both succeed
- Directory-prefix overlap detected (pathA = `src/python/ndjson/`, pathB = `src/python/ndjson/models.py` → conflict)

---

### TC-CONC-006: Checkpoint Module
**Status:** CLOSED
**Prerequisites:** TC-CONC-003

**New file:** `tools/supervisor/concurrency/checkpoint.py`

**Storage:** `.local/supervisor/checkpoints/` — already gitignored via `.local/` rule in `.gitignore` line 7.

```python
CHECKPOINT_DIR = Path(".local/supervisor/checkpoints")

class CheckpointManager:
    def __init__(self, db_path: Path, repo_root: Path | None = None):
        self.db_path = db_path
        self.repo_root = repo_root or Path.cwd()
        from tools.supervisor.control_index.db import ensure_db
        ensure_db(db_path)

    def create(self, task_id: str, worker_id: str, description: str = '') -> str:
        """Capture current working-tree + staged diffs as a patch file.

        Returns checkpoint_id. Safe to call on a clean tree (empty patch recorded).
        """
        import secrets, subprocess
        from datetime import datetime, timezone

        cid = f"ckpt-{task_id}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}-{secrets.token_hex(4)}"

        # Get HEAD SHA
        base_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(self.repo_root),
            capture_output=True, text=True, timeout=10
        ).stdout.strip() or "unknown"

        # Capture both staged and unstaged changes
        diff_staged = subprocess.run(
            ["git", "diff", "--cached", "HEAD"], cwd=str(self.repo_root),
            capture_output=True, text=True, timeout=30
        ).stdout
        diff_unstaged = subprocess.run(
            ["git", "diff", "HEAD"], cwd=str(self.repo_root),
            capture_output=True, text=True, timeout=30
        ).stdout
        patch_content = diff_staged + diff_unstaged

        # Changed files
        status_out = subprocess.run(
            ["git", "status", "--porcelain"], cwd=str(self.repo_root),
            capture_output=True, text=True, timeout=10
        ).stdout
        changed_files = [line[3:].strip() for line in status_out.splitlines() if line.strip()]

        # Write patch file
        ckpt_dir = self.repo_root / CHECKPOINT_DIR
        ckpt_dir.mkdir(parents=True, exist_ok=True)
        patch_path = ckpt_dir / f"{cid}.patch"
        patch_path.write_text(patch_content, encoding="utf-8")

        # Register in DB
        with _connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO concurrency_checkpoints
                (checkpoint_id, task_id, worker_id, description,
                 base_sha, patch_path, changed_files, created_at, status)
                VALUES (?,?,?,?,?,?,?,'VALID')
            """, (cid, task_id, worker_id, description, base_sha,
                  str(patch_path.resolve()), json.dumps(changed_files),
                  datetime.now(timezone.utc).isoformat()))
            conn.commit()
        return cid

    def restore(self, checkpoint_id: str, *, stash_first: bool = True) -> bool:
        """Apply checkpoint patch to working tree.

        stash_first: if True and tree is dirty, git stash before applying.
        Returns True on success, False if patch fails to apply.
        Raises StaleBaseRevision if current HEAD != checkpoint base_sha.
        """
        import subprocess
        with _connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM concurrency_checkpoints WHERE checkpoint_id=?",
                (checkpoint_id,)
            ).fetchone()
        if not row:
            raise CheckpointError(f"Checkpoint not found: {checkpoint_id}")

        patch_path = Path(row["patch_path"])
        if not patch_path.exists():
            raise CheckpointError(f"Patch file missing: {patch_path}")

        # Stale base check
        current_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(self.repo_root),
            capture_output=True, text=True, timeout=10
        ).stdout.strip()
        if current_sha and row["base_sha"] != current_sha:
            # Warn but attempt anyway (integration drift scenario)
            import warnings
            warnings.warn(StaleBaseRevision(row["base_sha"], current_sha))

        # Stash dirty tree if requested
        if stash_first:
            status = subprocess.run(
                ["git", "status", "--porcelain"], cwd=str(self.repo_root),
                capture_output=True, text=True, timeout=10
            ).stdout.strip()
            if status:
                subprocess.run(["git", "stash", "push", "--include-untracked",
                                "-m", f"pre-restore-{checkpoint_id}"],
                               cwd=str(self.repo_root), timeout=30)

        if not patch_path.stat().st_size:
            return True  # Empty patch — clean tree checkpoint; no-op

        result = subprocess.run(
            ["git", "apply", str(patch_path)],
            cwd=str(self.repo_root), capture_output=True, text=True, timeout=60
        )
        return result.returncode == 0

    def list(self, task_id: str) -> list[dict]:
        with _connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM concurrency_checkpoints WHERE task_id=? ORDER BY created_at DESC",
                (task_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    def invalidate(self, checkpoint_id: str, reason: str = '') -> None:
        with _connect(self.db_path) as conn:
            conn.execute(
                "UPDATE concurrency_checkpoints SET status='SUPERSEDED' WHERE checkpoint_id=?",
                (checkpoint_id,)
            )
            conn.commit()

    def cleanup_old(self, task_id: str, keep: int = 3) -> int:
        """Keep newest `keep` checkpoints for task; delete older patch files + mark SUPERSEDED."""
        rows = self.list(task_id)
        to_remove = rows[keep:]
        count = 0
        with _connect(self.db_path) as conn:
            for row in to_remove:
                pp = Path(row["patch_path"])
                if pp.exists():
                    pp.unlink(missing_ok=True)
                conn.execute(
                    "UPDATE concurrency_checkpoints SET status='SUPERSEDED' WHERE checkpoint_id=?",
                    (row["checkpoint_id"],)
                )
                count += 1
            conn.commit()
        return count
```

**Completion criteria:**
- `create()` produces a `.patch` file in `.local/supervisor/checkpoints/`
- `restore()` on empty patch returns True without modifying tree
- `restore()` on non-empty patch applies diff back to tree (round-trip test passes)
- `cleanup_old(keep=2)` deletes patch files and marks DB rows SUPERSEDED

---

### TC-CONC-007: Headless Controller Startup Guard
**Status:** CLOSED
**Prerequisites:** TC-CONC-004 (MissionLock), TC-CONC-006 (CheckpointManager)
**Files modified:** `tools/supervisor/sprint_executor.py`

**Step 1 — Add two helper functions** after the existing `_sha256()` function (line 114):

```python
def _db_path() -> Path:
    """Return absolute path to control-index.db."""
    return _REPO / ".local" / "supervisor" / "control-index.db"


def _get_session_id() -> str:
    """Return current session identity from continuation_identity.py."""
    try:
        sys.path.insert(0, str(_HERE))
        from continuation_identity import get_or_create_session_identity
        return get_or_create_session_identity(_REPO)["session_id"]
    except Exception:
        import socket, os
        return f"{socket.gethostname()}-{os.getpid()}"
```

**Step 2 — Modify `cmd_run_loop()`** — add mission lock acquisition block BEFORE
the `while True:` loop (at approximately line 394):

```python
def cmd_run_loop(repo_root: Path, *, max_cycles: int = 12, dry_run: bool = False) -> int:
    """..."""
    # ── MISSION LOCK: must be acquired before any work begins ──────────────
    from tools.supervisor.concurrency.mission_lock import MissionLock
    from tools.supervisor.concurrency.errors import MissionLockConflict

    MISSION_ID = "format-factory-main"
    _lock = MissionLock(db_path=_db_path())

    try:
        branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])  # list not string
        session_id = _get_session_id()
    except Exception:
        branch, session_id = "unknown", "unknown"

    try:
        _lock_cm = _lock.locked(
            mission_id=MISSION_ID,
            controller_type="headless",
            session_id=session_id,
            branch=branch,
        )
        _lock_cm.__enter__()
    except MissionLockConflict as e:
        print(
            f"\nBLOCKED: Mission '{MISSION_ID}' is locked by "
            f"{e.existing_controller} (PID {e.existing_pid}).\n"
            f"Last heartbeat: {e.heartbeat_at}\n"
            f"Cannot start headless run-loop while another controller is active.\n"
            f"Run 'python tools/supervisor/sprint_executor.py status' for details.",
            file=sys.stderr,
        )
        return 1
    # ────────────────────────────────────────────────────────────────────────

    cycle = 0
    autonomous_cycle_py = repo_root / "tools" / "supervisor" / "autonomous_cycle.py"

    try:
        while True:
            cycle += 1
            # ... (existing loop body unchanged) ...

            # ── PRE-SPRINT CHECKPOINT ────────────────────────────────────
            sprint_id_for_ckpt = f"autonomous-loop-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
            try:
                from tools.supervisor.concurrency.checkpoint import CheckpointManager
                ckpt = CheckpointManager(db_path=_db_path(), repo_root=repo_root)
                ckpt_id = ckpt.create(
                    task_id=sprint_id_for_ckpt,
                    worker_id="sprint_executor_headless",
                    description="pre-sprint working-tree snapshot",
                )
                print(f"[Checkpoint] Working-tree state saved: {ckpt_id}")
            except Exception as ckpt_err:
                print(f"[Checkpoint] Warning: checkpoint creation failed (non-blocking): {ckpt_err}")
            # ─────────────────────────────────────────────────────────────

            # ... (rest of existing loop body) ...

    finally:
        try:
            _lock_cm.__exit__(None, None, None)
        except Exception:
            pass

    return 0
```

**Step 3 — Modify `cmd_status()`** — add lock diagnostic output:

```python
def cmd_status(repo_root: Path) -> int:
    signal = _load_continuation_signal(repo_root)
    # ... existing code ...
    # Add after existing output:
    try:
        from tools.supervisor.concurrency.mission_lock import MissionLock
        ml = MissionLock(db_path=_db_path())
        active = ml.get_active_lock("format-factory-main")
        output["mission_lock"] = active or {"status": "no active lock"}
    except Exception as e:
        output["mission_lock"] = {"error": str(e)}
    print(json.dumps(output, indent=2))
    return 0
```

**Completion criteria:**
- `python tools/supervisor/sprint_executor.py run-loop --dry-run` acquires lock, prints lock_id, releases lock
- Second concurrent invocation exits 1 with BLOCKED message
- `status` subcommand shows active lock info

---

### TC-CONC-007b: Interactive /autonomous-loop Guard
**Status:** CLOSED
**Prerequisites:** TC-CONC-004 (MissionLock)
**Files modified:** `.supervisor/skill-registry.yaml` (the `/autonomous-loop` skill prompt)

The interactive path must also acquire the mission lock. Since `/autonomous-loop`
is a skill (not a Python script), the guard is implemented as a PREFLIGHT step
in the skill's prompt template.

**Add to the `/autonomous-loop` skill prompt template** in `.supervisor/skill-registry.yaml`
under the `autonomous-loop` entry, prepend this preflight block:

```
PREFLIGHT — MISSION LOCK (mandatory, run before any sprint work):

1. Check for an active mission lock:
   python tools/supervisor/sprint_executor.py status
   Look for "mission_lock": {"status": "ACTIVE", ...} in the output.

2. If an ACTIVE lock exists and the controller_type is "headless":
   - Print: "BLOCKED: Headless run-loop holds mission lock (PID X). Stop it before starting interactive session."
   - STOP. Do not proceed.

3. If no active lock OR the active lock belongs to an interactive session:
   - Acquire the lock:
     python -c "
     from tools.supervisor.concurrency.mission_lock import MissionLock
     from tools.supervisor.control_index import DEFAULT_DB_PATH
     from pathlib import Path
     import json, sys
     ml = MissionLock(db_path=Path('.') / '.local/supervisor/control-index.db')
     try:
         cm = ml.locked('format-factory-main', 'interactive', 'interactive-session', 'main')
         cm.__enter__()
         # Write lock_id to .local/supervisor/interactive-lock-session.json
         Path('.local/supervisor').mkdir(parents=True, exist_ok=True)
         print('LOCK_ACQUIRED')
     except Exception as e:
         print(f'LOCK_FAILED: {e}', file=sys.stderr)
         sys.exit(1)
     "
   - Record the lock acquisition in your evidence declaration.

4. When the interactive session ends (final closeout), release the lock:
   (The context manager in step 3 handles release if the process exits normally.)
```

**Note:** Full enforcement requires the skill to be invoked through the skill
runner which calls this preflight. For VSCode interactive sessions (where the
user runs `/autonomous-loop` manually), the preflight is advisory but recorded
in evidence. Machine enforcement exists only in `sprint_executor.py`.

**Completion criteria:**
- `skill-registry.yaml` autonomous-loop entry has preflight block
- The preflight is documented and references `sprint_executor.py status`

---

### TC-CONC-008: Pre-Write Path Ownership Guards in autonomous_cycle.py
**Status:** CLOSED
**Prerequisites:** TC-CONC-004 (errors.py), TC-CONC-005 (WorkerClaims)
**Files modified:** `tools/supervisor/autonomous_cycle.py`

**`_extract_declared_paths(declaration_path: Path) -> list[str]`:**

The function receives the declaration file's `Path` (autonomous_cycle.py takes a
Path object, not a dict). It reads the YAML and extracts paths:

```python
def _extract_declared_paths(declaration_path: Path) -> list[str]:
    """Extract all file paths declared in an evidence-declaration.yaml.

    Sources:
      - evidence_paths (list of str, may include .local/ paths — skip those)
      - changed_files (list of str, repo-relative)
    Returns normalized repo-relative paths, deduplicated, .local excluded.
    """
    import yaml
    try:
        data = yaml.safe_load(declaration_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    paths = set()
    for item in data.get("planned_work_items", []):
        for p in item.get("evidence_paths", []):
            if isinstance(p, str) and not p.startswith(".local"):
                paths.add(p.lstrip("./"))
    for p in data.get("changed_files", []):
        if isinstance(p, str) and not p.startswith(".local"):
            paths.add(p.lstrip("./"))
    return list(paths)
```

**Integration point in `run_cycle()` (Step 1, after declaration validation):**

After the existing Step 1 (validate declaration) and before Step 2 (inspect evidence),
insert:

```python
# ── PATH OWNERSHIP GUARD (TC-CONC-008) ─────────────────────────────────────
_declared_paths = _extract_declared_paths(declaration_path)
_worker_id = f"autonomous_cycle_{run_id}"
_db = _repo_root / ".local" / "supervisor" / "control-index.db"
_active_lock = None

try:
    from tools.supervisor.concurrency.worker_claim import WorkerClaims
    from tools.supervisor.concurrency.errors import PathOwnershipConflict
    _claims_mgr = WorkerClaims(db_path=_db)
    _conflicts = _claims_mgr.claim(
        worker_id=_worker_id,
        task_id=declared_scope.get("task_id", run_id),
        paths=_declared_paths,
        mission_id="format-factory-main",
        lock_id="unknown",  # no mission lock held by cycle itself; claims are advisory
        mode="WRITE",
    )
    logger.info(f"Path ownership claimed: {len(_conflicts)} paths")
except PathOwnershipConflict as poe:
    hard_stops.append({
        "type": "PATH_OWNERSHIP_CONFLICT",
        "path": poe.path,
        "existing_owner": poe.existing_worker_id,
        "task": poe.existing_task_id,
        "claim_id": poe.existing_claim_id,
    })
    # Return exit 3 to signal rework needed (not a crash)
    return _exit(3, hard_stops=hard_stops, ...)
except Exception as e:
    logger.warning(f"Path ownership check failed (non-blocking): {e}")
    _claims_mgr = None
# ─────────────────────────────────────────────────────────────────────────────
```

**In the finally block** at end of `run_cycle()`, add:
```python
if _claims_mgr is not None and _worker_id:
    try:
        _claims_mgr.release_all(_worker_id)
    except Exception:
        pass
```

**Completion criteria:**
- autonomous_cycle.py acquires path claims after Step 1
- PATH_OWNERSHIP_CONFLICT added to hard_stops causes exit 3
- Claims are released in finally block even on exception

---

### TC-CONC-009: Tests
**Status:** CLOSED
**Prerequisites:** TC-CONC-004, TC-CONC-005, TC-CONC-006, TC-CONC-007, TC-CONC-008

**Critical requirement for ALL unit tests:** Use pytest `tmp_path` fixture for DB
isolation. Never use the production `.local/supervisor/control-index.db`.

```python
# Pattern for all test files:
@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / "test-control-index.db"
    from tools.supervisor.control_index.db import init_db
    init_db(db_path)
    return db_path
```

**New files:**
- `tests/supervisor/test_mission_lock.py` — 14 test cases
- `tests/supervisor/test_worker_claims.py` — 10 test cases
- `tests/supervisor/test_checkpoint.py` — 8 test cases
- `tests/supervisor/test_concurrency_pilots.py` — 10 subprocess/integration pilots

#### `test_mission_lock.py` — 14 cases

```
test_01_first_acquire_returns_lock_id
test_02_second_acquire_same_mission_raises_conflict
test_03_stale_heartbeat_and_dead_pid_allows_steal
test_04_fresh_heartbeat_live_pid_cannot_steal
test_05_release_allows_second_acquire
test_06_heartbeat_extends_lease_expiry
test_07_dead_pid_expired_heartbeat_stealable
test_08_live_pid_expired_heartbeat_NOT_stealable (pid check takes precedence)
test_09_nonexistent_db_auto_created_on_acquire
test_10_context_manager_releases_on_exception
test_11_get_active_lock_returns_none_after_release
test_12_transition_log_records_acquired_released
test_13_idempotent_double_release_is_safe
test_14_concurrent_subprocess_exactly_one_wins (subprocess test)
```

For test_03/test_07: Use `heartbeat_ttl=1` (1 second) + mock dead PID (use PID=99999).
For test_08: Use `heartbeat_ttl=1` but actual live PID + sleep 2s.
For test_14: Launch 5 subprocesses via `multiprocessing`, each calls `_acquire()`,
assert exactly 1 succeeds.

#### `test_worker_claims.py` — 10 cases

```
test_01_claim_returns_claim_ids
test_02_disjoint_paths_both_workers_succeed
test_03_same_file_write_write_raises_conflict
test_04_read_read_no_conflict
test_05_expired_claim_does_not_block_new
test_06_release_all_removes_worker_claims
test_07_directory_prefix_overlap_detected
test_08_context_manager_releases_on_exception
test_09_list_active_returns_only_active
test_10_check_overlap_returns_empty_when_none
```

For test_05: Insert a claim with `lease_expires` in the past, then claim same path.
For test_07: Worker A claims `src/python/ndjson/`, Worker B claims
`src/python/ndjson/models.py` → PathOwnershipConflict.

#### `test_checkpoint.py` — 8 cases

```
test_01_create_saves_patch_file
test_02_create_on_clean_tree_saves_empty_patch
test_03_list_returns_newest_first
test_04_restore_round_trip (create→dirty→restore→verify)
test_05_invalidate_marks_superseded
test_06_cleanup_old_keep_2_removes_oldest
test_07_create_captures_staged_changes
test_08_base_sha_matches_head_at_checkpoint_time
```

For test_04: Use a temp git repo (initialize with `git init` in tmp_path).

#### `test_concurrency_pilots.py` — 10 pilots

Each pilot must write an evidence file to `reports/concurrency/pilot-evidence/`:
`pilot-{N:02d}-{name}-result.json` with fields: pilot_number, name, passed, details.

**Pilot 1 — Competing controllers** (subprocess)
```
evidence_output: reports/concurrency/pilot-evidence/pilot-01-competing-controllers-result.json
steps:
  1. Start subprocess A: acquire lock in a helper script, signal via Event, sleep 10s
  2. In-process: attempt lock acquisition
  3. Assert MissionLockConflict raised within 2s
  4. Terminate subprocess A
  5. Wait heartbeat_ttl + 2s (with ttl=2, wait 4s)
  6. Re-acquire lock in-process → succeeds
passed: MissionLockConflict raised AND second acquire succeeds after kill
```

**Pilot 2 — Safe parallel lanes** (in-process)
```
evidence_output: reports/concurrency/pilot-evidence/pilot-02-parallel-lanes-result.json
steps:
  1. Worker A claims src/python/ndjson/models.py (WRITE)
  2. Worker B claims src/python/csv/models.py (WRITE)
  3. Assert both claim_ids returned (no conflict)
  4. Assert DB has 2 ACTIVE rows
passed: both claims exist in DB
```

**Pilot 3 — Overlapping path claims** (in-process)
```
evidence_output: reports/concurrency/pilot-evidence/pilot-03-overlapping-claims-result.json
steps:
  1. Worker A claims src/python/ndjson/models.py (WRITE)
  2. Worker B attempts same path
  3. Assert PathOwnershipConflict raised
  4. Assert DB still has exactly 1 ACTIVE claim for that path
passed: exception raised, no double-claim in DB
```

**Pilot 4 — Lost-lock protection** (heartbeat TTL parameterized to 2s)
```
evidence_output: reports/concurrency/pilot-evidence/pilot-04-lost-lock-result.json
steps:
  1. Acquire lock with heartbeat_ttl=2
  2. Immediately stop the heartbeat timer (call timer.cancel() after 1 interval)
  3. Also create a checkpoint
  4. Wait 3s (heartbeat expires) + mock PID as dead (pid=99999 in the row)
  5. New controller acquires lock → succeeds (steal)
  6. Verify original checkpoint patch file still exists on disk
passed: lock stolen AND checkpoint patch file present
```

**Pilot 5 — Crash recovery** (temp git repo)
```
evidence_output: reports/concurrency/pilot-evidence/pilot-05-crash-recovery-result.json
steps:
  1. In a temp git repo, make an uncommitted change to a file
  2. Create checkpoint (saves the diff)
  3. Simulate crash: discard working-tree change (git checkout -- .)
  4. Restore from checkpoint
  5. Assert the change is back in working tree
passed: restored file content matches original change
```

**Pilot 6 — Integration drift** (temp git repo)
```
evidence_output: reports/concurrency/pilot-evidence/pilot-06-integration-drift-result.json
steps:
  1. Checkpoint at HEAD (record base_sha)
  2. Amend HEAD (git commit --allow-empty -m "drift") → new SHA
  3. Call restore() on checkpoint
  4. Assert StaleBaseRevision warning emitted
passed: warning raised with correct old/new SHAs
```

**Pilot 7 — R1227-style loss prevention** (subprocess, real working tree)
```
evidence_output: reports/concurrency/pilot-evidence/pilot-07-r1227-prevention-result.json
steps:
  1. Write a sentinel string to a test file (do NOT commit)
  2. Record sentinel in variable
  3. Attempt to start headless run-loop as subprocess
  4. Assert: subprocess exits 1 with BLOCKED message
     (interactive session implicitly holds no machine lock yet, BUT
      headless sees no active lock and would acquire it — in this pilot
      the interactive session first acquires the lock, then headless attempts)
  5. Read test file — sentinel string must still be there (not wiped)
passed: BLOCKED message in subprocess stderr AND sentinel file unchanged
```

**Pilot 8 — Task closure survival** (in-process)
```
evidence_output: reports/concurrency/pilot-evidence/pilot-08-task-closure-result.json
steps:
  1. Create checkpoint for task A
  2. Close task A (invalidate checkpoint → SUPERSEDED)
  3. "Integrate lane B": write a new file and commit in temp repo
  4. Assert checkpoint_id record still exists in DB (status=SUPERSEDED)
  5. Assert patch file on disk is still present (invalidate does NOT delete files)
passed: DB row exists, patch file exists
```

**Pilot 9 — SQLite contention** (multiprocessing)
```
evidence_output: reports/concurrency/pilot-evidence/pilot-09-sqlite-contention-result.json
steps:
  1. Start 10 concurrent processes (multiprocessing.Process), each calls
     MissionLock(tmp_db).locked("test-mission", "headless", f"s{i}", "main")
     and records success/failure
  2. Collect results via multiprocessing.Queue
  3. Assert exactly 1 success, 9 MissionLockConflict
  4. Query DB: SELECT COUNT(*) FROM mission_locks WHERE mission_id='test-mission' AND status='ACTIVE'
  5. Assert count = 1
passed: exactly 1 ACTIVE row, exactly 9 conflicts
```

**Pilot 10 — Idempotency** (in-process)
```
evidence_output: reports/concurrency/pilot-evidence/pilot-10-idempotency-result.json
steps:
  1. Run full cycle: acquire lock → claim 3 paths → checkpoint → release lock → release claims
  2. Record DB row counts: mission_locks=1, worker_claims=3, checkpoints=1
  3. Run same cycle again from scratch (new lock_id, new claim_ids, new checkpoint_id)
  4. Record DB row counts: mission_locks=2, worker_claims=6, checkpoints=2
  5. Assert counts increased by EXACTLY the expected amounts (not doubled wrong)
  6. Assert no ACTIVE duplicates (only 1 new ACTIVE lock at a time)
passed: counts match expected increments, no duplicate ACTIVE rows
```

**Test execution commands:**
```bash
.venv/Scripts/pytest tests/supervisor/test_mission_lock.py -v
.venv/Scripts/pytest tests/supervisor/test_worker_claims.py -v
.venv/Scripts/pytest tests/supervisor/test_checkpoint.py -v
.venv/Scripts/pytest tests/supervisor/test_concurrency_pilots.py -v --timeout=60
```

**Completion criteria:** All 42 unit tests + 10 pilots PASS.

---

### TC-CONC-010: Incident Reports + Mutator Inventory Completion
**Status:** CLOSED
**Prerequisites:** TC-CONC-001, TC-CONC-002

This taskcard ensures the three report deliverables from TC-CONC-001 and TC-CONC-002
are complete and cross-referenced.

**Deliverables:**
- `reports/concurrency/incident-root-cause.yaml` (from TC-CONC-001)
- `reports/concurrency/lost-work-reconciliation.yaml` (from TC-CONC-001)
- `reports/concurrency/mutator-inventory.yaml` (from TC-CONC-002)

**Verification queries for completion gate counters:**

```bash
# UNINVENTORIED_MUTATORS — count entries in mutator-inventory.yaml missing required fields
python -c "
import yaml
data = yaml.safe_load(open('reports/concurrency/mutator-inventory.yaml'))
missing = [m['mutator_id'] for m in data
           if not all(k in m for k in ['lock_behavior','workspace_behavior','conflict_behavior'])]
print('UNINVENTORIED_MUTATORS =', len(missing))
"

# UNGOVERNED_MUTATION_PATHS — entries with lock_behavior: NONE and not READ-ONLY
python -c "
import yaml
data = yaml.safe_load(open('reports/concurrency/mutator-inventory.yaml'))
ungov = [m['mutator_id'] for m in data
         if m.get('lock_behavior') == 'NONE' and m.get('workspace_behavior') != 'READ_ONLY']
print('UNGOVERNED_MUTATION_PATHS =', len(ungov))
# After hardening, headless and interactive controllers should report MISSION_LOCK
# All others remain NONE but are bounded-scope (advisory acceptable if READ_ONLY)
"

# UNRECONCILED_LOST_OR_ORPHANED_WORK
python -c "
import yaml
data = yaml.safe_load(open('reports/concurrency/lost-work-reconciliation.yaml'))
print('UNRECONCILED_LOST_OR_ORPHANED_WORK =', data.get('unreconciled_count', 0))
"
```

**Completion criteria:** All three report files exist, UNINVENTORIED_MUTATORS = 0.

---

### TC-CONC-011: Final Completion Gate + Verdict Report
**Status:** CLOSED
**Prerequisites:** ALL previous taskcards (TC-CONC-001 through TC-CONC-010)

**Deliverable:** `reports/concurrency/final-report.md`

**Counter verification block** (must run and show all zeros):

```bash
# Active competing controllers in DB
python -c "
from tools.supervisor.control_index.db import connect
from pathlib import Path
db = Path('.local/supervisor/control-index.db')
if db.exists():
    with connect(db) as c:
        n = c.execute(\"SELECT COUNT(*) FROM mission_locks WHERE status='ACTIVE'\").fetchone()[0]
        print('ACTIVE_COMPETING_MISSION_CONTROLLERS =', max(0, n-1))
else:
    print('ACTIVE_COMPETING_MISSION_CONTROLLERS = 0 (no DB)')
"

# Overlapping write claims
python -c "
from tools.supervisor.control_index.db import connect
from pathlib import Path
db = Path('.local/supervisor/control-index.db')
if db.exists():
    with connect(db) as c:
        rows = c.execute(
            \"SELECT resource_pattern, COUNT(*) as n FROM worker_claims WHERE status='ACTIVE' AND mode='WRITE' GROUP BY resource_pattern HAVING n>1\"
        ).fetchall()
        print('OVERLAPPING_ACTIVE_WRITE_CLAIMS =', len(rows))
else:
    print('OVERLAPPING_ACTIVE_WRITE_CLAIMS = 0 (no DB)')
"

# Failed pilots — count pilot evidence files with passed=false
python -c "
import json, os, glob
failed = 0
for f in sorted(glob.glob('reports/concurrency/pilot-evidence/pilot-*-result.json')):
    data = json.load(open(f))
    if not data.get('passed', False): failed += 1
print('FAILED_REQUIRED_PILOTS =', failed)
"
```

**Final report structure:**
```markdown
# Concurrent Agent Execution Hardening — Final Report
date: YYYY-MM-DD
mission_id: CONC-HARDENING-2026-07-02

## Incident Summary
## Root Cause
## Implementation Summary
## Counter Verification
UNINVENTORIED_MUTATORS = 0
UNGOVERNED_MUTATION_PATHS = 0
ACTIVE_COMPETING_MISSION_CONTROLLERS = 0
OVERLAPPING_ACTIVE_WRITE_CLAIMS = 0
SHARED_WORKING_TREE_MUTATION_WORKERS = 0
MUTATIONS_WITHOUT_VALID_LEASE = 0
TASKS_CLOSED_WITHOUT_SURVIVING_DIFF = 0
UNRECONCILED_LOST_OR_ORPHANED_WORK = 0
FAILED_REQUIRED_PILOTS = 0
MATERIAL_SECOND_RUN_CHANGES = 0
## Test Results
## Pilot Results
## Remaining Risks + Assumptions
## Verdict
```

**Allowed verdicts:**
- `CONCURRENT_AGENT_EXECUTION_HARDENED_RECOVERY_PROVEN_AND_IDEMPOTENT`
- `CONCURRENT_AGENT_EXECUTION_REQUIRES_REWORK`

**Completion criteria:** final-report.md exists, all 10 counters = 0, verdict issued.

---

## Files Created/Modified Summary

### New files
| Path | TC | Purpose |
|------|----|---------|
| `tools/supervisor/concurrency/__init__.py` | TC-CONC-004 | Package init |
| `tools/supervisor/concurrency/errors.py` | TC-CONC-004 | Exception classes |
| `tools/supervisor/concurrency/mission_lock.py` | TC-CONC-004 | SQLite-backed mission lock |
| `tools/supervisor/concurrency/worker_claim.py` | TC-CONC-005 | Atomic path ownership |
| `tools/supervisor/concurrency/checkpoint.py` | TC-CONC-006 | Git-diff checkpoint manager |
| `tests/supervisor/test_mission_lock.py` | TC-CONC-009 | 14 mission lock tests |
| `tests/supervisor/test_worker_claims.py` | TC-CONC-009 | 10 path claim tests |
| `tests/supervisor/test_checkpoint.py` | TC-CONC-009 | 8 checkpoint tests |
| `tests/supervisor/test_concurrency_pilots.py` | TC-CONC-009 | 10 concurrency pilots |
| `reports/concurrency/incident-root-cause.yaml` | TC-CONC-001 | Incident record |
| `reports/concurrency/lost-work-reconciliation.yaml` | TC-CONC-001 | Recovery proof |
| `reports/concurrency/mutator-inventory.yaml` | TC-CONC-002 | All mutators |
| `reports/concurrency/pilot-evidence/pilot-{01-10}-*-result.json` | TC-CONC-009 | Pilot proofs |
| `reports/concurrency/final-report.md` | TC-CONC-011 | Verdict report |

### Modified files
| Path | TC | Change |
|------|----|--------|
| `tools/supervisor/control_index/schema.sql` | TC-CONC-003 | Add 4 tables + partial unique index |
| `tools/supervisor/control_index/__init__.py` | TC-CONC-003 | `SCHEMA_VERSION = 1` → `2` |
| `tools/supervisor/sprint_executor.py` | TC-CONC-007 | Add `_db_path()`, `_get_session_id()`, mission lock + pre-sprint checkpoint in `cmd_run_loop()`, lock diagnostic in `cmd_status()` |
| `tools/supervisor/autonomous_cycle.py` | TC-CONC-008 | Add `_extract_declared_paths()`, path claim acquisition, release in finally |
| `.supervisor/skill-registry.yaml` | TC-CONC-007b | Add preflight block to autonomous-loop skill |

---

## Remaining Risks + Assumptions

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Interactive session holds no machine lock unless preflight runs | MEDIUM | TC-CONC-007b adds skill preflight; full enforcement deferred to future sprint with skill runner integration |
| `psutil` may not be installed | LOW | Fallback to `os.kill(pid, 0)` pattern specified in TC-CONC-004 |
| Pilot 7 requires true concurrent process state to reproduce R1227 | MEDIUM | Pilot uses subprocess + temporary uncommitted file; verifies BLOCKED output + file unchanged |
| `BEGIN EXCLUSIVE` may cause timeout under high SQLite contention | LOW | `PRAGMA busy_timeout = 5000` (inherited from db.py) provides 5s retry window |
| Stale base revision in restore() is a warning not an error | LOW | Documented; StaleBaseRevision raised as warning to allow recovery scenarios |

---

## Taskcard Status Summary (for lifecycle_audit.py)

| Taskcard | Title | Status |
|----------|-------|--------|
| TC-CONC-001 | Incident Bind + Root Cause Report | CLOSED |
| TC-CONC-002 | Mutator Inventory | CLOSED |
| TC-CONC-003 | SQLite Concurrency Schema + Version Bump | CLOSED |
| TC-CONC-004 | Mission Lock Module | CLOSED |
| TC-CONC-005 | Worker Path Claim Module | CLOSED |
| TC-CONC-006 | Checkpoint Module | CLOSED |
| TC-CONC-007 | Headless Controller Startup Guard | CLOSED |
| TC-CONC-007b | Interactive /autonomous-loop Guard | CLOSED |
| TC-CONC-008 | Pre-Write Path Ownership Guards | CLOSED |
| TC-CONC-009 | Tests (42 unit + 10 pilots) | CLOSED |
| TC-CONC-010 | Incident Reports + Mutator Completion | CLOSED |
| TC-CONC-011 | Final Completion Gate + Verdict Report | CLOSED |


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-02T13:42:50.698882+00:00"
  locked_by: "cd6ed0f7aef8"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
  closure_note: "Duplicate OPEN TC-CONC-011 row removed; all 12 taskcards CLOSED. CONC-HARDENING-2026-07-02 complete."
-->
