# FF-OCRD-001 — Operational Control Record and Discovery Layer
# Plan: silly-popping-tower
# Mission: Production-Grade Control-Layer Structural Repairs + Enhanced Discovery Overlay
# Type: infrastructure_hardening
# Mode: MICRO_TASKCARDIZED — every actionable item decomposed to atomic executable steps
# Revision: 2 (micro-taskcardization pass, corrections applied)

---

## PREFLIGHT — Verified Code Facts

These facts were confirmed by reading source files directly. They override any
documentation claim made before this plan.

| Fact | Verified Value |
|---|---|
| Gap selection entry point | `tools/supervisor/capability_queue_consumer.py::load_foss_gaps()` lines 114-161 |
| Gap selection source | `gap-ledger.json` (NOT SQLite DB) |
| Gap exhaustion filter inject point | Lines 150-152, after assigned-gaps filter |
| SyncReport fields | `results: list[IngestResult]`, `started_at: str`, `completed_at: str` — NO `stale_files` |
| `conn.commit()` in sync.py | Line 136 (single final commit for all ingestors) |
| FTS population in sync.py | Lines 131-135, silenced with bare `except: pass` |
| check_continuation.py CONTINUE fields | `verdict`, `iteration`, `max_iterations`, `continuation_state`, `session_id`, `track`, `product_chat_id`, `next_work_items_path`, `next_sprint_path`, `rework_items`, `lane_starvation_warnings`, `resume_command`, optional `warning` (singular) |
| check_continuation.py `warnings` field | DOES NOT EXIST — plan must use new `control_index_warnings` key |
| autonomous_cycle.py signal write | Line 2207 via `atomic_write_json()` |
| autonomous_cycle.py contradictions | `bridge_to_legacy_format()` WRITES contradictions.json — does NOT read it |
| SCHEMA_VERSION | 2 (in `tools/supervisor/control_index/__init__.py`) |
| gap_attempts table | DOES NOT EXIST in current schema |
| trust_registry / quarantines tables | DO NOT EXIST in current schema |

---

## REQUIREMENTS REGISTRY

| REQ-ID | Statement | Source Finding | Group |
|---|---|---|---|
| REQ-OCRD-001 | Loop MUST NOT re-select gaps with ≥3 failed outcomes without reset | RC-1, Finding 2 | A |
| REQ-OCRD-002 | gap_attempts table MUST be written by evidence_ingestor.py | RC-1 | A |
| REQ-OCRD-003 | get_exhausted_gaps() MUST be called by capability_queue_consumer.py::load_foss_gaps() | RC-1, Preflight | A/B |
| REQ-OCRD-004 | Each ingestor MUST run in an isolated transaction boundary | Finding 5, RC-5 | A |
| REQ-OCRD-005 | Ingestor failure MUST roll back only that ingestor's changes, not others | Finding 5 | A |
| REQ-OCRD-006 | SyncReport MUST gain stale_files field and be written to last-sync-report.json | RC-5 | A |
| REQ-OCRD-007 | Schema MUST support column additions to existing tables without data loss | Finding 6 | A |
| REQ-OCRD-008 | SCHEMA_VERSION bump MUST trigger idempotent ALTER TABLE migrations | Finding 6 | A |
| REQ-OCRD-009 | FTS rebuild MUST trigger when records are updated, not just inserted | Finding 8 | A |
| REQ-OCRD-010 | Evidence spot-check MUST compare actual test function count vs declared | RC-3 | A |
| REQ-OCRD-011 | critical_contradiction_count MUST appear in continuation-signal.json | Finding 4, RC-4 | B |
| REQ-OCRD-012 | check_continuation.py MUST surface control_index_warnings without changing verdict | Finding 1, Preflight | B |
| REQ-OCRD-013 | Exhausted gap IDs MUST be queryable as a machine-readable file | REQ-OCRD-003 | B |
| REQ-OCRD-014 | existing-control-layers.yaml MUST have ≥12 entries with verified status | Protocol §3 | C |
| REQ-OCRD-015 | Each control layer entry MUST distinguish claimed vs observable features | Protocol §4 | C |
| REQ-OCRD-016 | feature-parity-register.yaml MUST have zero valid_features_lost | Protocol §5 | C |
| REQ-OCRD-017 | ADR-001 MUST document component choice with rejected alternatives | Protocol §6 | C |
| REQ-OCRD-018 | New schema tables MUST be added via migration framework (TC-OCRD-A4) | REQ-OCRD-007 | C |
| REQ-OCRD-019 | 8 new query subcommands MUST be added to query.py | Protocol §25 | C |
| REQ-OCRD-020 | 6 new governance validators MUST be registered in runner | Protocol §31 | C |
| REQ-OCRD-021 | 10 new skills MUST be registered in skill-registry.yaml | Protocol §32 | C |
| REQ-OCRD-022 | Permanent layer plan MUST be created as L29 | Protocol §55 | C |

---

## Honest Diagnosis

### What the code actually does vs what documentation claims

This section is the foundation for the plan. It is based on reading actual source files,
not documentation.

**Finding 1 — Control index is not in any decision loop (CRITICAL)**
`check_continuation.py` reads `.local/supervisor/continuation-signal.json` and
`.local/supervisor/plan-locks/*.json` directly. It makes zero SQLite queries. The control
index database produces no decision signals at all. If the DB is stale, wrong, or absent,
continuation behavior is unchanged. The DB is useful only for human offline queries.

MEMORY.md and CLAUDE.md present the control index as a central coordination layer. The code
does not implement this. The DB is an overlay cache with no write-back to decision paths.

**Finding 2 — Gap re-selection is unbounded (CRITICAL)**
`sprint_work_items.gap_ledger_ref` is a text string with no foreign key constraint. There
is no `gap_attempts` table. There is no query in the gap selection path that filters out
previously-attempted gaps. A gap that fails with rework_items in sprint N can be selected
again in sprint N+1, N+2, and N+3 without any mechanical prevention. This is the primary
cause of rerun inconsistency: the loop does not learn from prior attempts.

**Finding 3 — Evidence grading is partially self-reported (HIGH)**
`inspect_declared_evidence.py` verifies that evidence_paths files exist on disk. It does
not read their content beyond existence. `grade_declared_work.py` reads `test_results` from
the declaration dict — the same dict the agent wrote — and trusts the declared
passed/failed counts without running tests or counting test functions independently. An agent
that declares 1,000 tests passed when 10 exist will pass the grading check as long as some
test files exist.

**Finding 4 — Contradictions have no effect on continuation (HIGH)**
`check_continuation.py` does not read `reports/supervisor/contradictions.json`. There is no
code path where `critical_count > 0` in that file causes a STOP verdict. CLAUDE.md instructs
agents to "address contradictions first" but no code enforces this. The Supreme Directive
("never stop") is the actual runtime behavior.

**Finding 5 — Silent failure modes in sync compound over time (HIGH)**
`sync.py sync_all()` wraps each ingestor in a try/except that catches all exceptions and
logs them to a SyncReport object that no automated process inspects. FTS5 population is
explicitly silenced with `except: pass`. The staleness check function `check_staleness()`
exists in `staleness.py` but is NOT called by `sync_all()` — it must be called explicitly.
All ingestors share one connection and one final commit, so a partial insert failure from
ingestor 5 persists silently alongside correct data from ingestor 6.

**Finding 6 — Schema migration is incomplete for column additions (HIGH)**
`SCHEMA_VERSION = 2` triggers `init_db()` which runs `CREATE TABLE IF NOT EXISTS` for all
tables. If a new schema version adds a column to an existing table, that column will NOT be
applied to an existing database because `CREATE TABLE IF NOT EXISTS` skips existing tables.
Only entirely new tables are applied. Column additions require `ALTER TABLE`, which is not
implemented.

**Finding 7 — Plan lock accumulation creates ambiguity across multiple plans per session (MEDIUM)**
`check_continuation.py` selects the most-recently-updated lock for the current session_id.
When a session completes 3 sequential plans, all 3 locks exist with the same session_id.
If plans complete in unexpected order or if timestamps are close, the wrong lock can be
selected.

**Finding 8 — FTS5 search returns all records regardless of staleness (MEDIUM)**
`search()` in `search.py` queries `fts_operational` with no filter for quarantined, stale,
or superseded records. The populate step is triggered only when ingestors insert new rows,
not when records are updated.

---

## Root Causes (not symptoms)

**RC-1: Gap selection is stateless.**
The core loop has no memory of which gaps it tried and what happened. `gap_ledger.json`
is a snapshot of current gap status; it does not record attempt history. There is no
data structure linking sprints to specific gap attempts with outcomes. This makes
convergence unprovable.

**RC-2: The control index is architecturally disconnected from decisions.**
The DB was built as a queryable overlay but no code was written to feed its outputs back
into the loop's decision points. It answers human questions but does not prevent repeated
mistakes.

**RC-3: Evidence grading has no independent verification step.**
The pipeline is: agent writes declaration → supervisor validates schema → supervisor
grades based on declared values. No step independently verifies what the agent claims.

**RC-4: Quality gates are bypassable by design.**
The Supreme Directive ("never stop except TRUE_EXTERNAL_GATEs") is the highest
priority rule. Contradiction detection, governance validator FAILs, and rework_items
do not produce STOP verdicts in `check_continuation.py`.

**RC-5: Sync errors are invisible to operators and agents.**
`SyncReport` is returned from `sync_all()` but is never written to a file or surfaced
in any status output. Ingestor failures accumulate silently.

---

## What to preserve

- SQLite + FTS5 as the storage engine (correct choice, confirmed by FF-CTRL-INDEX-001)
- The ingestor pattern (source adapters + hash-based incremental sync)
- The gap ledger as the canonical gap source of truth
- The evidence declaration schema (thorough and well-designed)
- The governance validator architecture (165 validators in separate files)
- The plan lock dual-mechanism (session-keyed + shared fallback handles races)
- The continuation-signal.json schema (backward-compatible additions only)
- The layer plan system (28 layers, index.yaml, task-register.yaml)
- SCHEMA_VERSION + `ensure_db()` pattern (correct base, just incomplete for column changes)

---

## Solution Options Analysis

### Group A — Structural Repairs

**Option A-OPT-1 (Selected):** SQLite SAVEPOINTs for per-ingestor isolation.
- Pros: standard SQLite feature, no new dependency, ~1ms overhead per ingestor, nested within outer connection
- Cons: does not protect against outer transaction failure (acceptable — total rollback is correct)
- Rejected: BEGIN/COMMIT per ingestor (cannot nest in open transaction)
- Rejected: separate DB connection per ingestor (connection overhead + lock contention)

**Option A-OPT-2 (Selected):** Python `PRAGMA table_info` for idempotent migrations.
- Pros: works without procedural SQL, readable, idempotent
- Rejected: `CREATE TEMP TABLE _col_check AS SELECT COUNT(*) FROM pragma_table_info(...)` (valid SQL but harder to compose dynamically)

### Group B — Signal Improvements

**Option B-OPT-1 (Selected):** New `control_index_warnings: list[str]` key in check_continuation.py CONTINUE output.
- Rationale: `lane_starvation_warnings` exists but is semantically wrong for sync health. `warning` (singular) is for single-string advisory messages. A new list field is the cleanest backward-compatible addition.
- `warnings` (plural) does NOT exist in the current output — using it would be a bug.

**Option B-OPT-2 (Selected for B2):** Inject `get_exhausted_gaps()` into `capability_queue_consumer.py::load_foss_gaps()` at lines 150-152.
- Rationale: Gap selection is 100% code-based (confirmed). The inject point is after the assigned-gaps filter where exhausted gaps should also be excluded. DB access is read-only and gated on DB existence.
- Rejected: Exhausted-gaps.json file + CLAUDE.md instruction (weaker — prompt-based, not code-based)

### Group C — Enhanced Discovery Overlay

**Option C-OPT-1 (Selected):** Add new tables via migration framework (TC-OCRD-A4) to ensure column safety.
- This requires A4 to complete before C3 begins.
- Rejected: direct `CREATE TABLE IF NOT EXISTS` in schema.sql only (bypasses migration safety)

---

## Execution DAG

```yaml
execution_dag:
  groups:
    - group: A
      sequential: true
      tasks:
        - id: TC-OCRD-A4
          note: "Schema migration framework — prerequisite for all table additions"
        - id: TC-OCRD-A1
          depends_on: [TC-OCRD-A4]
          note: "gap_attempts table via migration"
        - id: TC-OCRD-A2
          depends_on: [TC-OCRD-A1]
          note: "per-ingestor SAVEPOINTs — safe after schema stable"
        - id: TC-OCRD-A3
          depends_on: [TC-OCRD-A2]
          note: "staleness + SyncReport persistence"
        - id: TC-OCRD-A5
          depends_on: [TC-OCRD-A3]
          note: "evidence spot-check (needs SyncReport field added by A3)"
    - group: B
      depends_on_group: A
      parallel: true
      tasks:
        - id: TC-OCRD-B1
          note: "contradiction signal in autonomous_cycle.py"
        - id: TC-OCRD-B2
          depends_on: [TC-OCRD-A1]
          note: "gap selection filter in capability_queue_consumer.py"
    - group: C
      depends_on_group: A
      sequential: true
      tasks:
        - id: TC-OCRD-C1
          note: "YAML inventories (written by human reading codebase)"
        - id: TC-OCRD-C2
          depends_on: [TC-OCRD-C1]
        - id: TC-OCRD-C3
          depends_on: [TC-OCRD-A4]
          note: "new schema tables via migration"
        - id: TC-OCRD-C4
          depends_on: [TC-OCRD-C3, TC-OCRD-C1]
          note: "new ingestors for C3 tables"
        - id: TC-OCRD-C5
          depends_on: [TC-OCRD-C4]
        - id: TC-OCRD-C6
          depends_on: [TC-OCRD-C5, TC-OCRD-A1]
        - id: TC-OCRD-C7
          depends_on: [TC-OCRD-C6]
        - id: TC-OCRD-C8
          depends_on: [TC-OCRD-C7]
        - id: TC-OCRD-C9
          depends_on: [TC-OCRD-C8]

  gate:
    between: [A, C]
    condition: "All Group A regression tests PASS before Group C begins"
    enforced_by: "manual checkpoint — no automated gate exists"
```

---

## Taskcards — Full Hierarchy

Status codes: OPEN | IN_PROGRESS | VERIFIED | CLOSED | BLOCKED
Micro-step states: PENDING | ACTIVE | COMPLETE | FAILED | BLOCKED | SKIPPED_NA

---

### TC-OCRD-A4 (Parent): Schema Migration Framework

**Status:** OPEN
**Priority:** P0 — prerequisite for all table additions (TC-OCRD-A1, TC-OCRD-C3)
**Quality Score Target:** 4/5 (column migration idempotency is the hard part)
**Addresses:** Finding 6, REQ-OCRD-007, REQ-OCRD-008

**Problem:** `CREATE TABLE IF NOT EXISTS` skips existing tables. Column additions silently
fail on databases already at SCHEMA_VERSION=2.

**Target state:**
- `db.py` gains `MIGRATIONS: list[tuple[int, int, str]]` and `apply_migrations(conn, current_version)`
- `_add_column_if_missing(conn, table, column, definition)` helper available
- `ensure_db()` calls `apply_migrations()` after `init_db()`
- SCHEMA_VERSION bumped to 3

---

#### TC-OCRD-A4-01 (Child): Add Migration Framework to db.py

**Depends on:** nothing (first task)

##### MS-A4-01-01 — Read db.py in full
- **Action:** `Read tools/supervisor/control_index/db.py`
- **Expected:** Confirm SCHEMA_VERSION, ensure_db(), init_db() locations
- **State:** PENDING

##### MS-A4-01-02 — Add MIGRATIONS list and apply_migrations()
- **Action:** Edit db.py — add after SCHEMA_VERSION definition:
  ```python
  MIGRATIONS: list[tuple[int, int, str]] = []
  # Populated by each schema version change. Format: (from_version, to_version, description)
  # Each entry uses Python callable, not raw SQL, for idempotency.
  MIGRATION_FUNCS: list[tuple[int, int, callable]] = []

  def _add_column_if_missing(conn: sqlite3.Connection, table: str,
                              column: str, definition: str) -> bool:
      """Add column to table if it doesn't exist. Returns True if added."""
      existing = {row[1] for row in conn.execute(
          f"PRAGMA table_info({table})"
      ).fetchall()}
      if column not in existing:
          conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
          return True
      return False

  def apply_migrations(conn: sqlite3.Connection, current_version: int) -> int:
      """Apply all pending migrations in order. Returns new schema version."""
      pending = sorted(
          [(fv, tv, fn) for fv, tv, fn in MIGRATION_FUNCS if fv >= current_version],
          key=lambda x: x[0]
      )
      new_version = current_version
      for from_v, to_v, migration_fn in pending:
          try:
              migration_fn(conn)
              conn.execute(
                  "UPDATE schema_meta SET value = ? WHERE key = 'schema_version'",
                  (str(to_v),)
              )
              conn.commit()
              new_version = to_v
          except sqlite3.OperationalError:
              # Migration may already be applied — continue
              pass
      return new_version
  ```
- **Expected:** db.py compiles, `from tools.supervisor.control_index.db import apply_migrations` succeeds
- **State:** PENDING

##### MS-A4-01-03 — Call apply_migrations in ensure_db()
- **Action:** Edit db.py `ensure_db()` — after `init_db(conn)`, add:
  ```python
  current_v = get_schema_version(conn)
  apply_migrations(conn, current_v)
  ```
- **Expected:** ensure_db() calls migration on every DB open
- **State:** PENDING

##### MS-A4-01-04 — Bump SCHEMA_VERSION to 3
- **Action:** Edit `__init__.py` (or db.py where SCHEMA_VERSION lives): `SCHEMA_VERSION = 3`
- **Expected:** `python -c "from tools.supervisor.control_index import SCHEMA_VERSION; print(SCHEMA_VERSION)"` prints `3`
- **State:** PENDING

---

#### TC-OCRD-A4-02 (Child): Regression Tests

##### MS-A4-02-01 — Write tests/supervisor/test_schema_migrations.py
- **Action:** Create test file with:
  - Test 1: fresh DB at v3 has SCHEMA_VERSION=3
  - Test 2: simulate v2 DB → call apply_migrations → version advances
  - Test 3: _add_column_if_missing on missing column → column appears
  - Test 4: _add_column_if_missing on existing column → no error, no duplicate
  - Test 5: apply_migrations called twice is idempotent
- **State:** PENDING

##### MS-A4-02-02 — Run tests and confirm PASS
- **Action:** `.venv/Scripts/pytest tests/supervisor/test_schema_migrations.py -v`
- **Expected:** 5/5 PASS
- **State:** PENDING

---

**TC-OCRD-A4 Validation:**
```bash
python -m tools.supervisor.control_index init
python -c "from tools.supervisor.control_index import SCHEMA_VERSION; print(SCHEMA_VERSION)"
# Expect: 3
python -c "from tools.supervisor.control_index.db import _add_column_if_missing; print('OK')"
# Expect: OK
```

**TC-OCRD-A4 Evidence contract:**
- File: `tools/supervisor/control_index/db.py` — modified (apply_migrations added)
- File: `tests/supervisor/test_schema_migrations.py` — new (5 tests, all PASS)
- Proof: `.venv/Scripts/pytest tests/supervisor/test_schema_migrations.py --tb=short` output

---

### TC-OCRD-A1 (Parent): Gap Attempt Registry

**Status:** OPEN
**Priority:** P0
**Depends on:** TC-OCRD-A4 (migration framework)
**Quality Score Target:** 4/5
**Addresses:** RC-1, Finding 2, REQ-OCRD-001, REQ-OCRD-002

**Problem:** No data structure records which sprint attempted which gap and what the outcome
was. The loop cannot avoid re-selecting previously-failed gaps.

**Target state:**
- `gap_attempts` table added via migration (SCHEMA_VERSION 3→3, new table)
- `evidence_ingestor.py` writes one row per sprint_work_item with non-null gap_ledger_ref
- `gap_selection.py` (new file) provides `get_exhausted_gaps()` and `get_recent_attempt()`
- CLI query: `python -m tools.supervisor.control_index.query gap-attempts --gap-id GAP-XYZ`
- `.supervisor/policies.yaml` gains `gap_selection.max_failed_attempts: 3`

---

#### TC-OCRD-A1-01 (Child): gap_attempts Table via Migration

##### MS-A1-01-01 — Read current schema.sql
- **Action:** Read `tools/supervisor/control_index/schema.sql` — confirm gap_attempts does not exist
- **Expected:** No `gap_attempts` in file
- **State:** PENDING

##### MS-A1-01-02 — Add gap_attempts to schema.sql (for new DBs)
- **Action:** Append to schema.sql:
  ```sql
  -- T-GA: gap_attempts — one row per sprint-gap attempt
  CREATE TABLE IF NOT EXISTS gap_attempts (
      attempt_id     TEXT PRIMARY KEY,
      gap_id         TEXT NOT NULL,
      sprint_id      TEXT NOT NULL,
      item_id        TEXT,
      outcome        TEXT,
      rework_reason  TEXT,
      attempted_at   TEXT NOT NULL,
      source_file    TEXT,
      ingested_at    TEXT DEFAULT (datetime('now'))
  );
  CREATE INDEX IF NOT EXISTS idx_ga_gap ON gap_attempts(gap_id);
  CREATE INDEX IF NOT EXISTS idx_ga_sprint ON gap_attempts(sprint_id);
  CREATE INDEX IF NOT EXISTS idx_ga_outcome ON gap_attempts(outcome);
  ```
- **Expected:** schema.sql parses without error
- **State:** PENDING

##### MS-A1-01-03 — Register migration function in db.py for existing DBs
- **Action:** Add to db.py MIGRATION_FUNCS:
  ```python
  def _migrate_v2_add_gap_attempts(conn: sqlite3.Connection) -> None:
      conn.executescript("""
          CREATE TABLE IF NOT EXISTS gap_attempts (
              attempt_id TEXT PRIMARY KEY, gap_id TEXT NOT NULL,
              sprint_id TEXT NOT NULL, item_id TEXT, outcome TEXT,
              rework_reason TEXT, attempted_at TEXT NOT NULL,
              source_file TEXT, ingested_at TEXT DEFAULT (datetime('now'))
          );
          CREATE INDEX IF NOT EXISTS idx_ga_gap ON gap_attempts(gap_id);
          CREATE INDEX IF NOT EXISTS idx_ga_sprint ON gap_attempts(sprint_id);
          CREATE INDEX IF NOT EXISTS idx_ga_outcome ON gap_attempts(outcome);
      """)

  MIGRATION_FUNCS.append((2, 3, _migrate_v2_add_gap_attempts))
  ```
- **Expected:** Existing v2 DB gets gap_attempts table on next ensure_db() call
- **State:** PENDING

##### MS-A1-01-04 — Verify table creation on existing DB
- **Action:**
  ```bash
  python -c "
  from tools.supervisor.control_index import get_connection, DEFAULT_DB_PATH
  conn = get_connection(DEFAULT_DB_PATH)
  tables = {r[0] for r in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()}
  print('gap_attempts' in tables)
  "
  ```
- **Expected:** `True`
- **State:** PENDING

---

#### TC-OCRD-A1-02 (Child): evidence_ingestor.py — Write gap_attempts Rows

##### MS-A1-02-01 — Read evidence_ingestor.py in full
- **Action:** Read `tools/supervisor/control_index/ingestors/evidence_ingestor.py`
- **Expected:** Locate sprint_work_items insert loop, find gap_ledger_ref field usage
- **State:** PENDING

##### MS-A1-02-02 — Add outcome classification function
- **Action:** Add to evidence_ingestor.py (before the main sync method):
  ```python
  def _classify_outcome(item_status: str, sprint_verdict: str,
                        item_id: str, rework_items: list) -> str | None:
      """Classify gap attempt outcome. Returns None to skip (external gate)."""
      if item_status == 'blocked_external_gate':
          return None  # Skip — external, not a failure
      if item_status == 'completed' and sprint_verdict in ('ACCEPTED', 'COMPLETE'):
          rework_ids = [r.get('item_id') for r in (rework_items or [])]
          if item_id in rework_ids:
              return 'rework'
          return 'closed'
      if item_status == 'partial':
          return 'partial'
      if item_status == 'completed':  # completed but verdict not ACCEPTED
          return 'rework'
      return 'failed'
  ```
- **Expected:** Function available in module scope
- **State:** PENDING

##### MS-A1-02-03 — Insert gap_attempts rows after sprint_work_items insert
- **Action:** After the sprint_work_items INSERT loop, add:
  ```python
  # Write gap_attempts for items with a gap_ledger_ref
  rework_items = sprint_data.get('rework_items', [])
  sprint_verdict = sprint_data.get('verdict', '')
  for item in work_items:
      gap_id = item.get('gap_ledger_ref')
      if not gap_id:
          continue
      item_id = item.get('item_id', '')
      outcome = _classify_outcome(
          item.get('status', 'unknown'), sprint_verdict,
          item_id, rework_items
      )
      if outcome is None:
          continue
      attempt_id = f"{sprint_id}::{gap_id}"
      conn.execute(
          """INSERT OR REPLACE INTO gap_attempts
             (attempt_id, gap_id, sprint_id, item_id, outcome,
              rework_reason, attempted_at, source_file)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
          (attempt_id, gap_id, sprint_id, item_id, outcome,
           item.get('rework_reason'), sprint_data.get('end_time', ''),
           str(source_file))
      )
  ```
- **Expected:** gap_attempts rows written after each evidence sync
- **State:** PENDING

##### MS-A1-02-04 — Verify gap_attempts rows after sync
- **Action:** Run sync and query:
  ```bash
  python -m tools.supervisor.control_index sync
  python -m tools.supervisor.control_index.query sql \
    "SELECT gap_id, outcome, COUNT(*) FROM gap_attempts GROUP BY gap_id, outcome LIMIT 10"
  ```
- **Expected:** Rows visible (may be empty if no declarations have gap_ledger_ref)
- **State:** PENDING

---

#### TC-OCRD-A1-03 (Child): gap_selection.py — New Module

##### MS-A1-03-01 — Create tools/supervisor/control_index/gap_selection.py
- **Action:** Create new file:
  ```python
  """Gap selection utilities — query gap_attempts to identify exhausted gaps."""
  from __future__ import annotations
  import sqlite3
  from pathlib import Path

  def get_exhausted_gaps(conn: sqlite3.Connection,
                         max_failed_attempts: int = 3) -> set[str]:
      """Return gap_ids with >= max_failed_attempts 'failed'|'rework' outcomes."""
      rows = conn.execute(
          """SELECT gap_id, COUNT(*) as cnt
             FROM gap_attempts
             WHERE outcome IN ('failed', 'rework')
             GROUP BY gap_id
             HAVING cnt >= ?""",
          (max_failed_attempts,),
      ).fetchall()
      return {row[0] for row in rows}

  def get_recent_attempt(conn: sqlite3.Connection, gap_id: str) -> dict | None:
      """Return most recent attempt for a gap, or None if none exists."""
      row = conn.execute(
          """SELECT * FROM gap_attempts WHERE gap_id = ?
             ORDER BY attempted_at DESC LIMIT 1""",
          (gap_id,),
      ).fetchone()
      if row is None:
          return None
      return dict(row)

  def write_exhausted_gaps_json(conn: sqlite3.Connection,
                                output_path: Path,
                                max_failed_attempts: int = 3) -> int:
      """Write exhausted gap IDs to JSON file. Returns count."""
      import json
      exhausted = sorted(get_exhausted_gaps(conn, max_failed_attempts))
      output_path.parent.mkdir(parents=True, exist_ok=True)
      output_path.write_text(json.dumps({
          "exhausted_gaps": exhausted,
          "max_failed_attempts": max_failed_attempts,
          "count": len(exhausted),
      }, indent=2))
      return len(exhausted)
  ```
- **Expected:** Module importable, functions callable
- **State:** PENDING

##### MS-A1-03-02 — Update .supervisor/policies.yaml
- **Action:** Read `.supervisor/policies.yaml`, then add under gap_selection section:
  ```yaml
  gap_selection:
    max_failed_attempts: 3
    exhausted_gaps_path: reports/control-layer/exhausted-gaps.json
  ```
- **Expected:** YAML parses, key present
- **State:** PENDING

---

#### TC-OCRD-A1-04 (Child): CLI query — gap-attempts subcommand

##### MS-A1-04-01 — Read tools/supervisor/control_index/query.py
- **Action:** Read query.py to find subcommand registration pattern
- **State:** PENDING

##### MS-A1-04-02 — Add gap-attempts subcommand
- **Action:** Add parser and handler following existing pattern:
  ```python
  # In subparsers section:
  p_ga = sub.add_parser('gap-attempts', help='Query gap attempt history')
  p_ga.add_argument('--gap-id', help='Filter by specific gap ID')
  p_ga.add_argument('--outcome', help='Filter by outcome (failed/closed/partial/rework)')
  p_ga.add_argument('--limit', type=int, default=20)

  # In dispatch section:
  elif args.command == 'gap-attempts':
      q = "SELECT * FROM gap_attempts WHERE 1=1"
      params = []
      if args.gap_id:
          q += " AND gap_id = ?"
          params.append(args.gap_id)
      if args.outcome:
          q += " AND outcome = ?"
          params.append(args.outcome)
      q += " ORDER BY attempted_at DESC LIMIT ?"
      params.append(args.limit)
      rows = conn.execute(q, params).fetchall()
      print(json.dumps([dict(r) for r in rows], indent=2))
  ```
- **Expected:** `python -m tools.supervisor.control_index.query gap-attempts` runs without error
- **State:** PENDING

---

#### TC-OCRD-A1-05 (Child): Regression Tests

##### MS-A1-05-01 — Write tests/supervisor/test_gap_attempt_registry.py
- **Action:** Create test file covering:
  - Test 1: ingest declaration with gap_ledger_ref, sprint verdict ACCEPTED → outcome='closed'
  - Test 2: ingest declaration, work_item in rework_items → outcome='rework'
  - Test 3: get_exhausted_gaps with 3 failed attempts for same gap_id → returns that gap_id
  - Test 4: get_exhausted_gaps with 2 failed + 1 closed → excludes gap (not enough failures)
  - Test 5: outcome='closed' never appears in exhausted set
  - Test 6: blocked_external_gate item → no gap_attempts row written
  - Test 7: INSERT OR REPLACE — same attempt_id updates rather than errors
- **State:** PENDING

##### MS-A1-05-02 — Run tests, confirm 7/7 PASS
- **Action:** `.venv/Scripts/pytest tests/supervisor/test_gap_attempt_registry.py -v`
- **Expected:** 7/7 PASS
- **State:** PENDING

---

**TC-OCRD-A1 Validation:**
```bash
python -m tools.supervisor.control_index sync
python -m tools.supervisor.control_index.query gap-attempts --outcome failed
python -c "
from tools.supervisor.control_index import get_connection, DEFAULT_DB_PATH
from tools.supervisor.control_index.gap_selection import get_exhausted_gaps
conn = get_connection(DEFAULT_DB_PATH)
print('Exhausted gaps:', len(get_exhausted_gaps(conn, max_failed_attempts=3)))
conn.close()
"
```

**TC-OCRD-A1 Evidence contract:**
- schema.sql modified (gap_attempts table)
- db.py modified (migration function registered)
- evidence_ingestor.py modified (gap_attempts writes)
- gap_selection.py created (new module)
- query.py modified (gap-attempts subcommand)
- .supervisor/policies.yaml modified (gap_selection key)
- test_gap_attempt_registry.py created (7 tests PASS)

---

### TC-OCRD-A2 (Parent): Per-Ingestor Transactions

**Status:** OPEN
**Priority:** P1
**Depends on:** TC-OCRD-A1 (schema stable)
**Quality Score Target:** 4/5
**Addresses:** Finding 5, REQ-OCRD-004, REQ-OCRD-005

**Problem:** All 15+ ingestors share one connection and one final commit. Partial failures
persist silently.

**Target state:** Each ingestor runs within a SQLite SAVEPOINT. Failure rolls back only
that ingestor. Shared final `conn.commit()` retained.

---

#### TC-OCRD-A2-01 (Child): Audit Existing Ingestors for Self-Commits

##### MS-A2-01-01 — Grep for self-commits in ingestors
- **Action:**
  ```bash
  grep -rn "conn.commit\|\.commit()" tools/supervisor/control_index/ingestors/
  ```
- **Expected:** List of any ingestors calling commit themselves (must remove those commits)
- **State:** PENDING

##### MS-A2-01-02 — Remove any self-commits found
- **Action:** For each ingestor found in MS-A2-01-01, read it and remove the `conn.commit()` call
- **Expected:** No ingestor calls conn.commit() directly
- **State:** PENDING (SKIPPED_NA if grep returns empty)

---

#### TC-OCRD-A2-02 (Child): Replace Sync Loop with SAVEPOINT Pattern

##### MS-A2-02-01 — Read sync.py lines around the main loop
- **Action:** Read `tools/supervisor/control_index/sync.py` lines 90-145
- **Expected:** Confirm exact structure of current loop + single conn.commit()
- **State:** PENDING

##### MS-A2-02-02 — Replace loop with SAVEPOINT pattern
- **Action:** Edit sync.py — replace the ingestor loop:
  ```python
  for ingestor_cls in ALL_INGESTORS:
      ingestor = ingestor_cls(conn, repo_root)
      savepoint = f"sp_{ingestor.entity_type}"
      try:
          conn.execute(f"SAVEPOINT {savepoint}")
          result = ingestor.sync(force=force)
          conn.execute(f"RELEASE SAVEPOINT {savepoint}")
          report.add(result)
      except Exception as e:
          try:
              conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
              conn.execute(f"RELEASE SAVEPOINT {savepoint}")
          except Exception:
              pass  # If savepoint ops fail, outer conn state is unknown
          report.add(IngestResult(
              entity_type=getattr(ingestor, 'entity_type', 'unknown'),
              error=str(e)
          ))
  conn.commit()  # Single commit for all successful savepoints
  ```
- **Expected:** sync.py compiles, no syntax errors
- **State:** PENDING

##### MS-A2-02-03 — Verify savepoint-based sync produces same row counts
- **Action:**
  ```bash
  python -m tools.supervisor.control_index rebuild
  python -c "
  from tools.supervisor.control_index import get_connection, DEFAULT_DB_PATH
  conn = get_connection(DEFAULT_DB_PATH)
  for t in ['sprints','capabilities','gaps','events']:
      print(t, conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0])
  conn.close()
  "
  ```
- **Expected:** Row counts match pre-change counts (or higher if new data was ingested)
- **State:** PENDING

---

#### TC-OCRD-A2-03 (Child): Regression Tests

##### MS-A2-03-01 — Write tests/supervisor/test_ingestor_transactions.py
- **Action:** Create test with mock ingestors:
  - Test 1: mock ingestor raises after inserting 5 rows → 0 rows persisted from it
  - Test 2: ingestor A succeeds, ingestor B fails → A's rows persist, B's do not
  - Test 3: sync after partial failure → next sync retries failed ingestor
  - Test 4: SAVEPOINT name does not contain SQL-special chars (entity_type validation)
- **State:** PENDING

##### MS-A2-03-02 — Run tests, confirm PASS
- **Action:** `.venv/Scripts/pytest tests/supervisor/test_ingestor_transactions.py -v`
- **Expected:** 4/4 PASS
- **State:** PENDING

---

**TC-OCRD-A2 Evidence contract:**
- sync.py modified (SAVEPOINT loop)
- Any ingestors with self-commits modified
- test_ingestor_transactions.py created (4 tests PASS)

---

### TC-OCRD-A3 (Parent): Staleness Detection + SyncReport Persistence

**Status:** OPEN
**Priority:** P1
**Depends on:** TC-OCRD-A2
**Quality Score Target:** 4/5
**Addresses:** RC-5, Finding 5, REQ-OCRD-006, REQ-OCRD-012

**CORRECTION FROM PREFLIGHT:** The original plan referenced adding to a `warnings` field
in check_continuation.py output. That field DOES NOT EXIST. The correct fix is to add a
new `control_index_warnings: list[str]` key to the CONTINUE output dict (lines 623-647).

**Target state:**
- `SyncReport` dataclass gains `stale_files: list[dict] = field(default_factory=list)`
- `sync_all()` calls `check_staleness()` after final commit
- `sync_all()` writes `.local/supervisor/last-sync-report.json`
- `check_continuation.py` reads last-sync-report.json and adds `control_index_warnings` to CONTINUE output

---

#### TC-OCRD-A3-01 (Child): SyncReport Dataclass Enhancement

##### MS-A3-01-01 — Read sync.py dataclass definitions
- **Action:** Read sync.py lines 1-55 to confirm SyncReport and IngestResult fields
- **Expected:** Confirm `stale_files` field does NOT exist, `add()` method signature
- **State:** PENDING

##### MS-A3-01-02 — Add stale_files field to SyncReport
- **Action:** Edit sync.py — add to SyncReport dataclass:
  ```python
  stale_files: list[dict] = field(default_factory=list)
  ```
  Also update `to_dict()` method if it exists to include `stale_files`.
- **Expected:** `SyncReport().stale_files` is an empty list
- **State:** PENDING

---

#### TC-OCRD-A3-02 (Child): Call check_staleness() in sync_all()

##### MS-A3-02-01 — Read staleness.py to confirm check_staleness() signature
- **Action:** Read `tools/supervisor/control_index/staleness.py`
- **Expected:** Confirm function signature: `check_staleness(conn, repo_root) -> list[dict]` (or similar)
- **State:** PENDING

##### MS-A3-02-02 — Import check_staleness in sync.py
- **Action:** Add import to sync.py:
  ```python
  from tools.supervisor.control_index.staleness import check_staleness
  ```
- **State:** PENDING

##### MS-A3-02-03 — Call check_staleness after final commit
- **Action:** Edit sync.py — after `conn.commit()`, before function return:
  ```python
  try:
      stale = check_staleness(conn, repo_root)
      report.stale_files = stale
  except Exception as e:
      report.stale_files = [{"error": str(e)}]
  ```
- **Expected:** SyncReport.stale_files populated after sync
- **State:** PENDING

---

#### TC-OCRD-A3-03 (Child): Write last-sync-report.json

##### MS-A3-03-01 — Add JSON write after staleness check
- **Action:** Edit sync.py — after setting report.stale_files:
  ```python
  import json
  sync_report_path = repo_root / ".local/supervisor/last-sync-report.json"
  sync_report_path.parent.mkdir(parents=True, exist_ok=True)
  sync_report_path.write_text(json.dumps({
      "completed_at": report.completed_at,
      "total_inserted": sum(
          getattr(r, 'inserted', 0) for r in report.results if not r.error
      ),
      "total_errors": sum(1 for r in report.results if r.error),
      "error_entities": [r.entity_type for r in report.results if r.error],
      "stale_files": report.stale_files,
      "schema_version": SCHEMA_VERSION,
  }, indent=2))
  ```
- **Expected:** `.local/supervisor/last-sync-report.json` exists after `python -m tools.supervisor.control_index sync`
- **State:** PENDING

##### MS-A3-03-02 — Verify file content after sync
- **Action:**
  ```bash
  python -m tools.supervisor.control_index sync
  python -m json.tool .local/supervisor/last-sync-report.json
  ```
- **Expected:** Valid JSON with `completed_at`, `total_inserted`, `total_errors`, `stale_files`
- **State:** PENDING

---

#### TC-OCRD-A3-04 (Child): Add control_index_warnings to check_continuation.py

**CORRECTION NOTE:** The original plan said "adds to a `warnings` field". No such field exists.
This micro-step adds a NEW key `control_index_warnings: list[str]` to the CONTINUE output dict.

##### MS-A3-04-01 — Read check_continuation.py CONTINUE output block
- **Action:** Read `tools/supervisor/check_continuation.py` lines 620-650
- **Expected:** Confirm exact dict keys in CONTINUE output: `verdict`, `iteration`, `lane_starvation_warnings`, etc.
- **State:** PENDING

##### MS-A3-04-02 — Add sync health check function
- **Action:** Add function near top of check_continuation.py (before main()):
  ```python
  def _get_control_index_warnings(repo_root: Path) -> list[str]:
      """Read last-sync-report.json and return advisory warnings. Non-blocking."""
      warnings = []
      sync_report_path = repo_root / ".local/supervisor/last-sync-report.json"
      if not sync_report_path.exists():
          return warnings
      try:
          report = json.loads(sync_report_path.read_text())
          completed_at_str = report.get("completed_at", "2000-01-01T00:00:00")
          from datetime import datetime, timezone
          completed_at = datetime.fromisoformat(
              completed_at_str.replace("Z", "+00:00")
          )
          age_hours = (
              datetime.now(timezone.utc) - completed_at
          ).total_seconds() / 3600
          if age_hours > 24:
              warnings.append(
                  f"control_index_stale: last sync {age_hours:.0f}h ago"
              )
          if report.get("error_entities"):
              warnings.append(
                  f"control_index_errors: {report['error_entities']}"
              )
      except Exception:
          pass  # Non-blocking per Supreme Directive
      return warnings
  ```
- **Expected:** Function importable and callable
- **State:** PENDING

##### MS-A3-04-03 — Add control_index_warnings to CONTINUE output dict
- **Action:** Edit check_continuation.py CONTINUE output dict — add new key:
  ```python
  "control_index_warnings": _get_control_index_warnings(REPO_ROOT),
  ```
  Place after `lane_starvation_warnings` in the output dict.
- **Expected:** `python tools/supervisor/check_continuation.py | python -m json.tool` shows `control_index_warnings` key
- **State:** PENDING

---

#### TC-OCRD-A3-05 (Child): Regression Tests

##### MS-A3-05-01 — Write tests/supervisor/test_sync_health.py
- **Action:** Create test file:
  - Test 1: sync writes last-sync-report.json with required keys
  - Test 2: _get_control_index_warnings with fresh report → empty list
  - Test 3: _get_control_index_warnings with report >24h old → stale warning
  - Test 4: _get_control_index_warnings with error_entities → error warning
  - Test 5: missing last-sync-report.json → empty list, no exception
  - Test 6: CONTINUE output dict contains control_index_warnings key
- **State:** PENDING

##### MS-A3-05-02 — Run tests, confirm PASS
- **Action:** `.venv/Scripts/pytest tests/supervisor/test_sync_health.py -v`
- **Expected:** 6/6 PASS
- **State:** PENDING

---

**TC-OCRD-A3 Evidence contract:**
- sync.py modified (SyncReport.stale_files, check_staleness() call, JSON write)
- check_continuation.py modified (_get_control_index_warnings, control_index_warnings in output)
- test_sync_health.py created (6 tests PASS)
- `.local/supervisor/last-sync-report.json` exists after sync

---

### TC-OCRD-A5 (Parent): Evidence Spot-Check

**Status:** OPEN
**Priority:** P2
**Depends on:** TC-OCRD-A3
**Quality Score Target:** 3/5 (Python-only, cannot detect stub gaming)
**Addresses:** RC-3, Finding 3, REQ-OCRD-010

**Target state:**
- `tools/supervisor/evidence_verifier.py` (new) provides `spot_check_test_count()`
- Called from `inspect_declared_evidence.py` after collecting found_paths
- Adds `test_count_check` dict to inspection result (non-blocking WARN only)

---

#### TC-OCRD-A5-01 (Child): Create evidence_verifier.py

##### MS-A5-01-01 — Read inspect_declared_evidence.py
- **Action:** Read `tools/supervisor/inspect_declared_evidence.py`
- **Expected:** Confirm return dict structure, where to inject spot_check call
- **State:** PENDING

##### MS-A5-01-02 — Create tools/supervisor/evidence_verifier.py
- **Action:** Create new file:
  ```python
  """Evidence verification utilities — independent check of declared test counts."""
  import ast
  from pathlib import Path

  def spot_check_test_count(
      repo_root: Path,
      changed_files: list[str],
      declared_passed: int,
      declared_failed: int,
  ) -> dict:
      """
      Count actual test functions in changed test files via AST.
      Returns dict with actual_count, declared_count, ratio, warning.
      """
      total_declared = (declared_passed or 0) + (declared_failed or 0)
      if total_declared == 0:
          return {"actual_count": 0, "declared_count": 0,
                  "ratio": 1.0, "warning": None}

      test_files = [
          f for f in (changed_files or [])
          if f.endswith(".py") and "test_" in Path(f).name
      ]
      actual_count = 0
      for rel_path in test_files:
          abs_path = Path(repo_root) / rel_path
          if not abs_path.exists():
              continue
          try:
              tree = ast.parse(
                  abs_path.read_text(encoding="utf-8", errors="replace")
              )
              actual_count += sum(
                  1 for node in ast.walk(tree)
                  if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                  and node.name.startswith("test_")
              )
          except SyntaxError:
              continue

      ratio = actual_count / total_declared if total_declared > 0 else 1.0
      warning = None
      if actual_count > 0 and ratio < 0.5:
          warning = (
              f"WARN_TEST_COUNT_MISMATCH: declared {total_declared} tests "
              f"but found only {actual_count} test_ functions in changed files "
              f"(ratio: {ratio:.2f})"
          )
      return {
          "actual_count": actual_count,
          "declared_count": total_declared,
          "ratio": round(ratio, 3),
          "warning": warning,
      }
  ```
- **Expected:** `from tools.supervisor.evidence_verifier import spot_check_test_count` succeeds
- **State:** PENDING

##### MS-A5-01-03 — Integrate into inspect_declared_evidence.py
- **Action:** Edit inspect_declared_evidence.py — after collecting found_paths, add:
  ```python
  from tools.supervisor.evidence_verifier import spot_check_test_count
  # ...existing found_paths logic...
  test_results = declaration.get('test_results', {})
  test_count_check = spot_check_test_count(
      repo_root=REPO_ROOT,
      changed_files=declaration.get('changed_files', []),
      declared_passed=test_results.get('passed', 0),
      declared_failed=test_results.get('failed', 0),
  )
  result['test_count_check'] = test_count_check
  if test_count_check.get('warning'):
      result.setdefault('warnings', []).append(test_count_check['warning'])
  ```
- **Expected:** Inspection result includes test_count_check field
- **State:** PENDING

---

#### TC-OCRD-A5-02 (Child): Regression Tests

##### MS-A5-02-01 — Write tests/supervisor/test_evidence_verifier.py
- **Action:** Create test:
  - Test 1: 30 declared, 30 actual test functions → no warning, ratio≈1.0
  - Test 2: 100 declared, 10 actual → WARN_TEST_COUNT_MISMATCH
  - Test 3: declared_passed=0 → ratio=1.0, no warning
  - Test 4: non-existent file in changed_files → actual_count=0, no exception
  - Test 5: syntactically broken test file → skipped, no exception
  - Test 6: no test files in changed_files (only .py without test_ in name) → actual_count=0
- **State:** PENDING

##### MS-A5-02-02 — Run tests
- **Action:** `.venv/Scripts/pytest tests/supervisor/test_evidence_verifier.py -v`
- **Expected:** 6/6 PASS
- **State:** PENDING

---

**TC-OCRD-A5 Evidence contract:**
- evidence_verifier.py created
- inspect_declared_evidence.py modified (spot_check_test_count call)
- test_evidence_verifier.py created (6 tests PASS)

---

### TC-OCRD-B1 (Parent): Contradiction Signal in Continuation Loop

**Status:** OPEN
**Priority:** P2
**Depends on:** TC-OCRD-A3 (control_index_warnings pattern established)
**Quality Score Target:** 3/5 (warning only, no verdict change)
**Addresses:** Finding 4, REQ-OCRD-011

**Target state:**
- `autonomous_cycle.py` signal dict (line 2207) gains `critical_contradiction_count` and `contradiction_summary`
- `check_continuation.py` CONTINUE output gains `contradiction_warnings` (list) populated from signal

---

#### TC-OCRD-B1-01 (Child): Add Contradiction Fields to Signal

##### MS-B1-01-01 — Read autonomous_cycle.py signal construction
- **Action:** Read `tools/supervisor/autonomous_cycle.py` lines 2190-2220
- **Expected:** Confirm exact dict keys being written to continuation-signal.json
- **State:** PENDING

##### MS-B1-01-02 — Read contradictions.json structure
- **Action:** Read `reports/supervisor/contradictions.json`
- **Expected:** Confirm `critical_count`, `overall`, and `contradictions[].severity` fields
- **State:** PENDING

##### MS-B1-01-03 — Add contradiction fields to signal dict
- **Action:** Edit autonomous_cycle.py — before the `atomic_write_json()` call at line ~2207, add:
  ```python
  # Read contradictions and embed summary in signal (non-blocking)
  _contradictions_path = REPO_ROOT / "reports/supervisor/contradictions.json"
  _critical_count = 0
  _contradiction_summary = []
  try:
      if _contradictions_path.exists():
          _c_data = json.loads(_contradictions_path.read_text())
          _critical_count = _c_data.get("critical_count", 0)
          _contradiction_summary = [
              c.get("id") for c in _c_data.get("contradictions", [])
              if c.get("severity") == "CRITICAL"
          ]
  except Exception:
      pass  # Non-blocking per Supreme Directive
  signal["critical_contradiction_count"] = _critical_count
  signal["contradiction_summary"] = _contradiction_summary
  ```
- **Expected:** continuation-signal.json contains critical_contradiction_count after next cycle
- **State:** PENDING

---

#### TC-OCRD-B1-02 (Child): Surface Contradiction Warnings in check_continuation.py

##### MS-B1-02-01 — Add contradiction_warnings to CONTINUE output
- **Action:** Edit check_continuation.py — in CONTINUE output dict (after control_index_warnings):
  ```python
  # Read contradiction count from signal
  _critical_contradictions = signal.get("critical_contradiction_count", 0)
  _contradiction_warnings = []
  if _critical_contradictions > 0:
      _contradiction_warnings.append(
          f"critical_contradictions_active: {_critical_contradictions}"
      )
  ```
  Add to output dict: `"contradiction_warnings": _contradiction_warnings`
- **Expected:** CONTINUE output contains contradiction_warnings list
- **State:** PENDING

---

#### TC-OCRD-B1-03 (Child): Regression Tests

##### MS-B1-03-01 — Write tests/supervisor/test_contradiction_signal.py
- **Action:** Create test:
  - Test 1: contradictions.json with critical_count=2 → signal contains critical_contradiction_count=2
  - Test 2: contradictions.json with critical_count=0 → no contradiction_warnings in output
  - Test 3: missing contradictions.json → no error, critical_contradiction_count=0
  - Test 4: CONTINUE output always contains contradiction_warnings key (even when empty)
- **State:** PENDING

##### MS-B1-03-02 — Run tests
- **Action:** `.venv/Scripts/pytest tests/supervisor/test_contradiction_signal.py -v`
- **Expected:** 4/4 PASS
- **State:** PENDING

---

**TC-OCRD-B1 Evidence contract:**
- autonomous_cycle.py modified (contradiction fields in signal)
- check_continuation.py modified (contradiction_warnings in CONTINUE output)
- test_contradiction_signal.py created (4 tests PASS)

---

### TC-OCRD-B2 (Parent): Gap Selection Integration

**Status:** OPEN
**Priority:** P1
**Depends on:** TC-OCRD-A1 (gap_attempts table + get_exhausted_gaps())
**Quality Score Target:** 4/5
**Addresses:** RC-1, REQ-OCRD-003, REQ-OCRD-013

**CORRECTION FROM PREFLIGHT:** The original plan stated "Expected finding: The prompt-based
path is more likely given the system architecture." This is WRONG. Gap selection is 100%
code-based in `tools/supervisor/capability_queue_consumer.py::load_foss_gaps()` lines 114-161.
The inject point is lines 150-152, after the assigned-gaps filter. DB access is read-only
and gated on DB existence (non-blocking).

**Target state:**
- `load_foss_gaps()` calls `get_exhausted_gaps()` from a read-only DB connection
- Exhausted gaps are filtered from the candidate set before ranking
- `exhausted_gap_count` logged to stderr for observability
- Exhausted gaps also written to `reports/control-layer/exhausted-gaps.json` for human inspection

---

#### TC-OCRD-B2-01 (Child): Read and Understand load_foss_gaps()

##### MS-B2-01-01 — Read capability_queue_consumer.py
- **Action:** Read `tools/supervisor/capability_queue_consumer.py` lines 100-170
- **Expected:** Confirm exact structure of load_foss_gaps(), where assigned-gaps filter is (lines 150-152), return type
- **State:** PENDING

---

#### TC-OCRD-B2-02 (Child): Inject Exhausted Gap Filter

##### MS-B2-02-01 — Add DB import and filter after assigned-gaps filter
- **Action:** Edit `tools/supervisor/capability_queue_consumer.py`:

  Step 1 — Add import at top of file:
  ```python
  # Optional DB integration — non-blocking if DB absent
  try:
      from tools.supervisor.control_index import get_connection, DEFAULT_DB_PATH
      from tools.supervisor.control_index.gap_selection import get_exhausted_gaps
      _CONTROL_INDEX_AVAILABLE = True
  except ImportError:
      _CONTROL_INDEX_AVAILABLE = False
  ```

  Step 2 — After assigned-gaps filter in load_foss_gaps() (lines ~150-152), add:
  ```python
  # Filter exhausted gaps (non-blocking — DB may not be available)
  if _CONTROL_INDEX_AVAILABLE:
      try:
          _db_conn = get_connection(DEFAULT_DB_PATH, read_only=True)
          _exhausted = get_exhausted_gaps(_db_conn, max_failed_attempts=3)
          _db_conn.close()
          if _exhausted:
              _before = len(foss_gaps)
              foss_gaps = [g for g in foss_gaps if g.get('gap_id') not in _exhausted]
              import sys
              print(
                  f"[gap-filter] Excluded {_before - len(foss_gaps)} exhausted gaps "
                  f"from {_before} candidates.",
                  file=sys.stderr
              )
      except Exception as _e:
          # Non-blocking per Supreme Directive
          import sys
          print(f"[gap-filter] DB unavailable, skipping exhaustion filter: {_e}",
                file=sys.stderr)
  ```
- **Expected:** load_foss_gaps() excludes exhausted gaps when DB is available
- **State:** PENDING

##### MS-B2-02-02 — Confirm gap_id field name matches gap-ledger.json
- **Action:** Read first 5 entries of `reports/capability-layer/gap-ledger.json` to confirm the field name used for gap ID
- **Expected:** Confirm whether field is `gap_id`, `id`, `gap-id`, or other
- **State:** PENDING

##### MS-B2-02-03 — Correct field name in filter if needed
- **Action:** If field name differs from `gap_id`, update the filter condition in MS-B2-02-01
- **State:** PENDING (SKIPPED_NA if gap_id is confirmed correct)

---

#### TC-OCRD-B2-03 (Child): Write exhausted-gaps.json

##### MS-B2-03-01 — Add write step to gap_selection.py (already has write_exhausted_gaps_json)
- **Action:** Verify `write_exhausted_gaps_json()` exists from TC-OCRD-A1-03-01. If yes, SKIPPED_NA.
  If not, add it now per the code in MS-A1-03-01.
- **State:** PENDING

##### MS-B2-03-02 — Add CLI command to generate exhausted-gaps.json
- **Action:** Add to query.py (or as standalone script `tools/supervisor/generate_exhausted_gaps.py`):
  ```python
  # python tools/supervisor/generate_exhausted_gaps.py
  if __name__ == '__main__':
      from pathlib import Path
      from tools.supervisor.control_index import get_connection, DEFAULT_DB_PATH
      from tools.supervisor.control_index.gap_selection import write_exhausted_gaps_json
      conn = get_connection(DEFAULT_DB_PATH)
      count = write_exhausted_gaps_json(
          conn,
          Path("reports/control-layer/exhausted-gaps.json"),
          max_failed_attempts=3
      )
      conn.close()
      print(f"Wrote {count} exhausted gaps to reports/control-layer/exhausted-gaps.json")
  ```
- **State:** PENDING

---

#### TC-OCRD-B2-04 (Child): Regression Tests

##### MS-B2-04-01 — Write tests/supervisor/test_gap_selection.py
- **Action:** Create test:
  - Test 1: get_exhausted_gaps after 3 failed attempts for GAP-X → includes GAP-X
  - Test 2: get_exhausted_gaps after 2 failed + 1 closed for GAP-Y → excludes GAP-Y
  - Test 3: no attempts → empty set
  - Test 4: load_foss_gaps() with mocked DB returning exhausted=[GAP-X] → GAP-X not in result
  - Test 5: load_foss_gaps() with DB unavailable → returns full list, no exception
- **State:** PENDING

##### MS-B2-04-02 — Run tests
- **Action:** `.venv/Scripts/pytest tests/supervisor/test_gap_selection.py -v`
- **Expected:** 5/5 PASS
- **State:** PENDING

---

**TC-OCRD-B2 Evidence contract:**
- capability_queue_consumer.py modified (exhausted gap filter injected)
- gap_selection.py has write_exhausted_gaps_json() (from A1 or added here)
- generate_exhausted_gaps.py created (CLI entry point)
- test_gap_selection.py created (5 tests PASS)

---

### TC-OCRD-C1 (Parent): Control Layer Inventory Files

**Status:** OPEN
**Priority:** P3 (Group C prerequisite)
**Depends on:** TC-OCRD-A1, TC-OCRD-A2, TC-OCRD-A3 (Group A complete)
**Quality Score Target:** 3/5 (YAML files become stale without update process)
**Addresses:** REQ-OCRD-014, REQ-OCRD-015

**Target state:** 4 machine-readable YAML files produced by reading codebase + running CLIs.

---

#### TC-OCRD-C1-01 (Child): Baseline YAML

##### MS-C1-01-01 — Create reports/control-layer/ directory
- **Action:** Ensure `reports/control-layer/` exists (create if missing)
- **State:** PENDING

##### MS-C1-01-02 — Write operational-control-baseline.yaml
- **Action:** Create `reports/control-layer/operational-control-baseline.yaml` with:
  - mission_id, repository_root, branch, HEAD (from git)
  - source_roots: [tools/supervisor/, tools/supervisor/control_index/]
  - schema_roots: [tools/supervisor/control_index/schema.sql]
  - existing_databases: [.local/supervisor/control-index.db]
  - existing_control_layer_candidates: [list of ≥12 systems read from codebase]
- **State:** PENDING

---

#### TC-OCRD-C1-02 (Child): existing-control-layers.yaml

##### MS-C1-02-01 — Write existing-control-layers.yaml with ≥12 entries
- **Action:** Create `reports/control-layer/existing-control-layers.yaml`. Required entries:
  control_index_db, continuation_signal, plan_lock_system, gap_ledger,
  layer_plan_system, reports_system, governance_validators, skill_registry,
  capability_registry, format_registry, oracle_system, evidence_system,
  qname_registry, supervisor_pipeline

  For each entry: layer_key, name, status (ACTIVE|ACTIVE_WITH_GAPS|PARTIAL|STALE|BROKEN|UNKNOWN),
  claimed_features (list), observable_features (list — SEPARATE from claimed).

  Key statuses:
  - control_index_db: ACTIVE_WITH_GAPS (RC-2: disconnected from decision loop)
  - gap_ledger: ACTIVE_WITH_GAPS (RC-1: no attempt history)
- **Expected:** `python -c "import yaml; d=yaml.safe_load(open('reports/control-layer/existing-control-layers.yaml')); print(len(d['existing_control_layers']))"` → ≥12
- **State:** PENDING

---

#### TC-OCRD-C1-03 (Child): existing-control-features.yaml

##### MS-C1-03-01 — Write existing-control-features.yaml
- **Action:** Create `reports/control-layer/existing-control-features.yaml`.
  One entry per observable feature per control layer. Status must distinguish
  WORKING_AND_PROVEN from DOCUMENTED_ONLY. Include behavioral_verification
  (the CLI command run and its result).
- **State:** PENDING

---

#### TC-OCRD-C1-04 (Child): control-feature-consumers.yaml

##### MS-C1-04-01 — Write control-feature-consumers.yaml
- **Action:** Create `reports/control-layer/control-feature-consumers.yaml`.
  Map of feature_id → list of consumer script paths with invocation pattern.
- **State:** PENDING

---

#### TC-OCRD-C1-05 (Child): Validation

##### MS-C1-05-01 — Validate all YAMLs parse
- **Action:**
  ```bash
  python -c "
  import yaml
  for f in [
      'reports/control-layer/operational-control-baseline.yaml',
      'reports/control-layer/existing-control-layers.yaml',
      'reports/control-layer/existing-control-features.yaml',
      'reports/control-layer/control-feature-consumers.yaml',
  ]:
      yaml.safe_load(open(f))
      print(f'OK: {f}')
  "
  ```
- **Expected:** All 4 print OK
- **State:** PENDING

---

### TC-OCRD-C2 (Parent): Feature-Parity Register + ADR-001

**Status:** OPEN
**Priority:** P3
**Depends on:** TC-OCRD-C1
**Quality Score Target:** 3/5
**Addresses:** REQ-OCRD-016, REQ-OCRD-017

---

#### TC-OCRD-C2-01 (Child): feature-parity-register.yaml

##### MS-C2-01-01 — Create reports/control-layer/feature-parity-register.yaml
- **Action:** For each feature in existing-control-features.yaml, add disposition:
  REUSE_AS_IS | REUSE_WITH_VALIDATION | REPLICATE_IN_ENHANCED_LAYER | SUPERSEDE_WITH_MIGRATION | RETAIN_AS_LEGACY
  Gate: valid_existing_features_lost == 0, active_consumers_broken == 0
- **State:** PENDING

---

#### TC-OCRD-C2-02 (Child): ADR-001

##### MS-C2-02-01 — Create docs/architecture-decisions/ directory (if missing)
- **State:** PENDING

##### MS-C2-02-02 — Write ADR-001-control-layer-component.md
- **Action:** Create `docs/architecture-decisions/ADR-001-control-layer-component.md` with:
  - Component evaluation matrix (SQLite vs DuckDB vs plain JSON)
  - Decision: SQLite + FTS5 confirmed
  - Rationale: existing FF-CTRL-INDEX-001 investment, portability, stdlib, WAL mode, FTS5
  - DuckDB reconsider threshold: sprint count >100K or complex multi-table aggregations latency-sensitive
  - Rejected alternatives with reasons
  - Risks recorded: schema migration complexity (addressed TC-OCRD-A4), single-writer (addressed TC-OCRD-A2)
- **State:** PENDING

---

### TC-OCRD-C3 (Parent): Schema Extension — New Tables

**Status:** OPEN
**Priority:** P3
**Depends on:** TC-OCRD-A4 (migration framework must exist)
**Quality Score Target:** 4/5
**Addresses:** REQ-OCRD-018

**Tables to add via migration (NOT via CREATE TABLE IF NOT EXISTS only):**
control_layers, control_features, control_feature_consumers, feature_parity_results,
quarantines, trust_registry

---

#### TC-OCRD-C3-01 (Child): Add Tables to schema.sql

##### MS-C3-01-01 — Append new table DDL to schema.sql
- **Action:** Append to `tools/supervisor/control_index/schema.sql`:
  ```sql
  CREATE TABLE IF NOT EXISTS control_layers (
      layer_key TEXT PRIMARY KEY,
      name TEXT NOT NULL, status TEXT NOT NULL,
      authority_scope TEXT, primary_purpose TEXT,
      implementation_paths TEXT, data_paths TEXT, consumers TEXT,
      observable_features_count INTEGER DEFAULT 0,
      last_assessed TEXT, ingested_at TEXT DEFAULT (datetime('now'))
  );
  CREATE TABLE IF NOT EXISTS control_features (
      feature_id TEXT PRIMARY KEY,
      control_layer_key TEXT REFERENCES control_layers(layer_key),
      feature_name TEXT NOT NULL, category TEXT, entry_points TEXT,
      current_status TEXT NOT NULL, authority_effect TEXT,
      observable_behavior TEXT, ingested_at TEXT DEFAULT (datetime('now'))
  );
  CREATE TABLE IF NOT EXISTS control_feature_consumers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      feature_id TEXT REFERENCES control_features(feature_id),
      consumer_id TEXT NOT NULL, consumer_type TEXT, consumer_path TEXT,
      expected_contract TEXT, dependency_strength TEXT, migration_risk TEXT
  );
  CREATE TABLE IF NOT EXISTS feature_parity_results (
      feature_id TEXT PRIMARY KEY REFERENCES control_features(feature_id),
      reuse_strategy TEXT, parity_status TEXT NOT NULL,
      intentional_changes TEXT, verified_at TEXT
  );
  CREATE TABLE IF NOT EXISTS quarantines (
      quarantine_id TEXT PRIMARY KEY, artifact_path TEXT NOT NULL,
      detected_at TEXT DEFAULT (datetime('now')),
      validation_failures TEXT, severity TEXT, status TEXT DEFAULT 'ACTIVE'
  );
  CREATE TABLE IF NOT EXISTS trust_registry (
      artifact_path TEXT PRIMARY KEY, authority_level TEXT NOT NULL,
      trusted INTEGER NOT NULL DEFAULT 0, reason TEXT,
      assessed_at TEXT DEFAULT (datetime('now'))
  );
  CREATE INDEX IF NOT EXISTS idx_cf_layer ON control_features(control_layer_key);
  CREATE INDEX IF NOT EXISTS idx_cfc_feature ON control_feature_consumers(feature_id);
  CREATE INDEX IF NOT EXISTS idx_q_status ON quarantines(status);
  CREATE INDEX IF NOT EXISTS idx_tr_trusted ON trust_registry(trusted);
  ```
- **State:** PENDING

---

#### TC-OCRD-C3-02 (Child): Register Migration Function

##### MS-C3-02-01 — Add _migrate_v3_add_control_tables to db.py
- **Action:** Add migration function and append to MIGRATION_FUNCS:
  ```python
  def _migrate_v3_add_control_tables(conn: sqlite3.Connection) -> None:
      """Add control layer discovery tables (v3 schema)."""
      # Run the C3 table SQL (same as schema.sql additions)
      # Use executescript for multi-statement DDL
      conn.executescript("""
          CREATE TABLE IF NOT EXISTS control_layers ( ... );
          -- etc — same DDL as schema.sql addition
      """)

  MIGRATION_FUNCS.append((3, 4, _migrate_v3_add_control_tables))
  ```
  Update SCHEMA_VERSION to 4.
- **State:** PENDING

##### MS-C3-02-02 — Verify new tables exist after init
- **Action:**
  ```bash
  python -m tools.supervisor.control_index init
  python -m tools.supervisor.control_index.query sql \
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
  ```
- **Expected:** control_layers, control_features, control_feature_consumers, feature_parity_results, quarantines, trust_registry visible
- **State:** PENDING

---

### TC-OCRD-C4 (Parent): New Ingestors

**Status:** OPEN
**Priority:** P3
**Depends on:** TC-OCRD-C3, TC-OCRD-C1
**Quality Score Target:** 3/5
**Addresses:** Protocol §§19-21

**Deliverables:**
- `control_layer_ingestor.py` — reads existing-control-layers.yaml + related files
- `contradiction_ingestor.py` — reads contradictions.json, writes to events table (or new table)
- `plan_ingestor.py` — scans plans/ directory, writes plans table
- `upstream_validator.py` — shared validation utility (quarantine on schema failure)

---

#### TC-OCRD-C4-01 (Child): upstream_validator.py

##### MS-C4-01-01 — Create tools/supervisor/control_index/upstream_validator.py
- **Action:** Create file with `ValidationResult` dataclass and `validate_upstream_source()`:
  ```python
  from dataclasses import dataclass, field
  from pathlib import Path
  from typing import Any
  import json, yaml

  @dataclass
  class ValidationResult:
      valid: bool
      failures: list[str] = field(default_factory=list)
      quarantine: bool = False

  def validate_upstream_source(source_path: Path,
                                required_fields: list[str] = None) -> ValidationResult:
      """Validate a JSON or YAML source file before ingestion."""
      failures = []
      if not source_path.exists():
          return ValidationResult(valid=False,
                                  failures=[f"NOT_FOUND: {source_path}"],
                                  quarantine=True)
      try:
          text = source_path.read_text(encoding='utf-8')
          if source_path.suffix in ('.yaml', '.yml'):
              data = yaml.safe_load(text)
          else:
              data = json.loads(text)
      except Exception as e:
          return ValidationResult(valid=False,
                                  failures=[f"PARSE_ERROR: {e}"],
                                  quarantine=True)
      if required_fields:
          for f in required_fields:
              if not (isinstance(data, dict) and f in data):
                  failures.append(f"MISSING_FIELD: {f}")
      return ValidationResult(valid=len(failures) == 0, failures=failures,
                               quarantine=len(failures) > 0)
  ```
- **State:** PENDING

---

#### TC-OCRD-C4-02 (Child): control_layer_ingestor.py

##### MS-C4-02-01 — Create ingestors/control_layer_ingestor.py
- **Action:** Create ingestor following existing ingestor pattern (BaseIngestor subclass):
  - Source: `reports/control-layer/existing-control-layers.yaml`
  - Validates with upstream_validator before insert
  - Writes to: control_layers, control_features, control_feature_consumers, feature_parity_results
  - On validation failure: write quarantine record, skip insert
  - Hash-based skip: hash the source YAML file
- **State:** PENDING

##### MS-C4-02-02 — Register in sync.py ALL_INGESTORS
- **Action:** Add `ControlLayerIngestor` to ALL_INGESTORS list in sync.py
- **State:** PENDING

---

#### TC-OCRD-C4-03 (Child): contradiction_ingestor.py

##### MS-C4-03-01 — Create ingestors/contradiction_ingestor.py
- **Action:** Create ingestor:
  - Source: `reports/supervisor/contradictions.json`
  - Uses events table (event_type='contradiction_detected') if schema supports it,
    else create a minimal `ingested_contradictions` table
  - If overall=CLEAN: delete prior contradiction events
  - If not CLEAN: insert one event per critical contradiction
- **State:** PENDING

##### MS-C4-03-02 — Register in sync.py
- **Action:** Add `ContradictionIngestor` to ALL_INGESTORS
- **State:** PENDING

---

#### TC-OCRD-C4-04 (Child): plan_ingestor.py

##### MS-C4-04-01 — Create plans table if not in schema
- **Action:** Add to schema.sql and migration:
  ```sql
  CREATE TABLE IF NOT EXISTS plans (
      plan_id TEXT PRIMARY KEY, plan_path TEXT NOT NULL,
      plan_type TEXT, title TEXT, status TEXT,
      open_taskcards INTEGER DEFAULT 0, closed_taskcards INTEGER DEFAULT 0,
      ingested_at TEXT DEFAULT (datetime('now'))
  );
  ```
- **State:** PENDING

##### MS-C4-04-02 — Create ingestors/plan_ingestor.py
- **Action:** Create ingestor:
  - Scans `plans/` directory for *.md files
  - Reads YAML frontmatter (if present) for type/status/title
  - Counts TC-* items by status using regex on file content
  - Type classification: plans/strategic/ → strategic, plans/.claude/ → per_chat, plans/layers/*.md → layer
  - Writes to plans table
- **State:** PENDING

##### MS-C4-04-03 — Register in sync.py
- **Action:** Add `PlanIngestor` to ALL_INGESTORS
- **State:** PENDING

---

### TC-OCRD-C5 (Parent): New Query Commands + Views

**Status:** OPEN
**Priority:** P3
**Depends on:** TC-OCRD-C4
**Quality Score Target:** 3/5
**Addresses:** REQ-OCRD-019

---

#### TC-OCRD-C5-01 (Child): New Subcommands in query.py

##### MS-C5-01-01 — Add 8 new subcommands to query.py
- **Action:** Following existing pattern in query.py, add:
  - `control-layers` — list control_layers with status + feature count
  - `task-context <task_id>` — join plan, layer, gaps, evidence for a task
  - `resume-context` — current sprint: signal + next task + trust warnings
  - `trust-status <path>` — look up trust_registry for artifact path
  - `contradictions [--severity CRITICAL]` — query events or ingested_contradictions
  - `parity-status` — feature_parity_results summary
  - `quarantine [--severity CRITICAL]` — list quarantines table
  - `gap-attempts [--gap-id X] [--outcome failed]` — already added in TC-OCRD-A1-04
- **State:** PENDING

---

#### TC-OCRD-C5-02 (Child): views.py

##### MS-C5-02-01 — Create tools/supervisor/control_index/views.py
- **Action:** Create file with 4 functions:
  ```python
  def get_task_context(conn, task_id: str) -> dict: ...
  def get_resume_context(conn, repo_root) -> dict: ...
  def get_product_context(conn, format_id: str) -> dict: ...
  def get_control_feature_context(conn, feature_id: str) -> dict: ...
  ```
  All views join against trust_registry for trust_warnings. Return dict (not string).
- **State:** PENDING

---

#### TC-OCRD-C5-03 (Child): Validation

##### MS-C5-03-01 — Run new query commands
- **Action:**
  ```bash
  python -m tools.supervisor.control_index.query control-layers
  python -m tools.supervisor.control_index.query resume-context
  python -m tools.supervisor.control_index.query gap-attempts --outcome failed
  python -m tools.supervisor.control_index.query trust-status reports/supervisor/next-sprint.md
  ```
- **Expected:** All commands return JSON without error
- **State:** PENDING

---

### TC-OCRD-C6 (Parent): Control Layer Governance Validators

**Status:** OPEN
**Priority:** P3
**Depends on:** TC-OCRD-C5, TC-OCRD-A1
**Quality Score Target:** 4/5
**Addresses:** REQ-OCRD-020

---

#### TC-OCRD-C6-01 (Child): Create governance_validators_control_layer.py

##### MS-C6-01-01 — Read governance_validators_ext4.py for pattern
- **Action:** Read `tools/supervisor/governance_validators_ext4.py` to confirm validator function signature
- **State:** PENDING

##### MS-C6-01-02 — Write 6 validators
- **Action:** Create `tools/supervisor/governance_validators_control_layer.py`:

  | V-ID | Validator | Effect |
  |---|---|---|
  | V{N} | validate_evidence_paths_resolve | FAIL — evidence files must exist |
  | V{N+1} | validate_receipt_claimed_before_closure | WARN — advisory |
  | V{N+2} | validate_no_quarantined_plan_source | FAIL — quarantined plan blocked |
  | V{N+3} | validate_contradiction_signal_checked | WARN — advisory |
  | V{N+4} | validate_gap_not_exhausted | WARN — advisory |
  | V{N+5} | validate_sync_report_fresh | WARN — advisory |

  Validators needing DB access: open control-index.db read-only; if DB absent → WARN_MISSING_CONTROL_INDEX (not FAIL)
- **State:** PENDING

---

#### TC-OCRD-C6-02 (Child): Register in governance_validator_runner.py

##### MS-C6-02-01 — Add import and +6 to expected_count
- **Action:** Edit `tools/supervisor/governance_validator_runner.py`:
  - Add import of new validators
  - Add 6 new validators to runner list
  - Increment expected_count by 6 (165 → 171)
- **State:** PENDING

##### MS-C6-02-02 — Run governance validator test to confirm new count
- **Action:** `.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -v -k expected_count`
- **Expected:** PASS with updated count
- **State:** PENDING

---

### TC-OCRD-C7 (Parent): Skill Registration (10 Skills)

**Status:** OPEN
**Priority:** P3
**Depends on:** TC-OCRD-C6
**Quality Score Target:** 3/5
**Addresses:** REQ-OCRD-021

---

#### TC-OCRD-C7-01 (Child): Register 10 Skills in skill-registry.yaml

##### MS-C7-01-01 — Read .supervisor/skill-registry.yaml for format
- **Action:** Read `.supervisor/skill-registry.yaml` — confirm skill block format and placement rule (before top-level keys)
- **State:** PENDING

##### MS-C7-01-02 — Add 10 skills
- **Action:** Add the following skills (blocks BEFORE top-level keys per MEMORY.md pattern):

  | Command | Entry Point |
  |---|---|
  | /discover-existing-control-layers | tools/supervisor/control_index/artifact_scanner.py |
  | /inventory-existing-control-features | tools/supervisor/control_index/feature_scanner.py |
  | /verify-control-feature-parity | tools/supervisor/control_index/parity_checker.py |
  | /build-task-context | tools/supervisor/control_index/views.py |
  | /build-resume-context | tools/supervisor/control_index/views.py |
  | /build-product-context | tools/supervisor/control_index/views.py |
  | /rebuild-operational-index | existing CLI |
  | /validate-operational-index | tools/supervisor/control_index/upstream_validator.py |
  | /quarantine-invalid-artifact | tools/supervisor/control_index/upstream_validator.py |
  | /audit-enhanced-control-layer | tools/supervisor/control_index/audit.py |

- **State:** PENDING

---

#### TC-OCRD-C7-02 (Child): Update command-registry.yaml and capabilities/registry.yaml

##### MS-C7-02-01 — Add 10 entries to .claude/commands/command-registry.yaml
- **State:** PENDING

##### MS-C7-02-02 — Add 10 entries to .governance/capabilities/registry.yaml
- **State:** PENDING

##### MS-C7-02-03 — Create 10 command .md files in .claude/commands/
- **Action:** For each new skill, create a minimal command file with: purpose, entry point, usage
- **State:** PENDING

---

### TC-OCRD-C8 (Parent): Pilot Test Suite (22 Pilots)

**Status:** OPEN
**Priority:** P3
**Depends on:** TC-OCRD-C7
**Quality Score Target:** 4/5
**Addresses:** Protocol §§38-44

**High-value pilots (address root causes):**
- Pilot 2: feature inventory completeness (≥50 features)
- Pilot 5: plan_ingestor populates plans table correctly
- Pilot 7: taskcard indexing — gap_attempts queryable
- Pilot 12: contradiction detection — B1 signal works end-to-end
- Pilot 13: malformed upstream — quarantine instead of silent skip
- Pilot 15: incremental sync — hash-based dedup works after A2/A3 changes
- Pilot 16: full rebuild — regression test for all structural repairs
- Pilot 19: secret exclusion — synthetic key `sk-ant-SYNTHETIC-TEST-KEY-DO-NOT-INDEX`
- Pilot 21: idempotency — second sync produces zero material changes

---

#### TC-OCRD-C8-01 (Child): test_pilots_group_ab.py (Pilots 1-6)

##### MS-C8-01-01 — Write tests/supervisor/test_pilots_group_ab.py
- Pilots 1-6: discovery, inventory, consumer map
- All use `tmp_path` fixture (never touch .local/supervisor/control-index.db)
- **State:** PENDING

---

#### TC-OCRD-C8-02 (Child): test_pilots_group_cd.py (Pilots 7-11)

##### MS-C8-02-01 — Write tests/supervisor/test_pilots_group_cd.py
- Pilots 7-11: taskcard indexing, evidence spot-check, gap attempt history
- **State:** PENDING

---

#### TC-OCRD-C8-03 (Child): test_pilots_group_ef.py (Pilots 12-16)

##### MS-C8-03-01 — Write tests/supervisor/test_pilots_group_ef.py
- Pilots 12-16: contradiction, malformed upstream, stale sync, incremental, full rebuild
- **State:** PENDING

---

#### TC-OCRD-C8-04 (Child): test_pilots_group_gh.py (Pilots 17-22)

##### MS-C8-04-01 — Write tests/supervisor/test_pilots_group_gh.py
- Pilots 17-22: compatibility, supervisor integration, secret exclusion, human navigation, idempotency, recovery
- Pilot 19: use `sk-ant-SYNTHETIC-TEST-KEY-DO-NOT-INDEX` (not a real key)
- **State:** PENDING

---

#### TC-OCRD-C8-05 (Child): Run All Pilots

##### MS-C8-05-01 — Run all pilot test files
- **Action:**
  ```bash
  .venv/Scripts/pytest tests/supervisor/test_pilots_group_ab.py \
    tests/supervisor/test_pilots_group_cd.py \
    tests/supervisor/test_pilots_group_ef.py \
    tests/supervisor/test_pilots_group_gh.py -v
  ```
- **Expected:** 22/22 PASS
- **State:** PENDING

---

### TC-OCRD-C9 (Parent): Permanent Layer Plan + Index Update

**Status:** OPEN
**Priority:** P3
**Depends on:** TC-OCRD-C8
**Quality Score Target:** 4/5
**Addresses:** REQ-OCRD-022

---

#### TC-OCRD-C9-01 (Child): Create Layer Plan

##### MS-C9-01-01 — Read plans/layers/ for next available layer number
- **Action:** Read `plans/layers/index.yaml` — find highest layer_id
- **State:** PENDING

##### MS-C9-01-02 — Create plans/layers/operational-control-record-discovery-layer.md
- **Action:** Create permanent layer plan with:
  - YAML frontmatter: layer_id=L29 (or next available), status=GOVERNED_OPERATIONAL,
    health=HEALTHY, maturity_current=3, maturity_target=4 (NOT 5 — deferred)
  - plane: GOVERNANCE
  - dependencies: [L08, L09, L11, L12, L13]
  - skill_ids: all 10 new skills from TC-OCRD-C7
  - Taskcard Status Table (REQUIRED by lifecycle_audit.py — table format, 2 columns):
    ```
    | TC-ID | Status |
    |---|---|
    | TC-OCRD-A4 | CLOSED |
    ... (all 16 TC-OCRD-* entries)
    ```
  - Known Limitations section (honest — DB disconnected from decision loop, self-reported evidence)
- **State:** PENDING

---

#### TC-OCRD-C9-02 (Child): Update Index Files

##### MS-C9-02-01 — Add L29 to plans/layers/index.yaml
- **State:** PENDING

##### MS-C9-02-02 — Add TC-OCRD-* to plans/layers/task-register.yaml
- **State:** PENDING

##### MS-C9-02-03 — Add L29 to plans/layers/dependency-register.yaml
- **State:** PENDING

##### MS-C9-02-04 — Add L29 to plans/layers/handoff-register.yaml
- Handoffs: H1 gap_attempts→L11, H2 existing-control-layers.yaml→L12, H3 views.get_resume_context()→agents
- **State:** PENDING

---

#### TC-OCRD-C9-03 (Child): Update operational-control-index.md

##### MS-C9-03-01 — Add new query commands to docs/automation/operational-control-index.md
- **Action:** Document all 8 new subcommands with examples
- **State:** PENDING

---

#### TC-OCRD-C9-04 (Child): Validation

##### MS-C9-04-01 — Verify layer plan YAML frontmatter parses
- **Action:**
  ```bash
  python -c "
  import yaml, re
  text = open('plans/layers/operational-control-record-discovery-layer.md').read()
  m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
  if m: yaml.safe_load(m.group(1)); print('YAML OK')
  "
  ```
- **Expected:** YAML OK
- **State:** PENDING

##### MS-C9-04-02 — Verify index.yaml contains L29
- **Action:**
  ```bash
  python -c "
  import yaml
  data = yaml.safe_load(open('plans/layers/index.yaml'))
  ids = [l.get('layer_id') for l in data.get('layers', [])]
  print('L29 in index:', 'L29' in ids)
  "
  ```
- **Expected:** True
- **State:** PENDING

---

## State Machine

```yaml
state_machine:
  parent_taskcard_states:
    - OPEN: initial state, no work started
    - IN_PROGRESS: at least one child ACTIVE
    - CHILDREN_IN_PROGRESS: all children executing
    - INTEGRATION_PENDING: all children COMPLETE, integration validation pending
    - VERIFIED: integration validation PASSED
    - CLOSED: evidence contract satisfied, status table updated

  child_taskcard_states:
    - OPEN: not started
    - IN_PROGRESS: micro-steps executing
    - COMPLETE: all micro-steps COMPLETE, child-level validation passed
    - FAILED: a micro-step FAILED, cannot continue without fix
    - BLOCKED: depends on incomplete parent/child

  micro_step_states:
    - PENDING: not started
    - ACTIVE: currently executing
    - COMPLETE: action taken, expected result confirmed
    - FAILED: action taken, expected result NOT met
    - BLOCKED: dependency not satisfied
    - SKIPPED_NA: condition in MS description not applicable

  transitions:
    parent_open_to_in_progress: "First child moves to IN_PROGRESS"
    child_complete_to_parent_verified: "All children COMPLETE AND integration validation PASS"
    any_ms_failed_to_child_failed: "Any FAILED micro-step fails the child unless SKIPPED_NA applies"
    child_failed_blocks_next_child: "Sequential children only — parallel children unaffected"

  rollback_rules:
    - "If MS-A4-01-02 FAILS: revert db.py to pre-edit state (git checkout)"
    - "If MS-A2-02-02 FAILS: revert sync.py to pre-edit state"
    - "If any schema SQL MS FAILS: drop added tables via migration rollback function"
    - "If test MS FAILS: fix implementation (not tests) before marking COMPLETE"
```

---

## Validation Matrix

| Taskcard | Command | Expected Output | Gate Type |
|---|---|---|---|
| TC-OCRD-A4 | `python -c "from tools.supervisor.control_index.db import apply_migrations; print('OK')"` | `OK` | blocking |
| TC-OCRD-A4 | `.venv/Scripts/pytest tests/supervisor/test_schema_migrations.py -v` | `5 passed` | blocking |
| TC-OCRD-A1 | `python -m tools.supervisor.control_index.query sql "SELECT count(*) FROM gap_attempts"` | integer (≥0) | blocking |
| TC-OCRD-A1 | `.venv/Scripts/pytest tests/supervisor/test_gap_attempt_registry.py -v` | `7 passed` | blocking |
| TC-OCRD-A2 | `.venv/Scripts/pytest tests/supervisor/test_ingestor_transactions.py -v` | `4 passed` | blocking |
| TC-OCRD-A3 | `python -m tools.supervisor.control_index sync && python -m json.tool .local/supervisor/last-sync-report.json` | valid JSON with required keys | blocking |
| TC-OCRD-A3 | `.venv/Scripts/pytest tests/supervisor/test_sync_health.py -v` | `6 passed` | blocking |
| TC-OCRD-A5 | `.venv/Scripts/pytest tests/supervisor/test_evidence_verifier.py -v` | `6 passed` | blocking |
| TC-OCRD-B1 | `python tools/supervisor/check_continuation.py \| python -m json.tool \| grep contradiction_warnings` | key present | advisory |
| TC-OCRD-B2 | `.venv/Scripts/pytest tests/supervisor/test_gap_selection.py -v` | `5 passed` | blocking |
| TC-OCRD-C1 | `python -c "import yaml; d=yaml.safe_load(open('reports/control-layer/existing-control-layers.yaml')); print(len(d['existing_control_layers']))"` | ≥12 | blocking |
| TC-OCRD-C3 | `python -m tools.supervisor.control_index.query sql "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"` | includes control_layers, quarantines, trust_registry | blocking |
| TC-OCRD-C6 | `.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -v -k expected_count` | PASS | blocking |
| TC-OCRD-C8 | `.venv/Scripts/pytest tests/supervisor/test_pilots_group_*.py -v` | 22 passed | blocking |
| TC-OCRD-C9 | `python -c "import yaml; yaml.safe_load(open('plans/layers/index.yaml'))"` | no error, L29 present | advisory |

---

## Evidence Contract

### Obligation Matrix

| TC-ID | Deliverable Type | Minimum Evidence |
|---|---|---|
| TC-OCRD-A4 | code + test | db.py modified, 5 tests PASS |
| TC-OCRD-A1 | schema + code + test | schema.sql modified, evidence_ingestor.py modified, gap_selection.py created, 7 tests PASS |
| TC-OCRD-A2 | code + test | sync.py modified, 4 tests PASS |
| TC-OCRD-A3 | code + test + artifact | sync.py modified, check_continuation.py modified, last-sync-report.json exists, 6 tests PASS |
| TC-OCRD-A5 | code + test | evidence_verifier.py created, inspect_declared_evidence.py modified, 6 tests PASS |
| TC-OCRD-B1 | code + test | autonomous_cycle.py modified, check_continuation.py modified, 4 tests PASS |
| TC-OCRD-B2 | code + test + artifact | capability_queue_consumer.py modified, 5 tests PASS, exhausted-gaps.json exists |
| TC-OCRD-C1 | artifact (YAML files) | 4 YAML files created, all parse without error |
| TC-OCRD-C2 | artifact | feature-parity-register.yaml, ADR-001 created |
| TC-OCRD-C3 | schema + migration | schema.sql modified, migration function registered, new tables exist |
| TC-OCRD-C4 | code | 3 new ingestors created, registered in sync.py |
| TC-OCRD-C5 | code | 7 new query subcommands added, views.py created |
| TC-OCRD-C6 | code + test | 6 validators created, expected_count updated, test PASS |
| TC-OCRD-C7 | registry | 10 skills in skill-registry.yaml, 10 command files created |
| TC-OCRD-C8 | test | 22 pilot tests PASS |
| TC-OCRD-C9 | artifact + registry | layer plan created, index.yaml updated |

### Traceability Map

| REQ-ID | Parent TC | Child TC | Micro-Step |
|---|---|---|---|
| REQ-OCRD-001 | TC-OCRD-A1 | TC-OCRD-A1-01 | MS-A1-01-02 (gap_attempts table) |
| REQ-OCRD-002 | TC-OCRD-A1 | TC-OCRD-A1-02 | MS-A1-02-03 (ingestor writes rows) |
| REQ-OCRD-003 | TC-OCRD-B2 | TC-OCRD-B2-02 | MS-B2-02-01 (inject filter) |
| REQ-OCRD-004 | TC-OCRD-A2 | TC-OCRD-A2-02 | MS-A2-02-02 (SAVEPOINT pattern) |
| REQ-OCRD-005 | TC-OCRD-A2 | TC-OCRD-A2-02 | MS-A2-02-02 (ROLLBACK TO SAVEPOINT) |
| REQ-OCRD-006 | TC-OCRD-A3 | TC-OCRD-A3-01, TC-OCRD-A3-03 | MS-A3-01-02, MS-A3-03-01 |
| REQ-OCRD-007 | TC-OCRD-A4 | TC-OCRD-A4-01 | MS-A4-01-02 (MIGRATIONS list) |
| REQ-OCRD-008 | TC-OCRD-A4 | TC-OCRD-A4-01 | MS-A4-01-03 (apply_migrations in ensure_db) |
| REQ-OCRD-010 | TC-OCRD-A5 | TC-OCRD-A5-01 | MS-A5-01-02 (evidence_verifier.py) |
| REQ-OCRD-011 | TC-OCRD-B1 | TC-OCRD-B1-01 | MS-B1-01-03 (signal dict fields) |
| REQ-OCRD-012 | TC-OCRD-A3 | TC-OCRD-A3-04 | MS-A3-04-03 (control_index_warnings key) |
| REQ-OCRD-013 | TC-OCRD-B2 | TC-OCRD-B2-03 | MS-B2-03-02 (generate_exhausted_gaps.py) |

---

## Plan Reconciliation

### Corrections Applied in This Revision

**Correction 1 — TC-OCRD-B2 implementation path:**
- Previous text: "Expected finding: The prompt-based path is more likely given the system architecture."
- Verified fact: Gap selection is 100% code-based in `capability_queue_consumer.py::load_foss_gaps()` lines 114-161
- Correction applied: TC-OCRD-B2-02 targets lines 150-152 of that specific function

**Correction 2 — TC-OCRD-A3/B1 `warnings` field:**
- Previous text: "adds to a `warnings` field in the output"
- Verified fact: `check_continuation.py` CONTINUE output has no `warnings` field. Fields are `lane_starvation_warnings` (list) and `warning` (singular string)
- Correction applied: TC-OCRD-A3-04 adds new key `control_index_warnings: list[str]`. TC-OCRD-B1-02 adds new key `contradiction_warnings: list[str]`. Neither overwrites existing fields.

**Correction 3 — get_connection() read_only parameter:**
- The call in TC-OCRD-B2-02 uses `get_connection(DEFAULT_DB_PATH, read_only=True)`
- Implementation must verify `get_connection()` accepts a `read_only` parameter, or use `sqlite3.connect(str(DEFAULT_DB_PATH), uri=True)` with `?mode=ro` query string as alternative

### What was preserved from original analysis

- All 8 findings (accurate, code-verified)
- All 5 root causes (accurate)
- All items in "What to preserve" (architecturally sound)
- TC-OCRD-A4 moving to P0 (prerequisite ordering was correct)
- Schema SQL for gap_attempts (unchanged)
- SAVEPOINT rationale (unchanged)
- Evidence spot-check AST approach (unchanged)
- Group A before Group C gate (unchanged)

---

## Tradeoffs and Known Limits

**What this plan does NOT solve:**
- Supreme Directive tension: contradictions remain non-blocking (TC-OCRD-B1 adds signal, not enforcement)
- Evidence self-reporting remains partially gameable (spot-check detects gross mismatches only)
- Control index remains disconnected from continuation for gap/task state (partial cure via exhausted gaps filter)

**Risks:**
- Per-ingestor SAVEPOINTs may surface previously-hidden bugs that survived because partial writes persisted
- gap_attempts threshold=3 may quarantine legitimate hard gaps — threshold should be per-gap-configurable in gap_ledger.json
- plan_ingestor may misclassify plans in non-standard directories

**Confidence levels:**
- TC-OCRD-A4: HIGH (standard SQLite + Python PRAGMA pattern)
- TC-OCRD-A1: HIGH (schema addition + ingestor modification are mechanical)
- TC-OCRD-A2: HIGH (SAVEPOINTs are standard SQLite)
- TC-OCRD-A3: HIGH (staleness.py exists, SyncReport dataclass modification is straightforward)
- TC-OCRD-B2: HIGH (inject point confirmed by code read — not speculative)
- TC-OCRD-C4: MEDIUM (each ingestor is straightforward; risk is C1 YAML files being incomplete)

---

## End-to-End Verification Sequence

```bash
# 1. Schema foundation
python -m tools.supervisor.control_index init
python -c "from tools.supervisor.control_index import SCHEMA_VERSION; assert SCHEMA_VERSION >= 3"

# 2. Group A structural tests
.venv/Scripts/pytest tests/supervisor/test_schema_migrations.py -v         # 5 PASS
.venv/Scripts/pytest tests/supervisor/test_gap_attempt_registry.py -v      # 7 PASS
.venv/Scripts/pytest tests/supervisor/test_ingestor_transactions.py -v     # 4 PASS
.venv/Scripts/pytest tests/supervisor/test_sync_health.py -v               # 6 PASS
.venv/Scripts/pytest tests/supervisor/test_evidence_verifier.py -v         # 6 PASS

# 3. Sync produces health report
python -m tools.supervisor.control_index sync
python -m json.tool .local/supervisor/last-sync-report.json

# 4. Gap attempts queryable
python -m tools.supervisor.control_index.query gap-attempts --outcome failed

# 5. Exhausted gap detection
python -c "
from tools.supervisor.control_index import get_connection, DEFAULT_DB_PATH
from tools.supervisor.control_index.gap_selection import get_exhausted_gaps
conn = get_connection(DEFAULT_DB_PATH)
print('Exhausted gaps:', len(get_exhausted_gaps(conn, 3)))
conn.close()
"

# 6. Signal improvements
python tools/supervisor/check_continuation.py | python -m json.tool | grep -E "control_index_warnings|contradiction_warnings"

# 7. Group B tests
.venv/Scripts/pytest tests/supervisor/test_contradiction_signal.py -v      # 4 PASS
.venv/Scripts/pytest tests/supervisor/test_gap_selection.py -v             # 5 PASS

# 8. Group C validations (after C1-C8 complete)
python -m tools.supervisor.control_index.query control-layers
python -m tools.supervisor.control_index.query resume-context
.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -v -k expected_count
.venv/Scripts/pytest tests/supervisor/test_pilots_group_ab.py tests/supervisor/test_pilots_group_cd.py \
  tests/supervisor/test_pilots_group_ef.py tests/supervisor/test_pilots_group_gh.py -v

# 9. Idempotency (second sync zero material changes)
python -m tools.supervisor.control_index sync
python -c "
import json
r = json.load(open('.local/supervisor/last-sync-report.json'))
print('Errors:', r['total_errors'])
# Expect: 0 errors, total_inserted approximately same as first sync (or 0 for incremental)
"

# 10. Full rebuild proof
python -m tools.supervisor.control_index rebuild
python -m tools.supervisor.control_index status
```

---

## Execution Handoff

**Next action:** Start with TC-OCRD-A4 — it is P0 and has no dependencies.

**Execution order (strictly sequential within group):**
1. TC-OCRD-A4 → TC-OCRD-A1 → TC-OCRD-A2 → TC-OCRD-A3 → TC-OCRD-A5
2. Then B1 and B2 in parallel (both depend on A group)
3. Then C1 → C2 → C3 → C4 → C5 → C6 → C7 → C8 → C9

**Gate between A and C:** All Group A regression tests must PASS. Manual check required.

**Per-taskcard handoff rule:** When a parent taskcard's last child is COMPLETE, immediately
verify the TC-level validation commands (listed per TC above) before marking parent CLOSED.

**Plan lock:** After all 16 TC-OCRD-* are CLOSED:
```bash
python tools/supervisor/lifecycle_audit.py --mission-id FF-OCRD-001 --sprint-id TC-OCRD-C9
python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/silly-popping-tower.md --terminal --audit-gate
```

---

## Taskcard Status Table (for lifecycle_audit.py)

| TC-ID | Status |
|---|---|
| TC-OCRD-A4 | OPEN |
| TC-OCRD-A1 | OPEN |
| TC-OCRD-A2 | OPEN |
| TC-OCRD-A3 | OPEN |
| TC-OCRD-A5 | OPEN |
| TC-OCRD-B1 | OPEN |
| TC-OCRD-B2 | OPEN |
| TC-OCRD-C1 | OPEN |
| TC-OCRD-C2 | OPEN |
| TC-OCRD-C3 | OPEN |
| TC-OCRD-C4 | OPEN |
| TC-OCRD-C5 | OPEN |
| TC-OCRD-C6 | OPEN |
| TC-OCRD-C7 | OPEN |
| TC-OCRD-C8 | OPEN |
| TC-OCRD-C9 | OPEN |
