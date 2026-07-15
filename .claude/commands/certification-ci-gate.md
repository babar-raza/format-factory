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

## Idempotency Contract

Running twice on an unchanged baseline produces identical exit codes and identical
per-dimension verdicts. Gate is read-only against `reports/certification/` — no
mutation side effects.

## Output Contract

```
exit 0  → PASS  (no regression vs locked baseline)
exit 1  → FAIL  (one or more dimensions regressed)

Console:
  [PASS] stub-audit: 0 regressions
  [FAIL] mutation-kill-rate: 82% < threshold 85%
```

## Error Handling

- Missing baseline file: exit 1 with `BASELINE_NOT_FOUND` message.
- Malformed baseline JSON: exit 1 with `BASELINE_PARSE_ERROR`.
- Partial dimension failure: report all dimensions, exit 1 if any FAIL.

## Scope Constraint

Read-only: reads `reports/certification/certification-baseline.json` and per-format
reports. Never writes. Safe to run in CI without state risk.

## Parity Note

PARTIAL parity: command file is complete for automation use. Full 20-dimension quality
grading deferred to SKILL-QUALITY-004. Repair: TC-SFE3-FU-002 (2026-07-15).
