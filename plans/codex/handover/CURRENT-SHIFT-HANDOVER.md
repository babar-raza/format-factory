---
artifact_id: FF6-CURRENT-SHIFT-HANDOVER-7FC49C29
artifact_type: provider_neutral_shift_checkpoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Current Shift Handover

This document is the current provider-neutral continuation record for Claude,
Codex, or another governed executor. It records the clean GitLab checkpoint,
the concurrent dirty-worktree boundary, completed proof work, unresolved
state transitions, exact next decisions, and the validation needed before a
future agent can hand the same mission back without conversation memory.

The canonical repository, native FF6 event journal, controller, taskcards,
proof inputs, and coordination database override this derived document when
they have advanced. Never overwrite newer state to make it match this file.

## 1. Mission and terminal condition

Mission ID: `FF6-PRODUCTION-LIBRARIES-001`.

Build six independently publishable, professional Python libraries for:

- Jupyter Notebook;
- OpenRaster;
- NRRD;
- XLIFF;
- SafeTensors;
- OASIS UBL.

The terminal condition is not source presence or a passing focused suite.
Every library must have a complete authority-bound capability denominator,
production implementation, security/resource controls, independent
interoperability evidence, installed-wheel validation, cross-platform
coverage, reproducible release artifacts, SBOM, provenance, documentation,
and an independently computed certification. Current result: `0/6`.

## 2. Clean committed checkpoint

| Field | Value |
|---|---|
| Canonical forge | GitLab |
| Remote and branch | `origin/main` |
| Packet input checkpoint | `d5e8927a85ed0f2e8c68e1e061084c67b85363c9` |
| Latest bounded implementation checkpoint | `7fc49c290bdbfcb8c27bb8ca5c39f6f5576f242c` |
| Packet input commit | `docs(ff6): checkpoint UBL authority handover` |
| Remote verification | local `HEAD` and `origin/main` equal at capture |
| Controller state | `CONTRACT` |
| Native journal head | `FF6-EVENT-000026` |
| Event hash | `34b36bf5dc4344713ac1c0f026b30e6b15fb6a63b86f4876ee98230952fabcd0` |
| Canonical active task | `TC-FF6-XLIFF-PROFILE-SURFACE-001` |
| Exact canonical microstep | `XLF-04-BATCH-005` |
| Product certifications | `0/6` |
| Promotion state | all six `UNASSESSED` |

Commit `7fc49c29` is a valid bounded UBL evidence checkpoint. It is not a
native FF6 task-state transition. The journal remains at Event 26 and the UBL
taskcard remains `READY`; a future serialized plan-control event must record
the UBL-01 and UBL-02 evidence before the task projection can advance.

The packet input commit `d5e8927a` contains the previously validated handover.
It adds no product evidence. The commit containing this refresh must descend
from it and cannot embed its own final hash.

## 3. What this Codex shift achieved

The prior UBL package census at commit `7b5cce4f` already proved 890 package
members and exactly 91 document roots. This shift closed its stale authority
proof dependency:

1. Reproduced the stale `SRC-UBL-001` member-digest failure.
2. Added the negative control
   `test_stale_shared_target_cannot_overwrite_receipt_or_store`.
3. Revalidated the three prose assertions against the current pinned UBL 2.3
   prose bytes before changing any digest.
4. Updated only the stale prose target digest.
5. Replayed the UBL SAL receipt and promoted fact store.
6. Verified all 34 UBL facts through `validate_fact_promotion`.
7. Recompiled all six capability/obligation projections because their proof
   dependency closure changed.
8. Proved the generated scope was semantically unchanged after removing only
   `source_input_digests`, `direct_inputs`, and `invalidation_inputs`.
9. Committed exactly 20 owned paths and pushed only to GitLab `main`.
10. Preserved and excluded the active XLIFF worker's five dirty paths.
11. Reconciled the handover again from GitLab `main`, current coordination,
    the Event 26 journal, the UBL replay, and the foreign Batch 005 worktree.
12. Added a provider-shift contract that fixes the cross-provider transaction,
    Event 27 serialization, clean-checkpoint definition, and handback record.

Key evidence:

| Evidence | Result |
|---|---|
| UBL evidence manifest SHA-256 | `eb7db8167299ff9f547eb7909b1b67b7bc4ad24eb6dea9b43b4b2d9cfb405238` |
| UBL receipt SHA-256 | `2cc0f2cac163b7f42ab18bbe5220837d1f49a808904ac964c536085ca6d111a0` |
| UBL promoted store SHA-256 | `0de10d403fead08373c7a3e137ea3b7a84090b2adf24787bf066dc1dc24a3103` |
| UBL authority audit | `3 MATCH`, no missing/mismatch |
| UBL fact promotion | `34/34 PASS` |
| UBL package graph check | 890 members, 91 roots |
| Capability aggregate | `e199e84e9f7ee0579959db28283ecb89e014077cdd1605fbf0c82aee553d9960` |
| Capability three-run digest | `eafd6f8657ed83b73dbd5975046698d24fda6d8fd58c3d6aea962e6b6a85cf7c` |
| Verifier canonical receipt replay | three identical runs |
| Verifier tests | `13 passed` |
| Capability compiler tests | `22 passed` |
| UBL census tests | `12 passed` |
| Production-program regression | `69 passed` |
| Changed-test Ruff/Mypy/Pyright/py_compile | PASS |

The exact evidence receipts are:

- `reports/skills-rff6/skill-transcripts/test-driven-development-ubl-prose-closure-001.json`;
- `reports/skills-rff6/skill-transcripts/sal-pipeline-heal-ubl-prose-closure-001.json`;
- `reports/skills-rff6/skill-transcripts/compile-production-capability-universe-ubl-prose-closure-001.json`.

## 4. Current shared-worktree boundary

At handover creation, only these XLIFF paths were dirty:

```text
 M reports/ff6/xliff-core-authority-candidate-census.yaml
 M tests/tools/test_extract_sal_facts.py
 M tools/spec/extract_sal_facts.py
?? tests/tools/test_extract_sal_facts_candidate_binding.py
?? tools/spec/xliff_core_candidate_binding.py
```

They belong to coordination identity
`agent-codex-20260729T190440-e2dd38`, task
`TC-FF6-XLIFF-PROFILE-SURFACE-001`. Last captured heartbeat:
`2026-07-29T19:17:24.722412Z`; TTL: 7,200 seconds. The recorded process was
absent, but process absence does not invalidate an active lease.

These bytes are `ACTIVE_XLIFF_BATCH005_FOREIGN_WORKING_SET`, not a clean
checkpoint and not evidence of completion. Never stage, overwrite, restore,
delete, stash, or release them under a different provider identity.

At `2026-07-29T20:17:53Z`, the coordination plane still reported that identity
and its eleven exact leases as `ACTIVE`; Git showed the same five dirty paths.
The wider coordination status returned exit 1 with 17 open conflicts. One
relevant preserved conflict is
`.local/transcripts/ubl-prose-closure-001.json`; it is local transcript state,
not a reason to invalidate the committed UBL evidence or touch the file.

## 5. Why reruns were inconsistent

### Symptoms

- Old PASS receipts survived after authority bytes or manifests changed.
- Generated capability projections changed widely after a small UBL proof
  repair.
- Status and taskcards lagged behind independently committed evidence.
- Shared mutable outputs appeared between test discovery and execution.
- Source/test presence was easy to mistake for production completion.
- Provider shifts risked inheriting tokens, leases, or uncommitted bytes.

### Root causes

- Proof results did not always bind the complete dependency closure.
- Status, ledgers, reports, and taskcards were competing partial authorities.
- Generated obligations repeat global invalidation inputs, so one authority
  acquisition legitimately invalidates several format projections.
- The native event journal serializes task state, while safe path-disjoint
  implementation can be committed in parallel; without an explicit follow-up
  event, evidence and projection temporarily diverge.
- Certification has not yet moved to immutable clean worktrees/containers
  with built-wheel imports and content-addressed fixtures.

### Structural weaknesses that remain

- The canonical ProductContract/proof graph/invalidation machinery is not yet
  the sole runtime authority.
- UBL task-state projection cannot represent the verified parallel checkpoint
  until a serialized event is appended.
- Strict Mypy following imports reports five pre-existing typing defects in
  `tools/spec/verify_sal_facts.py`.
- The XLIFF batch is local and live-leased, not remotely checkpointed.
- The known stateful CSV idempotency test can mutate tracked projections on a
  second run.
- Five product packages are partial and OpenRaster has no product package.
- No format has complete installed-wheel, oracle, corpus, cross-platform,
  fuzz, mutation, performance, reproducible-build, or release proof.

## 6. What to preserve and what to redesign

Preserve:

- GitLab `origin/main` and the hash-chained FF6 event history;
- all current authority bytes and SHA-256 bindings;
- the 110-capability/672-obligation denominator;
- the current XLIFF Batch 005 bytes until their owner commits or a governed
  takeover recaptures them;
- the UBL census, current 34-fact receipt, and dependency-closure projections;
- existing product behavior until characterization tests make migration safe;
- exact-path coordination and explicit-file staging.

Redesign or complete:

- one ProductContract and content-addressed proof graph as the sole computed
  readiness authority;
- descendant invalidation on every authority, contract, source, test, fixture,
  environment, lock, and generator change;
- isolated certification against installed wheels;
- complete format-specific schema/capability denominators;
- production package layers, public APIs, typing, docs, security, corpus,
  oracles, fuzzing, mutation, performance, and release artifacts.

## 7. Exact resume algorithm

The incoming agent must execute this algorithm, not select work from prose:

1. Fetch GitLab and read the current journal/controller/taskcards.
2. Run the handover validator.
3. Query coordination and classify every dirty path.
4. If Event 27 or later exists, rebuild from that event and ignore this
   document's task selection.
5. If XLIFF Batch 005 has been committed without a new event, independently
   validate its immutable commit and append one serialized event. Do not
   reimplement it.
6. If the XLIFF lease is still active, do not touch its files. The UBL
   authority repair is already complete; do not repeat it. The first safe
   path-disjoint action is a single Event 27 plan-control checkpoint that
   binds UBL-01/UBL-02 while preserving XLIFF as the active task.
7. If the XLIFF lease is stale and no newer commit exists, use governed
   `takeover --reason`, recapture every current file baseline, rerun the RED
   tests, and continue `XLF-04-BATCH-005`.
8. If no owner or dirty bytes exist and no newer commit exists, start
   `XLF-04-BATCH-005` from the Event 26 checkpoint.
9. After XLIFF reaches a bounded verified implementation commit, append one
   native event, refresh projections, push, then refresh this handover.
10. Under the next serialized plan-control window, record the already
    committed UBL-01 authority and UBL-02 census evidence. Only then advance
    the UBL taskcard through `AUTHORITY_REVALIDATED` and
    `PACKAGE_CENSUS_COMPLETE`; the first UBL implementation step after that is
    UBL-03, the complete reachable schema graph.

The Event 27 checkpoint writes the hash-chained journal first, then the
controller, UBL taskcard, task index, and refreshed handover. Its task
projection is `READY -> WORK_IN_PROGRESS`, completed steps are `UBL-01` and
`UBL-02`, first unmet step is `UBL-03`, and its promotion effect is `none`.
The controller active task and exact action remain XLIFF Batch 005. See
`PROVIDER-SHIFT-CONTRACT.md` and `PARALLEL-UBL-CHECKPOINT.yaml`.

## 8. Exact commands for the incoming shift

Run from:

```text
C:\Users\prora\OneDrive\Documents\GitHub\format-factory
```

```powershell
git fetch origin main
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor d5e8927a85ed0f2e8c68e1e061084c67b85363c9 origin/main
git merge-base --is-ancestor 7fc49c290bdbfcb8c27bb8ca5c39f6f5576f242c origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --self-test
.venv\Scripts\python.exe -m tools.supervisor.coordination status
```

Then read, in order:

1. `AGENTS.md`;
2. `plans/codex/handover/START-HERE.md`;
3. `plans/codex/handover/PROVIDER-SHIFT-CONTRACT.md`;
4. this file;
5. `plans/strategic/ff6/product-goal.yaml`;
6. `plans/strategic/autonomous-six-python-production-execution-plan.md`;
7. `plans/strategic/ff6/events.jsonl`;
8. `plans/strategic/ff6/controller-state.yaml`;
9. `plans/strategic/ff6/current-gaps.yaml`;
10. `taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md`;
11. `taskcards/TC-FF6-UBL-TYPING-001.md`;
12. `plans/codex/handover/PARALLEL-UBL-CHECKPOINT.yaml`.

For Codex, also read `docs/governance/codex-adapter.md`. Claude follows its
ambient hooks plus the same coordination contract.

## 9. XLIFF Batch 005 acceptance boundary

Do not reduce Batch 005 to a prompt tweak. It must:

- reject forged normalized text, member/source digests, and locations;
- assign an explicit semantic class and content-sensitive occurrence digest;
- classify all non-modal Core prose;
- replace all 78 coarse structural fallbacks;
- expand the expected denominator when authority requires it;
- preserve the identity and meaning of the 25 existing rows;
- compile source-bound obligations for every resolved expected ID;
- keep `complete: false` until the entire Core authority surface closes;
- rerun focused, format-contract, production-program, static, deterministic,
  authority, and transcript validation.

The detailed RED/GREEN commands remain in `CLAUDE-START.md`.

## 10. UBL next phase after serialization

UBL-03 must compile a complete reachable graph for every global element,
attribute, complex/simple/anonymous type, compositor, group, extension,
restriction, substitution, reference, cardinality, facet, wildcard,
namespace, and documentation node reachable from all 91 roots.

The graph must be:

- derived only from pinned `SRC-UBL-002` package bytes;
- network-independent;
- content-addressed and deterministic;
- cycle-safe and reference-complete;
- negative-tested for missing/foreign/ambiguous imports and unresolved QNames;
- independent of the existing shallow product classes.

Do not start Python generation until UBL-03 through UBL-07 are complete and
the taskcard reaches the required state.

## 11. Checkpoint and handback protocol

Every provider shift must end at one of two explicit states:

`RESUMABLE`

- owned implementation is verified;
- exact files are committed and pushed to GitLab main;
- any required native event is appended and projections agree;
- all owned leases are completed/released;
- the handover is refreshed, hash-bound, and validated.

`RECOVERY_REQUIRED`

- local owned work is RED/GREEN or otherwise incomplete;
- exact paths, digests, tests, owner, lease state, and next command are
  recorded;
- bytes are preserved but not described as a clean checkpoint.

Never call an uncommitted or unjournaled state `RESUMABLE`. Never transfer an
agent token as authority. The next agent always registers a new identity and
recomputes current state.

## 12. Mandatory regression controls

- Delete/rename a test and prove its obligation evidence is revoked.
- Modify a fixture and prove old proof cannot be reused.
- Change each input category and prove correct descendant invalidation.
- Run three identical generations and compare canonical bytes.
- Build and test installed wheels, never accidental source imports.
- Test concurrent formats in separate worktrees/environments/artifact roots.
- Prove manual status edits cannot override computed readiness.
- Prove repository extraction preserves canonical source/package digests.
- Keep strict negative tests for path traversal, archive bombs, entity
  expansion, overlap/offset corruption, invalid namespaces, and resource
  exhaustion as applicable per format.

## 13. Honest limits and risks

- OpenRaster's early draft authority permits an interoperability
  certification, not universal conformance.
- XLIFF all-module processing semantics and UBL's complete generated schema
  family are large, high-risk denominators.
- External implementations can disagree; contradictions require a
  discriminating test and primary-authority analysis.
- Some release actions may remain externally blocked by credentials or
  business Gate 10/11 authority, but all technical artifacts must still be
  completed.
- The current handover proves continuity and bounded UBL evidence only. It
  does not prove any production library ready for publication.

## 14. Forbidden actions

- no `git add .` or `git add -A`;
- no reset, clean, restore, checkout, broad stash, or deletion of unexplained
  work;
- no GitHub execution branch or non-main product branch;
- no mutation under another agent's lease;
- no manual promotion/status edit;
- no reuse of stale receipt as current proof;
- no product-source generation before its task state and gates authorize it;
- no claim of production readiness from counts, files, smoke tests, or local
  source imports.

## 15. Completion self-challenge for every future shift

Before reporting a checkpoint, answer:

1. Did I fetch and inspect GitLab `origin/main`?
2. Did I validate the native event chain?
3. Did I classify every dirty path?
4. Did I preserve foreign and unexplained bytes?
5. Did I use a new coordination identity and exact leases?
6. Did every write have a registered skill, manifest, guard, preflight, and
   write receipt?
7. Did I operate only on the controller-selected or explicitly path-disjoint
   safe task?
8. Did I bind evidence to current authority/source/test/fixture/tool/
   environment inputs?
9. Did I run a discriminating negative control?
10. Did I run the required focused and regression suites?
11. Did deterministic generation pass three times?
12. Did I avoid source-tree/import confusion?
13. Did I avoid manual gate, certification, or promotion claims?
14. Did I stage only an explicit reviewed file list?
15. Did I push only to GitLab main after ancestry verification?
16. Did I append no duplicate native event?
17. Did controller, taskcard, gap, proof, and handover projections agree?
18. Did I record every failure honestly, including inherited failures?
19. Is the shift truly `RESUMABLE`, or have I labeled it
    `RECOVERY_REQUIRED`?
20. Can the next provider resume without chat memory, tokens, or assumptions?

If any required answer is no, do not claim clean completion.
