---
version: "1.0"
last-updated: "2026-07-01"
phase-available: "all"
gate-required: null
created-by: TC-CERT-I-020
spec_qname_required: "false"
product_track: "governance"
---

# /certification-exception-checker

Check that each exception raised in source is exercised in tests and write an
`exception-coverage.json` evidence file.

## What It Does

1. Scans source files for `raise` statements and exception types
2. Cross-references test files for corresponding `pytest.raises` or `assertRaises` calls
3. Writes `reports/certification/{fmt}/exception-coverage.json`
4. Reports `uncovered_exception_count`

## Usage

```bash
python tools/certification/exception_coverage_checker.py \
  --src-path src/python/fods \
  --test-path tests/python/fods \
  --output reports/certification/fods/exception-coverage.json
```

## Verification

```bash
.venv/Scripts/pytest tests/certification/test_tool_pipeline.py -q
```

## Layer

L28 Certification Audit Layer (`plans/layers/certification-audit-layer.md`)

## Allowed Paths

- `tools/certification/exception_coverage_checker.py`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no .NET product source mutation
- `src/python/**` — no Python product source mutation
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if exception coverage cannot be evaluated
- Stop if the execution would modify any file under src/

## Output Format

- PASS / FAIL / PARTIAL verdict printed to stdout
- Per-item findings list with skill_id, issue, and severity
- Report file at `reports/` with structured YAML findings
