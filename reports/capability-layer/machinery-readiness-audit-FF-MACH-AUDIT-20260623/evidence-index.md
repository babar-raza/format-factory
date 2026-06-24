# Evidence Index — FF-MACH-AUDIT-20260623
**Plan:** sorted-purring-stardust | **Taskcard:** TC-MACH-CLOSE-01

## Files

| File | SHA256 |
|---|---|
| audit-phase-summary.md | `2a2439feb413dceb...` |
| backfill-facility-design.md | `1bfb67e6d8936c33...` |
| capability-compiler-completion-design.md | `e9a62869bf2ec2ee...` |
| evidence-index.md | `cbff3b94c9fc9162...` |
| final-verdict.md | `35dde84705a4c333...` |
| gap-ledger-stats.txt | `e0bac236af1558f8...` |
| gate11-readiness-review.md | `d22132aa5f832fec...` |
| lane-a-repo-governance-state.md | `c5c27ccb34c9f699...` |
| lane-b-qname-schema-audit.md | `0db431967a75cb8e...` |
| lane-c-product-source-quality.md | `a879835203113848...` |
| lane-d-skills-and-repeatability.md | `45a24e8181a69c48...` |
| lane-e-sal-audit.md | `88c642f565f642b3...` |
| lane-f-capability-layer-audit.md | `91d85eb56f8e78a8...` |
| lane-g-downstream-layers.md | `17245c03e2e044a9...` |
| lane-guard-design.md | `4d43a7a230a555b7...` |
| lane-h-supervisor-audit.md | `6a2fc86bb7ca0817...` |
| lane-i-backfill-facility-design.md | `5a23d8685bb6a00e...` |
| lane-j-product-readiness.md | `8cd9afade09ab35d...` |
| lane-separation-and-collision-risk.md | `d1be0fae26356268...` |
| machinery-repair-plan.md | `70f3d257279d7027...` |
| per-product-qname-compliance.yaml | `231d2ba2dc15230f...` |
| preflight-test-repair.txt | `6adc602fedbf96e1...` |
| product-deepening-execution-plan.md | `2c7180c28bdd2124...` |
| sal-refresh-check-output.txt | `9a312746b3f39583...` |
| system-gap-matrix.yaml | `a6066db04e6e8699...` |
| taskcards.yaml | `9d902780634f1824...` |
| v49-validator-design.md | `d5055bbbc01e1dc5...` |

## Phase 6 Implementation Files

| File | Change |
|---|---|
| tools/supervisor/capability_compiler.py | Added select_and_write_gaps() + select-gaps CLI |
| tools/supervisor/autonomous_task_generator.py | Wired compiler invocation + priority boost |
| tools/supervisor/governance_validators_ext.py | Added V62 + V63 |
| tools/supervisor/governance_validator_runner.py | Wired V62 + V63 |
| tools/supervisor/autonomous_cycle.py | Step 1c lane guard + Step 0a-staleness |
| tools/supervisor/failure_memory.py | Graduated severity escalation |
| tools/backfill/__init__.py | Created (empty) |
| tools/backfill/inventory.py | Created — format stub scanner |
| tools/backfill/plan_generator.py | Created — migration plan generator |
| reports/capability-layer/gap-ledger.json | 21 architecture_only stub entries appended |

## Test Files

- tests/supervisor/test_capability_compiler.py
- tests/supervisor/test_governance_validators.py
- tests/supervisor/test_lane_guard.py
- tests/supervisor/test_sal_staleness.py
- tests/supervisor/test_failure_memory.py
- tests/backfill/test_inventory.py
