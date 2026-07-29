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
     `a1316b4fae21c20c71ccb6d60e4b9fe634dca573` is an ancestor of fetched
     `origin/main`;
   - controller `CONTRACT`, sequence 21;
   - event `FF6-EVENT-000021`, hash
     `3e83a764c53da658cb1dd348ed20d041db850f1cef45bec5eaa5637ccafecc11`;
   - parent `TC-FF6-PROGRAM-CAPABILITIES-001` in `NEEDS_REPAIR`;
   - `TC-FF6-NRRD-PROFILE-SURFACE-001` in `PASS`;
   - `TC-FF6-XLIFF-PROFILE-SURFACE-001` in `WORK_IN_PROGRESS`, with
     `XLF-01` and `XLF-02` complete, `XLF-03` first unmet, and XLF-03
     microstate `GREEN_VERIFIED_CHECKPOINTED`;
   - 110 capabilities, 672 obligations, and aggregate
     `4d17d8c8c0ef3de74d59e1d5b16884c0210fd0836e0593591871f10d0af2efd2`;
   - 17/17 authority artifacts `MATCH`, including 5/5 XLIFF;
   - zero product certifications and no promotion.
5. Validate the native FF6 chain with `previous_event_hash`. The generic Plan
   Control journal schema is different and must not be used to rewrite FF6.
6. Query coordination, register this Claude session, inspect conflicts and
   leases, and claim exact task paths before writing. Preserve all unrelated
   state.

## Execute exactly this task

Resume `taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md` at `XLF-03` through its registered
authority-acquisition, SAL, family, research, contract,
capability-compiler, taskcard, and controller skills.

Do not reacquire XLIFF 2.0 unless event-20 authority inputs changed. First:

1. verify the event-21 source, test, and transcript SHA-256 values;
2. run `python -m pytest tests/tools/test_extract_sal_facts.py -q` and require
   3 passed;
3. rerun Ruff, strict Mypy, and bytecode compilation;
4. validate `reports/ff6/xliff-authority-member-inventory.yaml` against both
   pinned ZIPs;
5. add `test_cli_writes_and_checks_default_xliff_matrix` and prove it RED;
6. implement default curated Core/module/validation seeds and deterministic
   CLI/check mode to make it GREEN;
7. add the declared archive/XML/matrix negative controls;
8. generate the real matrix and prove three byte-identical outputs.

Preserve the existing tested compiler slice unless replay exposes a defect.
The CLI, default seed inventory, full negative suite, and real authority output
are absent at the checkpoint; XLF-03 is not complete.

Remaining required result:

- source-located XLIFF 2.0/2.1 Core and official-module delta matrices;
- exact profile applicability on every XLIFF capability and obligation;
- separate first-class capability ownership for all eight official modules:
  Translation Candidates/Matches, Glossary, Format Style, Metadata, Resource
  Data, Size and Length Restriction, Validation, and ITS;
- exact accounting for all nine module schema vocabularies, with `its` and
  `itsm` assigned to the single ITS module and informative Change Tracking
  excluded from normative module coverage;
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
- Use the TDD microstate in
  `STATE-MACHINE-AND-TASKCARD-PROTOCOL.md`; a planned shift may occur only
  after GREEN verification, journal, packet refresh, commit, push, and remote
  verification.
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
