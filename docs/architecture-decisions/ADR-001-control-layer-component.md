# ADR-001: Control Layer Component — Storage Engine Decision

**Status:** ACCEPTED
**Date:** 2026-07-12
**Mission:** FF-CTRL-OCRD-001
**Taskcard:** TC-OCRD-C2-02

---

## Context

The operational control record system (FF-CTRL-OCRD-001) requires a persistent store for
control layer state: gap attempts, sprint history, plan locks, staleness records,
feature parity results, quarantines, and trust registry. A storage engine decision
is needed before expanding the schema in TC-OCRD-C3.

The existing `FF-CTRL-INDEX-001` already established SQLite+FTS5 as the control index
backing store (.local/supervisor/control-index.db). This ADR evaluates whether to
continue with SQLite, migrate to DuckDB, or revert to plain JSON.

---

## Decision

**SQLite + FTS5 (existing)** — confirmed as the storage engine for all Phase C control
layer tables.

---

## Evaluation Matrix

| Criterion               | SQLite + FTS5 | DuckDB      | Plain JSON  |
|-------------------------|--------------|-------------|-------------|
| Zero new dependencies   | YES          | NO          | YES         |
| stdlib availability     | YES (sqlite3)| NO          | YES         |
| FTS5 full-text search   | YES (built-in)| NO (ext)   | NO          |
| WAL mode for concurrency| YES          | YES         | NO          |
| Multi-table JOINs       | YES          | SUPERIOR    | NO          |
| Complex aggregations    | ADEQUATE     | SUPERIOR    | NO          |
| SAVEPOINT isolation     | YES          | PARTIAL     | NO          |
| Schema migration path   | PROVEN (v1→v4)| UNPROVEN   | POOR        |
| Existing investment     | HIGH (11K rows, 11 ingestors, 16 tables)| NONE | PARTIAL |
| Portability             | EXCELLENT    | GOOD        | EXCELLENT   |
| Sprint count scale      | ADEQUATE (<100K)| BETTER   | POOR        |
| Operational complexity  | LOW          | MEDIUM      | LOW         |

---

## Rationale

1. **Existing investment**: FF-CTRL-INDEX-001 is complete (TERMINAL_CLOSED 2026-06-29).
   11 ingestors, 16 tables, FTS5 over 8 entity types, 30/30 tests passing. A migration
   to DuckDB would require rewriting all ingestors with no observable quality benefit
   at current sprint volumes.

2. **Zero new dependencies**: sqlite3 is Python stdlib. DuckDB requires `pip install duckdb`.
   Format Factory's dependency discipline (zero new deps for supervisor tooling) is
   a hard policy constraint.

3. **SAVEPOINT isolation**: TC-OCRD-A2 implemented per-ingestor SAVEPOINT transactions
   using sqlite3's native SAVEPOINT support. DuckDB's SAVEPOINT support is partial
   (no RELEASE SAVEPOINT in all versions).

4. **Migration framework**: TC-OCRD-A4 implemented a version-stamped migration framework
   (SCHEMA_VERSION, MIGRATION_FUNCS list). Phase C (TC-OCRD-C3) will add 6 new tables
   via a v3→v4 migration. The framework is already proven.

5. **FTS5**: Full-text search across gaps, qnames, sprint titles, and spec facts is a
   first-class feature. SQLite FTS5 is the only stdlib option; DuckDB would require
   custom extension or external indexer.

---

## DuckDB Reconsider Threshold

Revisit DuckDB if **both** conditions are met:
- Sprint count exceeds 100,000 (current: ~290 sprints)
- Multi-table aggregation queries take >2 seconds on production hardware

Neither condition applies. The decision will be revisited in a future ADR if thresholds
are crossed.

---

## Rejected Alternatives

### DuckDB
- **Reason**: New dependency violates zero-dep policy; no SAVEPOINT; no FTS5 stdlib;
  migration from existing 11-ingestor system is high-risk with no observable benefit.

### Plain JSON files
- **Reason**: Already proven insufficient (FF-CTRL-INDEX-001 motivation). No query
  capability, no FTS5, no transactional isolation, O(n) scans for gap attempt lookups.

### PostgreSQL / MySQL
- **Reason**: Requires running server, network configuration, credentials management.
  Incompatible with portability requirements and offline operation.

---

## Risks and Mitigations

| Risk | Addressed In |
|------|-------------|
| Schema migration complexity | TC-OCRD-A4: MIGRATION_FUNCS framework, version-stamped DB |
| Single-writer contention | TC-OCRD-A2: SAVEPOINT isolation; WAL mode enabled |
| DB corruption on crash | SQLite WAL journal mode; DB is reconstructible from sources |
| FTS5 index staleness | sync.py incremental sync with hash-based skip |

---

## Consequences

- Phase C schema extension (TC-OCRD-C3) proceeds as additive v3→v4 migration.
- All new ingestors (TC-OCRD-C4) follow the existing BaseIngestor pattern.
- No new Python dependencies are introduced.
- DuckDB is formally rejected for Phase C and documented here for future reference.
