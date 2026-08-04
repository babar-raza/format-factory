---
artifact_id: FF6-EXECUTION-RECOVERY-PLAN-HARDENING-20260803
artifact_type: plan_hardening_report
visibility: generated
publish_allowed: false
generated_by: codex
generated_at: 2026-08-03
goal_id: FF6-PRODUCTION-LIBRARIES-001
plan_version: 7
recovery_directive_revision: 1
status: PASS_FOR_INDEPENDENT_REVIEW_NOT_EXECUTION_PROOF
---

# FF6 Execution-Recovery Plan Hardening Report

## Verdict

`PASS_FOR_INDEPENDENT_REVIEW_NOT_EXECUTION_PROOF`, 22/22 bounded-plan criteria.

The revised route is materially safer and faster than the unamended version-7
route because it removes speculative supervisor construction and full-tree
classification from the product critical path while keeping the final
production/certification bar. This report does not prove that Stage 1 works, any
product obligation moved, or any library is closer to certification through
executed behavior. The review ZIP is evidence of planning completeness only.

## Current truth verified for this amendment

- Local `main`, `HEAD`, and `origin/main` were
  `0fa7b2bde542e71fc4b668fc2c317d81937f1e50` before planning edits.
- The native event journal still ends at `FF6-EVENT-000047`; neither
  `plans/strategic/ff6/events.jsonl` nor `controller-state.yaml` changed.
- Capability/obligation truth remains 110/689 and technical certification 0/6.
- NRRD's accepted R2 projection remains 17 implemented, 39 partial, 6 missing,
  3 preservation-only, and 48 unresolved out of 65.
- OpenRaster product source remains absent.
- Product `src/**` and `tests/**` were not modified by this planning sprint.
- The shared worktree had pre-existing plan-v7 changes. They were preserved and
  amended in place; no reset, stash, restore, clean, branch, commit, or push was
  used.

## Symptoms, root causes, and structural weaknesses

### Symptoms

1. Six technical product states remain `UNASSESSED` and 0/6 certified despite a
   large and growing planning/control surface.
2. The accepted Event-47 continuation required broad NRRD R3 corpus/oracle work
   before a source slice, even though the exact R2 projection already exposes
   48 unresolved obligations.
3. Version 7 proposed a full supervisor review and runtime implementation ahead
   of a tangible product delivery batch.
4. IPYNB, SafeTensors, and OpenRaster readiness cards required whole-product
   inventories before the first source changes.

### Root causes verified in current code

1. `tools/supervisor/product_action_guard.py` lines 62-78 and 125-138 use a
   hard-coded `ALLOWED_PRODUCT_SOURCE_PATCH_PATHS` list that omits all six FF6
   roots and is not bound to a live taskcard digest or exact owned paths.
2. `tools/supervisor/action_queue.py` lines 1-23 declares a durable JSONL queue;
   `_load_queue`/`_save_queue` rewrite the file, and enqueue/dequeue are not an
   atomic multi-process claim transaction with attempt/lease/heartbeat history.
3. `tools/supervisor/autonomous_orchestrator.py` initializes with
   `max_cycles=3` and `stop_after_idle=1` at lines 203-225. These are execution
   termination defaults, not evidence-derived true-block conditions.
4. Candidate author, validator, and integration roles are described by plans but
   are not yet proved end to end for an FF6 product card.

### Structural weaknesses

1. Abstraction preceded observation: the six-lane runtime tried to model all
   product coordination before two production slices demonstrated shared needs.
2. Plan/report work could recursively create more prerequisites without moving
   source behavior or executed proof.
3. Verification cadence was too broad for routine slices, encouraging repeated
   full reports and matrices instead of risk-proportionate feedback.
4. Continuation could stop because a configured cycle/idle limit was reached,
   not because work was genuinely unsafe or externally blocked.

## What is preserved

- The canonical production goal: six independently publishable, professionally
  structured Python libraries with comprehensive format-specific capabilities.
- All 110 capabilities, 689 obligations, authority digests, profile boundaries,
  proof invalidation rules, negative evidence, independent interoperability,
  installed-wheel isolation, security, static quality, documentation, fuzz,
  mutation, performance, cross-platform, reproducibility, SBOM, provenance,
  signature, and release requirements.
- GitLab `origin/main` as the only integration authority and main as the only
  branch target.
- Existing working product behavior, current source/test changes, controller
  journal, historical gaps, and old supervisor cards as audit records.
- Fail-closed controller, registry, promotion, release, other-format, and
  undeclared same-format path protection.
- Independent validation and serialized integration; authors cannot validate or
  integrate their own candidate.

## What is redesigned

- Full supervisor first becomes minimal demonstrated control repair first.
- Full NRRD R3/R4 prerequisite becomes slice-required Teem/pynrrd inputs plus a
  three-obligation raw scalar integrity slice.
- Full SafeTensors readiness becomes an eight-obligation header/layout/writer/
  lazy-access reference slice.
- Full source classification becomes a certification-milestone activity;
  implementation inspects only the selected slice's dependency closure.
- Default four-writer target becomes two writers, one prep worker, one validator,
  and one serialized integrator. Growth to three requires two clean disjoint
  integrations; four is not a target.
- Default cycle termination becomes `UNTIL_BLOCKED` with obligation-scoped
  repeated-root-cause blocking and continued disjoint work.
- Shared machinery may be extracted only after NRRD and SafeTensors evidence
  demonstrates repetition.

## Exact execution route after ZIP review

1. `TC-FF6-EXECUTION-RECOVERY-001`: reproduce and repair only taskcard-bound
   path authorization, transactional claim/attempt/lease state, real
   continuation, and a disposable end-to-end FF6 canary. It is incomplete
   unless it selects the exact NRRD golden slice.
2. `TC-FF6-NRRD-GOLDEN-SLICE-001`: close the three declared obligations with
   RED-to-GREEN tests, Teem/pynrrd evidence, installed-wheel proof, affected
   regression/static checks, independent validation, and one bounded candidate.
3. `TC-FF6-SAFETENSORS-REFERENCE-SLICE-001`: close the eight declared
   obligations against the pinned official implementation and prove lazy mmap/
   bounded allocation through installed wheels.
4. Compare both receipts. Extract only repeated shared behavior or record
   `STAGE_4_NOT_NEEDED`.
5. Continue IPYNB, XLIFF, UBL, and OpenRaster coherent vertical slices, then
   complete per-format certification graphs.

## 22-item hardening score

| # | Result | Evidence |
|---|---|---|
| 1 exact scope | YES | Machine directive defines one planning package and first three taskcards. |
| 2 current repo state | YES | Git/controller/product truth recorded with non-claims. |
| 3 referenced files inspected | YES | Bounded recovery references, guard, queue, orchestrator, continuation, obligation rows, source layouts, governance, skills, and predecessor cards were inspected. Later format implementation details remain future task inputs, not assumptions in Stage 1-3. |
| 4 facts vs assumptions | YES | Verified code facts are line-bound; future behavior is labelled required design. |
| 5 stale state | YES | Event 47 remains authority; plan-v7 supervisor target is explicitly non-implemented. |
| 6 contradictions | YES | Broad strategic healing remains final quality context; operator recovery directive controls FF6 execution order only. |
| 7 allowed paths | YES | Each of the first three taskcards has an exact writable path list. |
| 8 forbidden paths | YES | Product/control/global boundaries are explicit per stage. |
| 9 stream ownership | YES | Planning-only files are separated from future control and product packages. |
| 10 validation commands | YES | Stage 1, NRRD, and SafeTensors cards name exact focused/static/build commands and installed-use requirements. |
| 11 evidence outputs | YES | Contract, receipts, local evidence root, review ZIP, and required metadata are defined. |
| 12 taskcard updates | YES | Six predecessor dispositions and three exact successor cards are indexed. |
| 13 current-state update | YES | Master plan Section 111 and machine directive record planned/not-started truth; native event/state is intentionally unchanged. |
| 14 stop conditions | YES | True external/unsafe/spec contradiction/human gate/repeated-root-cause conditions are enumerated. |
| 15 final statuses | YES | State machine and task statuses distinguish review, blocked, accepted, and terminal states. |
| 16 no broad cleanup | YES | No stash/reset/restore/clean; preservation is binding. |
| 17 gaps preserved | YES | Remaining obligations stay in the current projection; old cards are superseded, not erased or called complete. |
| 18 autonomous feasible work | YES | `UNTIL_BLOCKED` continuation and disjoint-lane release remove routine human pauses. |
| 19 product-source authority | YES | Stage 1 forbids product mutation; exact Stage 2/3 cards own future source paths after prerequisites. |
| 20 no LLM/embedding misuse | YES | LLM output is planning only and cannot be proof; no vector/embedding work is authorized. |
| 21 final ZIP path | YES | Final response must print the absolute validated review ZIP path. |
| 22 self-challenge | YES | Twenty questions below are answered. |

## Self-challenge

1. Did this planning sprint move a product obligation? **No.**
2. Did it change certification from 0/6? **No.**
3. Did it append or imply Event 48? **No.**
4. Did it remove any final quality gate? **No.**
5. Can Stage 1 expand into a full supervisor? **No; exact paths and forbidden
   expansion prevent that.**
6. Is Stage 1 complete merely when tests pass? **No; it must select and
   authorize the exact NRRD card through the end-to-end canary.**
7. Can taskcard path authorization broaden with a glob or format root inferred
   from a name? **No; exact owned paths and deliberate directory entries only.**
8. Can a product lane edit controller, registry, promotion, or release state?
   **No.**
9. Can an author validate or integrate their own candidate? **No.**
10. Can synthetic NRRD/SafeTensors inputs be the sole interoperability proof?
    **No.**
11. Can a full readiness report be inserted before the NRRD slice? **No.**
12. Can unrelated obligations receive credit from a passing full suite? **No.**
13. Does SafeTensors begin before NRRD acceptance? **No, except if the NRRD
    obligation group is properly blocked while the shared execution path is
    independently safe.**
14. Must Stage 4 exist? **No; record `STAGE_4_NOT_NEEDED` if two slices do not
    prove meaningful repetition.**
15. Does the WIP target four writers? **No; two initially, three only after two
    clean disjoint integrations.**
16. Does an idle queue automatically terminate the mission? **No; idle must be
    classified and only a true blocked state can stop the applicable route.**
17. Can repeated-root-cause blocking stop all six formats? **No; it is scoped to
    the affected obligation/root cause.**
18. Were user/unrelated worktree changes cleaned or hidden? **No.**
19. Is this plan certain to reach production unchanged? **No.** Evidence from
    the first two slices may require bounded amendments, but it cannot lower the
    certification contract or restore speculative machinery.
20. What remains uncertain? **The exact amount of control code repair, oracle
    tool availability, actual RED failures in product slices, and whether shared
    extraction is worthwhile. Each has a discriminating test and stop/continue
    policy.**

## Independent reviewer instructions

Review the ZIP from the operator directive outward. Verify hashes and current
Git/controller truth, reproduce the three control defects, and challenge exact
taskcard path/obligation coverage. Reject the plan if Stage 1 can complete
without unlocking NRRD, if the hard-coded allowlist is replaced by a permissive
format-root rule, if the transactional store becomes evidence authority, if
author/validator roles can coincide, or if final production gates were weakened.

Permitted verdicts are `ACCEPT_EXECUTION_RECOVERY_ROUTE`,
`ACCEPT_WITH_BOUNDED_PRE_STAGE1_REPAIRS`, or `REJECT_WITH_EXACT_COUNTEREVIDENCE`.
Do not approve product certification or publication from this package.
