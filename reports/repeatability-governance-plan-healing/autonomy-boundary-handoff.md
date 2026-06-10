# Autonomy Sprint Boundary Handoff
# From: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-IDEMPOTENCY-CONTRACTS-001
# To: Autonomy Execution Sprint (future sprint)
# Date: 2026-06-08

## What This Sprint Does NOT Do
- Does NOT improve the system's autonomy level
- Does NOT implement queue dispatch maturity
- Does NOT implement new execution backends
- Does NOT run product source implementation pilots
- Does NOT integrate Qwen or external LLMs

## Governance Contracts Produced for the Autonomy Sprint
The autonomy sprint must consume these before claiming Level 3+:
1. docs/governance/execution-method-taxonomy.md
2. docs/governance/repeatability-contract.md
3. docs/governance/idempotency-contract.md
4. schemas/governance/product-mutation-evidence.schema.json
5. docs/governance/product-mutation-taskcard-state-machine.md

## Level 3+ Maturity Prerequisites
Before claiming Level 3 or higher:
1. All dispatched queue items must carry execution_method=QUEUE_DISPATCHED_EXECUTION
2. All mutations must have source_diff_path in execution result JSON
3. All mutations must have idempotency_key and source marker or sidecar
4. All evidence declarations must pass execution_method_required_validator
5. No MANUAL_UNGOVERNED or UNKNOWN_EXECUTION_METHOD work may be declared as autonomous
6. .supervisor/project-memory.md must not contain false cycle count claims

## Deferred Items

| Original TC | Title | Classification |
|---|---|---|
| TC-004 | Queue-backed source mutation pilot | HANDOFF_TO_AUTONOMY_SPRINT |
| TC-008 | Capability-gap-to-queue bridge | HANDOFF_TO_AUTONOMY_SPRINT |
| TC-010 | Continuation state repair | HANDOFF_TO_AUTONOMY_SPRINT |
| TC-011 | Qwen3 integration contract | HANDOFF_TO_AUTONOMY_SPRINT |
| TC-013 | Product implementation pilot | HANDOFF_TO_AUTONOMY_SPRINT |
| TC-015 | Autonomy maturity dashboard | HANDOFF_TO_AUTONOMY_SPRINT |
| TC-012 | Claude/ChatGPT skill compatibility | HANDOFF_TO_PRODUCT_CAPABILITY_SPRINT |

## Validator Implementation Deferred
The 10 validators in validator-hardening-plan.md are PLANNED but not implemented.
Implementation belongs to a validator implementation sprint, not the autonomy sprint.
The autonomy sprint consumes the governance contracts but implements its own validators
for queue dispatch, backend telemetry, and execution method enforcement.
