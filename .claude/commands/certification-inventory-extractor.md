---
version: "1.0"
last-updated: "2026-07-01"
phase-available: "all"
gate-required: null
created-by: TC-CERT-I-020
spec_qname_required: "false"
product_track: "governance"
---

# /certification-inventory-extractor

Extract API contracts (exports, functions, classes) for one or more formats and write
per-format `api-contract.json` evidence files under `reports/certification/{fmt}/`.

## What It Does

1. Scans source files under `src/python/{fmt}/` for public API members
2. Records exports, function signatures, and class definitions
3. Writes `reports/certification/{fmt}/api-contract.json`

## Usage

```bash
# Single format
python tools/certification/inventory_extractor.py --python --format fods \
  --output reports/certification/fods/api-contract.json

# All formats
python tools/certification/inventory_extractor.py --python \
  --output reports/certification/all-inventory.json
```

## Verification

```bash
.venv/Scripts/pytest tests/certification/test_tool_pipeline.py -q
```

## Layer

L28 Certification Audit Layer (`plans/layers/certification-audit-layer.md`)
