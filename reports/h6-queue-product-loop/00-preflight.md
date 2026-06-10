# Sprint Preflight — FORMAT-FACTORY-H6-AUTONOMOUS-PRODUCT-QUEUE-CONSUMPTION-001

## Sprint Purpose

Advance from H6 external host proven (Package 113) to queue-driven product-safe execution.
The external host must consume the durable action queue, execute at least one bounded
product-safe task, and update queue statuses — without Babar pasting a prompt.

## Starting State (Package 113 Baseline)

- Sprint: FORMAT-FACTORY-H6-EXTERNAL-HOST-ACTIVATION-AND-PROOF-001
- SHA-256: b9a09c8213a00f87a5af3df32a12d5716def1e55d08ea9282212de1bdd6107d6
- IV verdict: H6_EXTERNAL_HOST_PROVEN
- external_run_confirmed: true
- cycle_index: 10 (9 cycles executed)
- CLAUDECODE cleared during runs
- active-continuation.json: autonomous_continue=true, advisory_prompt_executable=false
- next-action.json: action_type=RUN_JSON_VALIDATION (machine-readable)
- action-queue.jsonl: 5 items, ALL still PENDING (queue not consumed by prior runs)

## Gap Identified (this sprint's reason for existence)

The orchestrator loop used `next_action_generator.py` exclusively — the durable queue
was never dequeued. Queued items remain pending after 9 orchestrator cycles.

This sprint closes that gap by:
1. Adding `--queue-first` flag to orchestrator (queue beats generator)
2. Seeding a `PRODUCT_GAP_CLASSIFICATION_READONLY` product-safe item
3. Running external host with queue-first mode
4. Proving at least one queued item moves pending→running→done

## Lane Ownership

| Lane | Owner | Paths |
|------|-------|-------|
| L0 | Coordinator | reports/h6-queue-product-loop/ |
| L1 | Queue Primary | tools/supervisor/autonomous_orchestrator.py, tools/supervisor/action_queue.py |
| L2 | Continuation | tools/supervisor/evidence_continuation.py |
| L3 | Product Pilot | tools/supervisor/product_action_guard.py, tools/supervisor/backends/ |
| L4 | Host Run | reports/h6-queue-product-loop/host-run/ |
| L5 | Post-Closeout | reports/h6-queue-product-loop/post-closeout/ |
| L6 | Tests | tests/supervisor/ |
| L7 | IV | reports/h6-queue-product-loop/iv/ |
| LE | Evidence | .local/evidences/h6-queue-product-loop/ |

## Non-Negotiable Rules

- No src/ mutations
- No poc-targets.yaml mutations
- No git push/commit/reset/clean/stash
- No Gate 8 or Gate 11 approval
- No advisory Markdown treated as executable
- No nested Claude CLI invocation
