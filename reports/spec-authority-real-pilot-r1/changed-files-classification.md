# Changed Files Classification
Pilot: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Generated: 2026-06-05

## Classification Rules

| Category | Files | Allowed |
|----------|-------|---------|
| Pilot reports (new) | `reports/spec-authority-real-pilot-r1/**` | YES — pilot output |
| Pilot tests (new) | `tests/spec_authority/**` | YES — regression tests |
| Pilot driver (new) | `reports/spec-authority-real-pilot-r1/_pilot_driver.py` | YES — pilot tool |
| Evidence (new) | `.local/evidences/spec-authority-real-pilot-r1/**` | YES — evidence output |
| SAL implementation | `tools/specification-authority-layer/**` | READ-ONLY |
| Product source (Python) | `src/python/**` | FORBIDDEN |
| Product source (.NET) | `src/net/**` | FORBIDDEN |
| Product tests (.NET) | `tests/net/**` | FORBIDDEN |
| Product tests (Python) | `tests/python/**` | FORBIDDEN |
| POC targets | `product-capability-matrix/poc-targets.yaml` | FORBIDDEN |
| Format registry | `registry/format-registry.yaml` | FORBIDDEN |

## New Files Created (allowed)

### Pilot Reports (`reports/spec-authority-real-pilot-r1/`)
- `00-preflight.md` — Preflight governance + SAL discovery
- `_pilot_driver.py` — Pilot pipeline driver script
- `command-ledger.json` — Command audit trail
- `taskcard-state.json` — Taskcard lifecycle tracking
- `layer-implementation-inventory.md` — SAL subsystem inventory
- `spec-authority-entrypoints.json` — Subsystem entry points
- `subsystem-coverage-matrix.json` — Per-format coverage
- `source-acquisition-report.md` — Source provenance + SHA-256
- `spec-source-registry-pilot.json` — Pilot source registry
- `spec-vault-manifest.json` — Vault integrity manifest
- `normalization-report.md` — Parse/normalize/digest results
- `requirement-extraction-report.md` — Extracted requirements summary
- `context-pack-generation-report.md` — Context pack results + determinism
- `context-pack-determinism-result.json` — Determinism proof (run1 == run2)
- `staleness-refresh-report.md` — Staleness detection results
- `staleness-test-result.json` — Synthetic staleness test proof
- `recomputation-queue.json` — Empty queue (all fresh)
- `downstream-contract-check.md` — Authority boundary compliance
- `spec-authority-output-contract.json` — Context pack contract
- `sample-requirement-authority-input-packet.json` — ZST sample packet
- `normalized-output-index.json` — Per-source artifact index
- `parser-defects-and-limitations.md` — Parser limitations for R2
- `candidate-requirements.jsonl` — Representative extracted requirements
- `authority-classification-summary.json` — Authority classification breakdown
- `rejected-or-caveated-requirements.md` — Caveat documentation
- `staleness-runtime-defects.md` — Staleness defects for R2
- `test-run-report.md` — Test results summary
- `regression-test-plan.md` — Regression test plan for future pilots
- `raw-test-logs.md` — Full pytest output
- `minimal-repair-report.md` — Repair documentation
- `changed-files-classification.md` — This file

### Pilot Tests (new, allowed)
- `tests/spec_authority/__init__.py` — Package init
- `tests/spec_authority/test_real_pilots.py` — 17 pilot regression tests

### Evidence (new, allowed)
- `.local/evidences/spec-authority-real-pilot-r1/` — Evidence root

## Production Files Changed

**NONE.** No production source files were modified.

## Governance Compliance

- No src/python/* changes: CONFIRMED
- No src/net/* changes: CONFIRMED
- No tests/python/* changes: CONFIRMED
- No tests/net/* changes: CONFIRMED
- No poc-targets.yaml mutation: CONFIRMED
- No registry/format-registry.yaml mutation: CONFIRMED
- No commits: CONFIRMED
- No pushes: CONFIRMED

## Verdict

`CLASSIFICATION_COMPLETE — ALL_CHANGES_WITHIN_ALLOWED_SCOPE`
