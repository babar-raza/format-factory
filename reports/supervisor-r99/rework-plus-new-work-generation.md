# Train F: Rework Plus New Work Generation

## Principle
Partial evidence failures must NOT stop the entire sprint. The generated next prompt must:
1. Include a **rework lane** for items that failed grading (REWORK_REQUIRED, OVERCLAIMED)
2. Include **safe new product/skill/supervisor work** in parallel
3. Hard-stop only for true global blockers (test baseline broken, overclaimed, rejected)

## Current Implementation
`generate_next_worker_prompt.py` already implements this via `synthesize_trains()`:
- G2 group: Rework trains generated from any item with REWORK_REQUIRED or OVERCLAIMED grades
- G3-G7 groups: Product, FOSS, dogfood, package, state trains generated independently

`autonomous_cycle.py` supports `true_with_rework` continuation mode (R91+):
- Rework items exist but safe lanes can continue
- Hard stops only for OVERCLAIMED or REJECTED items

## Hard Stop Conditions
Only these produce `autonomous_continue: false`:
1. OVERCLAIMED items present
2. REJECTED items present
3. Test failures (failed > 0)
4. Max iterations reached
5. External gate blocks (credentials, push, Gate 8/11)

Non-blocking conditions (safe lanes continue):
- REWORK_REQUIRED items
- ACCEPTED_WITH_LIMITATIONS items
- INSUFFICIENT_EVIDENCE items
- DEFERRED_WITH_REASON items
