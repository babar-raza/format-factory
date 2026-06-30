# Operational Control Index — SQLite Overlay Plan

authoritative_plan: plans/.claude/dazzling-nibbling-liskov.md
plan_type: machinery_hardening
mission_id: FF-CTRL-INDEX-001

---

## Context

Format Factory has an extremely mature autonomous supervision system — 191+ Python tools in `tools/supervisor/`, 86 governance validators, 74 registered skills, 27 JSON schemas, 27 independent layers. However, ALL operational state lives in scattered JSON/YAML/JSONL/Markdown files across `.local/supervisor/`, `reports/`, `.supervisor/`, `registry/`, `plans/layers/`, and `shared/qname-registry/`. There is **no central queryable store**.

**Problem:** Agents must scan directories and parse multiple large files for routine lookups. The gap-ledger alone is 424K lines. 104 plan-lock files are scanned linearly. There's no full-text search, no relationship traversal (gap→work-item→evidence→grade), no unified history, and no cross-entity contradiction detection.

**Solution:** Add a **non-destructive SQLite+FTS5 overlay index** at `.local/supervisor/control-index.db`. Source files remain the authority. The index is disposable and reconstructible. Zero breaking changes to existing tools.

---

## Architecture Decision

**Component:** SQLite 3 (Python stdlib `sqlite3`) + FTS5 extension
**Location:** `.local/supervisor/control-index.db` (gitignored — `.local/` already in `.gitignore`)
**Justification:**
- Zero new dependencies (`sqlite3` is stdlib, `yaml` already used by 37+ supervisor modules)
- Data volume is modest (~5K rows across all tables)
- Single-file, portable, offline, Windows-compatible
- FTS5 enables full-text search across all operational text
- WAL mode handles concurrent reads during writes
- Reconstructible from source files in <60 seconds

**Alternatives rejected:**
- DuckDB: requires pip install, analytical focus, overkill for this volume
- TinyDB: no FTS, no SQL joins, would need custom index code
- Plain JSON with jq: already the status quo; the whole point is to get beyond it

---

## Existing Control Layers Discovered

| Layer | Location | Status | Features |
|---|---|---|---|
| Supervisor Control Plane | `tools/supervisor/` (191 files) | ACTIVE | Autonomous cycle, continuation, grading, evidence, governance |
| State Management | `.local/supervisor/` | ACTIVE | Continuation signal, plan locks, grade cache, failure memory |
| Governance Registry | `.supervisor/`, `.governance/` | ACTIVE | Skill registry, capability registry, 27 schemas, policies |
| Report Layer | `reports/supervisor/`, `reports/capability-layer/` | ACTIVE | Session-resume, approval-gates, gap-ledger, capability maps |
| Format & Product Registry | `registry/` | ACTIVE | Format registry, parity matrix, source baseline |
| Layer Architecture | `plans/layers/` | ACTIVE | 27 layer plans, task/dependency/decision registers |
| Oracle Layer | `tools/oracle/` | ACTIVE | 20 format executors, all VERIFIED |
| QName Registry | `shared/qname-registry/` | ACTIVE | 21 format YAML files, 66 entries |

**Key finding:** No existing database, index, or central query tool exists. The enhanced layer fills a genuine gap without replacing anything.

---

## Verified Source Schemas

All source file structures verified at HEAD. Exact field names confirmed.

| Source File | Format | Top-level Key | Record Count | Key Fields |
|---|---|---|---|---|
| `reports/capability-layer/gap-ledger.json` | JSON | `{"gaps": [...]}` | ~1277 | gap_id, format, product_type, capability_name, status, priority, spec_facts[], notes |
| `registry/format-registry.yaml` | YAML | `formats: [...]` | ~25 | format_id, display_name, family, extensions[], mime_type, tier_target, legal_category, scoring{} |
| `.supervisor/skill-registry.yaml` | YAML | `skills: [...]` | ~74 | command, command_file, skill_id, status, product_track, purpose, idempotency |
| `.governance/capabilities/registry.yaml` | YAML | `capabilities: [...]` | ~93 | capability_id, parity_status, product_track, status, agent_surfaces{}, purpose |
| `.local/supervisor/failure-memory.json` | JSON | `{"failures": [...]}` | ~31 | id, category, root_cause, correction, severity, occurrence_count, escalated, resolved |
| `.local/supervisor/plan-locks/*.json` | JSON | flat object | ~104 files | plan_path, status, session_id, track_type, last_taskcard, terminal_reason |
| `.local/supervisor/continuation-ledger.jsonl` | JSONL | one obj/line | ~5809 | timestamp, event_type, artifact_path, session_id, sprint_id |
| `plans/layers/index.yaml` | YAML | `layers: [...]` | ~11 | layer_id, canonical_name, plane, status, health, maturity_current, dependencies[], skill_ids[] |
| `shared/qname-registry/*.yaml` | YAML | flat array | ~66 total | qname, namespace_uri, local_name, canonical_class, spec_fact_ref, status, facade_names[] |
| `registry/source-structure-baseline.json` | JSON | `{"known_violations": {...}}` | varies | file_path (key), loc, baseline_loc_cap, functions, baseline_functions_cap, category |
| `.local/evidences/*/evidence-declaration.yaml` | YAML | flat object | ~3199 dirs | run_id, sprint_id, verdict, tests_run, declared_scope, planned_work_items[] |
| `.local/supervisor/continuation-signal.json` | JSON | flat object | 1 | autonomous_continue, iteration, max_iterations, session_id, continuation_state |
| `.local/supervisor/grade-cache.json` | JSON | `{key: grade}` | varies | adequate, confidence, llm_used, _cached_at, stub_detected, deficiencies[] |

---

## Infrastructure Verification

| Check | Result |
|---|---|
| `.local/` in `.gitignore` | YES (lines 7-8) |
| `tools/supervisor/control_index/` exists | NO — must create |
| PyYAML available | YES — 37+ supervisor modules use `import yaml` |
| `atomic_io.py` pattern | write-to-temp + `os.replace()` — reuse for consistency |
| CLI pattern | `if __name__ == "__main__": main()` + `__main__.py` for packages |
| Test directory | `tests/supervisor/test_*.py` — established convention |
| Schema migration pattern | `cci_migration.py` — version stamp + scan + detect + stamp |
| `control-index.db` exists | NO — will be created on first `--init` |

---

## Implementation Structure

```
tools/supervisor/control_index/
    __init__.py          # Package root + ControlIndex class
    __main__.py          # CLI entry: python -m tools.supervisor.control_index
    db.py                # Connection manager (WAL, busy_timeout, migrations)
    schema.sql           # DDL for all tables, indexes, FTS5
    sync.py              # Orchestrator: incremental + full rebuild
    query.py             # CLI query interface
    search.py            # FTS5 search wrapper
    staleness.py         # Stale/contradiction detection
    adapters/
        __init__.py
        json_adapter.py  # JSON + JSONL parser
        yaml_adapter.py  # YAML (single + multi-doc)
    ingestors/
        __init__.py
        format_ingestor.py       # registry/format-registry.yaml → formats
        gap_ingestor.py          # gap-ledger.json → gaps, gap_spec_facts
        qname_ingestor.py        # shared/qname-registry/*.yaml → qnames
        capability_ingestor.py   # .governance/capabilities/registry.yaml → capabilities
        skill_ingestor.py        # .supervisor/skill-registry.yaml → skills
        evidence_ingestor.py     # .local/evidences/*/evidence-declaration.yaml → sprints, sprint_work_items
        failure_ingestor.py      # failure-memory.json → failures
        layer_ingestor.py        # plans/layers/index.yaml → layers, layer_dependencies
        plan_lock_ingestor.py    # .local/supervisor/plan-locks/*.json → plan_locks
        violation_ingestor.py    # source-structure-baseline.json → source_violations
        event_ingestor.py        # continuation-ledger.jsonl → events

tests/supervisor/
    test_control_index_db.py
    test_control_index_adapters.py
    test_control_index_ingestors.py
    test_control_index_sync.py
    test_control_index_query.py
    test_control_index_parity.py
```

---

## Core Schema (full DDL)

```sql
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;

-- Schema version tracking
CREATE TABLE schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Sync tracking (one row per source file)
CREATE TABLE source_manifest (
    source_path   TEXT PRIMARY KEY,
    entity_type   TEXT NOT NULL,
    last_hash     TEXT,
    last_ingested TEXT,
    last_modified TEXT,
    row_count     INTEGER,
    file_size     INTEGER
);

-- T1: Formats (~25 rows)
CREATE TABLE formats (
    format_id    TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    family       TEXT,
    extensions   TEXT,  -- JSON array
    mime_type    TEXT,
    spec_body    TEXT,
    spec_version TEXT,
    legal_category INTEGER,
    tier_target  INTEGER,
    visibility   TEXT,
    scoring_total INTEGER,
    raw_json     TEXT NOT NULL,
    source_file  TEXT NOT NULL,
    ingested_at  TEXT NOT NULL,
    source_hash  TEXT NOT NULL
);

-- T2: Gaps (~1277 rows)
CREATE TABLE gaps (
    gap_id       TEXT PRIMARY KEY,
    format       TEXT,
    product_type TEXT,
    capability_name TEXT,
    current_state TEXT,
    gap_type     TEXT,
    status       TEXT NOT NULL,
    priority     TEXT,
    blocks_poc   INTEGER,
    blocks_readiness INTEGER,
    commercial_impact TEXT,
    foss_impact  TEXT,
    owning_lane  INTEGER,
    related_capability_id TEXT,
    notes        TEXT,
    raw_json     TEXT NOT NULL,
    source_file  TEXT NOT NULL,
    ingested_at  TEXT NOT NULL,
    source_hash  TEXT NOT NULL
);
CREATE INDEX idx_gaps_format ON gaps(format);
CREATE INDEX idx_gaps_status ON gaps(status);
CREATE INDEX idx_gaps_priority ON gaps(priority);

-- T2b: Gap spec_facts junction
CREATE TABLE gap_spec_facts (
    gap_id       TEXT NOT NULL,
    spec_fact_ref TEXT NOT NULL,
    PRIMARY KEY (gap_id, spec_fact_ref)
);

-- T3: QNames (~66 rows)
CREATE TABLE qnames (
    qname        TEXT PRIMARY KEY,
    format_id    TEXT,
    namespace_uri TEXT,
    local_name   TEXT,
    canonical_class TEXT,
    spec_fact_ref TEXT,
    status       TEXT,
    source_layer TEXT,
    python_file  TEXT,
    dotnet_file  TEXT,
    facade_names TEXT,  -- JSON array
    raw_yaml     TEXT NOT NULL,
    source_file  TEXT NOT NULL,
    ingested_at  TEXT NOT NULL,
    source_hash  TEXT NOT NULL
);
CREATE INDEX idx_qnames_format ON qnames(format_id);

-- T4: Capabilities (~93 rows)
CREATE TABLE capabilities (
    capability_id TEXT PRIMARY KEY,
    command_file TEXT,
    parity_status TEXT,
    product_track TEXT,
    purpose      TEXT,
    status       TEXT,
    claude_code  INTEGER,
    codex        INTEGER,
    ci           INTEGER,
    raw_yaml     TEXT NOT NULL,
    source_file  TEXT NOT NULL,
    ingested_at  TEXT NOT NULL,
    source_hash  TEXT NOT NULL
);

-- T5: Skills (~74 rows)
CREATE TABLE skills (
    skill_id     TEXT PRIMARY KEY,
    command      TEXT NOT NULL,
    command_file TEXT,
    idempotency  TEXT,
    product_track TEXT,
    purpose      TEXT,
    status       TEXT,
    overflow_split_allowed INTEGER,
    raw_yaml     TEXT NOT NULL,
    source_file  TEXT NOT NULL,
    ingested_at  TEXT NOT NULL,
    source_hash  TEXT NOT NULL
);

-- T6: Sprints / Evidence Runs (~3199 rows)
CREATE TABLE sprints (
    sprint_id    TEXT PRIMARY KEY,
    run_id       TEXT,
    evidence_root TEXT,
    declared_scope TEXT,
    start_time   TEXT,
    end_time     TEXT,
    git_head_start TEXT,
    git_head_end TEXT,
    verdict      TEXT,
    test_count   INTEGER,
    fail_count   INTEGER,
    worker_self_grade TEXT,
    raw_yaml     TEXT,
    source_file  TEXT NOT NULL,
    ingested_at  TEXT NOT NULL,
    source_hash  TEXT NOT NULL
);
CREATE INDEX idx_sprints_verdict ON sprints(verdict);

-- T6b: Sprint work items
CREATE TABLE sprint_work_items (
    sprint_id    TEXT NOT NULL,
    item_id      TEXT NOT NULL,
    title        TEXT,
    item_type    TEXT,
    status       TEXT,
    gap_ledger_ref TEXT,
    PRIMARY KEY (sprint_id, item_id)
);
CREATE INDEX idx_swi_gap ON sprint_work_items(gap_ledger_ref);

-- T7: Failures (~31 rows)
CREATE TABLE failures (
    failure_id   TEXT PRIMARY KEY,
    category     TEXT NOT NULL,
    root_cause   TEXT,
    correction   TEXT,
    severity     TEXT,
    sprint_discovered TEXT,
    last_seen_sprint TEXT,
    discovered_at TEXT,
    last_seen_at TEXT,
    occurrence_count INTEGER,
    escalated    INTEGER,
    resolved     INTEGER,
    resolution   TEXT,
    resolved_at  TEXT,
    raw_json     TEXT NOT NULL,
    source_file  TEXT NOT NULL,
    ingested_at  TEXT NOT NULL,
    source_hash  TEXT NOT NULL
);
CREATE INDEX idx_failures_resolved ON failures(resolved);

-- T8: Layers (~11 rows)
CREATE TABLE layers (
    layer_id     TEXT PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    permanent_plan_path TEXT,
    plane        TEXT,
    status       TEXT,
    health       TEXT,
    maturity_current INTEGER,
    maturity_target INTEGER,
    active_task_count INTEGER,
    next_task_id TEXT,
    next_action  TEXT,
    raw_yaml     TEXT NOT NULL,
    source_file  TEXT NOT NULL,
    ingested_at  TEXT NOT NULL,
    source_hash  TEXT NOT NULL
);

-- T8b: Layer dependencies
CREATE TABLE layer_dependencies (
    upstream_layer_id TEXT NOT NULL,
    downstream_layer_id TEXT NOT NULL,
    PRIMARY KEY (upstream_layer_id, downstream_layer_id)
);

-- T9: Plan locks (~104 rows)
CREATE TABLE plan_locks (
    lock_file    TEXT PRIMARY KEY,
    plan_path    TEXT,
    status       TEXT NOT NULL,
    session_id   TEXT,
    track_type   TEXT,
    last_taskcard TEXT,
    updated_at   TEXT,
    terminal_reason TEXT,
    raw_json     TEXT NOT NULL,
    source_file  TEXT NOT NULL,
    ingested_at  TEXT NOT NULL,
    source_hash  TEXT NOT NULL
);
CREATE INDEX idx_plan_locks_status ON plan_locks(status);

-- T10: Source violations
CREATE TABLE source_violations (
    file_path    TEXT PRIMARY KEY,
    loc          INTEGER,
    baseline_loc_cap INTEGER,
    functions    INTEGER,
    baseline_functions_cap INTEGER,
    category     TEXT,
    healing_priority TEXT,
    healing_sprint TEXT,
    raw_json     TEXT NOT NULL,
    source_file  TEXT NOT NULL,
    ingested_at  TEXT NOT NULL,
    source_hash  TEXT NOT NULL
);

-- E1: Event log (append-only)
CREATE TABLE events (
    event_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp    TEXT NOT NULL,
    event_type   TEXT NOT NULL,
    source       TEXT NOT NULL,
    session_id   TEXT,
    sprint_id    TEXT,
    artifact_path TEXT,
    detail       TEXT,
    ingested_at  TEXT NOT NULL
);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_session ON events(session_id);
CREATE INDEX idx_events_ts ON events(timestamp);

-- FTS5 search
CREATE VIRTUAL TABLE fts_operational USING fts5(
    entity_type, entity_id, content,
    tokenize = 'porter unicode61'
);
```

---

## Sync Model

**Incremental (default):** For each source file, compare SHA-256 hash against `source_manifest`. Skip unchanged files. For changed files: delete all rows with that `source_file`, re-insert from parsed source, update manifest. Evidence directories: only scan dirs not yet in manifest (immutable once created).

**Full rebuild:** Delete DB file, recreate schema, run all ingestors. Expected time: <60 seconds.

**Idempotency:** Running sync twice with no file changes = zero inserts/updates on second run.

**Ingest order (dependency-aware):** formats → capabilities → skills → layers → failures → plan_locks → violations → gaps → qnames → sprints → events

---

## Query Interface

```bash
# CLI via __main__.py
python -m tools.supervisor.control_index init          # Create/migrate DB
python -m tools.supervisor.control_index sync          # Incremental sync
python -m tools.supervisor.control_index rebuild       # Full rebuild
python -m tools.supervisor.control_index status        # Show manifest + staleness

# Queries via query.py
python -m tools.supervisor.control_index.query search "stale queue qname"
python -m tools.supervisor.control_index.query gaps --format fods --status open
python -m tools.supervisor.control_index.query sprints --limit 10 --verdict ACCEPTED
python -m tools.supervisor.control_index.query failures --unresolved
python -m tools.supervisor.control_index.query plan-locks --status IN_PROGRESS
python -m tools.supervisor.control_index.query chain --gap GAP-FODS-COMM-SAVE_SAME_FO-001
python -m tools.supervisor.control_index.query format fods
python -m tools.supervisor.control_index.query stale
python -m tools.supervisor.control_index.query sql "SELECT format, COUNT(*) FROM gaps GROUP BY format"
```

Output: JSON (default), `--table` for human-readable.

---

## Key Principles

1. **Source files are ALWAYS authoritative** — index is a disposable read-only mirror
2. **Zero breaking changes** — existing tools continue reading/writing files unchanged
3. **Index is optional** — deleting `.local/supervisor/control-index.db` breaks nothing
4. **Every row has provenance** — source_file, ingested_at, source_hash on every record
5. **No write-back** — index NEVER modifies source files
6. **Sync is idempotent** — running twice = same result
7. **FTS5 replaces custom search** — built-in BM25 ranking, zero custom code

---

## Requirements Inventory

| REQ ID | Source | Requirement |
|---|---|---|
| REQ-CI-001 | Context | SQLite DB at `.local/supervisor/control-index.db`, gitignored, disposable |
| REQ-CI-002 | Context | WAL mode, busy_timeout=5000, foreign keys ON |
| REQ-CI-003 | Architecture | Zero new pip dependencies (stdlib sqlite3 + existing yaml) |
| REQ-CI-004 | Schema | 10 entity tables with provenance fields (source_file, ingested_at, source_hash) |
| REQ-CI-005 | Schema | 3 relationship tables (gap_spec_facts, sprint_work_items, layer_dependencies) |
| REQ-CI-006 | Schema | FTS5 virtual table for full-text search |
| REQ-CI-007 | Schema | source_manifest table for incremental sync tracking |
| REQ-CI-008 | Schema | schema_meta table with version tracking |
| REQ-CI-009 | Sync | SHA-256 hash-based incremental sync (skip unchanged files) |
| REQ-CI-010 | Sync | Full rebuild from source files in <60 seconds |
| REQ-CI-011 | Sync | Idempotent: sync twice = zero changes on second run |
| REQ-CI-012 | Sync | Dependency-aware ingest order |
| REQ-CI-013 | Adapters | JSON adapter: single-object + JSONL support |
| REQ-CI-014 | Adapters | YAML adapter: single-doc + list-of-records |
| REQ-CI-015 | Ingestors | One ingestor per source file type (11 total) |
| REQ-CI-016 | Query | CLI commands for search, entity queries, chain traversal, staleness |
| REQ-CI-017 | Query | JSON output (default) + --table for human-readable |
| REQ-CI-018 | Search | FTS5 search across all entity types with BM25 ranking |
| REQ-CI-019 | Staleness | Detect stale entries via source_manifest vs file mtime |
| REQ-CI-020 | Staleness | Detect contradictions (closed gap w/o evidence, etc.) |
| REQ-CI-021 | Tests | Unit tests for db, adapters, ingestors, sync, query |
| REQ-CI-022 | Tests | Parity tests: index results match direct file reads |
| REQ-CI-023 | Tests | Idempotency test: sync twice = zero changes |
| REQ-CI-024 | Tests | Recovery test: delete DB, rebuild, compare |
| REQ-CI-025 | Compat | Zero changes to existing supervisor tools |
| REQ-CI-026 | Perf | Queries <200ms, incremental sync <2s |

---

## Taskcards

### Taskcard State Machine

**Parent transitions:** PROPOSED → READY → IN_PROGRESS → CHILDREN_IN_PROGRESS → INTEGRATION_PENDING → VERIFIED → CLOSED | BLOCKED

**Child transitions:** TODO → READY → IN_PROGRESS → IMPLEMENTED → VERIFIED → CLOSED | BLOCKED | REROUTED

**Invalid transitions (blocked):** TODO → CLOSED, READY → CLOSED, IMPLEMENTED → CLOSED (must verify first), parent CLOSED while children incomplete

---

### TC-CI-001: Package Skeleton + Schema + DB Manager (Wave 0)

```
Parent Taskcard ID: TC-CI-001
Title: Create control_index package with schema and DB manager
Type: PARENT
Status: PROPOSED
Source: REQ-CI-001, REQ-CI-002, REQ-CI-003, REQ-CI-004, REQ-CI-005, REQ-CI-006, REQ-CI-007, REQ-CI-008

Objective: Working package at tools/supervisor/control_index/ that creates a SQLite DB with the full schema

Scope:
  Allowed: tools/supervisor/control_index/
  Forbidden: any existing tools/supervisor/ files

Dependencies: none (first wave)

Acceptance:
  - python -m tools.supervisor.control_index init creates DB
  - DB has all tables from schema
  - schema_meta has version=1
  - WAL mode active
  - DB at .local/supervisor/control-index.db

Rollback: delete tools/supervisor/control_index/ directory
```

#### TC-CI-001-01: Create package __init__.py

```
Child Taskcard ID: TC-CI-001-01
Parent: TC-CI-001
Title: Create control_index/__init__.py with ControlIndex class stub
Status: TODO
Source: REQ-CI-001

Scope:
  Allowed: tools/supervisor/control_index/__init__.py
  Forbidden: all other files

Micro-steps:
  MS-CI-001-01-01: Create tools/supervisor/control_index/ directory
  MS-CI-001-01-02: Create __init__.py with ControlIndex class
    - __init__(self, db_path=None) defaulting to .local/supervisor/control-index.db
    - get_db_path() returning resolved Path
    - Module-level DEFAULT_DB_PATH constant

Expected output: importable package with ControlIndex stub

Acceptance: `from tools.supervisor.control_index import ControlIndex` succeeds

Next: TC-CI-001-02
```

#### TC-CI-001-02: Create schema.sql

```
Child Taskcard ID: TC-CI-001-02
Parent: TC-CI-001
Title: Create schema.sql with full DDL
Status: TODO
Source: REQ-CI-004, REQ-CI-005, REQ-CI-006, REQ-CI-007, REQ-CI-008

Scope:
  Allowed: tools/supervisor/control_index/schema.sql
  Forbidden: all other files

Micro-steps:
  MS-CI-001-02-01: Create schema.sql with PRAGMA statements (WAL, FK, busy_timeout)
  MS-CI-001-02-02: Add schema_meta and source_manifest table DDL
  MS-CI-001-02-03: Add all 10 entity table DDL (formats through source_violations)
  MS-CI-001-02-04: Add 3 relationship table DDL (gap_spec_facts, sprint_work_items, layer_dependencies)
  MS-CI-001-02-05: Add events table DDL
  MS-CI-001-02-06: Add FTS5 virtual table DDL
  MS-CI-001-02-07: Add all CREATE INDEX statements

Expected output: Complete DDL file matching Core Schema section above

Acceptance: File parses as valid SQL (no syntax errors when executed)

Next: TC-CI-001-03
```

#### TC-CI-001-03: Create db.py

```
Child Taskcard ID: TC-CI-001-03
Parent: TC-CI-001
Title: Create db.py with connection manager and schema initialization
Status: TODO
Source: REQ-CI-001, REQ-CI-002, REQ-CI-008

Scope:
  Allowed: tools/supervisor/control_index/db.py
  Forbidden: all other files

Micro-steps:
  MS-CI-001-03-01: Create db.py with get_connection(db_path) function
    - Opens SQLite connection with WAL mode
    - Sets busy_timeout=5000, foreign_keys=ON
    - Returns context-managed connection
  MS-CI-001-03-02: Add init_db(db_path) function
    - Creates parent directory if needed
    - Reads schema.sql from package directory
    - Executes DDL within transaction
    - Inserts schema_version=1 into schema_meta
    - Inserts created_at timestamp
  MS-CI-001-03-03: Add get_schema_version(conn) function
    - Returns current schema version from schema_meta
    - Returns 0 if table doesn't exist
  MS-CI-001-03-04: Add ensure_db(db_path) function
    - Creates DB if not exists, else verifies schema version
    - Returns connection

Expected output: db.py that can create and connect to the database

Acceptance: init_db() creates DB with all tables, get_schema_version() returns 1

Dependencies: TC-CI-001-02 (needs schema.sql)
Next: TC-CI-001-04
```

#### TC-CI-001-04: Create __main__.py CLI entry point

```
Child Taskcard ID: TC-CI-001-04
Parent: TC-CI-001
Title: Create __main__.py with init/status subcommands
Status: TODO
Source: REQ-CI-001

Scope:
  Allowed: tools/supervisor/control_index/__main__.py
  Forbidden: all other files

Micro-steps:
  MS-CI-001-04-01: Create __main__.py with argparse
    - Subcommands: init, status
    - --db-path optional argument (default: .local/supervisor/control-index.db)
  MS-CI-001-04-02: Implement "init" subcommand
    - Calls db.init_db(db_path)
    - Prints table count and schema version
  MS-CI-001-04-03: Implement "status" subcommand
    - Shows DB path, file size, schema version
    - Shows source_manifest row count (0 initially)

Expected output: Working CLI at python -m tools.supervisor.control_index init

Acceptance: Running init creates DB, status shows version=1

Dependencies: TC-CI-001-03
Next: TC-CI-001-05
```

#### TC-CI-001-05: Create unit tests for Wave 0

```
Child Taskcard ID: TC-CI-001-05
Parent: TC-CI-001
Title: Create test_control_index_db.py
Status: TODO
Source: REQ-CI-021

Scope:
  Allowed: tests/supervisor/test_control_index_db.py
  Forbidden: all other files

Micro-steps:
  MS-CI-001-05-01: Create test file with pytest fixtures
    - tmp_path fixture for disposable DB
    - db_path fixture returning tmp_path / "test.db"
  MS-CI-001-05-02: Add test_init_creates_db
    - Call init_db(db_path)
    - Assert file exists
    - Assert schema_version = 1
  MS-CI-001-05-03: Add test_init_creates_all_tables
    - Call init_db(db_path)
    - Query sqlite_master for table names
    - Assert all 17 tables exist (10 entity + 3 relationship + events + source_manifest + schema_meta + fts_operational)
  MS-CI-001-05-04: Add test_wal_mode_active
    - Connect to initialized DB
    - Assert PRAGMA journal_mode returns 'wal'
  MS-CI-001-05-05: Add test_init_idempotent
    - Call init_db twice
    - Assert no error, schema_version still 1
  MS-CI-001-05-06: Run tests with .venv/Scripts/pytest tests/supervisor/test_control_index_db.py -v
    - All tests must PASS

Expected output: Passing test suite for DB initialization

Acceptance: All tests PASS

Dependencies: TC-CI-001-01, TC-CI-001-02, TC-CI-001-03
```

---

### TC-CI-002: Source Adapters + Sync Framework (Wave 1)

```
Parent Taskcard ID: TC-CI-002
Title: Create source adapters and sync orchestrator
Type: PARENT
Status: PROPOSED
Source: REQ-CI-009, REQ-CI-011, REQ-CI-013, REQ-CI-014

Objective: Adapters that parse JSON/JSONL/YAML source files with hash-based change detection, plus sync orchestrator

Dependencies: TC-CI-001 (needs DB)

Acceptance:
  - JSON adapter parses gap-ledger.json, failure-memory.json, continuation-signal.json
  - YAML adapter parses format-registry.yaml, skill-registry.yaml, qname files
  - JSONL adapter parses continuation-ledger.jsonl
  - sync.py orchestrates incremental and rebuild modes
  - needs_sync() correctly skips unchanged files

Rollback: delete adapters/ directory and sync.py
```

#### TC-CI-002-01: Create adapters/__init__.py with base class

```
Child Taskcard ID: TC-CI-002-01
Parent: TC-CI-002
Title: Create SourceAdapter base class
Status: TODO
Source: REQ-CI-013, REQ-CI-014

Scope:
  Allowed: tools/supervisor/control_index/adapters/__init__.py

Micro-steps:
  MS-CI-002-01-01: Create adapters/ directory with __init__.py
  MS-CI-002-01-02: Define SourceAdapter base class with:
    - __init__(self, source_path: Path)
    - file_hash(self) -> str: SHA-256 of file content
    - file_mtime(self) -> str: ISO-8601 mtime
    - file_size(self) -> int
    - needs_sync(self, manifest_row: dict | None) -> bool
      Logic: if no manifest_row, return True
             if hash matches manifest, return False
             else return True
    - read_records(self) -> Iterator[dict]: abstract

Expected output: Base class with hash-based change detection

Next: TC-CI-002-02
```

#### TC-CI-002-02: Create json_adapter.py

```
Child Taskcard ID: TC-CI-002-02
Parent: TC-CI-002
Title: Create JSON and JSONL adapter
Status: TODO
Source: REQ-CI-013

Scope:
  Allowed: tools/supervisor/control_index/adapters/json_adapter.py

Micro-steps:
  MS-CI-002-02-01: Create JsonAdapter(SourceAdapter) class
    - __init__(self, source_path, records_key=None)
    - records_key: for {"gaps": [...]} style, pass "gaps"
    - read_records(): if records_key, yield from data[records_key]; else yield data as single record
  MS-CI-002-02-02: Create JsonlAdapter(SourceAdapter) class
    - read_records(): read line by line, json.loads each, yield
  MS-CI-002-02-03: Create DictAdapter(SourceAdapter) class
    - For files like grade-cache.json where keys are record IDs
    - read_records(): yield {"_key": k, **v} for each k,v in data.items()
  MS-CI-002-02-04: Create MultiFileJsonAdapter(SourceAdapter) class
    - For plan-locks/*.json: reads a glob pattern of individual JSON files
    - read_records(): for each file, yield parsed JSON with _source_file added

Expected output: Adapters that parse all JSON/JSONL source file patterns

Next: TC-CI-002-03
```

#### TC-CI-002-03: Create yaml_adapter.py

```
Child Taskcard ID: TC-CI-002-03
Parent: TC-CI-002
Title: Create YAML adapter
Status: TODO
Source: REQ-CI-014

Scope:
  Allowed: tools/supervisor/control_index/adapters/yaml_adapter.py

Micro-steps:
  MS-CI-002-03-01: Create YamlAdapter(SourceAdapter) class
    - __init__(self, source_path, records_key=None)
    - records_key: for "formats: [...]" style, pass "formats"
    - read_records(): yaml.safe_load, then yield from data[records_key] if key, else yield data
  MS-CI-002-03-02: Create YamlArrayAdapter(SourceAdapter) class
    - For qname files that are plain arrays (not wrapped in a key)
    - read_records(): yaml.safe_load, yield from result (which is a list)
  MS-CI-002-03-03: Create MultiFileYamlAdapter(SourceAdapter) class
    - For shared/qname-registry/*.yaml: reads multiple YAML files
    - read_records(): for each file, parse and yield records with _source_file

Expected output: Adapters that parse all YAML source file patterns

Next: TC-CI-002-04
```

#### TC-CI-002-04: Create sync.py orchestrator

```
Child Taskcard ID: TC-CI-002-04
Parent: TC-CI-002
Title: Create sync orchestrator
Status: TODO
Source: REQ-CI-009, REQ-CI-011, REQ-CI-012

Scope:
  Allowed: tools/supervisor/control_index/sync.py

Micro-steps:
  MS-CI-002-04-01: Create SyncReport dataclass
    - Fields: synced, skipped, errors (all lists of entity_type strings)
    - Method: summary() returning formatted string
  MS-CI-002-04-02: Create get_manifest_row(conn, source_path) function
    - Query source_manifest for existing row
    - Return dict or None
  MS-CI-002-04-03: Create update_manifest(conn, source_path, entity_type, hash, row_count, file_size) function
    - INSERT OR REPLACE into source_manifest
  MS-CI-002-04-04: Create sync_all(db_path, repo_root, force=False) function
    - Calls ensure_db(db_path)
    - Iterates ALL_INGESTORS in dependency order
    - For each: check needs_sync via manifest, skip if unchanged (unless force)
    - Returns SyncReport
  MS-CI-002-04-05: Create rebuild(db_path, repo_root) function
    - Delete DB file if exists
    - Call init_db, then sync_all with force=True
  MS-CI-002-04-06: Add "sync" and "rebuild" subcommands to __main__.py

Expected output: Working sync framework (ingestors will be added in TC-CI-003/004)

Dependencies: TC-CI-001, TC-CI-002-01
Next: TC-CI-002-05
```

#### TC-CI-002-05: Create adapter unit tests

```
Child Taskcard ID: TC-CI-002-05
Parent: TC-CI-002
Title: Create test_control_index_adapters.py
Status: TODO
Source: REQ-CI-021

Scope:
  Allowed: tests/supervisor/test_control_index_adapters.py

Micro-steps:
  MS-CI-002-05-01: Create test fixtures: tmp JSON, JSONL, YAML files with known content
  MS-CI-002-05-02: Add test_json_adapter_with_records_key — parse {"gaps": [{...}]}
  MS-CI-002-05-03: Add test_jsonl_adapter — parse multi-line JSONL
  MS-CI-002-05-04: Add test_yaml_adapter_with_records_key — parse "formats: [...]"
  MS-CI-002-05-05: Add test_needs_sync_true_when_no_manifest — first sync always needed
  MS-CI-002-05-06: Add test_needs_sync_false_when_hash_matches — skip unchanged
  MS-CI-002-05-07: Add test_needs_sync_true_when_hash_differs — detect changes
  MS-CI-002-05-08: Run tests: .venv/Scripts/pytest tests/supervisor/test_control_index_adapters.py -v

Expected output: All adapter tests PASS

Dependencies: TC-CI-002-01 through TC-CI-002-03
```

---

### TC-CI-003: Small Entity Ingestors (Wave 2)

```
Parent Taskcard ID: TC-CI-003
Title: Create ingestors for small entity tables
Type: PARENT
Status: PROPOSED
Source: REQ-CI-015

Objective: Ingestors for formats, capabilities, skills, layers, failures, plan_locks, source_violations — all tables with <200 rows

Dependencies: TC-CI-002 (needs adapters + sync framework)

Acceptance:
  - All 7 ingestors populate their tables correctly
  - Row counts match source files
  - Sync is idempotent (second run = zero changes)
  - Relationship tables populated (layer_dependencies)

Rollback: delete ingestor files
```

#### TC-CI-003-01: Create ingestors/__init__.py with base class

```
Child Taskcard ID: TC-CI-003-01
Parent: TC-CI-003
Title: Create BaseIngestor class
Status: TODO

Scope:
  Allowed: tools/supervisor/control_index/ingestors/__init__.py

Micro-steps:
  MS-CI-003-01-01: Create ingestors/ directory with __init__.py
  MS-CI-003-01-02: Define BaseIngestor class with:
    - entity_type: str (class attribute)
    - source_paths: list[str] (class attribute, relative to repo root)
    - __init__(self, conn, repo_root: Path)
    - get_adapter(self, source_path) -> SourceAdapter: abstract
    - ingest_records(self, conn, records: Iterator[dict], source_path: str, source_hash: str): abstract
    - sync(self, force=False) -> IngestResult
      Logic: for each source_path, check manifest, skip if unchanged,
             else delete existing rows for that source_file, call ingest_records, update manifest
  MS-CI-003-01-03: Define IngestResult dataclass: inserted, updated, skipped, errors

Expected output: Base class that all ingestors extend

Next: TC-CI-003-02
```

#### TC-CI-003-02: Create format_ingestor.py

```
Child Taskcard ID: TC-CI-003-02
Parent: TC-CI-003
Title: Create format ingestor (registry/format-registry.yaml → formats)
Status: TODO

Scope:
  Allowed: tools/supervisor/control_index/ingestors/format_ingestor.py

Micro-steps:
  MS-CI-003-02-01: Create FormatIngestor(BaseIngestor) class
    - entity_type = "format"
    - source_paths = ["registry/format-registry.yaml"]
    - get_adapter: YamlAdapter with records_key="formats"
  MS-CI-003-02-02: Implement ingest_records
    - For each record: INSERT INTO formats
    - Map: format_id, display_name, family, extensions (json.dumps), mime_type,
      spec_body, spec_version, legal_category, tier_target, visibility,
      scoring.total_points as scoring_total, raw_json=json.dumps(record)

Expected output: Formats table populated from format-registry.yaml

Acceptance: Row count matches len(data["formats"]) in source file

Next: TC-CI-003-03
```

#### TC-CI-003-03: Create capability_ingestor.py

```
Child Taskcard ID: TC-CI-003-03
Parent: TC-CI-003
Title: Create capability ingestor
Status: TODO

Scope:
  Allowed: tools/supervisor/control_index/ingestors/capability_ingestor.py

Micro-steps:
  MS-CI-003-03-01: Create CapabilityIngestor(BaseIngestor) class
    - source_paths = [".governance/capabilities/registry.yaml"]
    - get_adapter: YamlAdapter with records_key="capabilities"
  MS-CI-003-03-02: Implement ingest_records
    - Map: capability_id, command_file, parity_status, product_track, purpose, status
    - Extract agent_surfaces: claude_code=1/0, codex=1/0, ci=1/0

Next: TC-CI-003-04
```

#### TC-CI-003-04: Create skill_ingestor.py

```
Child Taskcard ID: TC-CI-003-04
Parent: TC-CI-003
Title: Create skill ingestor
Status: TODO

Scope:
  Allowed: tools/supervisor/control_index/ingestors/skill_ingestor.py

Micro-steps:
  MS-CI-003-04-01: Create SkillIngestor(BaseIngestor) class
    - source_paths = [".supervisor/skill-registry.yaml"]
    - get_adapter: YamlAdapter with records_key="skills"
  MS-CI-003-04-02: Implement ingest_records
    - Map: skill_id (from command field, strip leading /), command, command_file,
      idempotency, product_track, purpose, status, overflow_split_allowed

Next: TC-CI-003-05
```

#### TC-CI-003-05: Create layer_ingestor.py

```
Child Taskcard ID: TC-CI-003-05
Parent: TC-CI-003
Title: Create layer ingestor (layers + layer_dependencies)
Status: TODO

Scope:
  Allowed: tools/supervisor/control_index/ingestors/layer_ingestor.py

Micro-steps:
  MS-CI-003-05-01: Create LayerIngestor(BaseIngestor) class
    - source_paths = ["plans/layers/index.yaml"]
    - get_adapter: YamlAdapter with records_key="layers"
  MS-CI-003-05-02: Implement ingest_records
    - Map: layer_id, canonical_name, permanent_plan_path, plane, status, health,
      maturity_current, maturity_target, active_task_count, next_task_id, next_action
  MS-CI-003-05-03: Also populate layer_dependencies
    - For each layer: iterate downstream_layers[], insert (layer_id, downstream_id) pairs

Next: TC-CI-003-06
```

#### TC-CI-003-06: Create failure_ingestor.py

```
Child Taskcard ID: TC-CI-003-06
Parent: TC-CI-003
Title: Create failure ingestor
Status: TODO

Scope:
  Allowed: tools/supervisor/control_index/ingestors/failure_ingestor.py

Micro-steps:
  MS-CI-003-06-01: Create FailureIngestor(BaseIngestor) class
    - source_paths = [".local/supervisor/failure-memory.json"]
    - get_adapter: JsonAdapter with records_key="failures"
  MS-CI-003-06-02: Implement ingest_records
    - Map: failure_id=id, category, root_cause, correction, severity,
      sprint_discovered, last_seen_sprint, discovered_at, last_seen_at,
      occurrence_count, escalated (1/0), resolved (1/0), resolution, resolved_at

Next: TC-CI-003-07
```

#### TC-CI-003-07: Create plan_lock_ingestor.py

```
Child Taskcard ID: TC-CI-003-07
Parent: TC-CI-003
Title: Create plan lock ingestor (multi-file)
Status: TODO

Scope:
  Allowed: tools/supervisor/control_index/ingestors/plan_lock_ingestor.py

Micro-steps:
  MS-CI-003-07-01: Create PlanLockIngestor(BaseIngestor) class
    - source_paths = [".local/supervisor/plan-locks/"]  (directory)
    - Custom sync: glob *.json in directory, process each file
  MS-CI-003-07-02: Implement ingest_records
    - For each JSON file: lock_file=filename, plan_path, status, session_id,
      track_type, last_taskcard, updated_at, terminal_reason

Next: TC-CI-003-08
```

#### TC-CI-003-08: Create violation_ingestor.py

```
Child Taskcard ID: TC-CI-003-08
Parent: TC-CI-003
Title: Create source violation ingestor
Status: TODO

Scope:
  Allowed: tools/supervisor/control_index/ingestors/violation_ingestor.py

Micro-steps:
  MS-CI-003-08-01: Create ViolationIngestor(BaseIngestor) class
    - source_paths = ["registry/source-structure-baseline.json"]
    - Custom parsing: read known_violations dict, each key=file_path, value=violation data
  MS-CI-003-08-02: Implement ingest_records
    - Map: file_path, loc, baseline_loc_cap, functions, baseline_functions_cap,
      category, healing_priority, healing_sprint

Next: TC-CI-003-09
```

#### TC-CI-003-09: Register ingestors in sync.py + test

```
Child Taskcard ID: TC-CI-003-09
Parent: TC-CI-003
Title: Register all Wave 2 ingestors and test
Status: TODO

Scope:
  Allowed: tools/supervisor/control_index/sync.py, tests/supervisor/test_control_index_ingestors.py

Micro-steps:
  MS-CI-003-09-01: Add ALL_INGESTORS list in sync.py with Wave 2 ingestors in dependency order
  MS-CI-003-09-02: Create test_control_index_ingestors.py
  MS-CI-003-09-03: Add test_format_ingestor_populates_table — sync, check row count matches source
  MS-CI-003-09-04: Add test_capability_ingestor_populates_table
  MS-CI-003-09-05: Add test_skill_ingestor_populates_table
  MS-CI-003-09-06: Add test_layer_ingestor_populates_with_dependencies
  MS-CI-003-09-07: Add test_failure_ingestor_populates_table
  MS-CI-003-09-08: Add test_plan_lock_ingestor_populates_table
  MS-CI-003-09-09: Add test_violation_ingestor_populates_table
  MS-CI-003-09-10: Add test_sync_idempotent — sync twice, second run reports zero changes
  MS-CI-003-09-11: Run tests: .venv/Scripts/pytest tests/supervisor/test_control_index_ingestors.py -v

Expected output: All 7 ingestors verified against real source files

Acceptance: All tests PASS, row counts match source files
```

---

### TC-CI-004: Large Entity Ingestors + Relationships (Wave 3)

```
Parent Taskcard ID: TC-CI-004
Title: Create ingestors for large tables (gaps, qnames, evidence, events)
Type: PARENT
Status: PROPOSED
Source: REQ-CI-015

Dependencies: TC-CI-003 (needs base ingestor pattern + formats table for FK)

Acceptance:
  - gaps table has ~1277 rows with gap_spec_facts populated
  - qnames table has ~66 rows
  - sprints table populated from evidence directories
  - sprint_work_items relationship table populated
  - events table populated from continuation-ledger.jsonl
  - Full sync <60 seconds

Rollback: delete ingestor files
```

#### TC-CI-004-01: Create gap_ingestor.py

```
Child Taskcard ID: TC-CI-004-01
Parent: TC-CI-004
Title: Create gap ingestor (gaps + gap_spec_facts)
Status: TODO

Scope:
  Allowed: tools/supervisor/control_index/ingestors/gap_ingestor.py

Micro-steps:
  MS-CI-004-01-01: Create GapIngestor(BaseIngestor)
    - source_paths = ["reports/capability-layer/gap-ledger.json"]
    - get_adapter: JsonAdapter with records_key="gaps"
  MS-CI-004-01-02: Implement ingest_records
    - Map all gap fields to columns
    - For each gap: also insert gap_spec_facts from spec_facts[] array
    - Use executemany for batch insert performance
  MS-CI-004-01-03: Test: verify gap count = 1277, gap_spec_facts populated

Next: TC-CI-004-02
```

#### TC-CI-004-02: Create qname_ingestor.py

```
Child Taskcard ID: TC-CI-004-02
Parent: TC-CI-004
Title: Create QName ingestor (multi-file YAML)
Status: TODO

Scope:
  Allowed: tools/supervisor/control_index/ingestors/qname_ingestor.py

Micro-steps:
  MS-CI-004-02-01: Create QNameIngestor(BaseIngestor)
    - source_paths = ["shared/qname-registry/"]  (directory of YAML files)
    - Custom sync: glob *.yaml (exclude schema.yaml), parse each
  MS-CI-004-02-02: Implement ingest_records
    - Derive format_id from filename (e.g., fods.yaml → fods)
    - Map: qname, namespace_uri, local_name, canonical_class, spec_fact_ref,
      status, source_layer, python_file, dotnet_file, facade_names (json.dumps)
  MS-CI-004-02-03: Test: verify ~66 qnames across all files

Next: TC-CI-004-03
```

#### TC-CI-004-03: Create evidence_ingestor.py

```
Child Taskcard ID: TC-CI-004-03
Parent: TC-CI-004
Title: Create evidence/sprint ingestor (sprints + sprint_work_items)
Status: TODO

Scope:
  Allowed: tools/supervisor/control_index/ingestors/evidence_ingestor.py

Micro-steps:
  MS-CI-004-03-01: Create EvidenceIngestor(BaseIngestor)
    - source_paths = [".local/evidences/"]  (directory of run dirs)
    - Custom sync: scan subdirectories, check for evidence-declaration.yaml
    - Track per-directory in source_manifest (one entry per evidence dir)
  MS-CI-004-03-02: Implement ingest_records
    - Parse evidence-declaration.yaml per directory
    - Insert into sprints: sprint_id, run_id, evidence_root, declared_scope,
      start_time, end_time, git_head_start, git_head_end, verdict=worker_self_verdict,
      test_count=tests_run, worker_self_grade
    - Insert sprint_work_items from planned_work_items[]
  MS-CI-004-03-03: Handle missing/malformed declarations gracefully (skip, log warning)
  MS-CI-004-03-04: Use batch processing: 100 directories per transaction
  MS-CI-004-03-05: Test: verify sprints populated, sprint_work_items linked

Next: TC-CI-004-04
```

#### TC-CI-004-04: Create event_ingestor.py

```
Child Taskcard ID: TC-CI-004-04
Parent: TC-CI-004
Title: Create event ingestor (continuation-ledger.jsonl → events)
Status: TODO

Scope:
  Allowed: tools/supervisor/control_index/ingestors/event_ingestor.py

Micro-steps:
  MS-CI-004-04-01: Create EventIngestor(BaseIngestor)
    - source_paths = [".local/supervisor/continuation-ledger.jsonl"]
    - get_adapter: JsonlAdapter
  MS-CI-004-04-02: Implement ingest_records
    - Map: timestamp, event_type, source="continuation_ledger",
      session_id, sprint_id, artifact_path, detail=json.dumps(remaining fields)
    - Use executemany for batch insert (5809+ rows)
  MS-CI-004-04-03: Test: verify event count matches line count in JSONL

Next: TC-CI-004-05
```

#### TC-CI-004-05: Register Wave 3 ingestors + integration test

```
Child Taskcard ID: TC-CI-004-05
Parent: TC-CI-004
Title: Register large ingestors and run full sync test
Status: TODO

Scope:
  Allowed: sync.py (add to ALL_INGESTORS), tests/supervisor/test_control_index_sync.py

Micro-steps:
  MS-CI-004-05-01: Add Wave 3 ingestors to ALL_INGESTORS in sync.py (after Wave 2 ingestors)
  MS-CI-004-05-02: Create test_control_index_sync.py
  MS-CI-004-05-03: Add test_full_sync_completes — sync_all on real repo, verify no errors
  MS-CI-004-05-04: Add test_full_sync_under_60_seconds — time the sync, assert <60s
  MS-CI-004-05-05: Add test_rebuild_matches_sync — rebuild, compare row counts with sync
  MS-CI-004-05-06: Add test_sync_idempotent_full — sync twice, second run=zero changes
  MS-CI-004-05-07: Run: .venv/Scripts/pytest tests/supervisor/test_control_index_sync.py -v

Acceptance: Full sync completes <60s, all entity counts match source files, idempotent
```

---

### TC-CI-005: FTS5 Search + Query CLI (Wave 4)

```
Parent Taskcard ID: TC-CI-005
Title: Create FTS5 search engine and query CLI
Type: PARENT
Status: PROPOSED
Source: REQ-CI-016, REQ-CI-017, REQ-CI-018

Dependencies: TC-CI-004 (needs populated tables)

Acceptance:
  - FTS5 search returns relevant results for test queries
  - CLI query commands work for all entity types
  - --table output is human-readable
  - Queries <200ms

Rollback: delete search.py and query.py
```

#### TC-CI-005-01: Create search.py

```
Child Taskcard ID: TC-CI-005-01
Parent: TC-CI-005
Title: Create FTS5 search module
Status: TODO
Source: REQ-CI-018

Scope:
  Allowed: tools/supervisor/control_index/search.py

Micro-steps:
  MS-CI-005-01-01: Create populate_fts(conn) function
    - Delete existing FTS content
    - Insert into fts_operational from each entity table:
      gaps: entity_type="gap", entity_id=gap_id, content=gap_id||' '||capability_name||' '||notes||' '||status||' '||format
      failures: entity_type="failure", entity_id=failure_id, content=failure_id||' '||category||' '||root_cause||' '||correction
      skills: entity_type="skill", entity_id=skill_id, content=skill_id||' '||purpose||' '||product_track
      capabilities: entity_type="capability", entity_id=capability_id, content=capability_id||' '||purpose
      layers: entity_type="layer", entity_id=layer_id, content=layer_id||' '||canonical_name||' '||next_action
      qnames: entity_type="qname", entity_id=qname, content=qname||' '||canonical_class||' '||spec_fact_ref
      sprints: entity_type="sprint", entity_id=sprint_id, content=sprint_id||' '||declared_scope||' '||verdict
  MS-CI-005-01-02: Create search(conn, query, entity_types=None, limit=20) function
    - Execute FTS5 MATCH query with BM25 ranking
    - Optionally filter by entity_type
    - Return list of {entity_type, entity_id, rank, snippet}
  MS-CI-005-01-03: Add populate_fts call to sync_all() after all ingestors complete

Next: TC-CI-005-02
```

#### TC-CI-005-02: Create query.py CLI

```
Child Taskcard ID: TC-CI-005-02
Parent: TC-CI-005
Title: Create query CLI with all commands
Status: TODO
Source: REQ-CI-016, REQ-CI-017

Scope:
  Allowed: tools/supervisor/control_index/query.py

Micro-steps:
  MS-CI-005-02-01: Create query.py with argparse subcommands
    - Global: --db-path, --format (json|table)
  MS-CI-005-02-02: Implement "search" subcommand
    - Calls search() from search.py
    - Accepts query text + optional --type filter
  MS-CI-005-02-03: Implement "gaps" subcommand
    - --format, --status, --priority, --blocks-poc filters
    - SELECT from gaps with WHERE clauses
  MS-CI-005-02-04: Implement "sprints" subcommand
    - --limit, --verdict, --after filters
  MS-CI-005-02-05: Implement "failures" subcommand
    - --unresolved (resolved=0), --category, --severity
  MS-CI-005-02-06: Implement "plan-locks" subcommand
    - --status, --session filters
  MS-CI-005-02-07: Implement "format" subcommand (dashboard)
    - Joins formats + gaps + qnames for one format_id
    - Returns: format info, gap counts by status, qname counts by status
  MS-CI-005-02-08: Implement "chain" subcommand
    - --gap GAP_ID: find gap → linked sprint_work_items → sprints → evidence
    - Multi-table JOIN traversal
  MS-CI-005-02-09: Implement "stale" subcommand
    - Check source_manifest mtimes vs current file mtimes
    - Report stale sources
  MS-CI-005-02-10: Implement "sql" subcommand
    - Execute arbitrary read-only SQL
    - Safety: reject INSERT/UPDATE/DELETE/DROP/ALTER
  MS-CI-005-02-11: Implement table_format(rows) for --table output
    - Simple column-aligned text table

Next: TC-CI-005-03
```

#### TC-CI-005-03: Create query tests

```
Child Taskcard ID: TC-CI-005-03
Parent: TC-CI-005
Title: Create test_control_index_query.py
Status: TODO
Source: REQ-CI-021

Scope:
  Allowed: tests/supervisor/test_control_index_query.py

Micro-steps:
  MS-CI-005-03-01: Create test fixture: init DB, sync from real repo, use for all tests
  MS-CI-005-03-02: Add test_search_returns_results — search "FODS", expect gap/qname results
  MS-CI-005-03-03: Add test_gaps_filter_by_format — query gaps --format fods, verify all results have format=FODS
  MS-CI-005-03-04: Add test_failures_unresolved — query failures --unresolved, verify resolved=0
  MS-CI-005-03-05: Add test_format_dashboard — query format fods, verify gap counts present
  MS-CI-005-03-06: Add test_sql_rejects_writes — "DROP TABLE gaps" must be rejected
  MS-CI-005-03-07: Add test_query_under_200ms — time a complex query, assert <200ms
  MS-CI-005-03-08: Run: .venv/Scripts/pytest tests/supervisor/test_control_index_query.py -v
```

---

### TC-CI-006: Enhanced Features + Parity + Integration (Waves 5-6)

```
Parent Taskcard ID: TC-CI-006
Title: Staleness detection, contradiction detection, parity tests, skill registration
Type: PARENT
Status: PROPOSED
Source: REQ-CI-019, REQ-CI-020, REQ-CI-022, REQ-CI-023, REQ-CI-024, REQ-CI-025

Dependencies: TC-CI-005 (needs working queries)

Acceptance:
  - Staleness detector finds stale entries when source files change
  - Contradiction detector finds real contradictions
  - Parity tests pass (index matches direct file reads)
  - Idempotency proven (sync twice = zero changes)
  - Recovery proven (delete + rebuild = identical)
  - Registered as skill in .supervisor/skill-registry.yaml

Rollback: delete staleness.py, revert skill-registry.yaml changes
```

#### TC-CI-006-01: Create staleness.py

```
Child Taskcard ID: TC-CI-006-01
Parent: TC-CI-006
Title: Create staleness and contradiction detection
Status: TODO
Source: REQ-CI-019, REQ-CI-020

Scope:
  Allowed: tools/supervisor/control_index/staleness.py

Micro-steps:
  MS-CI-006-01-01: Create check_staleness(conn, repo_root) function
    - For each row in source_manifest: compare last_modified with current file mtime
    - Return list of stale sources with age_seconds
  MS-CI-006-01-02: Create detect_contradictions(conn) function
    - Check: gaps with status='closed' that have no sprint_work_items referencing them
    - Check: plan_locks with status='IN_PROGRESS' and updated_at > 24h ago
    - Check: failures with resolved=0 and occurrence_count > 5
    - Return list of {type, entity_id, description}
  MS-CI-006-01-03: Create detect_orphans(conn) function
    - sprint_work_items referencing gap_ledger_ref not in gaps table
    - layer_dependencies referencing layer_ids not in layers table

Next: TC-CI-006-02
```

#### TC-CI-006-02: Create parity tests

```
Child Taskcard ID: TC-CI-006-02
Parent: TC-CI-006
Title: Create test_control_index_parity.py
Status: TODO
Source: REQ-CI-022, REQ-CI-023, REQ-CI-024

Scope:
  Allowed: tests/supervisor/test_control_index_parity.py

Micro-steps:
  MS-CI-006-02-01: Add test_gap_count_parity
    - Load gap-ledger.json directly, count gaps
    - Query SELECT COUNT(*) FROM gaps
    - Assert equal
  MS-CI-006-02-02: Add test_gap_content_parity
    - For 10 random gaps: compare raw_json column with source file content
  MS-CI-006-02-03: Add test_format_count_parity — same pattern for formats
  MS-CI-006-02-04: Add test_skill_count_parity — same for skills
  MS-CI-006-02-05: Add test_qname_count_parity — same for qnames
  MS-CI-006-02-06: Add test_idempotency
    - Sync, record all row counts
    - Sync again
    - Verify zero inserts on second run (check SyncReport)
    - Verify row counts identical
  MS-CI-006-02-07: Add test_recovery
    - Sync to populate
    - Record all row counts
    - Delete DB file
    - Rebuild
    - Verify row counts identical
  MS-CI-006-02-08: Run: .venv/Scripts/pytest tests/supervisor/test_control_index_parity.py -v

Next: TC-CI-006-03
```

#### TC-CI-006-03: Register skill + integration hook

```
Child Taskcard ID: TC-CI-006-03
Parent: TC-CI-006
Title: Register control-index as skill and add optional sync hook
Status: TODO
Source: REQ-CI-025

Scope:
  Allowed: .supervisor/skill-registry.yaml (add entry), tools/supervisor/autonomous_cycle.py (optional non-blocking hook)

Micro-steps:
  MS-CI-006-03-01: Add skill entry to .supervisor/skill-registry.yaml:
    - command: /query-control-index
    - skill_id: query-control-index
    - status: active
    - product_track: infrastructure
    - purpose: "Query the operational control index for gaps, sprints, failures, search"
    - idempotency: read_only
  MS-CI-006-03-02: Add optional --sync-index flag to autonomous_cycle.py
    - At end of cycle, if flag set: try sync_all, except pass (non-blocking)
    - Must not affect exit code
  MS-CI-006-03-03: Test: verify skill entry parses correctly
  MS-CI-006-03-04: Test: verify autonomous_cycle.py still works without --sync-index
```

---

## Execution DAG

```
TC-CI-001 (package + schema + DB)
    │
    ├── TC-CI-001-01 → TC-CI-001-02 → TC-CI-001-03 → TC-CI-001-04 → TC-CI-001-05
    │
    ▼
TC-CI-002 (adapters + sync)
    │
    ├── TC-CI-002-01 → TC-CI-002-02 ──┐
    │                  TC-CI-002-03 ──┤ (02 and 03 are parallel-safe)
    │                                  ▼
    │                  TC-CI-002-04 → TC-CI-002-05
    │
    ▼
TC-CI-003 (small ingestors)
    │
    ├── TC-CI-003-01 → TC-CI-003-02 ──┐
    │                  TC-CI-003-03 ──┤
    │                  TC-CI-003-04 ──┤ (02-08 are parallel-safe after 01)
    │                  TC-CI-003-05 ──┤
    │                  TC-CI-003-06 ──┤
    │                  TC-CI-003-07 ──┤
    │                  TC-CI-003-08 ──┘
    │                       ▼
    │                  TC-CI-003-09
    │
    ▼
TC-CI-004 (large ingestors)
    │
    ├── TC-CI-004-01 ──┐
    │   TC-CI-004-02 ──┤ (01-04 are parallel-safe)
    │   TC-CI-004-03 ──┤
    │   TC-CI-004-04 ──┘
    │        ▼
    │   TC-CI-004-05
    │
    ▼
TC-CI-005 (search + query)
    │
    ├── TC-CI-005-01 → TC-CI-005-02 → TC-CI-005-03
    │
    ▼
TC-CI-006 (enhanced + parity + integration)
    │
    ├── TC-CI-006-01 ──┐
    │   TC-CI-006-02 ──┤ (parallel-safe)
    │                   ▼
    │   TC-CI-006-03
```

---

## File Ownership

| File/Directory | Owner Taskcard | Parallel-Safe |
|---|---|---|
| `tools/supervisor/control_index/__init__.py` | TC-CI-001-01 | No — singleton |
| `tools/supervisor/control_index/__main__.py` | TC-CI-001-04 | No — singleton |
| `tools/supervisor/control_index/db.py` | TC-CI-001-03 | No — singleton |
| `tools/supervisor/control_index/schema.sql` | TC-CI-001-02 | No — singleton |
| `tools/supervisor/control_index/sync.py` | TC-CI-002-04, TC-CI-003-09, TC-CI-004-05 | No — sequential |
| `tools/supervisor/control_index/search.py` | TC-CI-005-01 | No — singleton |
| `tools/supervisor/control_index/query.py` | TC-CI-005-02 | No — singleton |
| `tools/supervisor/control_index/staleness.py` | TC-CI-006-01 | No — singleton |
| `tools/supervisor/control_index/adapters/*` | TC-CI-002-01 to 03 | No — sequential |
| `tools/supervisor/control_index/ingestors/*` | TC-CI-003-*, TC-CI-004-* | Yes — each ingestor is independent file |
| `.supervisor/skill-registry.yaml` | TC-CI-006-03 | No — shared file |
| `tools/supervisor/autonomous_cycle.py` | TC-CI-006-03 | No — shared file |
| `tests/supervisor/test_control_index_*.py` | TC-CI-001-05, 002-05, 003-09, 005-03, 006-02 | Yes — each test file independent |

---

## Verification Matrix

| Test | Taskcard | Type | Command |
|---|---|---|---|
| DB init creates all tables | TC-CI-001-05 | Unit | `.venv/Scripts/pytest tests/supervisor/test_control_index_db.py -v` |
| WAL mode active | TC-CI-001-05 | Unit | same |
| Init idempotent | TC-CI-001-05 | Unit | same |
| JSON adapter parses records | TC-CI-002-05 | Unit | `.venv/Scripts/pytest tests/supervisor/test_control_index_adapters.py -v` |
| YAML adapter parses records | TC-CI-002-05 | Unit | same |
| needs_sync detects changes | TC-CI-002-05 | Unit | same |
| Format ingestor row count | TC-CI-003-09 | Integration | `.venv/Scripts/pytest tests/supervisor/test_control_index_ingestors.py -v` |
| All small ingestors populate | TC-CI-003-09 | Integration | same |
| Sync idempotent (small) | TC-CI-003-09 | Integration | same |
| Full sync <60s | TC-CI-004-05 | Performance | `.venv/Scripts/pytest tests/supervisor/test_control_index_sync.py -v` |
| Rebuild matches sync | TC-CI-004-05 | Integration | same |
| FTS search returns results | TC-CI-005-03 | Integration | `.venv/Scripts/pytest tests/supervisor/test_control_index_query.py -v` |
| Gap count parity | TC-CI-006-02 | Parity | `.venv/Scripts/pytest tests/supervisor/test_control_index_parity.py -v` |
| Idempotency proof | TC-CI-006-02 | Idempotency | same |
| Recovery proof | TC-CI-006-02 | Recovery | same |
| SQL rejects writes | TC-CI-005-03 | Negative | `.venv/Scripts/pytest tests/supervisor/test_control_index_query.py -v` |

---

## Execution Handoff

**Execution agent instructions:**

1. Read this plan completely before starting.
2. Execute taskcards in DAG order: TC-CI-001 → TC-CI-002 → TC-CI-003 → TC-CI-004 → TC-CI-005 → TC-CI-006.
3. Within each parent, execute children in order (respect "Next" links).
4. For each child taskcard:
   a. Confirm preconditions (dependencies closed).
   b. Execute micro-steps in order.
   c. After all micro-steps: run the acceptance check.
   d. If tests fail: fix immediately, do not proceed until green.
   e. Mark child CLOSED only after tests pass.
5. After all children of a parent close: run parent acceptance checks.
6. Mark parent CLOSED only after parent acceptance passes.
7. Do NOT modify any existing supervisor tools except where explicitly allowed (TC-CI-006-03: skill-registry.yaml and autonomous_cycle.py).
8. Do NOT modify source data files — they are read-only inputs.
9. All new code goes under `tools/supervisor/control_index/` and `tests/supervisor/test_control_index_*.py`.
10. Use `tools/supervisor/atomic_io.py` as a reference pattern but do not import it — SQLite handles its own atomicity.

**First action:** Execute TC-CI-001-01 (create package __init__.py).

---

## Taskcard Status Summary

| Taskcard | Status |
|---|---|
| TC-CI-001 | CLOSED |
| TC-CI-001-01 | CLOSED |
| TC-CI-001-02 | CLOSED |
| TC-CI-001-03 | CLOSED |
| TC-CI-001-04 | CLOSED |
| TC-CI-001-05 | CLOSED |
| TC-CI-002 | CLOSED |
| TC-CI-002-01 | CLOSED |
| TC-CI-002-02 | CLOSED |
| TC-CI-002-03 | CLOSED |
| TC-CI-002-04 | CLOSED |
| TC-CI-002-05 | CLOSED |
| TC-CI-003 | CLOSED |
| TC-CI-003-01 | CLOSED |
| TC-CI-003-02 | CLOSED |
| TC-CI-003-03 | CLOSED |
| TC-CI-003-04 | CLOSED |
| TC-CI-003-05 | CLOSED |
| TC-CI-003-06 | CLOSED |
| TC-CI-003-07 | CLOSED |
| TC-CI-003-08 | CLOSED |
| TC-CI-003-09 | CLOSED |
| TC-CI-004 | CLOSED |
| TC-CI-004-01 | CLOSED |
| TC-CI-004-02 | CLOSED |
| TC-CI-004-03 | CLOSED |
| TC-CI-004-04 | CLOSED |
| TC-CI-004-05 | CLOSED |
| TC-CI-005 | CLOSED |
| TC-CI-005-01 | CLOSED |
| TC-CI-005-02 | CLOSED |
| TC-CI-005-03 | CLOSED |
| TC-CI-006 | CLOSED |
| TC-CI-006-01 | CLOSED |
| TC-CI-006-02 | CLOSED |
| TC-CI-006-03 | CLOSED |



<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-06-29T14:00:20.638121+00:00"
  locked_by: "dbc1a484a2fb"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
