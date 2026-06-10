# Vertical Slice — NDJSON

## Selected Format
**NDJSON** (Newline-Delimited JSON / JSON Lines)

## Capability Before This Sprint
| Function | Status |
|----------|--------|
| probe_ndjson() | PASS |
| load_ndjson() | PASS |
| write_ndjson() | PASS |
| get_record_count() | PASS |

## Capability After This Sprint
| Function | Status |
|----------|--------|
| probe_ndjson() | PASS |
| load_ndjson() | PASS |
| write_ndjson() | PASS |
| append_record() | PASS (NEW) |
| filter_records() | PASS (NEW) |
| get_record_count() | PASS |

## What Changed
- Added `append_record(dest, record)`: creates or appends to NDJSON file atomically
- Added `filter_records(source, key, value)`: query-like filtering of dict records

## Vertical Slice Status
| Phase | Status |
|-------|--------|
| Probe / Detect | COMPLETE |
| Load / Read | COMPLETE |
| Create / Append | COMPLETE (write_ndjson + append_record) |
| Filter / Query | COMPLETE (filter_records) |
| Roundtrip | COMPLETE (write → load → verify) |
| Tests | COMPLETE (47+ tests across 2 test files) |
| Export | PARTIAL (no CSV/HTML export yet) |
| Package/import | COMPLETE (src.python.ndjson module) |

## Remaining
- export_to_csv() / export_to_html() for cross-format output
- Schema validation / field discovery
- Streaming read for large files
