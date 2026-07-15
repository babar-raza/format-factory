# Plan: Fix tests/supervisor/ Test Suite Hang

## Context

pytest hangs with zero output when targeting `tests/supervisor/` (407 files, 94K lines),
while a single targeted test file runs instantly. Three separate invocations (full run,
foreground-with-timeout, scoped/filtered subset) all reproduced. 14 Python processes are
running system-wide (8 with 580-850 MB memory — likely hung pytest sessions).

The repo lives on an OneDrive-synced path (`C:\Users\prora\OneDrive\Documents\GitHub\format-factory`),
and the supervisor test infrastructure has a 212 MB SQLite database (`control-index.db`)
at `.local/supervisor/` with WAL mode, 5-second busy_timeout, and `BEGIN EXCLUSIVE`
transactions in the concurrency layer.

---

## Assessment

### Assessment Scope
- **System:** pytest test suite under `tests/supervisor/` (407 test files)
- **Intended outcome:** Tests run reliably and complete in reasonable time
- **Sources of truth:** `pyproject.toml`, conftest files, `tools/supervisor/control_index/db.py`, test files
- **Evidence inspected:** All conftest.py files (4 in hierarchy), db.py, schema.sql, worker_claim.py, mission_lock.py, autonomous_orchestrator.py, continuation_state.py, atomic_io.py, 20+ test files, running processes, lock file state, WAL/SHM file state

### Current-State Reconstruction

**Execution flow:**
1. `pytest tests/supervisor/` starts → loads plugins (pytest-timeout, pytest-cov)
2. Reads conftest chain: `tests/conftest.py` → `tests/supervisor/conftest.py`
3. `tests/supervisor/conftest.py` does `sys.path.insert()` at import time (lines 11-13)
4. Collection phase: pytest imports all 407 test modules to discover tests
5. Each module's top-level code executes: `sys.path.insert()`, imports from `tools/supervisor/`
6. First import of `control_index.db` triggers `_SCHEMA_SQL = Path(...).read_text()` (line 13) — reads 525-line schema.sql from OneDrive
7. After collection, `pytest_collection_modifyitems` iterates all items 4+ times
8. Tests begin executing in filesystem order (`test_a*` first)
9. Early tests include `test_autonomous_orchestrator.py` (touches real LOCK_PATH) and `test_control_index_sync.py` (20 full rebuild() calls scanning entire repo)

**Components actually used:**
- `control_index/db.py`: import-time file read, WAL mode, busy_timeout
- `concurrency/worker_claim.py`: `BEGIN EXCLUSIVE` transactions (in execution, not collection)
- `concurrency/mission_lock.py`: SQLite-backed lock with heartbeat thread
- `autonomous_orchestrator.py`: JSON cooperative lock at `.local/supervisor/orchestrator.lock`

### Symptoms
1. Zero output from pytest for extended periods across 3 invocations
2. Small 8-test file runs instantly in same environment
3. 14 Python processes running (8 with 580-850 MB — likely hung pytest sessions)
4. Issue is consistent and reproducible

### Root Causes

**RC-1: Collection + early-execution bottleneck on OneDrive** (HIGH confidence)
- Evidence: 407 file collection + first tests calling `rebuild()` scanning entire repo through OneDrive VFS
- First boundary: OneDrive virtual filesystem I/O for 407 file imports
- Scope: All tests/supervisor/ runs
- Why missed: Small files don't trigger the same volume of OneDrive I/O
- OneDrive's "Files On-Demand" can require cloud fetch for each file stat/read

**RC-2: test_control_index_sync.py calls rebuild() 20 times** (HIGH confidence)
- Evidence: Each `rebuild()` invokes 18 ingestors scanning hundreds of repo files through OneDrive
- First boundary: `rebuild(db_path, _REPO)` at lines 31, 36, 46, 65, 71, 90, 95, 101, 110, 123, 132, 145, 159, 171, 184, 201, 218, 232, 244, 258
- Scope: This single file could take 20+ minutes (60s × 20 rebuilds)
- Why missed: Test worked on local disk; OneDrive I/O amplifies latency

**RC-3: Tests touching production state without isolation** (MEDIUM confidence)
- Evidence: `test_autonomous_orchestrator.py` and `test_orchestrator_resume.py` have autouse fixtures operating on real `LOCK_PATH` and `STATE_DIR`
- `save_orchestrator_state()` and `write_stop_reason()` write to real `.local/supervisor/` paths
- These tests modify real state that concurrent processes may also be using

**RC-4: Subprocess calls without timeout (15+ files)** (MEDIUM confidence)
- Evidence: `subprocess.run()` without `timeout=` in test_sprint_executor.py, test_build_capability_routes.py, test_detect_ad_hoc_execution.py, test_lane_pipeline_integration.py, test_machinery_mission_ledger.py, test_r90_poc_gap_selector.py, test_run_skill_idempotency.py, test_scan_residual_bypasses.py, test_skill_inventory.py, test_validate_skill_contracts.py, test_capability_wire_tc_wire_001.py, test_validate_prompt_registry.py, test_pilots_group_gh.py, test_phase2_two_track.py
- On Windows, pytest-timeout (thread method) cannot kill child processes

**RC-5: Concurrent process amplification** (MEDIUM confidence)
- Evidence: 14 Python processes (8 large) competing for OneDrive I/O
- Previous pytest runs likely hung and were not killed, accumulating over attempts

### Structural Weaknesses
1. No production-state isolation boundary in test conftest
2. No subprocess timeout enforcement
3. 20 redundant rebuild() calls in one test file (should share a module-scoped fixture)
4. No `@pytest.mark.slow` separation for integration tests that scan real repo
5. SQLite database on OneDrive-synced path (fragile by design)
6. `timeout_method` not explicitly set in pyproject.toml (Windows default may be `signal`, which doesn't work)

### What Should Be Preserved
- `_restore_sys_path` module-scoped autouse fixture (tests/conftest.py)
- `_cap_grader_timeout` autouse fixture (tests/supervisor/conftest.py)
- Layer marker system (`pytest_collection_modifyitems`)
- `tmp_path`-based database fixtures (used correctly in most tests)
- Existing test assertions and expected values
- `continuation/conftest.py` fixtures (properly isolated)

---

## Implementation

### Phase 0: Immediate — Kill Stale Processes and Diagnose

Before any code changes, verify the diagnosis:

```bash
# Kill all hanging Python processes (manually review PIDs first)
taskkill /F /PID <pid> for each of the 8 large processes

# Test collection speed in isolation:
.venv/Scripts/pytest tests/supervisor/ --collect-only -q 2>&1 | head -5

# Time a single rebuild:
.venv/Scripts/python -c "
import time, sys; sys.path.insert(0, 'tools/supervisor')
from control_index.sync import rebuild
from pathlib import Path
t = time.time(); rebuild(Path('.local/supervisor/test-diag.db'), Path('.')); print(f'{time.time()-t:.1f}s')
"
```

### Phase 1: Lazy-load schema.sql in db.py

**File:** [db.py](tools/supervisor/control_index/db.py)

Change line 13 from:
```python
_SCHEMA_SQL = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")
```
to a lazy accessor:
```python
_SCHEMA_SQL: str | None = None

def _get_schema_sql() -> str:
    global _SCHEMA_SQL
    if _SCHEMA_SQL is None:
        _SCHEMA_SQL = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")
    return _SCHEMA_SQL
```

Update the single call site in `init_db()` (line 218): `conn.executescript(_SCHEMA_SQL)` → `conn.executescript(_get_schema_sql())`

**Rationale:** Removes a synchronous 525-line file read from import time. The read now happens only when `init_db()` is actually called. This eliminates I/O during collection for the 14+ test files that import `control_index.db`.

### Phase 2: Add conftest safety fixtures

**File:** [conftest.py](tests/supervisor/conftest.py)

Add two autouse fixtures after the existing `_cap_grader_timeout`:

**2a. Production database guard (session-scoped):**
```python
@pytest.fixture(autouse=True, scope="session")
def _guard_production_db(tmp_path_factory):
    """Prevent tests from connecting to the production control-index.db."""
    import control_index
    sentinel = tmp_path_factory.mktemp("guard") / "guard-control-index.db"
    original = control_index.DEFAULT_DB_PATH
    control_index.DEFAULT_DB_PATH = sentinel
    yield
    control_index.DEFAULT_DB_PATH = original
```

**2b. Subprocess timeout guard (function-scoped):**
```python
@pytest.fixture(autouse=True)
def _subprocess_timeout_guard(monkeypatch):
    """Enforce a 60s default timeout on all subprocess.run calls."""
    import subprocess as _sp
    _original_run = _sp.run
    def _guarded_run(*args, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = 60
        return _original_run(*args, **kwargs)
    monkeypatch.setattr(_sp, "run", _guarded_run)
```

### Phase 3: Isolate orchestrator tests from production state

**File:** [test_autonomous_orchestrator.py](tests/supervisor/test_autonomous_orchestrator.py)

Replace the `clean_lock` autouse fixture (lines 26-33) with:
```python
@pytest.fixture(autouse=True)
def _isolate_lock(tmp_path, monkeypatch):
    """Redirect the orchestrator lock file to tmp_path."""
    import tools.supervisor.autonomous_orchestrator as orch_mod
    monkeypatch.setattr(orch_mod, "LOCK_PATH", tmp_path / "orchestrator.lock")
```

Note: Only LOCK_PATH is redirected. State files remain on real paths because the
orchestrator's internal modules import paths at their own module level, making deep
monkeypatching fragile. State files are gitignored and designed for this use.

**File:** [test_orchestrator_resume.py](tests/supervisor/test_orchestrator_resume.py)

Apply the same `_isolate_lock` fixture pattern (replace the `clean_lock` fixture at lines 25-31).

### Phase 4: Reduce rebuild() calls in test_control_index_sync.py

**File:** [test_control_index_sync.py](tests/supervisor/test_control_index_sync.py)

Add a module-scoped shared database fixture:
```python
@pytest.fixture(scope="module")
def synced_db(tmp_path_factory):
    """Single rebuild() shared across read-only query tests."""
    db = tmp_path_factory.mktemp("shared_sync") / "shared.db"
    rebuild(db, _REPO)
    return db
```

Refactor `TestFTS5Search`, `TestQueries`, and `TestParity` to use `synced_db` instead of calling `rebuild()` per-test. These classes only do read-only queries after rebuild.

Add `@pytest.mark.slow` to `TestFullSync` (keeps its per-test rebuilds — tests rebuild behavior):
```python
@pytest.mark.slow
class TestFullSync:
    ...
```

This reduces 20 rebuild() calls to 8 (7 in TestFullSync + 1 shared).

### Phase 5: Configure pytest-timeout for Windows

**File:** [pyproject.toml](pyproject.toml)

Add to `[tool.pytest.ini_options]`:
```toml
timeout_method = "thread"
```

The `signal` method does not work on Windows (no `SIGALRM`). Explicitly setting `thread`
ensures timeouts are enforced. Keep `timeout = 120` (lowering is a separate concern).

---

## Verification Strategy

### V1: Collection speed (must pass before proceeding)
```bash
.venv/Scripts/pytest tests/supervisor/ --collect-only -q
# EXPECT: completes in <30s, prints "N tests collected"
```

### V2: State isolation
```bash
# Snapshot .local/supervisor/ state before test
dir .local\supervisor\ > before.txt
.venv/Scripts/pytest tests/supervisor/test_autonomous_orchestrator.py tests/supervisor/test_orchestrator_resume.py -v
dir .local\supervisor\ > after.txt
# EXPECT: no new files in .local/supervisor/ (diff should be empty)
```

### V3: Subprocess timeout enforcement
```bash
.venv/Scripts/pytest tests/supervisor/test_sprint_executor.py -v --timeout=30
# EXPECT: completes (passes or fails with TimeoutExpired), does not hang
```

### V4: Fast tests pass
```bash
.venv/Scripts/pytest tests/supervisor/ -m "not slow" --timeout=60 -x
# EXPECT: passes (or controlled failures, not hangs)
```

### V5: Full suite
```bash
.venv/Scripts/pytest tests/supervisor/ --timeout=120 -x -v
# EXPECT: completes within ~10 minutes, no hangs
```

### V6: Existing assertions unchanged
```bash
.venv/Scripts/pytest tests/supervisor/test_control_index_sync.py -v
# EXPECT: all assertions pass with shared fixture, same results as before
```

---

## Tradeoffs

| | Benefit | Cost |
|---|---|---|
| Lazy schema load | Eliminates import-time I/O | Negligible complexity (standard pattern) |
| Production DB guard | Prevents accidental state corruption | Tests relying on DEFAULT_DB_PATH must use tmp_path explicitly |
| Subprocess timeout | Prevents indefinite hangs | Tests expecting >60s subprocess runs will need explicit timeout |
| Shared rebuild fixture | Reduces 20→8 rebuilds (~12 minutes saved) | Read-only tests share DB state (verified safe — all are SELECT-only) |
| Orchestrator isolation | Tests can't corrupt production state | Slightly more complex fixture setup |

**Risks:**
- The subprocess timeout guard will cause `subprocess.TimeoutExpired` in tests with legitimately slow subprocesses. These need explicit `timeout=` values.
- The production DB guard changes `DEFAULT_DB_PATH` at import time. Any test that directly accesses the path variable (not through an instance) will see the guarded value. This is the intended behavior.

**Not addressed (future work):**
- Moving `control-index.db` off OneDrive to a local path
- Adding `collect_ignore_glob` for heavy integration tests
- pytest-xdist parallel execution
- Windows Defender exclusion for `.venv/` and `tests/`

## Final Assessment

**PRODUCTION_HARDENING_REQUIRED** — The test infrastructure is architecturally sound
(tmp_path isolation, layer markers, LLM timeout guards) but has 5 specific gaps
(import-time I/O, production state leaks, missing subprocess timeouts, redundant rebuilds,
unconfigured timeout method) that combine to produce hangs on OneDrive-synced environments.
The fixes are targeted, low-risk, and preserve all existing test semantics.
