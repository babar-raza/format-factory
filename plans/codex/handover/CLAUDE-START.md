---
artifact_id: FF6-CLAUDE-START-001
artifact_type: agent_resume_prompt
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
authoritative_state: false
---

# Claude Resume Instruction

Continue mission `FF6-PRODUCTION-LIBRARIES-001` autonomously from the
repository’s verified GitLab `main` checkpoint. Do not use chat memory, an old
branch, a stale worktree, or a local transcript as authority.

## Read before action

1. `AGENTS.md`
2. `docs/governance/claude-adapter.md` if present, otherwise the applicable
   provider governance adapter
3. `plans/codex/handover/START-HERE.md`
4. `plans/strategic/ff6/product-goal.yaml`
5. `plans/strategic/autonomous-six-python-production-execution-plan.md`
6. `plans/strategic/ff6/controller-state.yaml`
7. all 16 records in `plans/strategic/ff6/events.jsonl`
8. `plans/strategic/ff6/current-gaps.yaml`
9. `taskcards/TC-FF6-PROGRAM-CAPABILITIES-001.md`
10. `taskcards/TC-FF6-ORA-PROFILE-SURFACE-001.md`
11. `plans/codex/handover/ACTIVE-WORK-CHECKPOINT.md`
12. `.supervisor/knowledge/registry.yaml` and every verified-current contract
    applicable before any later product-source mutation

## Required reconstruction

Fetch `origin/main` and require that the checkout contains:

- controller state `CONTRACT`;
- event `FF6-EVENT-000016` with hash
  `2ea206536ff0ccecaa0a4e93df32ada3e7575018f4cdcafb7525c59d51dd50ba`;
- parent `TC-FF6-PROGRAM-CAPABILITIES-001` in `NEEDS_REPAIR`;
- completed `TC-FF6-AUTHORITY-CLOSURE-001` in `PASS`;
- exact next task `TC-FF6-ORA-PROFILE-SURFACE-001` in `READY`;
- 15/15 authority artifacts `MATCH`;
- capability aggregate
  `667cd4cb69773e6746ad46173b53de39c18ef44d39ef7db91c6337d8a3761a73`.

Validate the FF6 journal using its native
`previous_event_hash`/`ff6/controller-event@1` contract. The generic
`tools.plan_control doctor` uses a different `previous_hash` schema and is
already tracked as incompatible under `FF6-GAP-011`; its failure is not
permission to alter either journal.

## Execute exactly this task

Execute `TC-FF6-ORA-PROFILE-SURFACE-001`. Repair the OpenRaster 0.0.3,
0.0.4, and 0.0.5 profile applicability and explicit image/layer/mask/
compositing/rendering capability surface through the registered SAL, contract,
capability-compiler, taskcard, and controller skills.

Do not:

- recreate the authority lock or materializer;
- modify product source or product tests during this task;
- suppress `FF6-ORA-SURFACE-001` or `FF6-ORA-PROFILE-001` in policy;
- treat an early OpenRaster draft as universal conformance authority;
- close the parent while another mandatory profile/surface gap remains;
- create a branch or use GitHub;
- ask for continuation.

Use the coordination protocol on the shared `main` worktree, preserve all
unexplained changes, preflight every write, append close intent before final
projections, independently verify the close event, refresh this packet, commit
only explicit owned paths, and push only to GitLab `origin/main`.
