---
version: "1.0"
last-updated: "2026-06-29"
phase-available: "all"
gate-required: null
created-by: TC-CI-006-03
spec_qname_required: "false"
product_track: "infrastructure"
---

# /query-control-index

Query the operational control index for gaps, sprints, failures, search, format dashboards, chain traversal, and staleness detection. Read-only overlay on existing JSON/YAML/JSONL source files.

## What It Does

1. Searches the SQLite+FTS5 operational control index
2. Retrieves gap records, sprint history, failure logs, plan locks, and format dashboards
3. Performs chain traversal and staleness detection
4. Zero new dependencies — reconstructible from source files at any time

## Usage

```bash
# Initialize or sync the index
python -m tools.supervisor.control_index init
python -m tools.supervisor.control_index sync

# Query operations
python -m tools.supervisor.control_index.query search "<term>"
python -m tools.supervisor.control_index.query gaps
python -m tools.supervisor.control_index.query sprints
python -m tools.supervisor.control_index.query failures
python -m tools.supervisor.control_index.query plan-locks
python -m tools.supervisor.control_index.query format <fmt>
python -m tools.supervisor.control_index.query stale
```

## Layer

Infrastructure — Operational Control Index (TC-CI-006-03)
