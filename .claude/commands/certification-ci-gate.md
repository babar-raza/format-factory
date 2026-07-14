---
version: "1.0"
last-updated: "2026-07-13"
phase-available: "all"
gate-required: null
created-by: TC-007-precious-wandering-lighthouse
spec_qname_required: "false"
product_track: "governance"
---

# /certification-ci-gate

Run the CI certification gate — verifies no regression against locked baseline thresholds.

## What It Does

1. Reads `reports/certification/certification-baseline.json`
2. Checks per-format stub-audit, assertion-quality, and INCOMPLETE_EVIDENCE verdicts
3. Checks mutation kill rate against locked thresholds
4. Exits 0 (PASS) or 1 (FAIL) with detailed regression report

## Usage

```bash
python tools/certification/ci_certification_gate.py
python tools/certification/ci_certification_gate.py --strict
```

## Outputs

- Console report with PASS/FAIL per dimension
- Exit code 0 or 1

## Tests

`tests/certification/test_tool_detection.py::TestCIGateBlocksOnRegression`
