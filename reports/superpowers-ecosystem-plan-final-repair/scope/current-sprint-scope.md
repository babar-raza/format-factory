# Current Sprint Scope
Sprint: FORMAT-FACTORY-SUPERPOWERS-ECOSYSTEM-PLAN-FINAL-REPAIR-001

## In Scope (THIS SPRINT)
Plan artifacts, design documents, integration design, validator specs, execution prompt, evidence only.

- Preflight and lane ownership (TC-FR-000)
- Runtime verification — read-only discovery (TC-FR-001)
- Scope separation document (TC-FR-002, this file)
- Tool setup classification (TC-FR-003)
- Taskcard state model (TC-FR-004)
- Swarm/file ownership model (TC-FR-005)
- Verification commands spec (TC-FR-006)
- Rollback/recovery model (TC-FR-007)
- Superpowers fallback taxonomy (TC-FR-008)
- next-execution-prompt.md (TC-FR-009)
- Independent plan review (TC-FR-010)
- Evidence bundle (TC-FR-011)

## NOT In Scope (FUTURE EXECUTION)
- next_action_runner.py implementation
- backend_selector.py implementation
- backends/ directory (MCP, LLM, deterministic)
- autonomous_host_daemon.py
- H3–H6 proof (two-cycle, agentic, external host)
- cognee, openspec, skill_seekers installation
- Any src/ modifications
- Any test file creation

## Verdict Constraint
This sprint cannot produce verdict COMPLETE_BACKEND_SELECTOR_*.
Valid verdicts: READY_FOR_SINGLE_GO_EXECUTION / PLAN_READY_WITH_LIMITATIONS / PLAN_NEEDS_REPAIR.
