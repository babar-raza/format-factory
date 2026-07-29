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
7. all 17 records in `plans/strategic/ff6/events.jsonl`
8. `plans/strategic/ff6/current-gaps.yaml`
9. `taskcards/TC-FF6-PROGRAM-CAPABILITIES-001.md`
10. `taskcards/TC-FF6-IPYNB-PROFILE-SURFACE-001.md`
11. `plans/codex/handover/ACTIVE-WORK-CHECKPOINT.md`
12. `.supervisor/knowledge/registry.yaml` and every verified-current contract
    applicable before any later product-source mutation

## Required reconstruction

Fetch `origin/main` and require that the checkout contains:

- controller state `CONTRACT`;
- event `FF6-EVENT-000017` with hash
  `44cb90a67aec8fff244de05d84c047f1d31077d694eda1ff1e27ee0aaa0f3015`;
- parent `TC-FF6-PROGRAM-CAPABILITIES-001` in `NEEDS_REPAIR`;
- completed `TC-FF6-ORA-PROFILE-SURFACE-001` in `PASS`;
- exact next task `TC-FF6-IPYNB-PROFILE-SURFACE-001` in `READY`;
- 15/15 authority artifacts `MATCH`;
- capability aggregate
  `de6a38a86aa7a82cc50dc7dc6ebfa0066c811d8de782a37684fd26d20a89272a`.

Validate the FF6 journal using its native
`previous_event_hash`/`ff6/controller-event@1` contract. The generic
`tools.plan_control doctor` uses a different `previous_hash` schema and is
already tracked as incompatible under `FF6-GAP-011`; its failure is not
permission to alter either journal.

## Execute exactly this task

Execute `TC-FF6-IPYNB-PROFILE-SURFACE-001`. Compile exact nbformat 4.0-4.5
capability and obligation applicability from the pinned official schemas and
documentation through the registered SAL, contract, capability-compiler,
taskcard, and controller skills.

Do not:

- recreate the authority lock or materializer;
- modify product source or product tests during this task;
- suppress `FF6-IPYNB-PROFILE-001` in policy;
- weaken the notebook no-execution boundary;
- close the parent while another mandatory profile/surface gap remains;
- create a branch or use GitHub;
- ask for continuation.

Use the coordination protocol on the shared `main` worktree, preserve all
unexplained changes, preflight every write, append close intent before final
projections, independently verify the close event, refresh this packet, commit
only explicit owned paths, and push only to GitLab `origin/main`.
