# Capability Layer Healing Report

**Plan:** moonlit-squishing-sonnet
**Mission:** capability-layer-healing
**Completed:** 2026-07-01
**Final Verdict:** CAPABILITY_LAYER_REBUILT_RECONCILED_PROVEN_AND_IDEMPOTENT

---

## Summary

The product capability matrix and all derived artifacts were rebuilt from authoritative
SAL/obligation-driven sources. All 17 required counters are at zero.

---

## Taskcards Closed

| TC-ID | Title | Status |
|-------|-------|--------|
| TC-CAP-001 | Generate capability-system-inventory.yaml | CLOSED |
| TC-CAP-002 | Generate capability-consumer-graph.yaml | CLOSED |
| TC-CAP-003 | Generate capability-authority-model.yaml | CLOSED |
| TC-CAP-004 | Identity Normalization | CLOSED |
| TC-CAP-005 | Coverage Universe Rebuild | CLOSED |
| TC-CAP-006 | SAL/Obligation-Driven Capability Compiler | CLOSED |
| TC-CAP-007 | Capability Proof Audit | CLOSED |
| TC-CAP-008 | Gap Ledger Reconciliation | CLOSED |
| TC-CAP-009 | Taskcard Linkage for Open Gaps | CLOSED |
| TC-CAP-010 | Action Queue Regeneration with Hash Tracking | CLOSED |
| TC-CAP-011 | Repair Supervisor and Skill Consumers | CLOSED |
| TC-CAP-012 | Dashboard Update Governance and Historical Cleanup | CLOSED |
| TC-CAP-013 | Validator Suite Extension + Transactional Pipeline | CLOSED |
| TC-CAP-014 | Run All 9 Required Pilots | CLOSED |
| TC-CAP-015 | Test Suite | CLOSED |
| TC-CAP-016 | Full Validation Run + Finding Registry | CLOSED |
| TC-CAP-017 | Terminal Closeout | CLOSED |

---

## Required Counters (All Zero)

| Counter | Value |
|---------|-------|
| UNINVENTORIED_CAPABILITY_ARTIFACTS | 0 |
| FALSE_CAPABILITY_CONSUMER_CLAIMS | 0 |
| AMBIGUOUS_CAPABILITY_AUTHORITIES | 0 |
| UNRESOLVED_PRODUCT_FORMAT_IDENTITIES | 0 |
| ELIGIBLE_SUBJECTS_WITHOUT_CAPABILITY_DISPOSITION | 0 |
| CAPABILITIES_WITHOUT_OBLIGATION_PROVENANCE | 0 |
| FALSE_VERIFIED_CAPABILITIES | 0 |
| MISSING_CAPABILITIES_HIDDEN_BY_SCOPE | 0 |
| ACTIVE_LEDGER_CLOSED_GAPS | 0 |
| READY_OPEN_GAPS_WITHOUT_TASKCARDS | 0 |
| CLOSED_GAPS_WITH_ACTIVE_TASKCARDS | 0 |
| CLOSED_GAPS_IN_ACTION_QUEUE | 0 |
| ACTION_QUEUE_STALE_RELATIVE_TO_LEDGER | false |
| HISTORICAL_GAPS_POLLUTING_ACTIVE_SELECTION | 0 |
| MATERIAL_CAPABILITY_FINDINGS_WITHOUT_GAPS | 0 |
| FAILED_REQUIRED_PILOTS | 0 |
| MATERIAL_SECOND_RUN_CHANGES | 0 |

---

## Key Artifacts Produced

- `reports/capability-layer/capability-system-inventory.yaml`
- `reports/capability-layer/capability-consumer-graph.yaml`
- `reports/capability-layer/capability-authority-model.yaml`
- `reports/capability-layer/capability-subjects.yaml`
- `reports/capability-layer/capability-coverage-universe.yaml`
- `reports/capability-layer/capability-proof-audit.yaml`
- `reports/capability-layer/gap-ledger-active.json` (32 active gaps)
- `reports/capability-layer/gap-ledger-archive.json` (1,245 closed gaps)
- `reports/capability-layer/taskcards/` (32 YAML taskcard stubs)
- `reports/capability-layer/taskcard-linkage-report.yaml`
- `reports/capability-layer/action-queue.json` (schema v2.0, hash-tracked)
- `reports/capability-layer/closure-receipt-index.json` (1,245 receipts)
- `reports/capability-layer/sal-driven-capability-map.json` (SAL-primary compiler output)
- `tools/capability_layer/capability_compiler.py` (NEW — SAL-driven)
- `tools/capability_layer/capability_pipeline.py` (NEW — transactional pipeline)
- `tests/capability_layer/` (7 new test files, 188 passing)
- `.local/evidences/capability-layer-healing-001/pilots/` (9 pilot evidence files, all PASS)

---

## Test Results

```
.venv/Scripts/pytest tests/capability_layer/ -q
188 passed, 1 pre-existing failure (SKILL-GAP-011 governance product_type), 4 skipped
```

---

## Validation Results

```
validate_capability_map.py: PASS | Errors: 0 | Warnings: 31 (all advisory)
capability_pipeline.py --validate-only: PASS | Errors: 0 | Warnings: 31
```
