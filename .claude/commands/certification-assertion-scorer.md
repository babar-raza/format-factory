---
version: "1.0"
last-updated: "2026-07-01"
phase-available: "all"
gate-required: null
created-by: TC-CERT-I-020
spec_qname_required: "false"
product_track: "governance"
---

# /certification-assertion-scorer

Score the quality of assertions in Python test files and write an `assertion-quality.json`
evidence file. Exits 1 when weak assertions are found (this is correct behavior — use
`check=False` or `|| true` in pipelines).

## What It Does

1. Scans Python test files for assertion patterns
2. Scores each assertion: strong (specific values/types), weak (bare `assert x` or `is not None`)
3. Writes `reports/certification/{fmt}/assertion-quality.json`
4. Exits 0 when `weak_assertion_count == 0`, exits 1 otherwise

## Usage

```bash
python tools/certification/assertion_quality_scorer.py \
  --path tests/python/fods \
  --output reports/certification/fods/assertion-quality.json
```

## Verification

```bash
.venv/Scripts/pytest tests/certification/test_tool_pipeline.py -q
```

## Layer

L28 Certification Audit Layer (`plans/layers/certification-audit-layer.md`)
