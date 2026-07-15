---
version: "1.0"
last-updated: "2026-07-13"
phase-available: "all"
gate-required: null
created-by: TC-007-precious-wandering-lighthouse
spec_qname_required: "false"
product_track: "governance"
---

# /certification-performance-benchmark

Run performance benchmarks for a format and produce a baseline report.

## What It Does

1. Runs parse/write/roundtrip operations on sample files
2. Records wall-clock and memory usage at p50/p95/p99
3. Compares against prior baseline if available

## Usage

```bash
python tools/certification/performance_benchmark.py \
  --format fods \
  --samples samples/by-format/fods/ \
  --output reports/certification/fods/performance-baseline.json
```

## Required Handoff Fields

- `format_id`: The format to benchmark (e.g. `fods`, `csv`)

## Output Contract

Writes `reports/certification/<format_id>/performance-baseline.json`:
```json
{
  "format_id": "fods",
  "parse_p50_ms": 12.4,
  "parse_p95_ms": 31.2,
  "parse_p99_ms": 58.0,
  "write_p50_ms": 8.1,
  "memory_peak_mb": 24.5,
  "verdict": "PASS | REGRESSION | NO_PRIOR_BASELINE"
}
```

## Idempotency Contract

Same sample files + same format → reproducible benchmark within ±10% tolerance.
Output file is overwritten with each run.

## Error Handling

- Missing samples directory: exit 1 with `SAMPLES_NOT_FOUND`.
- No prior baseline: records `"verdict": "NO_PRIOR_BASELINE"`, exit 0.
- Sample file unreadable: skip with warning, continue remaining samples.

## Parity Note

PARTIAL parity: command file expanded with output contract and idempotency.
Full 20-dimension grading deferred to SKILL-QUALITY-004.
Repair: TC-SFE3-FU-002 (2026-07-15).
