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

MODE: EXECUTION MODE

Continue `FF6-PRODUCTION-LIBRARIES-001` autonomously from the verified GitLab
`main` checkpoint. Do not use chat memory, an old branch, a stale worktree, or
provider-local artifacts as authority.

## Required reconstruction

1. Read `AGENTS.md`, `docs/governance/skill-only-policy.yaml`,
   `plans/codex/handover/START-HERE.md`, and every file in its ordered reading
   list. No separate Claude adapter is tracked; Claude must use its ambient
   hooks plus the shared `AGENTS.md` contract.
2. Fetch GitLab `origin/main`. Do not create or use another branch and do not
   use GitHub for this mission.
3. Validate `CURRENT-MACHINE-STATE.yaml` against live tracked state rather than
   trusting its labels.
4. Require:
   - controller `CONTRACT`, sequence 17;
   - event `FF6-EVENT-000017`, hash
     `44cb90a67aec8fff244de05d84c047f1d31077d694eda1ff1e27ee0aaa0f3015`;
   - parent `TC-FF6-PROGRAM-CAPABILITIES-001` in `NEEDS_REPAIR`;
   - `TC-FF6-ORA-PROFILE-SURFACE-001` in `PASS`;
   - `TC-FF6-IPYNB-PROFILE-SURFACE-001` in `READY`;
   - 99 capabilities, 738 obligations, and aggregate
     `de6a38a86aa7a82cc50dc7dc6ebfa0066c811d8de782a37684fd26d20a89272a`;
   - 15/15 authority artifacts `MATCH`;
   - zero product certifications and no promotion.
5. Validate the native FF6 chain with `previous_event_hash`. The generic Plan
   Control journal schema is different and must not be used to rewrite FF6.
6. Query coordination, register this Claude session, inspect conflicts and
   leases, and claim exact task paths before writing. Preserve all unrelated
   state.

## Execute exactly this task

Execute `taskcards/TC-FF6-IPYNB-PROFILE-SURFACE-001.md` through its registered
SAL, contract, capability-compiler, taskcard, and controller skills.

Required result:

- source-located nbformat 4.0, 4.1, 4.2, 4.3, 4.4, and 4.5 delta matrix;
- exact profile applicability on every IPYNB capability and obligation;
- capability splits wherever one current capability mixes version scopes;
- stable ownership of every `SAL-IPYNB-OBL-*` rule;
- preserved typed notebook/cell/output/attachment/MIME/metadata, validation,
  conversion, deterministic serialization, safe cleanup/filtering/ID handling,
  unknown metadata preservation, and structural inspection requirements;
- explicit absolute no-execution boundary;
- `FF6-IPYNB-PROFILE-001` removed only by compiled evidence;
- all six projections regenerated three byte-identical times;
- 15/15 authorities still match;
- task, gap, controller, event, and handover projections reconciled;
- no product, package, gate, certification, or promotion mutation.

## Execution discipline

- Work one atomic, independently verifiable substep at a time.
- Before each write: resolve skill, ensure execution manifest, own the lease,
  run preflight and mutation guard.
- After each write: record it in coordination.
- Never stage broadly; use an explicit reviewed path list.
- If the task completes, append close intent, independently verify, append the
  verified event, and select the next mandatory gap.
- If the shift must end first, reach an integration-safe substep boundary,
  record `WORK_IN_PROGRESS` and the first unmet criterion, refresh the packet,
  commit and push GitLab main, and remote-verify.
- Never ask for continuation. Continue safe unblocked work until a clean shift
  checkpoint is required.

## Forbidden

- product source or product tests during the current task;
- authority-lock recreation;
- status/policy edits that suppress failed evidence;
- execution of notebook code;
- self-certification or gate approval;
- stash, reset, restore, clean, checkout-discard, broad add, or another
  provider's lease release;
- publication authority bypass.

The final response must state the pushed GitLab commit, journal head, exact
task state, verification results, remaining gaps, and the absolute
`START-HERE.md` path. Repository state, not the response, is the handover.
