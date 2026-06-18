# Taskcard Layer States — Format Factory

## Overview

Every taskcard in a sprint passes through a state machine that ties test validation
to the governance lifecycle. The state machine ensures that no taskcard claims
completion without appropriate test evidence at the required layer.

## State Definitions

| State | Description | Entry Condition |
|-------|-------------|----------------|
| `backlog` | Not yet started | Default at sprint start |
| `ready` | Prerequisites met; can begin | All prerequisite TCs complete |
| `active` | Currently in progress | Agent begins work |
| `blocked` | Waiting on external dependency | External gate reached |
| `LAYER0_VALIDATING` | Running L0 structural tests | L0 command issued |
| `FOCUSED_VALIDATING` | Running L1 format-focused tests | L1 command issued |
| `COMPONENT_VALIDATING` | Running L2 family tests | L2 command issued |
| `INTEGRATION_VALIDATING` | Running L3 supervisor/governance tests | L3 command issued |
| `BROAD_VALIDATING` | Running L5 broad infrastructure tests | L5 command issued |
| `FULLSUITE_VALIDATING` | Running L6 full suite (all shards) | L6 shard command issued |
| `EVIDENCE_PACKAGING` | Writing evidence-declaration.yaml | All required layers passed |
| `ACCEPTED_VERIFIED` | All tests passed; evidence accepted by autonomous-cycle | Cycle exit 0 |
| `ACCEPTED_WITH_REWORK` | Accepted with documented limitations or rework items | Cycle exit 3, rework documented |
| `REJECTED_NEEDS_REWORK` | Failed; requires fix before re-submission | Cycle exit 1 or new failures |

## State Transitions

```
backlog
  └─► ready (all prereqs complete)
        └─► active (agent starts work)
              ├─► blocked (external gate)
              │     └─► active (gate resolved)
              └─► LAYER0_VALIDATING
                    └─► [pass] → FOCUSED_VALIDATING / COMPONENT_VALIDATING /
                                  INTEGRATION_VALIDATING / BROAD_VALIDATING /
                                  FULLSUITE_VALIDATING (depending on required layer)
                         [fail] → REJECTED_NEEDS_REWORK
                    └─► [at required layer, pass] → EVIDENCE_PACKAGING
                          └─► [cycle exit 0] → ACCEPTED_VERIFIED
                               [cycle exit 3] → ACCEPTED_WITH_REWORK
                               [cycle exit 1] → REJECTED_NEEDS_REWORK
```

## Required Layer by Item Type

| Item Type | Minimum Required Layer | Notes |
|-----------|----------------------|-------|
| `GOVERNANCE_TASKCARD` | L0 (structural) | Governance docs + evidence |
| `PRODUCT_SOURCE` | L2 (family) | Source change must test whole family |
| `TEST_INFRASTRUCTURE` | L3 (integration) | Test runner changes affect supervisor |
| `SUPERVISOR_TASKCARD` | L3 (integration) | Supervisor pipeline verification |
| `DOCUMENTATION` | L0 (structural) | Docs-only changes |
| `REGISTRY_UPDATE` | L3 (integration) | Registry is consumed by governance |
| `CI_CHANGE` | L6 (full suite) | CI changes require full verification |

## Transition Rules (Blocking)

1. **No promotion without test evidence at or above the required layer.**
   A `PRODUCT_SOURCE` taskcard cannot move to `EVIDENCE_PACKAGING` from `FOCUSED_VALIDATING`
   (L1). It must reach `COMPONENT_VALIDATING` (L2) minimum.

2. **L0 failure is always blocking.**
   If `LAYER0_VALIDATING` fails with NEW failures (not in known-failure-ledger.yaml),
   the taskcard moves to `REJECTED_NEEDS_REWORK`. Pre-existing known failures do NOT block.

3. **Timeout keeps the state.**
   If a test command times out, the taskcard remains in its current VALIDATING state.
   Do NOT advance it to `EVIDENCE_PACKAGING` on incomplete execution.

4. **Dry-run output is not test evidence.**
   A taskcard that ran only `--dry-run` commands cannot move out of `active` state.
   Dry-run is planning, not validation.

5. **Partial shard ≠ full-suite validation.**
   Running shard 1/4 of L6 does not satisfy `FULLSUITE_VALIDATING`. All 4 shards
   at exit_code=0 are required before `EVIDENCE_PACKAGING`.

6. **Known failures vs new failures.**
   Check every failing test against `registry/known-failure-ledger.yaml`:
   - Pre-existing known failure → document; does NOT block state transition
   - New failure (not in ledger) → moves to `REJECTED_NEEDS_REWORK`

7. **Advisory evidence does NOT satisfy VALIDATING states.**
   Prose summaries, grep outputs, or cited docs are informational; they do not
   satisfy any VALIDATING state. A real test execution result is required.

## Usage in Evidence Declarations

When writing `evidence-declaration.yaml`, include the final state for each taskcard:
```yaml
taskcards:
  - tc_id: TC-HEAL-001
    status: ACCEPTED_VERIFIED
    validation_state: EVIDENCE_PACKAGING  # highest state reached
    test_layer_run: 0
    test_results_reliable: true
```

## Relationship to Test Layers

| Validation State | Test Layer | Command Pattern |
|-----------------|------------|----------------|
| `LAYER0_VALIDATING` | L0 | `tools/test_runner.py --layer 0` |
| `FOCUSED_VALIDATING` | L1 | `tools/test_runner.py --layer 1 --format {fmt}` |
| `COMPONENT_VALIDATING` | L2 | `tools/test_runner.py --layer 2 --format {fmt}` |
| `INTEGRATION_VALIDATING` | L3 | `pytest -m "layer0 or layer1 or layer2 or layer3"` |
| `BROAD_VALIDATING` | L5 | `pytest -m "layer0 or ... or layer5"` |
| `FULLSUITE_VALIDATING` | L6 | `pytest --cov=src --cov-report=xml` or all 4 shards |
