# Operational Control Index

## Purpose

The Operational Control Index (`control-index.db`) is a **non-destructive SQLite+FTS5 overlay**
over the Format Factory repository's scattered operational state files. It makes routine lookups —
gap queries, sprint history, failure analysis, plan-lock status — instant and queryable without
scanning directories or parsing multi-megabyte source files.

**Source files remain the sole authority.** The index is disposable and reconstructible from
scratch in under 30 seconds. Zero breaking changes to any existing tool.

## Why It Exists

Before the index, agents had to:
- Scan `.local/supervisor/` to find 121+ plan-lock files for every continuation check
- Parse a 424K-line gap ledger for format-level gap queries
- Walk `.local/evidences/` to correlate 2,700+ sprint evidence files
- Perform no cross-entity relationship traversal (gap → sprint → evidence)
- Perform no full-text search at all

The index reduces all of these to sub-millisecond SQL queries.

## Location and Gitignore

```
.local/supervisor/control-index.db   # gitignored — reconstructible
```

The database is never committed. It is always rebuilt from source files on demand.

## Architecture

```
tools/supervisor/control_index/
  __init__.py          # ControlIndex class, DEFAULT_DB_PATH, SCHEMA_VERSION
  schema.sql           # DDL: 10 entity tables, 2 junction tables, FTS5, source_manifest
  db.py                # Connection manager: WAL, foreign_keys, busy_timeout=5000
  sync.py              # Orchestrator: sync_all(), rebuild(), register_ingestor()
  search.py            # FTS5: populate_fts(), search()
  query.py             # Query CLI: 9 subcommands
  staleness.py         # Hash-based staleness detection, contradiction checks
  adapters/
    __init__.py        # SourceAdapter base class
    json_adapter.py    # JsonAdapter, JsonlAdapter, DictAdapter, MultiFileJsonAdapter
    yaml_adapter.py    # YamlAdapter, YamlArrayAdapter, MultiFileYamlAdapter
  ingestors/
    __init__.py        # BaseIngestor base class with full sync loop
    format_ingestor.py
    capability_ingestor.py
    skill_ingestor.py
    layer_ingestor.py
    failure_ingestor.py
    plan_lock_ingestor.py
    violation_ingestor.py
    gap_ingestor.py
    qname_ingestor.py
    evidence_ingestor.py
    event_ingestor.py
```

## Entity Tables

| Table | Rows (typical) | Source |
|---|---|---|
| `formats` | 25 | `registry/format-registry.yaml` |
| `capabilities` | 102 | `.governance/capabilities/registry.yaml` |
| `skills` | 96 | `.supervisor/skill-registry.yaml` |
| `layers` | 28 | `plans/layers/index.yaml` |
| `layer_dependencies` | 44 | `plans/layers/index.yaml` (downstream_layers) |
| `failures` | 31 | `.local/supervisor/failure-memory.json` |
| `plan_locks` | 123 | `.local/supervisor/plan-locks/*.json` |
| `source_violations` | 278 | `registry/source-structure-baseline.json` |
| `gaps` | 1,277 | `reports/capability-layer/gap-ledger.json` |
| `gap_spec_facts` | 971,534 | `reports/capability-layer/gap-ledger.json` (junction) |
| `qnames` | 80 | `shared/qname-registry/*.yaml` |
| `sprints` | 2,774 | `.local/evidences/*/evidence-declaration.yaml` |
| `sprint_work_items` | 7,853 | `.local/evidences/*/evidence-declaration.yaml` (junction) |
| `events` | 5,933 | `.local/supervisor/continuation-ledger.jsonl` |
| `source_manifest` | 3,047 | Internal — one row per tracked source path |
| `fts_operational` | 4,397 | Virtual FTS5 table populated from 8 entity tables |

**Total: ~11,010 rows**

## Key Design Decisions

### Non-destructive overlay
Source files are never modified. The index contains `raw_json`/`raw_yaml` columns but these are
only copies for reference. Any write to a source file is reflected on the next `sync`.

### SHA-256 hash-based incremental sync
Every source file (or directory, for multi-file ingestors) is tracked by content hash in
`source_manifest`. On sync, if the hash matches, the ingestor skips. Only changed files trigger
a delete+re-insert. Second sync with no file changes = 0 inserts, 11 skips, 0.7 seconds.

### Provenance on every row
Every entity row carries:
- `source_file` — the source path
- `source_hash` — hash at ingest time
- `ingested_at` — ISO timestamp

### WAL mode
`journal_mode=WAL` with `busy_timeout=5000ms`. Allows concurrent readers during writes without
blocking.

### FTS5 with BM25 ranking
The `fts_operational` virtual table uses porter+unicode61 tokenizers. `search()` returns
`snippet()` extracts with `>>>highlight<<<` markers. Populated from 8 entity tables. FTS
refresh is best-effort (never blocks sync on failure).

### `@register_ingestor` decorator
Each ingestor module decorates its class with `@register_ingestor`. The decorator appends to
`ALL_INGESTORS` (with dedup guard). `sync.py` imports all ingestor modules at module load time
so decorators fire in dependency order.

### Type coercion for SQLite binding
Some YAML fields are dicts or lists where the schema expects TEXT. The evidence ingestor applies
`_str(val)` — `json.dumps()` for non-scalar values — preventing `type 'dict' is not supported`
binding errors.

## Usage

### CLI — Lifecycle commands (`__main__.py`)

```bash
# Initialize (creates DB if missing)
python -m tools.supervisor.control_index init

# Status — row counts + schema version
python -m tools.supervisor.control_index status

# Incremental sync (only changed sources)
python -m tools.supervisor.control_index sync

# Force full re-sync (rehash all sources)
python -m tools.supervisor.control_index sync --force

# Delete and rebuild from scratch
python -m tools.supervisor.control_index rebuild
```

### CLI — Query commands (`query.py`)

```bash
# Full-text search (FTS5, BM25 ranked)
python -m tools.supervisor.control_index.query search "FODS qname"
python -m tools.supervisor.control_index.query search "gap closure" --type gap,sprint --limit 10

# Gap queries
python -m tools.supervisor.control_index.query gaps --format fods
python -m tools.supervisor.control_index.query gaps --status open --priority P1
python -m tools.supervisor.control_index.query gaps --blocks-poc

# Sprint history
python -m tools.supervisor.control_index.query sprints --verdict PASS --limit 20
python -m tools.supervisor.control_index.query sprints --after 2026-06-01T00:00:00

# Failure analysis
python -m tools.supervisor.control_index.query failures --unresolved
python -m tools.supervisor.control_index.query failures --category SUPERVISOR_CONTROL_FAILURE

# Plan lock state
python -m tools.supervisor.control_index.query plan-locks --status TERMINAL_CLOSED
python -m tools.supervisor.control_index.query plan-locks --status IN_PROGRESS

# Format dashboard (format info + gap summary + qname count)
python -m tools.supervisor.control_index.query format fods

# Gap → sprint → evidence chain traversal
python -m tools.supervisor.control_index.query chain --gap GAP-FODS-COMM-EDIT_CELLS-001

# Staleness check (hash mismatch vs current files)
python -m tools.supervisor.control_index.query stale

# Read-only SQL passthrough
python -m tools.supervisor.control_index.query sql "SELECT format, COUNT(*) FROM gaps GROUP BY format"

# Human-readable table output for any command
python -m tools.supervisor.control_index.query gaps --format fods --table
```

### Python API

```python
from pathlib import Path
from tools.supervisor.control_index.sync import sync_all, rebuild
from tools.supervisor.control_index.search import search
from tools.supervisor.control_index.staleness import check_staleness
from tools.supervisor.control_index.db import get_connection
from tools.supervisor.control_index import DEFAULT_DB_PATH

# Incremental sync
report = sync_all(DEFAULT_DB_PATH, Path("."))
print(f"Inserted: {sum(r.inserted for r in report.results)}")

# Full rebuild
report = rebuild(DEFAULT_DB_PATH, Path("."))

# Search
conn = get_connection(DEFAULT_DB_PATH)
results = search(conn, "FODS qname", entity_types=["gap", "qname"], limit=10)

# Staleness
stale = check_staleness(conn, Path("."))
conn.close()
```

### Integration with `autonomous_cycle.py`

Pass `--sync-index` to refresh the index after each autonomous cycle:

```bash
python tools/supervisor/autonomous_cycle.py \
  --declaration .local/evidences/my-run/evidence-declaration.yaml \
  --sync-index
```

The hook is **non-blocking** — if the sync fails for any reason, the error is printed and
the cycle exits normally with the original exit code. The control index never blocks sprints.

## Performance

| Operation | Time |
|---|---|
| Full rebuild (11K rows, 11 ingestors) | ~28 seconds |
| Incremental sync (no changes) | ~0.7 seconds |
| `gaps-by-format` query | <1 ms |
| `failures-unresolved` query | <1 ms |
| Sprint + work-items JOIN (top 20) | ~17 ms |
| FTS5 search | <50 ms |

## Staleness and Contradiction Detection

`staleness.py` provides three functions:

- `check_staleness(conn, repo_root)` — compares `source_manifest` hashes against current files.
  Returns stale sources with `issue=hash_mismatch` or `issue=file_missing`.
- `detect_contradictions(conn)` — finds logical contradictions: closed gaps with no sprint work
  items, recurring unresolved failures (>5 occurrences).
- `detect_orphans(conn)` — finds sprint work items referencing non-existent gap IDs.

Run `python -m tools.supervisor.control_index.query stale` to surface stale sources and trigger
a targeted sync.

## Test Coverage

```
tests/supervisor/test_control_index_db.py    11 tests  — init, WAL, FK, schema version
tests/supervisor/test_control_index_sync.py  19 tests  — full sync, FTS5, queries, parity
```

**30/30 tests pass.** Parity tests directly compare index row counts to source file counts for
gaps, formats, skills, and failures.

Run:
```bash
.venv/Scripts/pytest tests/supervisor/test_control_index_db.py tests/supervisor/test_control_index_sync.py -v
```

## Registered Skill

The index is registered as a supervised skill:

```
skill_id: query-control-index
command:  /query-control-index
status:   active
track:    infrastructure
```

See `.supervisor/skill-registry.yaml` for the full entry with `implementation_paths` and
`test_paths`.

## Rebuild Safety

The index is **always safe to delete and rebuild**. Nothing in the repository reads from
`control-index.db` except agent-initiated query commands. No pipeline depends on it.

If the database is corrupted or stale, delete it and run:
```bash
python -m tools.supervisor.control_index rebuild
```

WAL and SHM companion files (`control-index.db-wal`, `control-index.db-shm`) are removed
automatically by `rebuild()`.

## Idempotency

Running `sync_all()` twice with no file changes between runs inserts zero rows:
- Every ingestor checks the source hash before deleting+reinserting
- If `source_hash == manifest.last_hash`, the ingestor returns `IngestResult(skipped=True)`
- FTS5 is only repopulated when at least one ingestor inserted data

## Adding a New Ingestor

1. Create `tools/supervisor/control_index/ingestors/my_ingestor.py`
2. Import `BaseIngestor` from `..ingestors` and `register_ingestor` from `..sync`
3. Decorate the class with `@register_ingestor`
4. Set `entity_type`, `source_paths`, and implement `ingest_records(conn, records, source_hash)`
5. Import the module in `sync.py` to trigger registration
6. Add the new table to `schema.sql` (bump `SCHEMA_VERSION` if breaking)
7. Add FTS content extraction to `search.py:populate_fts()` if the entity should be searchable
8. Add parity tests to `test_control_index_sync.py`
