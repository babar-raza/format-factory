# Next-Step Authority Note
# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001

## Authoritative Next Mainstream Input

The authoritative execution prompt for the next Mainstream sprint is:

```
reports/tri-lane-integration-refresh/mainstream-execution-handoff-v2.md
```

This supersedes:
- Any prior Mainstream execution prompt from before this refresh sprint
- Generic next-work-items.json product suggestions from the supervisor cycle
- Any review/next-worker-prompt.md content that conflicts with this handoff

## Why the Handoff Supersedes Generic Supervisor Output

The supervisor's `next-work-items.json` may suggest general product implementation steps.
However, the tri-lane integration refresh sprint has produced a curated, validated handoff
that:
1. Identifies the correct 4 families (FODS, FODT Markdown, FODT TXT, Netpbm)
2. References the correct packet v2, contract v2, and Skills finalization packets
3. Provides explicit test commands (`dotnet test --filter ...`)
4. Enforces the evidence closeout protocol (autonomous-cycle + review package)
5. Documents the Python portability pattern for closeout commands

## Gate 11 Clarification

Gate 11 is **not required** for product implementation work in Mainstream.

Gate 11 is the commercial readiness / release approval gate. It applies when:
- A format is being published to NuGet/PyPI
- Commercial release authorization is required
- Human approval from Babar Raza is needed for publication

Gate 11 does **not** block:
- Product source editing
- Test writing and execution
- Evidence declaration and autonomous-cycle
- Capability delta proposals

## Mainstream Pre-Flight Required

Before editing any product source, Mainstream must:
1. Read `reports/tri-lane-integration-refresh/mainstream-execution-handoff-v2.md`
2. Read `reports/tri-lane-integration-refresh/mainstream-execution-packet.v2.json`
3. Read `reports/tri-lane-integration-refresh/mainstream-readiness-gate.md`
4. Confirm `reports/tri-lane-integration-refresh/dirty-state-classification.json`:
   - `src/net/fods/FodsDocument.cs` — PRE_EXISTING_PRODUCT_WIP
   - `src/net/fodt/FodtDocument.cs` — PRE_EXISTING_PRODUCT_WIP
   - `src/net/netpbm/Model/NetpbmImage.cs` — PRE_EXISTING_PRODUCT_WIP
   - `src/python/sylk/sylk_parser.py` — PRE_EXISTING_PRODUCT_WIP (not in scope)
5. If any file shows UNSAFE_DIRTY_STATE_REQUIRES_STOP: halt and report to human.
