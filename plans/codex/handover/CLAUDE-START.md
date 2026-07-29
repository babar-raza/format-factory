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
   - source checkpoint
     `865558bb88243acda08c2a8d58a0d5ec887dedeb` is an ancestor of fetched
     `origin/main`;
   - controller `CONTRACT`, sequence 19;
   - event `FF6-EVENT-000019`, hash
     `76b580d72f865428e92bc5b6089a89487356c69163aadf6b615b70c6867221f8`;
   - parent `TC-FF6-PROGRAM-CAPABILITIES-001` in `NEEDS_REPAIR`;
   - `TC-FF6-NRRD-PROFILE-SURFACE-001` in `PASS`;
   - `TC-FF6-XLIFF-PROFILE-SURFACE-001` in `READY`;
   - 110 capabilities, 672 obligations, and aggregate
     `4d17d8c8c0ef3de74d59e1d5b16884c0210fd0836e0593591871f10d0af2efd2`;
   - 15/15 authority artifacts `MATCH`;
   - zero product certifications and no promotion.
5. Validate the native FF6 chain with `previous_event_hash`. The generic Plan
   Control journal schema is different and must not be used to rewrite FF6.
6. Query coordination, register this Claude session, inspect conflicts and
   leases, and claim exact task paths before writing. Preserve all unrelated
   state.

## Execute exactly this task

Execute `taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md` through its registered
authority-acquisition, SAL, family, research, contract,
capability-compiler, taskcard, and controller skills.

Required result:

- official XLIFF 2.0 OASIS Standard package independently digest-checked,
  legally classified, locked, and clean-offline reconstructible;
- source-located XLIFF 2.0/2.1 Core and official-module delta matrices;
- exact profile applicability on every XLIFF capability and obligation;
- separate first-class capability ownership for Matches, Glossary, Metadata,
  Resource Data, Size and Length Restriction, and Validation;
- semantic obligations for inline pairing/order/nesting/isolation,
  segmentation/re-segmentation, state/sub-state, original data, skeletons,
  extensions, ITS mappings, deterministic canonical XML, security, resource
  limits, downgrade-loss reporting, and normative agent processing;
- stable ownership of every `SAL-XLIFF-OBL-*` rule;
- XLIFF 2.2 absent or isolated preview-only and XLIFF 1.2 kept outside the 2.x
  model;
- `FF6-XLIFF-PROFILE-001` removed only by compiled evidence;
- all six projections regenerated three byte-identical times;
- every authority record, including the new XLIFF 2.0 record, matches;
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
- ad hoc authority-lock recreation or a 2.0 claim derived from 2.1 bytes;
- status/policy edits that suppress failed evidence;
- collapsing modules into a generic support claim or treating XSD validity as
  semantic/processing support;
- weakening XML external-resource or resource-exhaustion safety;
- self-certification or gate approval;
- stash, reset, restore, clean, checkout-discard, broad add, or another
  provider's lease release;
- publication authority bypass.

The final response must state the pushed GitLab commit, journal head, exact
task state, verification results, remaining gaps, and the absolute
`START-HERE.md` path. Repository state, not the response, is the handover.
