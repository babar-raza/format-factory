# Train G: Context Pack as Authority Snapshot

## Problem (D99-STALE-02)
Context pack was not rebuilt as part of the autonomous cycle. Workers consuming `next-sprint.md` had to read `.supervisor/context-pack.yaml` manually, and it could be stale.

## Fix (R99)
Added Step 7c to `autonomous_cycle.py` that calls `build_context_pack()` after grading and legacy markdown regeneration.

## Context Pack Contents
The context pack includes:
1. **Current state** — git HEAD, working tree clean/dirty, supervisor mode
2. **Master plan refs** — via latest sprint info
3. **POC matrix** — commercial .NET products, FOSS Python products, test counts, gate status
4. **Skill registry** — total skills, active skills, skill IDs, handoff/ledger requirements
5. **Product-code ledger** — total entries, governed changes, backfilled count
6. **Selected gaps** — referenced via path (`.local/supervisor/selected-product-gaps.json`)
7. **Work-item grades** — latest cycle summary (run_id, verdict, accepted/rework counts)
8. **Evidence model** — via declaration protocol in policies.yaml
9. **MCP status** — classification, file presence, mode, server count
10. **Continuation state** — autonomous_continue, iteration, max_iterations, hard stops
11. **Hard prohibitions** — listed in policies.yaml autonomous_continuation section

## Consumption
Every generated next-sprint prompt now consumes a current context pack because it is rebuilt immediately before the continuation signal is written.
