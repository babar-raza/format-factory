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
