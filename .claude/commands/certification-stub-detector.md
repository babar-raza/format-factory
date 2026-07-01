---
version: "1.0"
last-updated: "2026-07-01"
phase-available: "all"
gate-required: null
created-by: TC-CERT-I-020
spec_qname_required: "false"
product_track: "governance"
---

# /certification-stub-detector

Detect material stub functions (pass-only bodies, `raise NotImplementedError`, etc.)
in source files and write a `stub-report.json` evidence file.

## What It Does

1. Scans Python source files for stub patterns
2. Classifies findings as material (blocks certification) or informational
3. Writes `reports/certification/{fmt}/stub-report.json`
4. Exits 0 when `material_finding_count == 0`, exits 1 otherwise

## Usage

```bash
python tools/certification/stub_detector.py --path src/python/fods \
  --output reports/certification/fods/stub-report.json
```

## Verification

```bash
.venv/Scripts/pytest tests/certification/test_tool_pipeline.py -q
```

## Layer

L28 Certification Audit Layer (`plans/layers/certification-audit-layer.md`)
