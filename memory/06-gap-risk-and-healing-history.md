---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run013
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# 06 — Gap, Risk, and Healing History

## Standing open gaps before Phase 1

| ID | Gap | Why it matters | Status |
|---|---|---|---|
| G-001 | Latest evidence bundle must be inspected before next step | Prevents acting on bad summaries | **RESOLVED run015** — Phase 0 accepted by human; bundles inspected |
| G-002 | Phase 0 acceptance not formally recorded | Phase 1 cannot start | **RESOLVED run015** — Phase 0 formally accepted; baseline commit made |
| G-003 | Command/skill format not finalized | Commands needed for consistency | Phase 1 TC-0004 |
| G-004 | LLM endpoint discovery not implemented | Needed before LLM-assisted evidence work | Phase 1 TC-0005 |
| G-005 | Model selection policy not implemented | Needed before local/remote model use | Phase 1 TC-0005 |
| G-006 | Artifact index bootstrap not fully implemented | Needed for reuse automation | Phase 1 TC-0005 |
| G-007 | Visibility validation tooling not implemented | Needed before later gates/releases | TC-0006 |
| G-008 | Release manifest generator not built | Needed before Gate 10 release | TC-0006 |
| G-009 | Reuse/cache invalidation tooling not implemented | Needed for reruns | TC-0005/TC-0007 |
| G-010 | Prompt/response retention policy needs refinement | Needed before first LLM API call | TC-0005 |
| G-011 | Master-plan reproduction command not implemented | Needed for automated plan check | TC-0004 |
| G-012 | Neutral schema language not finalized | Blocks Gate 5 | TC-0002 |
| G-013 | SDK baseline not verified on machine | Blocks later product source | TC-0003 |
| G-014 | Commercial repo isolation deferred | Blocks commercial source | DD3 before commercial implementation |
| G-015 | Test framework not selected | Blocks Phase 4 tests | Later taskcard |
| G-016 | Version/release cadence not defined | Blocks release | Later taskcard |
| G-017 | Spec-cache tooling not implemented | Needed for systematic spec acquisition | TC-0007 |
| G-018 | Spec-cache index schema not implemented | Needed for cached spec reuse | TC-0007 |
| G-019 | Standards redistribution policy needs per-source validation | Needed before committing specs | Gate 2 and TC-0007 |
| G-020 | ~~Product source layout not yet propagated to master-plan.md~~ | ~~Blocks run011 and any src/ folder creation~~ | **RESOLVED run011**: src/net/{format}/ and src/python/{format}/ propagated to master-plan.md v2.8; verified in run013. |
| G-021 | .NET FOSS packaging model not resolved (.NET OSS vs. commercial only) | Blocks source layout finalization | run011 or Phase 1 planning |
| G-022 | docs/architecture.md does not reference /memory | Low — clarity gap | Phase 1 docs update |
| G-023 | /sync-memory command not implemented (TC-0008 planned only) | Memory consistency automation unavailable | TC-0008 Phase 1 implementation |

## Healing gaps found through bundle review

| ID | Problem | Status |
|---|---|---|
| G-HEAL-001 | run001 bundle missed required audit files | Resolved run002 |
| G-HEAL-002 | run001 bundle contained malformed `ocal/` path | Resolved run002 |
| G-HEAL-003 | Phase 0 files lacked visibility-classification consistency | Resolved run002 with hybrid policy |
| G-HEAL-004 | `.claude/settings.json` permitted broad future-phase writes | Resolved run002 |
| G-HEAL-005 | Phase 1 boundary ambiguity allowed `acquisition-packs/fods/` too early | Resolved run005/run006 |
| G-HEAL-006 | Scoring model contained FODS pre-score estimate | Resolved run005/run006/run008 |
| G-HEAL-007 | Master plan still listed acquisition pack as allowed from Gate 1 | Resolved run006 |
| G-HEAL-008 | Master plan still had FODS numeric pre-score | Resolved run006/run008 |
| G-HEAL-009 | Product implementation gate semantics ambiguous | Resolved run007 |
| G-HEAL-010 | Historical healing text still contained pre-score references and commercial folder annotations | Resolved run008 |
| G-HEAL-011 | TC-0007 was FODS-specific; spec-cache is generic tooling | Resolved run009 (TC-0007 corrected) |
| G-HEAL-012 | Spec-cache had no authorization model; agents could self-authorize downloads | Resolved run009 (stop-log-gap model added) |
| G-HEAL-013 | AGENTS.md had no /memory guidance; agents had no rule for memory usage | Resolved run010 (Section U added) |
| G-HEAL-014 | AGENTS.md had duplicate Section Q and P1-P4 internal IDs in Security Rules | Resolved run010 (sections renumbered Q→R, R→S, S→T; IDs corrected) |
| G-HEAL-015 | /memory files (03, 09, 07, 10, 00-index) still showed "pending propagation" for source layout after run011 had completed | Resolved run013 (stale notes removed; propagation status recorded) |
| G-HEAL-016 | Agent review items lacked independent verification before being presented for human approval | Resolved run016 (DEC-034 added; AGENTS.md Section V; GOVERNANCE.md Section 15 — independent verification sprint required before any human review request) |
| G-HEAL-017 | Gate 1 approval pending (FODS 93/100, Accept band, all pre-conditions met) | **RESOLVED run017** — Gate 1 approved by Babar Raza (2026-05-04); registry updated; TC-0001 closed; acquisition-packs/fods/ skeleton created; TC-0009 created |

## Major risks

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| R-001 | Agent drift | High | AGENTS.md, forbidden path checks, bundles |
| R-002 | Agent summary overstates completion | High | Always inspect bundle |
| R-003 | Master plan becomes stale | High | update at phase/gate/task changes |
| R-004 | Evidence bundle incomplete | High | strict bundle manifest |
| R-005 | Raw `.local/` or malformed path leaks into bundle | High | clean staging layout |
| R-006 | Secrets leak | Critical | `.env` ignored, secrets scan |
| R-007 | LLM prompts leak private/commercial/spec text | High | local-only cache, remote limits |
| R-008 | Visibility classification inconsistent | High | release-control doc, validation later |
| R-009 | Stale artifacts reused | High | source hashes, stale flags |
| R-010 | Product code starts too early | Critical | gate and explicit prompt model |
| R-011 | Commercial code leaks into OSS | Critical | folder deferral, boundary checks |
| R-012 | Legal review rubber-stamped | High | legal categories, Gate 2 rationale |
| R-013 | Oracle treated as truth | High | spec is authority policy |
| R-014 | Specs committed illegally | Critical | spec-cache local-only default |
| R-015 | Stale specs reused | High | spec-cache hash/version/ETag checks |
| R-016 | Paid/restricted standards fetched improperly | High | metadata only unless legal/human approval |
| R-017 | Agent self-authorizes spec download without prompt authorization | Critical | run009 stop-log-gap model; T-series rules in AGENTS.md |
| R-018 | Agent creates src/ folders using obsolete layout before run011 updates master plan | High | No source folder creation until master-plan.md explicitly authorizes layout |
| R-019 | Agent over-trusts stale /memory content and ignores contradictions with master-plan.md | High | AGENTS.md Section U5 contradiction rule; must log gap and wait for human resolution |
| R-020 | /memory diverges from master-plan.md after Phase 1 begins; agents receive conflicting signals | Medium | AGENTS.md Section U6 maintenance triggers; memory-sync run after major events |
| R-021 | Secrets, raw prompts, or copyrighted spec text stored in /memory | High | AGENTS.md Section U7 and GOVERNANCE.md 1.2a prohibit this |
| R-022 | run009 and run010 contradictions not reconciled before Phase 1 | High | run011 must reconcile; run012 captured pending items |

## Lesson from Phase 0

Every agent summary must be verified. Multiple runs claimed completion while contradictions remained. The correct workflow is evidence-first: inspect files, search for contradictions, then decide next prompt.
