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
     `4f0e8793d7aa694ccb45a57e9d3abc8f8cce92f7` is an ancestor of fetched
     `origin/main`;
   - controller `CONTRACT`, sequence 23;
   - event `FF6-EVENT-000023`, hash
     `01c265ecd5284320a82f31316b404e3f3f4edbab3b92cd071be8f9ec27f83641`;
   - parent `TC-FF6-PROGRAM-CAPABILITIES-001` in `NEEDS_REPAIR`;
   - `TC-FF6-NRRD-PROFILE-SURFACE-001` in `PASS`;
   - `TC-FF6-XLIFF-PROFILE-SURFACE-001` in `WORK_IN_PROGRESS`, with
     `XLF-01`, `XLF-02`, `XLF-03`, and `XLF-04-BATCH-001` complete,
     `XLF-04` still first unmet, and
     provider-shift microstate `RESUMABLE`;
   - 110 capabilities, 672 obligations, and aggregate
     `4d17d8c8c0ef3de74d59e1d5b16884c0210fd0836e0593591871f10d0af2efd2`;
   - 17/17 authority artifacts `MATCH`, including 5/5 XLIFF;
   - zero product certifications and no promotion.
5. Validate the native FF6 chain with `previous_event_hash`. The generic Plan
   Control journal schema is different and must not be used to rewrite FF6.
6. Query coordination, register this Claude session, inspect conflicts and
   leases, and claim exact task paths before writing. Preserve all unrelated
   state.

Do not reuse a Codex coordination token. If the outgoing Codex identity is
still `ACTIVE`, do not create a second writer on the same paths. Accept its
normal completion, or perform an audited stale-owner takeover only after
capturing and classifying the current filesystem state.

## Execute exactly this task

Resume `taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md` at `XLF-04` through its registered
authority-acquisition, SAL, family, research, contract,
capability-compiler, taskcard, and controller skills.

Do not reacquire XLIFF 2.0, rebuild XLF-03, or rewrite the seven batch-001
obligations unless their recorded inputs changed. First:

1. verify the event-23 source, test, matrix, Core inventory, and transcript
   SHA-256 values;
2. run `python -m pytest tests/tools/test_extract_sal_facts.py -q` and require
   23 passed;
3. rerun Ruff, strict Mypy, Pyright 1.1.411, and bytecode compilation;
4. validate `reports/ff6/xliff-authority-member-inventory.yaml` against both
   pinned ZIPs;
5. run matrix `--check` and require three byte-identical generations at
   `9f4ea4b8b71378217af26c0fb2b97a759817a0aca6c64255b8cd55170c60a090`;
6. verify three byte-identical Core-inventory generations at
   `d9c3fc4b9dd7002cc86ef0852864fb03acdc3be5fa4aead05efc15d39dfd11ff`;
7. add the `XLF-04-BATCH-002` RED tests for source-located
   identifier/reference/inheritance, language/direction/whitespace, and
   source-target correspondence obligations;
8. make only that bounded batch GREEN while retaining the seven batch-001 IDs;
9. keep `complete=false` until an explicit expected-obligation ID denominator
   is compiled and every ID is present. Category presence is never the
   completeness denominator.

The matrix acceptance count is 293/420 total DocBook `section` elements. The
197/312 figures are only the subsets with direct `id`/`xml:id` attributes;
sections without IDs remain evidence and receive deterministic title-path
locations. Treating 197/312 as the matrix denominator would lose normative
source coverage.

Preserve the existing tested compiler unless replay exposes a defect. Its 36
rows are source-surface anchors, not a complete semantic obligation inventory.
The seven batch-001 obligations are source-bound but unverified against
canonical SAL and are also not a complete inventory. Never satisfy XLF-04 by
relabeling anchors, counting XSD components, or counting covered categories.

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
- Before the Claude token budget becomes operationally unsafe, either finish
  the current RED/GREEN cycle and publish a resumable checkpoint or do not
  start another mutation cycle. Token pressure never permits a RED-only,
  unjournaled, or local-only handoff.
- Never ask for continuation. Continue safe unblocked work until a clean shift
  checkpoint is required.
- Treat the exact next action as deterministic but select its exact test name
  after inspecting the existing XLF-04 test namespace; record that name in the
  batch-002 RED receipt and next checkpoint. Do not invent a conflicting test ID.

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
