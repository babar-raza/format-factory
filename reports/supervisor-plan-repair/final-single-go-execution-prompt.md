# Final Single-Go Execution Prompt

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## Mission

Make the Supervisor stream a deterministic product-factory traffic controller that:
1. Prevents false PASS (evidence-only sprints claiming product breadth)
2. Prevents false STOP (prompt-quality issues blocking real product work)
3. Enforces Mainstream product-output floors
4. Routes blockers to correct streams
5. Governs external runtime tools (Ruflo, Superpowers, GhidraMCP)
6. Keeps AI advisory output non-authoritative
7. Supports 3 new continuation states

## Execution Order

Lane 0 (Coordinator) → Lane X (External Governance) + Lane A (Healing) + Lane B (Implementation) + Lane C (Evidence) → Lane D (Tests) → Lane 0 (Closeout)

## Key Facts

- CLI: `python tools/supervisor/autonomous_cycle.py --declaration <path>` (NO subcommand)
- Edit target: `classify_continuation_state()` in autonomous_cycle.py — ONE call site at ~line 602
- New states: NO_PRODUCT_OUTPUT_FLOOR, NO_MISSING_REQUIRED_ARTIFACTS, NO_UNCLASSIFIED_DIRTY_STATE
- AI advisory: all outputs must have `non_authoritative: true`, `advisory_mode: deterministic_advisory`
- External tools: Ruflo/claude-flow DETECTED_NOT_CONFIGURED (not invoked); Superpowers ABSENT; GhidraMCP DISABLED_DEFAULT

## Forbidden Actions

- No product source edits (`src/net/**`, `src/python/**`)
- No git commit, no git push, no publication
- No Gate 8, no Gate 11 approval
- No claude-flow/task-master-ai invocation
- No `.vscode/mcp.json` modification
