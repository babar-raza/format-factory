---
version: "1.0"
last-updated: "2026-07-01"
phase-available: "all"
gate-required: null
created-by: TC-CERT-I-020
spec_qname_required: "false"
product_track: "governance"
---

# /certification-fix-weak-assertions

Strengthen weak assertions in Python test files for a format.

**WARNING: Mutates test files in place — use with caution. Review output before committing.**

## What It Does

1. Reads assertion-quality.json to find weak assertions
2. Rewrites bare `assert x` / `assert x is not None` patterns to more specific assertions
3. Updates the test file in place

## Usage

```bash
python tools/certification/fix_weak_assertions.py \
  --path tests/python/fods \
  --quality-report reports/certification/fods/assertion-quality.json
```

## Layer

L28 Certification Audit Layer (`plans/layers/certification-audit-layer.md`)

## Allowed Paths

- `tools/certification/fix_weak_assertions.py`
- `reports/` — evidence output (write)

## Forbidden Paths

- `src/net/**` — no .NET product source mutation
- `src/python/**` — no Python product source mutation
- `plans/strategic/**` — strategic plans are read-only

## Stop Conditions

- Stop if weak assertion fixes cannot be validated
- Stop if focused tests do not pass after changes

## Output Format

- Certification report JSON written to `reports/certification/<format_id>/`
- Summary: total items, passing, failing, score
- Actionable findings for any failing items
