---
version: "1.0"
last-updated: "2026-07-01"
phase-available: "all"
gate-required: null
created-by: TC-CERT-I-020
spec_qname_required: "false"
product_track: "governance"
---

# /certification-generate-exception-tests

Generate missing exception-coverage test stubs for a format.

**WARNING: Mutates test files in place — use with caution. Review output before committing.**

## What It Does

1. Reads exception-coverage.json to find uncovered exceptions
2. Generates `pytest.raises` test stubs for each uncovered exception
3. Appends stubs to the format's test file

## Usage

```bash
python tools/certification/generate_exception_tests.py \
  --format fods \
  --src-path src/python/fods \
  --test-path tests/python/fods \
  --coverage-report reports/certification/fods/exception-coverage.json
```

## Layer

L28 Certification Audit Layer (`plans/layers/certification-audit-layer.md`)

## Allowed Paths

- `tools/certification/generate_exception_tests.py`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no .NET product source mutation
- `src/python/**` — no Python product source mutation
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if exception tests cannot be generated
- Stop if focused tests do not pass after changes

## Output Format

- Generated artifact written to the configured output path
- Confirmation message: file path and size
- Validation result confirming the output is well-formed
