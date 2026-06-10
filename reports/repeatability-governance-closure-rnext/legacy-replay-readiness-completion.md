# Legacy Replay Readiness Completion Report
# Sprint: FORMAT-FACTORY-GOVERNANCE-ENFORCEMENT-CLOSURE-AND-SOURCE-REPLAY-PILOT-001
# Run ID: governance-enforcement-closure-rnext
# Date: 2026-06-09

## Purpose

GR-REPLAY-001..004 taskcards from Sprint 2 were insufficiently detailed for the
autonomy sprint to execute. This report documents the completion of replay-readiness
fields and confirms handoff status.

## GR-REPLAY-001: set_cell_value (Gnumeric)

- **Current state**: BACKFILLED_LEGACY_ACCEPTED
- **Target state**: REPLAY_RECIPE_RECORDED
- **Skill candidate**: add-python-api v1.0
- **Replay inputs**:
  - format_id: gnumeric
  - function_name: set_cell_value
  - capability: modify cell value in a sheet by (row, col) index
  - signature: `def set_cell_value(data: bytes, sheet_index: int, row: int, col: int, value: str) -> bytes`
- **Expected diff behavior**: Add `set_cell_value` function to gnumeric_codec.py; no other changes
- **Validation commands**:
  - `.local/venv/Scripts/python -m pytest tests/python/gnumeric/test_r126_gnumeric_set_cell.py -v`
- **Stop conditions**:
  - Any test failure: abort, record in adaptation-log.md
  - Logic diverges from existing function: abort
- **Readiness**: READY_FOR_AUTONOMY_SPRINT

## GR-REPLAY-002: get_headers (TSV)

- **Current state**: BACKFILLED_LEGACY_ACCEPTED
- **Target state**: REPLAY_RECIPE_RECORDED
- **Skill candidate**: add-python-api v1.0
- **Replay inputs**:
  - format_id: tsv
  - function_name: get_headers
  - capability: return list of column header names from TSV bytes
  - signature: `def get_headers(data: bytes) -> list[str]`
- **Expected diff behavior**: Add `get_headers` function to tsv_parser.py; no other changes
- **Validation commands**:
  - `.local/venv/Scripts/python -m pytest tests/python/tsv/test_r126_tsv_get_headers.py -v`
- **Stop conditions**:
  - Any test failure: abort
  - Function returns wrong type (not list): abort
- **Readiness**: READY_FOR_AUTONOMY_SPRINT

## GR-REPLAY-003: get_paragraph (ABW)

- **Current state**: BACKFILLED_LEGACY_ACCEPTED
- **Target state**: REPLAY_RECIPE_RECORDED
- **Skill candidate**: add-python-api v1.0
- **Replay inputs**:
  - format_id: abw
  - function_name: get_paragraph
  - capability: return text of paragraph at given index from ABW bytes
  - signature: `def get_paragraph(data: bytes, index: int) -> str`
- **Expected diff behavior**: Add `get_paragraph` function to abw_codec.py
- **Validation commands**:
  - `.local/venv/Scripts/python -m pytest tests/python/abw/test_r126_abw_get_paragraph.py -v`
- **Stop conditions**:
  - Any test failure: abort
  - Index out-of-range behavior differs: abort, investigate
- **Readiness**: READY_FOR_AUTONOMY_SPRINT

## GR-REPLAY-004: export_to_csv (NDJSON)

- **Current state**: BACKFILLED_LEGACY_ACCEPTED
- **Target state**: REPLAY_RECIPE_RECORDED
- **Skill candidate**: add-python-api v1.0
- **Replay inputs**:
  - format_id: ndjson
  - function_name: export_to_csv
  - capability: convert NDJSON bytes to CSV bytes using headers from first record
  - signature: `def export_to_csv(data: bytes) -> bytes`
- **Expected diff behavior**: Add `export_to_csv` function + `_csv_field` helper to ndjson_codec.py
- **Validation commands**:
  - `.local/venv/Scripts/python -m pytest tests/python/ndjson/ -k "csv" -v`
- **Stop conditions**:
  - Any test failure: abort
  - CSV quoting or encoding differs: abort, investigate
  - Escape sequence corruption (known historical issue): check for literal backslash-n, fix immediately
- **Readiness**: READY_FOR_AUTONOMY_SPRINT (with known escape-sequence caveat)

## Overall Readiness Assessment

All 4 functions have:
- Idempotency key computed and recorded in sidecar
- Sidecar attribution file at `.local/attribution/`
- Existing tests that would validate replay
- Skill candidate identified (add-python-api v1.0)

**Verdict**: HANDOFF_READY — autonomy sprint can attempt replay recipe creation for all 4 functions.

The autonomy sprint must:
1. Read the idempotency-contract.md before any mutation
2. Capture before-content SHA-256 before any change
3. Create the replay recipe first, then validate it
4. Do NOT change existing function logic (replay must produce equivalent, not different, output)
