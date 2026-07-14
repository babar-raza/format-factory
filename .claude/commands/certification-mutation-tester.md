---
version: "1.0"
last-updated: "2026-07-13"
phase-available: "all"
gate-required: null
created-by: TC-007-precious-wandering-lighthouse
spec_qname_required: "false"
product_track: "governance"
---

# /certification-mutation-tester

Run mutation testing for a format and produce a kill-rate report.

## What It Does

1. Applies AST-level mutations to the format's source
2. Runs the format's test suite against each mutation
3. Reports kill rate (% mutations caught by tests)

## Usage

```bash
python tools/certification/mutation_tester.py \
  --format fods \
  --src-path src/python/fods \
  --test-path tests/python/fods \
  --output reports/certification/fods/mutation-baseline.json
```

## Required Handoff Fields

- `format_id`: The format to test (e.g. `fods`, `csv`)
