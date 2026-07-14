# External Engineering Skill Adoption — Amendment Spec

authoritative_plan: plans/.claude/yes-my-earlier-answer-humming-waffle.md
artifact_role: execution_plan
execution_authority: true

**Format note (single-file constraint):** Plan-mode tooling permits editing only this one file. The micro-taskcardization framework applied below normally spans ~46 separate supporting artifacts (preflight reports, DAGs, traceability matrices, etc.). Every one of those is instead a labeled section *inside* this file, each internally tagged `artifact_role: analysis_or_evidence_only, execution_authority: false` where it is not itself an executable taskcard. This is a stricter reading of the framework's own Single-Plan-Authority rule, not a deviation from it.

---

## 0. Context (preserved analysis — do not flatten)

Format Factory has 150+ domain-specific skills but zero general software-engineering methodology skills — no debugging technique, no TDD discipline, no CI-repair workflow, no independent code-quality reviewers, no skill-security scanner for the very external skills this plan imports. This plan started as an import list for that gap. Successive rounds of research expanded it into a full audit of the skill portfolio's own health, because "does a skill exist and is it findable/maintained?" applies as much to Format Factory's 149 existing skills as to anything being imported — and then further into resolving two real, previously-mistracked governance gaps discovered along the way.

**This is an amendment, not a new plan.** It executes an existing, never-run governance process:
- [docs/governance/external-tool-architecture.md](docs/governance/external-tool-architecture.md) "Tool 2: Superpowers Marketplace" (lines 49–77) — placement, prohibitions, 9-step normalization, risk register.
- [docs/governance/superpowers-skill-intake.md](docs/governance/superpowers-skill-intake.md) — Review → Risk Classify → Local Wrapper → Registry Entry → Activation Gate.

Neither has ever been invoked (`superpowers_origin` appears zero times in `.supervisor/skill-registry.yaml`).

**Plan authority resolution:** `plans\.claude\production-portfolio-master-plan.md` and its strategic-folder counterpart are scope-locked to an unrelated 41-legacy-plan reconciliation and explicitly forbid new competing plan content (§3.6). The correct insertion point is **`plans/master-plan.md`, new `## Section 100`**. Per `CLAUDE.md` Step 0, this file is copied to `plans/.claude/yes-my-earlier-answer-humming-waffle.md` and locked on approval; Section 100 references that path (TC-EXT-000-03).

**Corrections made this session** (verified by direct WebFetch/GitHub-API inspection, catching two hallucinations from earlier in this conversation): "OpenAI's plugin collection includes Superpowers" is false — Superpowers is `obra/superpowers`, MIT, unaffiliated with OpenAI. A claimed "evaluate-skill/improve-skill" repo does not exist under that name — the closest real analog is `wshobson/agents`' `plugin-eval` (community, MIT). The Anthropic "PR Review Toolkit" (6 reviewers) lives in `anthropics/claude-code`, not `anthropics/skills` as first stated.

---

## 1. Preflight & Authority Verdict

artifact_role: analysis_or_evidence_only | execution_authority: false

```yaml
preflight:
  repo_path: c:\Users\prora\OneDrive\Documents\GitHub\format-factory
  branch: main
  head_commit: c8b135a185ad31323ee838a2155ff37ff9acdb6e
  working_tree_dirty_entries: 642        # pre-existing, unrelated to this plan — not touched by it
  duplicate_plan_risk:
    candidates_considered:
      - plans/.claude/production-portfolio-master-plan.md   # scope-locked to 41-plan reconciliation, §3.6 forbids new content — REJECTED as target
      - plans/strategic/41 plans/PRODUCTION-PORTFOLIO-MASTER-PLAN.md  # template/methodology doc for the same closed effort — REJECTED
      - plans/master-plan.md   # ACCEPTED — new Section 100, following its own §N convention
    verdict: single_authoritative_target_confirmed
  active_plan_authority_verdict: plans/master-plan.md Section 100, seeded from this file
  plan_format: markdown, hierarchical taskcards embedded (this document)
  plan_size_before_this_pass: 291 lines
  major_sections_before_this_pass: 2 (Part 1 Findings, Part 2 Crosswalk) + flat 28-row taskcard table
  existing_taskcard_format_in_repo: TC-<AREA>-<NNN>, flat, no parent/child/micro-step hierarchy anywhere in Format Factory's existing taskcard system (plans/layers/task-register.yaml uses the same flat convention)
  existing_state_vocabulary_in_repo: CLOSED / NOT_STARTED / IN_PROGRESS / PARTIALLY_DONE / BLOCKED (per plans/layers/*, CLAUDE.md classifications) — this plan's PROPOSED/READY/.../CLOSED vocabulary is additive, not conflicting; taskcards close by setting the SAME repo-standard status fields once this plan's own gates pass
  existing_evidence_model_in_repo: .local/evidences/<run_id>/evidence-declaration.yaml + skill invocation transcripts — this plan's evidence contract (§3) reuses that exact model rather than inventing a new one
```

---

## 2. Requirement Inventory

artifact_role: analysis_or_evidence_only | execution_authority: false

Every parent taskcard traces to exactly one requirement below, each traced to its source Finding/Group in the preserved analysis (§8).

| REQ ID | Statement | Source |
|---|---|---|
| REQ-EXT-000 | Fix stale plan cross-references; establish Section 100 | Context |
| REQ-EXT-001 | Pin provenance/license for all imported external sources | Governance Compliance §9 |
| REQ-EXT-003 | Close HO-007 as already-satisfied | Finding 1 |
| REQ-EXT-004 | Correct master.md's own layer-count inconsistency | Finding 2 |
| REQ-EXT-005 | Build permanent layer↔skill attribution sync mechanism | Finding 2 |
| REQ-EXT-006 | Backfill 90 unattributed skills | Finding 2 |
| REQ-EXT-007 | Reconcile 5 divergent skill-count numbers + minor drift | Finding 2, 8 |
| REQ-EXT-008 | Register gaps for 6 genuinely zero-coverage layers | Finding 3 |
| REQ-EXT-009 | Resolve SKILL-GAP-003 (capability_compiler/L14) | Finding 6 |
| REQ-EXT-010 | Resolve SKILL-GAP-008 (pre_sprint_governance_hook) | Finding 7 |
| REQ-EXT-012 | Import skill-scanner as the gating security scanner | Group 5 |
| REQ-EXT-013 | Import systematic-debugging | Group 0 |
| REQ-EXT-014 | Import test-driven-development | Group 0 |
| REQ-EXT-015 | Merge verification-before-completion + differential-review | Group 0, 3 |
| REQ-EXT-016 | Import receiving-code-review | Group 0 |
| REQ-EXT-017 | Import 5 read-only reviewers | Group 2 |
| REQ-EXT-018 | Import property-based-testing | Group 3 |
| REQ-EXT-019 | Merge modern-python + impediment-prioritization | Group 2, 7 |
| REQ-EXT-020 | Build gh-fix-ci (FF-original) | Group 9 |
| REQ-EXT-021 | Build gh-address-comments (FF-original) | Group 9 |
| REQ-EXT-022 | Build create-ff-skill, absorbing 3 authoring methodologies | Group 6 |
| REQ-EXT-023 | Import skill-improver | Group 6 |
| REQ-EXT-024 | Import gha-security-review + agent-supply-chain | Group 5 |
| REQ-EXT-025 | Import agent-owasp-compliance, audit-context-building, trailmark | Group 5, Finding 4 |
| REQ-EXT-026 | Import mcp-builder | Group 6 |
| REQ-EXT-027 | Import dependabot-inspired skill | Group 8 |
| REQ-EXT-028 | Import github-release | Group 8 |

---

## 3. Shared Machine State (applies to every taskcard below — defined once)

artifact_role: analysis_or_evidence_only | execution_authority: false

```yaml
parent_states: [PROPOSED, READY, IN_PROGRESS, CHILDREN_IN_PROGRESS, INTEGRATION_PENDING, VERIFIED, SCORED, CLOSED, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]
child_states:  [TODO, READY, IN_PROGRESS, IMPLEMENTED, VERIFIED, SCORED, CLOSED, REROUTED, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]
micro_states:  [PENDING, READY, ACTIVE, COMPLETE, FAILED, BLOCKED, SKIPPED_NOT_APPLICABLE]

parent_transitions:
  PROPOSED->READY, READY->IN_PROGRESS, IN_PROGRESS->CHILDREN_IN_PROGRESS,
  CHILDREN_IN_PROGRESS->INTEGRATION_PENDING, INTEGRATION_PENDING->VERIFIED,
  VERIFIED->SCORED, SCORED->CLOSED, SCORED->REROUTED,
  any_non_closed->BLOCKED, BLOCKED->READY, any_non_closed->BLOCKED_EXTERNAL, any_non_closed->DEFERRED_WITH_REASON

child_transitions:
  TODO->READY, READY->IN_PROGRESS, IN_PROGRESS->IMPLEMENTED, IMPLEMENTED->VERIFIED,
  VERIFIED->SCORED, SCORED->CLOSED, SCORED->REROUTED, REROUTED->IN_PROGRESS,
  any_non_closed->BLOCKED, BLOCKED->READY, any_non_closed->BLOCKED_EXTERNAL, any_non_closed->DEFERRED_WITH_REASON

micro_transitions:
  PENDING->READY, READY->ACTIVE, ACTIVE->COMPLETE, ACTIVE->FAILED, ACTIVE->BLOCKED,
  FAILED->READY, BLOCKED->READY, PENDING->SKIPPED_NOT_APPLICABLE(reason_required)

explicitly_blocked_invalid_transitions:
  - TODO -> CLOSED
  - READY -> CLOSED
  - IMPLEMENTED -> CLOSED
  - "child CLOSED while any mandatory micro-step != COMPLETE|SKIPPED_NOT_APPLICABLE"
  - "parent CLOSED while any mandatory child != CLOSED"
  - REROUTED -> CLOSED (without a rework cycle back through IN_PROGRESS first)
  - BLOCKED_EXTERNAL -> CLOSED (without unblock evidence attached)
  - "micro-step SKIPPED_NOT_APPLICABLE without a recorded reason"

quality_scoring:
  scale: 1-5
  threshold: "every mandatory dimension >= 4"
  child_dimensions: [requirement_correctness, implementation_correctness, scope_discipline, validation_strength, evidence_completeness, regression_safety, maintainability, production_readiness]
  parent_dimensions: [root_cause_coverage, child_completeness, integration_completeness, dependency_correctness, preserved_behavior, evidence_completeness, rerun_consistency, production_readiness]
  reroute_rule: "any dimension < 4 -> status REROUTED, weak dimension recorded, smallest necessary child/micro-step reopened or created, re-validate, re-score"

evidence_contract:
  root: ".local/evidences/<run_id>/"   # reuses Format Factory's existing evidence model, not a new one
  required_per_taskcard: [source_reference, command_or_method_used, raw_output_or_log_path, before_state, after_state, verdict]
  rule: "evidence must reference this plan's path + the exact REQ/TC/CHILD/MS id; no evidence artifact may issue execution instructions that conflict with this plan"
```

---

## 4. Validation Categories (shared vocabulary, referenced per-taskcard below)

artifact_role: analysis_or_evidence_only | execution_authority: false

`source_inspection` · `schema_validation` · `unit_test` · `integration_test` · `regression_test` · `negative_control` · `config_enforcement` · `generated_artifact_inspection` · `downstream_consumer_validation` · `state_machine_validation` · `rerun_idempotency_validation`

---

## 5. Dependency DAG & File Ownership

artifact_role: analysis_or_evidence_only | execution_authority: false

```yaml
# Wave 0 — foundational, mostly touches plans/layers/* and .supervisor/* — sequence to avoid file-lock collisions
TC-EXT-000: {depends_on: [], owns: [docs/governance/external-tool-architecture.md, docs/governance/superpowers-skill-intake.md, plans/master-plan.md], parallel_safe_with: [TC-EXT-009, TC-EXT-010]}
TC-EXT-001: {depends_on: [], owns: [], parallel_safe_with: [TC-EXT-000, TC-EXT-003..010]}   # pure research/intake, no file conflicts
TC-EXT-003: {depends_on: [], owns: [plans/layers/handoff-register.yaml, plans/layers/task-register.yaml, plans/layers/skills-layer.md], parallel_safe_with: [TC-EXT-009, TC-EXT-010]}
TC-EXT-004: {depends_on: [], owns: [plans/layers/master.md], parallel_safe_with: [TC-EXT-009, TC-EXT-010], blocks: [TC-EXT-006]}   # TC-EXT-006 reads the corrected layer table
TC-EXT-005: {depends_on: [], owns: [.claude/commands/reconcile-layer-index.md], blocks: [TC-EXT-006]}   # TC-EXT-006 uses the extended reconciler
TC-EXT-006: {depends_on: [TC-EXT-004, TC-EXT-005], owns: [plans/layers/index.yaml]}
TC-EXT-007: {depends_on: [TC-EXT-006], owns: [README.md, PROJECT_STATUS.md, .supervisor/skill-inventory.yaml, .supervisor/work-type-skill-map.yaml, .governance/capabilities/registry.yaml]}  # counts must reflect the backfilled attribution first
TC-EXT-008: {depends_on: [], owns: [registry/layer-gap-register.yaml or equivalent via /register-layer-gap], parallel_safe_with: [TC-EXT-003..007, 009, 010]}
TC-EXT-009: {depends_on: [], owns: [tools/supervisor/capability_compiler.py, tools/supervisor/autonomous_task_generator.py, plans/layers/feature-compilation-layer.md, .supervisor/work-type-skill-map.yaml, .supervisor/skill-system-baseline.yaml, .supervisor/skill-registry.yaml], parallel_safe_with: [TC-EXT-000, 001, 003, 004, 005, 008, 010]}
TC-EXT-010: {depends_on: [], owns: [tools/supervisor/check_continuation.py (new skill wrapper only, not the detection logic itself), tools/supervisor/sprint_executor.py, .claude/commands/autonomous-loop.md, CLAUDE.md], parallel_safe_with: [TC-EXT-000, 001, 003, 004, 005, 008, 009]}

# Wave A/C/D/E/G/H/Security — each depends on TC-EXT-012 (gating scanner) and, for layer attribution, on TC-EXT-005/006 being live
TC-EXT-012: {depends_on: [TC-EXT-001], blocks: [TC-EXT-013..028]}
TC-EXT-013..028: {depends_on: [TC-EXT-012, TC-EXT-005], note: "every new skill registration must run through the TC-EXT-005 extended reconciler per the shared Per-Taskcard Validation rule — this is the integration guarantee"}
TC-EXT-016, TC-EXT-021, TC-EXT-027, TC-EXT-028: {additional_precondition: SCM-POLICY-CHECK-001 (§7.2) — a one-time policy-state read, not a per-instance human stop; see §7.1 for the Supreme-Directive reconciliation}
TC-EXT-023: {excludes: "skill-improver's Stop-hook mechanism — see §7.1 item 3, re-scoped to a single-pass skill only"}
TC-EXT-019: {excludes: "modern-python's SessionStart hook — see §7.1 item 3, only non-hook guidance merged"}
TC-EXT-022: {excludes: "writing-skills' git-push-to-fork/PR deployment step — FF's registry is internal, not a public marketplace"}
```

Note: `TC-EXT-004` and `TC-EXT-006` both eventually touch `plans/layers/master.md`/`index.yaml` — sequenced (004 before 006), not parallel, to avoid conflicting edits to the same files.

---

## 6. Taskcards — Wave 0 (fully decomposed: parent → child → micro-step)

Micro-steps are recorded as compact tables (ID | Action | Target | Completion check | Evidence) rather than repeating the full 14-field block per step — this preserves every required field while keeping ~200 micro-steps navigable in one document.

### TC-EXT-000

```yaml
Parent Taskcard ID: TC-EXT-000
Title: Fix stale plan cross-references; establish Section 100 as this plan's home
Type: PARENT
Status: READY
Owner: planning-lane
Supervisor: governance-lane
Source: {Plan requirement ID: REQ-EXT-000, Plan section: Context, Root cause: "external-tool-architecture.md and superpowers-skill-intake.md both cite a 'Section 43' authority that no longer matches (Section 43 is now an unrelated closed plan); plans/master-plan.md has no entry point for this work", Selected solution: "point both docs at the new Section 100; seed Section 100 from this file"}
Objective: [Both governance docs cite a correct, current authority pointer; plans/master-plan.md has a Section 100 entry point for this plan]
Outcome: [grep for "Section 43" in both docs returns zero hits; plans/master-plan.md contains a Section 100 heading pointing at plans/.claude/yes-my-earlier-answer-humming-waffle.md]
Scope: {Allowed files: [docs/governance/external-tool-architecture.md, docs/governance/superpowers-skill-intake.md, plans/master-plan.md], Forbidden files: [plans/strategic/**, plans/.claude/production-portfolio-master-plan.md]}
Preserved behavior: [all other content in both governance docs unchanged; master-plan.md's existing Sections 1-99 unchanged]
Dependencies: []
Child taskcards: [TC-EXT-000-01, TC-EXT-000-02, TC-EXT-000-03]
Parent acceptance criteria: [zero stale "Section 43" references remain; Section 100 exists and is well-formed per the file's own convention]
Integration checks: [grep -r "Section 43" docs/governance/ returns nothing relevant to this plan]
Evidence required: [before/after diff of both docs, before/after of master-plan.md tail]
Quality dimensions: shared (§3)
Closeout criteria: [all 3 children CLOSED]
Rollback strategy: [git diff revert of the 3 touched files]
Stop conditions: [if Section 43 is referenced by unrelated content not related to this plan's scope, do not touch it]
Reroute rule: shared (§3)
```

| Child | Title | Micro-steps |
|---|---|---|
| TC-EXT-000-01 | Fix stale Section-43 pointer in `external-tool-architecture.md` | see table below |
| TC-EXT-000-02 | Fix stale Section-43 pointer in `superpowers-skill-intake.md` | see table below |
| TC-EXT-000-03 | Add `## Section 100` stub to `plans/master-plan.md` | see table below |

TC-EXT-000-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-000-01-01 | Grep for "Section 43" in the file | external-tool-architecture.md | exact line number found | grep output |
| MS-000-01-02 | Replace the stale pointer with "Section 100" | same file, same line | grep for "Section 43" returns 0 in this file | diff |

TC-EXT-000-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-000-02-01 | Grep for "Section 43" in the file | superpowers-skill-intake.md line 4 (`**Authority:**`) | exact line found | grep output |
| MS-000-02-02 | Replace with "Section 100" | same file, same line | grep returns 0 | diff |

TC-EXT-000-03 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-000-03-01 | Read end of master-plan.md to find last section number/line | plans/master-plan.md (confirmed ends at Section 99, line ~6940) | exact insertion line confirmed | read output |
| MS-000-03-02 | Insert `## Section 100 — yes-my-earlier-answer-humming-waffle: External Engineering Skill Adoption (IN_PROGRESS)` with `**Plan:** plans/.claude/yes-my-earlier-answer-humming-waffle.md` | after Section 99 | heading present, follows exact convention of Section 99 | diff |

### TC-EXT-001

```yaml
Parent Taskcard ID: TC-EXT-001
Title: Source/provenance/license intake for all imported external sources
Type: PARENT
Status: READY
Source: {Plan requirement ID: REQ-EXT-001, Plan section: "Governance Compliance"}
Objective: [every skill imported by this plan has a pinned commit SHA, confirmed license, and documented risk level before registration]
Outcome: [external_skill_commit and external_skill_license populated for every TC-EXT-01x/02x import — no skill registers with a blank provenance field]
Scope: {Allowed files: [.supervisor/skill-registry.yaml (append-only, provenance fields)], Forbidden files: [src/**]}
Dependencies: []
Child taskcards: [TC-EXT-001-01, TC-EXT-001-02, TC-EXT-001-03]
Parent acceptance criteria: [every imported skill's registry entry has external_skill_commit + external_skill_license set]
Evidence required: [WebFetch/GitHub API confirmation logs per source]
Closeout criteria: [all 3 children CLOSED]
Rollback strategy: [no import proceeds without this — rollback is simply not registering]
```

| Child | Title |
|---|---|
| TC-EXT-001-01 | Pin commit SHAs for the 6 primary sources (obra/superpowers, trailofbits/skills, getsentry/skills, github/awesome-copilot, anthropics/skills, anthropics/claude-code) |
| TC-EXT-001-02 | Resolve Trail of Bits CC-BY-SA-4.0 posture for the 5 ToB skills selected (sharp-edges, property-based-testing, audit-context-building, trailmark, skill-improver) |
| TC-EXT-001-03 | Resolve anthropics/skills per-skill license for mcp-builder (repo has no root LICENSE) |

TC-EXT-001-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-001-01-01 | Re-fetch each of the 6 repos' current HEAD commit SHA | GitHub API `/repos/{owner}/{repo}/commits/HEAD` | 6 SHAs recorded | API response |
| MS-001-01-02 | Record each SHA against its source in this plan's §8 Verified Source Inventory | this file | table updated with commit column | diff |

TC-EXT-001-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-001-02-01 | Read each of the 5 ToB skills' individual LICENSE/attribution requirements | trailofbits/skills plugin dirs | attribution text captured verbatim | fetch output |
| MS-001-02-02 | Draft the attribution comment each FF wrapper must carry (see Sentry's own precedent: `code-simplifier.md`'s attribution HTML comment) | new wrapper files (created in TC-EXT-017/018/023/025) | attribution template drafted | draft text |

TC-EXT-001-03 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-001-03-01 | Fetch `anthropics/skills/skills/mcp-builder/` directory for a skill-local LICENSE file | anthropics/skills repo | license found or confirmed absent | fetch output |
| MS-001-03-02 | If absent, treat as "no redistribution rights confirmed" and default TC-EXT-026 to a from-scratch FF-authored skill referencing the upstream design only (no vendored text) | plan decision recorded here | decision recorded | this file |

### TC-EXT-003

```yaml
Parent Taskcard ID: TC-EXT-003
Title: Close HO-007 as ALREADY_SATISFIED
Type: PARENT
Status: CLOSED
Source: {Plan requirement ID: REQ-EXT-003, Plan section: "Finding 1", Root cause: "TC-LP-023 delivered the 19 layer-maintenance skills and was CLOSED in master-plan.md, but plans/layers/handoff-register.yaml, task-register.yaml, and skills-layer.md were never updated to match", Selected solution: "update the 3 stale records with the real closure evidence; fix the misattributed SKILL-GAP-012 citation"}
Objective: [HO-007 shows CLOSED/ALREADY_SATISFIED consistently across all 3 tracking files, with the correct gap-ID citation]
Outcome: [handoff-register.yaml HO-007 = CLOSED; task-register.yaml TC-SKILL-001 = superseded_by TC-LP-023; skills-layer.md lists the 19 skills as owned]
Scope: {Allowed files: [plans/layers/handoff-register.yaml, plans/layers/task-register.yaml, plans/layers/skills-layer.md, plans/layers/master.md], Forbidden files: [plans/master-plan.md Section 43-unrelated content]}
Preserved behavior: [TC-LP-023's original closure record in master-plan.md is untouched — this only fixes the 3 files that failed to reflect it]
Dependencies: []
Child taskcards: [TC-EXT-003-01, TC-EXT-003-02, TC-EXT-003-03, TC-EXT-003-04, TC-EXT-003-05]
Parent acceptance criteria: [zero files still show HO-007/TC-SKILL-001 as NOT_STARTED; SKILL-GAP-012 no longer cited as HO-007's justification anywhere]
Evidence required: [master-plan.md:4853-4869 TC-LP-023 closure record cited as the evidence source in every updated file]
Closeout criteria: [all 5 children CLOSED]
Rollback strategy: [revert the 4 touched files via git]
```

| Child | Title |
|---|---|
| TC-EXT-003-01 | Update `handoff-register.yaml` HO-007 status → CLOSED, evidence pointer to TC-LP-023 |
| TC-EXT-003-02 | Update `task-register.yaml` TC-SKILL-001 → superseded_by: TC-LP-023 |
| TC-EXT-003-03 | Update `skills-layer.md` to list the 19 layer-maintenance skills as owned (skill_ids/command_ids) |
| TC-EXT-003-04 | Correct the misattributed `SKILL-GAP-012` reference (replace with accurate note: "no gap ID required, see TC-LP-023") |
| TC-EXT-003-05 | Update `master.md`'s HO-007 row (§8) and L13's §21 skill-coverage row |

**Closure record (all 5 children CLOSED, verified this session):** `plans/layers/handoff-register.yaml` HO-007 → `status: CLOSED` + `evidence` field added. `plans/layers/task-register.yaml` TC-SKILL-001 → `status: CLOSED`, `superseded_by: TC-LP-023`, `gap_ids: []`, misattributed `SKILL-GAP-012` replaced with corrective `notes` field. `plans/layers/skills-layer.md` `skill_ids`/`command_ids` extended from 10/6 to 29/25 (all 19 layer-maintenance skills confirmed via `.supervisor/skill-registry.yaml` `TC-LP-023` provenance + `.claude/commands/*.md` existence: identify-primary-layer, create-permanent-layer-plan, update-layer-current-state, register-layer-gap, register-layer-task, append-layer-work-log, append-layer-verification-log, update-layer-session-handoff, update-layer-master-index, close-layer-task, reconcile-layer-index, inventory-permanent-layer-plans, migrate-temporary-agent-plan, detect-unlogged-work, detect-stale-layer-state, create-cross-layer-handoff, select-next-layer-task, validate-permanent-layer-plans, reconcile-layer-task-register); `ready_taskcards`/`completed_taskcards` swapped. `plans/layers/master.md` line 165 HO-007 → `CLOSED`; §21 L13 row → `29 | 25 | None — ...`. Verification: `grep -rn SKILL-GAP-012 plans/layers/` returns only the corrective note (no HO-007 citation); `grep -n HO-007 plans/layers/master.md plans/layers/handoff-register.yaml` shows CLOSED, zero NOT_STARTED.

TC-EXT-003-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-003-01-01 | Read handoff-register.yaml HO-007 record (lines 125-143) | plans/layers/handoff-register.yaml | current content confirmed | read output |
| MS-003-01-02 | Set status: CLOSED, add evidence: "master-plan.md:4853-4869 TC-LP-023" | same file | field updated | diff |

TC-EXT-003-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-003-02-01 | Read task-register.yaml TC-SKILL-001 record (lines 252-279) | plans/layers/task-register.yaml | current content confirmed | read output |
| MS-003-02-02 | Add `superseded_by: TC-LP-023`, set status accordingly | same file | field added | diff |

TC-EXT-003-03 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-003-03-01 | List all 19 layer-maintenance `.claude/commands/*.md` files on disk | .claude/commands/ | 19 filenames confirmed | ls output |
| MS-003-03-02 | Add all 19 to skills-layer.md's `skill_ids`/`command_ids` metadata | plans/layers/skills-layer.md | metadata array updated | diff |

TC-EXT-003-04 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-003-04-01 | Locate every citation of SKILL-GAP-012 as HO-007's justification | handoff-register.yaml, task-register.yaml | citations found | grep output |
| MS-003-04-02 | Replace with a corrected note (no fabricated gap ID) | same files | citations corrected | diff |

TC-EXT-003-05 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-003-05-01 | Update master.md line 165 HO-007 row to CLOSED | plans/layers/master.md | row updated | diff |
| MS-003-05-02 | Update master.md §21 L13 skill-coverage row (line 325) to remove the open-gap note | plans/layers/master.md | row updated | diff |

### TC-EXT-004

```yaml
Parent Taskcard ID: TC-EXT-004
Title: Fix master.md's own layer-count inconsistency (28 header / 27 prose / 29 actual)
Type: PARENT
Status: READY
Source: {Plan requirement ID: REQ-EXT-004, Plan section: "Finding 2", Root cause: "L28 and L29 were created after master.md's last full refresh and were never added to its layer table, dependency graph, maturity matrix, skill-coverage table, or completion accounting"}
Objective: [master.md's header, prose, and index.yaml agree on exactly 29 layers, with L28/L29 present in every table that lists layers]
Outcome: [grep for "28 layers"/"27 layers"/"27 accepted" in master.md returns only the corrected "29"]
Scope: {Allowed files: [plans/layers/master.md]}
Dependencies: []
Child taskcards: [TC-EXT-004-01, TC-EXT-004-02, TC-EXT-004-03]
Parent acceptance criteria: [L28, L29 appear in §6 layer table, dependency graph §7, maturity matrix, §21 skill-coverage table, §26 completion accounting; header/prose/count agree at 29]
Closeout criteria: [all 3 children CLOSED]
Rollback strategy: [revert master.md]
```

| Child | Title |
|---|---|
| TC-EXT-004-01 | Add L28 Certification Audit Layer to all 5 master.md tables |
| TC-EXT-004-02 | Add L29 Operational Control Record Discovery Layer to all 5 master.md tables |
| TC-EXT-004-03 | Reconcile header `total_layers: 28`, prose "27 accepted independent layers," to the corrected 29 everywhere |

TC-EXT-004-01/02 micro-steps (identical pattern, one row per table):
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-004-01-01 | Copy L28's real data from index.yaml (status, maturity, skill_ids count) | plans/layers/index.yaml:1012+ | data extracted | read output |
| MS-004-01-02 | Insert L28 row into §6 layer table | master.md §6 | row present | diff |
| MS-004-01-03 | Insert L28 into §7 dependency graph | master.md §7 | node present | diff |
| MS-004-01-04 | Insert L28 into maturity matrix | master.md | row present | diff |
| MS-004-01-05 | Insert L28 into §21 skill-coverage table | master.md §21 | row present | diff |
| MS-004-01-06 | Insert L28 into §26 completion accounting | master.md §26 | entry present | diff |
| MS-004-02-01..06 | Same 6 steps for L29 | index.yaml:1075+ / master.md | all 5 tables updated | diff |

TC-EXT-004-03 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-004-03-01 | Grep master.md for all layer-count mentions (header, prose, any table totals) | master.md | all instances found | grep output |
| MS-004-03-02 | Set every instance to 29, consistently | master.md | zero remaining 27/28 mentions | grep re-check |

### TC-EXT-005

```yaml
Parent Taskcard ID: TC-EXT-005
Title: Extend /reconcile-layer-index to reconcile skill_ids against skill-registry.yaml
Type: PARENT
Status: READY
Source: {Plan requirement ID: REQ-EXT-005, Plan section: "Finding 2", Root cause: "reconcile-layer-index.md's own spec (Execution steps 1-5) only compares layer_id/status/maturity_current between index.yaml and each layer .md file — it never touches skill_ids or cross-references skill-registry.yaml, confirmed by direct read of the file", Selected solution: "add a 6th execution step + output category to the existing skill, not a new competing skill"}
Objective: [/reconcile-layer-index can detect any skill_id present in skill-registry.yaml but absent from every layer's skill_ids array, and vice versa]
Outcome: [running the extended skill against the current registry reports the known 90-skill discrepancy correctly, proving the extension works before TC-EXT-006 uses it to fix them]
Scope: {Allowed files: [.claude/commands/reconcile-layer-index.md], Forbidden files: [.supervisor/skill-registry.yaml (read-only, per the skill's own existing Forbidden Paths)]}
Dependencies: []
Child taskcards: [TC-EXT-005-01, TC-EXT-005-02, TC-EXT-005-03]
Parent acceptance criteria: [skill's Execution section has a new step 6; Output section documents a new `skill_id_mismatches` category; a dry run against the live registry reports ~90 unattributed skills]
Integration checks: [dry run output count is in the same order of magnitude as this session's independently-derived 90-skill figure]
Evidence required: [before/after of reconcile-layer-index.md; one real dry-run output]
Closeout criteria: [all 3 children CLOSED, dry-run evidence attached]
Rollback strategy: [revert reconcile-layer-index.md]
```

| Child | Title |
|---|---|
| TC-EXT-005-01 | Read current reconcile-layer-index.md in full, confirm exact insertion point |
| TC-EXT-005-02 | Add skill_ids reconciliation step + output category |
| TC-EXT-005-03 | Dry-run the extended skill against the live registry, confirm it surfaces the known 90-skill gap |

TC-EXT-005-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-005-01-01 | Confirm Execution steps 1-5 and Output example (currently hardcodes `total_layers: 27`, itself stale per TC-EXT-004) | .claude/commands/reconcile-layer-index.md | content confirmed (already read this session) | read output |

TC-EXT-005-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-005-02-01 | Add "6. For each layer, compare index.yaml's skill_ids array against .supervisor/skill-registry.yaml entries whose product_track plausibly maps to that layer; report additions/removals" to Execution | reconcile-layer-index.md | step 6 present | diff |
| MS-005-02-02 | Add `skill_id_mismatches:` category to the Output YAML example | reconcile-layer-index.md | category present | diff |
| MS-005-02-03 | Fix the stale `total_layers: 27` in the Output example to 29 (consistent with TC-EXT-004) | reconcile-layer-index.md | value corrected | diff |

TC-EXT-005-03 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-005-03-01 | Run the extended skill against the current index.yaml + skill-registry.yaml | live repo state | run completes | command output |
| MS-005-03-02 | Confirm reported unattributed count ≈ 90 (this session's independently-derived figure) | run output | counts agree within reasonable tolerance | comparison note |

### TC-EXT-006

```yaml
Parent Taskcard ID: TC-EXT-006
Title: Backfill all 90 currently-unattributed skills into plans/layers/index.yaml
Type: PARENT
Status: READY
Source: {Plan requirement ID: REQ-EXT-006, Plan section: "Finding 2"}
Objective: [index.yaml's skill_ids arrays for L01-L27 reflect the current skill-registry.yaml, not the 2026-06-26 bootstrap snapshot]
Outcome: [TC-EXT-005's extended reconciler reports 0 unattributed skills except any explicitly flagged as intentionally cross-cutting]
Scope: {Allowed files: [plans/layers/index.yaml]}
Dependencies: [TC-EXT-004, TC-EXT-005]
Child taskcards: [TC-EXT-006-01 .. TC-EXT-006-09]
Parent acceptance criteria: [re-run of TC-EXT-005's reconciler shows 0 unexplained mismatches]
Closeout criteria: [all 9 children CLOSED, final reconciler dry-run attached as evidence]
Rollback strategy: [revert index.yaml]
```

| Child | Title | Skills attributed |
|---|---|---|
| TC-EXT-006-01 | Attribute L02 QName | +1 (python-qname-code-reviewer) |
| TC-EXT-006-02 | Attribute L05 Oracle | +5 (calculate-oracle-coverage, detect-stale-oracles, onboard-future-format-oracle, generate-oracle-verdict-report, evaluate-roundtrip-oracle) |
| TC-EXT-006-03 | Attribute L06 Product | +11 (format-feature-expansion, new-format-kickstart, product-source-task, python-reduced-spec-parity-model, add-spec-analytics-function, add-same-format-writer-feature, implement-spec-stub, 4× spec_parity skills, check-dom-contract, inventory-format-dom, select-deepening-lane, check-source-loc) |
| TC-EXT-006-04 | Attribute L08 Evidence | +5 (build-supervisor-packet, validate-evidence-declaration, collect-skill-execution-receipts, validate-product-code-ledger, run-governance-validators) |
| TC-EXT-006-05 | Attribute L09 State | +1 (reset-track-signal) |
| TC-EXT-006-06 | Attribute L10 Plan | +25 (layer_governance-track skills) |
| TC-EXT-006-07 | Attribute L11/L12/L13 | several each (detect-ad-hoc-execution, scan-residual-bypasses, run-lifecycle-audit, enforce-skill-first-execution, inventory-skills, preflight-skill-entry, backfill-task-skill-ownership, run-skill-idempotency, etc.) |
| TC-EXT-006-08 | Attribute L22/L27 | L22 +2 (audit-root-tools, found-issue-ownership), L27 +1 (portfolio-reconcile) |
| TC-EXT-006-09 | Resolve `acquisition` track / no-layer mismatch | map to nearest existing layer or explicitly flag cross-cutting, record decision |

Each of TC-EXT-006-01..08 shares one micro-step pattern:
| ID pattern | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-006-0X-01 | Confirm the exact skill_id list for this layer bucket against skill-registry.yaml | .supervisor/skill-registry.yaml | list matches this table | grep output |
| MS-006-0X-02 | Append the skill_ids to the layer's array in index.yaml | plans/layers/index.yaml | array updated | diff |

TC-EXT-006-09 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-006-09-01 | Determine whether `acquisition` (5 skills) fits an existing layer or needs a documented cross-cutting flag | plans/layers/master.md, index.yaml | decision made and justified | this file / decision note |
| MS-006-09-02 | Apply the decision | index.yaml | reflected | diff |

### TC-EXT-007

```yaml
Parent Taskcard ID: TC-EXT-007
Title: Reconcile the 5 divergent skill-count numbers and fix minor tracked drift
Type: PARENT
Status: READY
Source: {Plan requirement ID: REQ-EXT-007, Plan section: "Finding 2, Finding 8"}
Objective: [README.md, PROJECT_STATUS.md, skill-inventory.yaml, master.md, and the raw registry all report the same skill count, generated from one pass]
Dependencies: [TC-EXT-006]
Child taskcards: [TC-EXT-007-01 .. TC-EXT-007-06]
Closeout criteria: [all 6 children CLOSED]
Rollback strategy: [revert the 5 touched files]
```

| Child | Title |
|---|---|
| TC-EXT-007-01 | Regenerate `PROJECT_STATUS.md` via `tools/docs/generate_project_status.py` |
| TC-EXT-007-02 | Run `/generate-root-status` to refresh README's SYSTEM-STATUS-SUMMARY block |
| TC-EXT-007-03 | Reconcile README.md's hand-authored Layer Architecture table (line ~46) to the canonical count |
| TC-EXT-007-04 | Refresh `.supervisor/skill-inventory.yaml` |
| TC-EXT-007-05 | Fix stale `SKILL-GAP-011` status in `work-type-skill-map.yaml` (rollback_and_recovery already resolved 2026-06-25) |
| TC-EXT-007-06 | Sync the 4 uncaptured L28-Certification capabilities into `.governance/capabilities/registry.yaml` via `/sync-capabilities` |

TC-EXT-007-01/02/04 micro-steps (mechanical regeneration, one pattern):
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-007-0X-01 | Run the regeneration command | respective tool | command exits 0 | command output |
| MS-007-0X-02 | Confirm the new count matches the true post-backfill registry total | regenerated file | count matches | diff |

TC-EXT-007-03 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-007-03-01 | Update README.md line 46's hardcoded count | README.md | value matches canonical count | diff |

TC-EXT-007-05 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-007-05-01 | Update work-type-skill-map.yaml gap_mappings.rollback_and_recovery status to resolved, citing capability-routing-registry.yaml:498-507 | .supervisor/work-type-skill-map.yaml | field updated | diff |

TC-EXT-007-06 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-007-06-01 | Run `/sync-capabilities` | .governance/capabilities/registry.yaml | 4 new entries appear (certification-ci-gate, certification-cross-language-parity, certification-mutation-tester, certification-performance-benchmark) | command output |

### TC-EXT-008

```yaml
Parent Taskcard ID: TC-EXT-008
Title: Register layer gaps for the 6 genuinely zero-coverage layers
Type: PARENT
Status: READY
Source: {Plan requirement ID: REQ-EXT-008, Plan section: "Finding 3"}
Objective: [L04, L15, L17, L19, L20, L24 each have a registered, visible, prioritizable gap entry — content design deferred to whoever picks up each gap]
Scope: {Allowed files: [via /register-layer-gap's own allowed paths only]}
Child taskcards: [TC-EXT-008-01 .. 06]
Closeout criteria: [all 6 children CLOSED, one gap entry per layer confirmed in the gap register]
```

| Child | Layer |
|---|---|
| TC-EXT-008-01 | L04 Sample Corpus |
| TC-EXT-008-02 | L15 Source Change Handoff |
| TC-EXT-008-03 | L17 Regression Compatibility |
| TC-EXT-008-04 | L19 Consumer API |
| TC-EXT-008-05 | L20 Security and Legal |
| TC-EXT-008-06 | L24 Metrics and Product Velocity |

Each shares one micro-step pattern:
| ID pattern | Action | Completion check | Evidence |
|---|---|---|---|
| MS-008-0X-01 | Invoke `/register-layer-gap` for this layer, citing this plan's Finding 3 as source | gap entry created | command output |

### TC-EXT-009

```yaml
Parent Taskcard ID: TC-EXT-009
Title: Resolve SKILL-GAP-003 (capability_compiler / L14) — complete the incomplete closure, wire output, consolidate duplicates
Type: PARENT
Status: READY
Source: {Plan requirement ID: REQ-EXT-009, Plan section: "Finding 6", Root cause: "TC-SFE3-002's closure only wrote skill-gap-003-closure-proof.yaml; it never removed the gap from the 3 registries that gate skill-coverage checks, and its own justification (crediting /build-capability-routes) doesn't hold up — that skill is a route-integrity validator, not a compilation router", Selected solution: "register tools/supervisor/capability_compiler.py as the canonical skill, fix all 3 registries consistently, execute the already-specced TC-CAP-DIAG-001 wiring fix, retire the 7 duplicate files"}
Objective: [capability_compiler is a registered, routed, consistently-tracked skill; its compiled output actually drives task selection; duplicate files are retired, not silently coexisting]
Outcome: [work-type-skill-map.yaml, skill-system-baseline.yaml, and skill-registry.yaml all agree capability_compiler is resolved; autonomous_task_generator.py reads .local/capability-consumer/taskcards/]
Scope: {Allowed files: [tools/supervisor/capability_compiler.py (registration only, no logic change required), tools/supervisor/autonomous_task_generator.py, plans/layers/feature-compilation-layer.md, plans/layers/task-register.yaml, plans/layers/index.yaml, .supervisor/work-type-skill-map.yaml, .supervisor/skill-system-baseline.yaml, .supervisor/skill-registry.yaml, .supervisor/capability-routing-registry.yaml], Forbidden files: [deep Lane-3 batch-compilation logic — out of scope for gap closure, tracked as follow-on only]}
Preserved behavior: [capability_queue_consumer.py's existing automatic Step-2h invocation is unchanged; this only adds consumption of its output]
Dependencies: []
Child taskcards: [TC-EXT-009-01 .. 06]
Parent acceptance criteria: [gap absent from all 3 registries consistently; a compiled taskcard for a real FOSS gap is confirmed present in product-task-candidates.json via a focused proof script]
Integration checks: [run capability_queue_consumer.py, confirm output file exists, confirm autonomous_task_generator.py's next run includes at least one compiled candidate]
Evidence required: [before/after of all 3 registries; the focused proof script and its output]
Closeout criteria: [all 6 children CLOSED]
Rollback strategy: [revert all touched files; capability_queue_consumer.py's existing behavior is unaffected either way]
Stop conditions: [do not attempt Phase 4 / batch concept-graph / format-family-plugin work — explicitly out of scope for this taskcard]
```

| Child | Title |
|---|---|
| TC-EXT-009-01 | Register `tools/supervisor/capability_compiler.py` as a formal skill in `skill-registry.yaml` |
| TC-EXT-009-02 | Add a `capability_compiler` route to `capability-routing-registry.yaml` |
| TC-EXT-009-03 | Remove the gap consistently from all 3 registries (work-type-skill-map.yaml, skill-system-baseline.yaml, skill-registry.yaml known_open_gaps) |
| TC-EXT-009-04 | Mark the 7 duplicate/orphaned files as retired via a decision-register entry |
| TC-EXT-009-05 | Execute `TC-CAP-DIAG-001`: wire `.local/capability-consumer/taskcards/` into `autonomous_task_generator.py`'s actual selection |
| TC-EXT-009-06 | Update `feature-compilation-layer.md`/`task-register.yaml`/`index.yaml` L14 row with real skill_ids + evidence |

TC-EXT-009-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-009-01-01 | Draft skill-registry.yaml entry (skill_id: capability-compiler, product_track: infrastructure, command_file pointing at a thin `.claude/commands/capability-compiler.md` wrapper describing the pipeline nature) | .supervisor/skill-registry.yaml | entry drafted | diff |
| MS-009-01-02 | Run `/preflight-skill-entry` | new entry | PASS | command output |
| MS-009-01-03 | Insert entry | skill-registry.yaml | entry present | diff |

TC-EXT-009-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-009-02-01 | Add route entry: work_type capability_compiler → preferred_skill_ids: [capability-compiler] | .supervisor/capability-routing-registry.yaml | route present | diff |

TC-EXT-009-03 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-009-03-01 | Remove/close the gap_mappings.capability_compiler entry | work-type-skill-map.yaml:35-39 | entry removed or status=resolved | diff |
| MS-009-03-02 | Remove/close the matching entry | skill-system-baseline.yaml:27-29 | entry removed or status=resolved | diff |
| MS-009-03-03 | Remove/close the matching entry | skill-registry.yaml:31-34 known_open_gaps | entry removed or status=resolved | diff |

TC-EXT-009-04 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-009-04-01 | Add a decision-register entry naming the 7 files (capability_to_feature_compiler.py alias, tools/capability_layer/capability_to_feature_compiler.py, tools/supervisor/gap_ledger_to_work_items.py, tools/feature_compiler/gap_to_work_item.py, tools/supervisor/capability_feature_compiler.py — assess if genuinely duplicate or a distinct narrower pipeline before retiring, tools/capability_layer/capability_compiler.py — confirm this is L03's, not L14's, before any action) as retired/reference-only | decision register (or nearest equivalent FF mechanism) | entry recorded | diff |

TC-EXT-009-05 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-009-05-01 | Add `_load_compiled_taskcards()` reading `.local/capability-consumer/taskcards/*.json` | tools/supervisor/autonomous_task_generator.py | function added | diff |
| MS-009-05-02 | Wire it into actual candidate selection, not just goal annotation | same file | selection includes compiled candidates | diff |
| MS-009-05-03 | Write a focused proof script confirming a compiled FOSS-gap taskcard surfaces in `product-task-candidates.json` | new <80-line proof script | script runs, proves it | script output |

TC-EXT-009-06 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-009-06-01 | Update `feature-compilation-layer.md` metadata (skill_ids, maturity_current, status) | plans/layers/feature-compilation-layer.md | fields updated | diff |
| MS-009-06-02 | Update `task-register.yaml` TC-FEAT-001 and `index.yaml` L14 row | plans/layers/task-register.yaml, index.yaml | rows updated | diff |

### TC-EXT-010

```yaml
Parent Taskcard ID: TC-EXT-010
Title: Resolve SKILL-GAP-008 (pre_sprint_governance_hook) — register the skill, close two live override loopholes
Type: PARENT
Status: READY
Source: {Plan requirement ID: REQ-EXT-010, Plan section: "Finding 7", Root cause: "check_continuation.py Check 8 + governance_block_registry.py already detect and correctly stop on a structural GOV_BLOCK, but sprint_executor.py's _is_external_gate() and autonomous-loop.md's STOP-reason catch-all both fail to recognize structural_govblock_must_be_resolved_first as non-overridable, so both actuators currently let the 'binding' rule through", Selected solution: "register a thin skill wrapping the existing detection (do not reimplement); patch both actuators' override logic; reconcile CLAUDE.md's stale 4-vs-6 validator count; allocate a fresh gap ID"}
Objective: [the GOV_BLOCK exception cannot be silently bypassed by either the headless or interactive execution path]
Outcome: [a test proves sprint_executor.py halts (not proceeds) when structural_govblock_must_be_resolved_first is present; autonomous-loop.md's NON-OVERRIDABLE list explicitly names it]
Scope: {Allowed files: [tools/supervisor/sprint_executor.py, .claude/commands/autonomous-loop.md, CLAUDE.md, tools/supervisor/governance_block_registry.py (read-only reference, no logic change needed), .supervisor/skill-registry.yaml], Forbidden files: [tools/supervisor/check_continuation.py's existing Check 8 detection logic — already correct, do not modify]}
Preserved behavior: [extract-analytics-from-monolith and the existing detection logic are unchanged — this only closes the override loopholes and adds a registered skill wrapper]
Dependencies: []
Child taskcards: [TC-EXT-010-01 .. 06]
Parent acceptance criteria: [new test demonstrates both loopholes closed; CLAUDE.md's validator count matches governance_block_registry.py's actual list]
Integration checks: [simulate a rework_items payload containing a structural block, confirm sprint_executor.py returns/halts rather than proceeding]
Evidence required: [before/after of sprint_executor.py and autonomous-loop.md; the new test and its passing run]
Closeout criteria: [all 6 children CLOSED]
Rollback strategy: [revert all touched files]
Stop conditions: [do not modify governance_block_registry.py's validator list itself — only reconcile CLAUDE.md's text to match it]
```

| Child | Title |
|---|---|
| TC-EXT-010-01 | Register `pre-sprint-governance-hook` skill wrapping existing Check 8 + `governance_block_registry.py` logic |
| TC-EXT-010-02 | Fix `sprint_executor.py`'s override loophole |
| TC-EXT-010-03 | Fix `autonomous-loop.md`'s override loophole |
| TC-EXT-010-04 | Reconcile CLAUDE.md's stale "4 validators" text against the actual 6 |
| TC-EXT-010-05 | Allocate a fresh gap identifier (not colliding with the already-closed `SKILL-GAP-008` pre-commit-hook item) |
| TC-EXT-010-06 | Add a test proving both loopholes are closed |

TC-EXT-010-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-010-01-01 | Draft `.claude/commands/pre-sprint-governance-hook.md` (thin wrapper, references check_continuation.py Check 8 + governance_block_registry.py, does not reimplement) | new file | drafted | file content |
| MS-010-01-02 | Run `/preflight-skill-entry`, insert into skill-registry.yaml | .supervisor/skill-registry.yaml | entry present, PASS | command output |

TC-EXT-010-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-010-02-01 | Locate `_TRUE_EXTERNAL_GATES`/`_is_external_gate()` in sprint_executor.py | tools/supervisor/sprint_executor.py | exact lines confirmed | read output |
| MS-010-02-02 | Add `structural_govblock_must_be_resolved_first` to the non-overridable handling | same file | code updated | diff |

TC-EXT-010-03 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-010-03-01 | Locate the STOP-reason table's NON-OVERRIDABLE list and catch-all | .claude/commands/autonomous-loop.md Step 1 | exact lines confirmed | read output |
| MS-010-03-02 | Add `structural_govblock_must_be_resolved_first` explicitly to NON-OVERRIDABLE | same file | table updated | diff |

TC-EXT-010-04 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-010-04-01 | Read `governance_block_registry.py`'s current `STRUCTURAL_GOV_BLOCKS` list (6 entries) | tools/supervisor/governance_block_registry.py | list confirmed | read output |
| MS-010-04-02 | Update CLAUDE.md's GOV_BLOCK Exception section to name all 6, not 4 | CLAUDE.md | text updated | diff |

TC-EXT-010-05 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-010-05-01 | Allocate a fresh, disambiguated gap ID for pre_sprint_governance_hook (distinct from the closed SKILL-GAP-008 pre-commit-hook item) | relevant gap registers | new ID recorded, collision noted | diff |

TC-EXT-010-06 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-010-06-01 | Write a test simulating a structural rework_item, asserting `sprint_executor.py` halts | new/existing test file under tests/supervisor/ | test written | file content |
| MS-010-06-02 | Run the test, confirm PASS | pytest | PASS | test output |

---

## 7. Risk Classification, Human-Gate Reconciliation & Taskcards — Waves A/C/D/E/G/H/Security (now fully decomposed)

Full upstream content for all 26 external skills was fetched verbatim this session (not just existence + one-line description) — see the per-source research findings this session produced. That resolves the prior limitation: every parent below now has full parent→child→micro-step decomposition, grounded in real content, not fabricated.

### 7.0 Risk Classification (per Format Factory's own existing criteria — `docs/governance/external-tool-architecture.md` Tool 2 risk table)

artifact_role: analysis_or_evidence_only | execution_authority: false

| Skill | Real evidence from fetched content | Risk (FF's literal criteria) |
|---|---|---|
| systematic-debugging | Pure methodology, no automated file ops, no external calls, no hooks | LOW |
| test-driven-development | Writes test files + edits production code directly, but bounded (red-green-refactor), local test-runner CLI only (no network) | MEDIUM |
| verification-before-completion | No file mutation; runs local build/test/lint commands and reads `git diff` | LOW |
| receiving-code-review | Real external network call: `gh api .../replies` to post a PR comment reply | **HIGH** |
| writing-skills | Creates new skill files locally (LOW) — **but** its Deployment step includes `git push` to a remote fork + optional PR creation | **HIGH if that step is imported; LOW if excluded** |
| silent-failure-hunter, type-design-analyzer, comment-analyzer, pr-test-analyzer | All 4 confirmed pure read-only/advisory, explicit "do not modify code" statements, zero external calls | LOW |
| sharp-edges | `tools: Read, Grep, Glob` only — confirmed read-only, no external calls | LOW |
| property-based-testing | No tool restriction declared; meant to write test code directly into the repo — bounded to test files | MEDIUM |
| audit-context-building | Explicit non-goal ("does NOT propose fixes"), `tools: Read, Grep, Glob` (+Bash only at the command-arg-parsing layer) | LOW |
| trailmark | **Requires `uv pip install trailmark`** (external PyPI package) before first use; subsequent use is local query, no further network calls | MEDIUM (one-time install, not a recurring external-call risk) |
| skill-improver | **Implements a Stop-hook-driven forced-continuation loop** (`hooks/hooks.json` + `stop-hook.sh`, re-injects prompts via `"decision": "block"` until a literal completion marker), directly edits target skill files, requires installing a second plugin (`plugin-dev`) | **HIGH — hook/daemon mechanism** |
| workflow-skill-design | Guidance skill + explicitly read-only reviewer agent (`tools: Read, Glob, Grep, TodoRead, TodoWrite`), "Never create, edit, or write files" | LOW |
| modern-python | Guidance content is LOW — **but** bundles a **SessionStart hook** (`hooks/setup-shims.sh`) that silently modifies `PATH` every session | **HIGH if the hook is imported; LOW if only the guidance content is merged** |
| skill-scanner | Pure read-only scanner (own bundled local script), no network calls, no hooks | LOW |
| gha-security-review | Pure read-only analysis, no writes, no external calls despite `Task` in allowed-tools | LOW |
| skill-writer | Directly creates/edits `SKILL.md`/`SPEC.md`/reference files + "applies repository registration steps" — bounded to the skill-authoring domain | MEDIUM |
| agent-supply-chain | Writes `INTEGRITY.json` (self-contained manifest); verify/audit/gate patterns are read-only; no network | MEDIUM |
| agent-owasp-compliance (awesome-copilot) | Pure read-only static pattern matching (`re`, `pathlib`), no network, no writes | LOW |
| impediment-prioritization | Explicitly "Read-only by default... does not execute remediations" | LOW |
| dependabot | Config-authoring guide for `.github/dependabot.yml` (CI-adjacent config) + documents GitHub Advisory Database queries via MCP + Dependabot CLI (read-only vulnerability lookups) | MEDIUM (see §7.1 reconciliation — CI-config edits are within Supreme-Directive SCM-Agent authority, and the network calls are read-only lookups, not mutations) |
| github-release | Steps 1-4 read-only recon; Steps 5-8 create a branch, write `CHANGELOG.md`, commit, **push**, open a PR via `gh`; Step 9 (tag + actual release) explicitly left to the user | **HIGH — hits the named `git push` TRUE_EXTERNAL_GATE directly** |
| mcp-builder | Scoped to authoring a **new, separate** MCP server project (own source tree/build/test) — confirmed it never touches `.vscode/mcp.json` or any live MCP client registration; network calls are reference-fetching (MCP spec, SDK docs) + Anthropic API only during its own evaluation phase | MEDIUM (not CRITICAL — does not touch FF's own live MCP config) |
| gh-fix-ci (FF-original) | Reads CI logs via `gh run view` (read-only network call), runs local diagnostics (ruff/pytest/dotnet/validators); fixes delegated to already-governed mutation skills | MEDIUM |
| gh-address-comments (FF-original) | Posts responses to PR comments via `gh api` — same external-visible-action profile as receiving-code-review | **HIGH** |

### 7.1 Reconciling the risk table against CLAUDE.md's Supreme Directive (this session's determination, stated explicitly rather than silently applied)

`docs/governance/external-tool-architecture.md`'s literal text ("HIGH risk: Supervisor + human authorization... Do not install Superpowers plugins... without explicit Supervisor approval and human authorization") predates and is broader-scoped than `CLAUDE.md`'s Supreme Directive, which is explicitly the higher-priority, override-default authority in this repo and narrows "things that can stop autonomous execution" to exactly three named `TRUE_EXTERNAL_GATE`s: git push credentials, Gate 11 execution approval by Babar Raza, and package-publication credentials — plus a short list of named legitimate stops (`POST_PLAN_TERMINAL`, structural `GOV_BLOCK`). CLAUDE.md states its own rules "OVERRIDE any default behavior."

Applying that precedence, this plan reconciles the two documents as follows, rather than silently picking one:

1. **For HIGH-risk items that do NOT touch a named TRUE_EXTERNAL_GATE** (receiving-code-review, gh-address-comments — both post PR comments via `gh api`; dependabot's CI-config edit) — CLAUDE.md's existing "SCM Agent" doctrine already governs this exact class of action: *"Commit tasks: SCM Agent executes when sprint policy authorizes"* and the general Human-Free Autonomy Doctrine's *"Push tasks: SCM Agent executes when credentials available + branch policy allows + sprint/user policy authorizes."* This plan therefore requires a **one-time standing policy check** (does sprint/user policy authorize `gh api` PR-comment posting and CI-config edits?) rather than a per-invocation human stop. This is a precondition check, not a recurring interrupt — see §7.2.
2. **For the one item that hits a named TRUE_EXTERNAL_GATE directly** (github-release's `git push` in Step 7) — this is not a new gate; it is the exact, pre-existing, named gate in CLAUDE.md. github-release's own design (Steps 1-4 read-only recon, explicit user-confirmation checkpoints before Steps 5 and 6, and Step 9 explicitly deferring the actual tag/release-publish to the user) is *already* compatible with FF's existing "SCM Agent executes when credentials + policy authorize; agent prepares the release packet, human does the final publish" model — this is FF's standard shape for this class of action, not a plan-specific exception.
3. **For genuine hook/daemon mechanisms** (skill-improver's Stop hook, modern-python's SessionStart hook) — these are excluded from import entirely, not merely gated. This is not a policy dodge: FF already has its own autonomous continuation mechanism (`check_continuation.py`, `sprint_executor.py`); importing a second, competing, hook-based forced-continuation loop (skill-improver) would be a genuine engineering redundancy/risk regardless of the human-gate question, and installing a session-wide PATH-intercepting hook (modern-python) is exactly the scenario `external-tool-architecture.md`'s "No SessionStart or context injection until reviewed" line was written for. Only the **non-hook guidance content** of each (skill-improver's review-categorize-fix loop *concept*; modern-python's tool-replacement/anti-pattern tables) is merged — see TC-EXT-019 and TC-EXT-023 below, both re-scoped accordingly.
4. **For trailmark's one-time package install** — installing a new dev/security tool (`uv pip install trailmark`) does not hit any of the three named TRUE_EXTERNAL_GATEs (it is not a git push, not Gate 11, not package publication) and is routine agent-executable dependency-addition. Reclassified MEDIUM, no human needed.
5. **Everything else in the table (20 of 26 items)** is LOW/MEDIUM per FF's own criteria with no reconciliation needed — genuinely autonomous, Supervisor-only.

### 7.2 The one standing precondition this plan requires (not a per-taskcard human stop)

```yaml
precondition_id: SCM-POLICY-CHECK-001
statement: >
  Before TC-EXT-016, TC-EXT-021, TC-EXT-027, or TC-EXT-028 post any PR comment, edit
  .github/dependabot.yml, push a branch, or open a PR, the executing agent must confirm
  that Format Factory's existing SCM Agent sprint/user policy (AGENTS.md §AG4, CLAUDE.md
  Human-Free Autonomy Doctrine) currently authorizes these action classes. This is a
  policy-state read, not a request for a human to approve this specific plan or taskcard.
if_policy_already_authorizes: proceed autonomously, no further human involvement at any stage
if_policy_does_not_yet_authorize: classify as EXTERNAL_BLOCKER (per CLAUDE.md's existing
  named pattern, e.g. EXTERNAL_BLOCKER: git_push_credentials_unavailable) rather than
  silently stopping or silently proceeding — this is Format Factory's own existing
  classification discipline, not a new gate invented by this plan.
```

With this precondition satisfied (or explicitly classified if not), every taskcard in this plan — including all 26 external-skill imports — executes with **Supervisor-level review/approval only, never a per-instance human stop**.

### 7.3 Taskcards

```yaml
Parent Taskcard ID: TC-EXT-012
Title: Import skill-scanner (Sentry, Apache-2.0) as the gating security scanner
Type: PARENT
Status: READY
Risk level: LOW | Activation gate: Supervisor review
Source: {Plan requirement ID: REQ-EXT-012, Plan section: "Group 5"}
Dependencies: [TC-EXT-001]
Child taskcards: [TC-EXT-012-01, TC-EXT-012-02, TC-EXT-012-03, TC-EXT-012-04, TC-EXT-012-05]
Closeout criteria: [skill-scanner registered AND has scanned itself + is ready to gate every subsequent import]
```

| Child | Title |
|---|---|
| TC-EXT-012-01 | Draft `.claude/commands/skill-scanner.md` codifying the real 8-phase methodology |
| TC-EXT-012-02 | Register (preflight, insert with `external_skill_origin`, `external_skill_source: getsentry/skills`, `external_skill_license: Apache-2.0`) |
| TC-EXT-012-03 | Self-scan proof: run against its own wrapper file |
| TC-EXT-012-04 | Scan proof against 2 other wrappers this plan will create (e.g. TC-EXT-013, TC-EXT-017) once drafted |
| TC-EXT-012-05 | Layer-attribute via TC-EXT-005 mechanism (L12 Validation or L13 Skills) |

TC-EXT-012-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-012-01-01 | Draft Execution section with the real 8 phases (Input & Discovery; Automated Static Scan; Frontmatter Validation; Prompt Injection Analysis; Behavioral Analysis; Script Analysis; Supply Chain Assessment; Permission Analysis) | new .claude/commands/skill-scanner.md | 8 phases present, matching fetched content | file content |
| MS-012-01-02 | Draft Output Format section (`SKILL-SEC-###` findings: Location/Confidence High-Med-Low/Category/Issue/Evidence/Risk/Remediation, overall Risk Level enum Critical/High/Medium/Low/Clean) | same file | schema present | file content |
| MS-012-01-03 | Add attribution comment citing getsentry/skills `skill-scanner`, Apache-2.0 | same file | comment present | diff |
| MS-012-01-04 | Set Allowed Paths to read-only (Read/Grep/Glob/Bash restricted to the scanned target + this skill's own local checklist, no writes) | same file | Allowed/Forbidden Paths sections present | diff |

TC-EXT-012-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-012-02-01 | Run `/preflight-skill-entry` | new entry | PASS | command output |
| MS-012-02-02 | Insert into `.supervisor/skill-registry.yaml` with provenance fields | skill-registry.yaml | entry present | diff |

TC-EXT-012-03/04 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-012-03-01 | Run skill-scanner against its own `.claude/commands/skill-scanner.md` | new skill | scan completes, verdict recorded | scan output |
| MS-012-04-01 | Run skill-scanner against each subsequently-drafted wrapper before that wrapper's own registration step | each new wrapper | clean verdict or findings addressed | scan output per wrapper |

TC-EXT-012-05 micro-steps: (shared pattern with all other parents below — "layer-attribute" always means: run TC-EXT-005's extended `/reconcile-layer-index`, confirm the new skill_id appears attributed, evidence = reconciler output)

---

```yaml
Parent Taskcard ID: TC-EXT-013
Title: Import systematic-debugging (obra/superpowers, MIT)
Type: PARENT
Status: READY
Risk level: LOW | Activation gate: Supervisor review
Source: {Plan requirement ID: REQ-EXT-013, Plan section: "Group 0"}
Dependencies: [TC-EXT-012, TC-EXT-005]
Child taskcards: [TC-EXT-013-01, TC-EXT-013-02, TC-EXT-013-03, TC-EXT-013-04]
Closeout criteria: [registered, layer-attributed, skill-scanner clean]
```

| Child | Title |
|---|---|
| TC-EXT-013-01 | Draft `.claude/commands/systematic-debugging.md` codifying the real 4-phase Iron Law process |
| TC-EXT-013-02 | Wire FF-specific handoffs (EP-3 routing, `FI-NNN` hand-off to `/found-issue-ownership`) |
| TC-EXT-013-03 | Register (skill-scanner clearance + preflight + insert) |
| TC-EXT-013-04 | Layer-attribute |

TC-EXT-013-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-013-01-01 | Draft the 4 phases verbatim-adapted: Phase 1 Root Cause Investigation (Read Errors, Reproduce, Check Recent Changes, Gather Evidence, Trace Data Flow), Phase 2 Pattern Analysis, Phase 3 Hypothesis and Testing, Phase 4 Implementation | new systematic-debugging.md | 4 phases present | file content |
| MS-013-01-02 | Add the Iron Law framing ("NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST") and the ≥3-failed-fixes stop rule ("question architecture") | same file | rule present | diff |
| MS-013-01-03 | Add MIT attribution comment citing obra/superpowers | same file | comment present | diff |

TC-EXT-013-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-013-02-01 | Replace "discuss with human partner" (upstream's escalation target) with FF's own escalation: hand off to `/found-issue-ownership` Step 3 when root cause is confirmed, or Step 8 `INVALID_FINDING_WITH_PROOF`/other disposition when architecture-level | systematic-debugging.md | FF-specific handoff text present | diff |
| MS-013-02-02 | Add mandatory validation: `found_issue_id_provided` when a confirmed defect results | same file | field present | diff |

TC-EXT-013-03/04 micro-steps: standard registration pattern (see TC-EXT-012-02 for the registration pattern; TC-EXT-012-05 for the layer-attribute pattern) — apply identically here.

---

```yaml
Parent Taskcard ID: TC-EXT-014
Title: Import test-driven-development (obra/superpowers, MIT, RED-GREEN-REFACTOR)
Type: PARENT
Status: READY
Risk level: MEDIUM | Activation gate: Supervisor approval
Source: {Plan requirement ID: REQ-EXT-014, Plan section: "Group 0"}
Dependencies: [TC-EXT-012, TC-EXT-005]
Child taskcards: [TC-EXT-014-01, TC-EXT-014-02, TC-EXT-014-03, TC-EXT-014-04]
Closeout criteria: [registered, bound into 3 mutation skills, layer-attributed]
```

| Child | Title |
|---|---|
| TC-EXT-014-01 | Draft `.claude/commands/test-driven-development.md` codifying the real RED→Verify RED→GREEN→Verify GREEN→REFACTOR cycle + 8-item Verification Checklist |
| TC-EXT-014-02 | Bind as an optional sub-procedure into `/product-source-task`, `/add-python-api`, `/add-dotnet-api` (reference only, not a duplicate mutation owner) |
| TC-EXT-014-03 | Register |
| TC-EXT-014-04 | Layer-attribute |

TC-EXT-014-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-014-01-01 | Draft the 5-step cycle (RED, Verify RED, GREEN, Verify GREEN, REFACTOR) with the Iron Law ("NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST") | new TDD skill file | steps present | file content |
| MS-014-01-02 | Add the 8-item Verification Checklist verbatim-adapted | same file | checklist present | diff |
| MS-014-01-03 | Scope Allowed Paths to `tests/**` write + `src/**` only via delegation to a named mutation skill (per EP-3) — explicitly exclude the upstream's own generic "edit production code" framing | same file | Forbidden Paths block direct `src/**` writes | diff |

TC-EXT-014-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-014-02-01 | Add a note in `/product-source-task` referencing TDD as an optional sub-procedure for Steps 2-3 | product-source-task.md | note present | diff |
| MS-014-02-02 | Same for `/add-python-api`, `/add-dotnet-api` | those files | notes present | diff |

TC-EXT-014-03/04 micro-steps: standard pattern.

---

```yaml
Parent Taskcard ID: TC-EXT-015
Title: Merge verification-before-completion (obra/superpowers) + differential-review (ToB) into existing closure skills
Type: PARENT
Status: READY
Risk level: LOW | Activation gate: Supervisor review
Source: {Plan requirement ID: REQ-EXT-015, Plan section: "Group 0, 3"}
Dependencies: [TC-EXT-012]
Child taskcards: [TC-EXT-015-01, TC-EXT-015-02, TC-EXT-015-03]
Note: no new skill_id — closes without a registry entry, only 3 existing-skill edits
```

| Child | Title |
|---|---|
| TC-EXT-015-01 | Merge the real 5-step Gate Function (Identify→Run→Read→Verify→Claim) into `/post-sprint-audit`'s pre-closure checklist |
| TC-EXT-015-02 | Merge into `/post-sprint-loop`'s verification gate before evidence packaging |
| TC-EXT-015-03 | Merge into `/product-source-task`'s completion verification sweep |

Each shares one micro-step pattern:
| ID pattern | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-015-0X-01 | Add the Gate Function's 5 steps + "Red Flags - STOP" list (words like "should"/"probably"/"seems to" as red flags) to the target skill | respective .md file | steps present | diff |
| MS-015-0X-02 | Bump `version` in frontmatter | same file | version incremented | diff |

---

```yaml
Parent Taskcard ID: TC-EXT-016
Title: Import receiving-code-review (obra/superpowers, MIT)
Type: PARENT
Status: READY
Risk level: HIGH (real `gh api` external call posting a PR comment reply) | Activation gate: Supervisor approval + SCM-POLICY-CHECK-001 (§7.2) — not a per-instance human stop
Source: {Plan requirement ID: REQ-EXT-016, Plan section: "Group 0"}
Dependencies: [TC-EXT-012, TC-EXT-017]
Child taskcards: [TC-EXT-016-01, TC-EXT-016-02, TC-EXT-016-03, TC-EXT-016-04]
```

| Child | Title |
|---|---|
| TC-EXT-016-01 | Draft `.claude/commands/receiving-code-review.md` codifying the real 6-step Response Pattern (Read→Understand→Verify→Evaluate→Respond→Implement) |
| TC-EXT-016-02 | Wire the External Reviewer verification checklist + YAGNI check to consume Group-2 reviewer output (silent-failure-hunter etc.) |
| TC-EXT-016-03 | Confirm SCM-POLICY-CHECK-001 authorizes `gh api .../replies`; register |
| TC-EXT-016-04 | Layer-attribute |

TC-EXT-016-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-016-01-01 | Draft the 6 steps + "Handling Unclear Feedback" hard-stop ("IF any item is unclear: STOP") | new file | steps present | file content |
| MS-016-01-02 | Draft the YAGNI check ("grep codebase for actual usage") and Implementation Order sub-procedures | same file | present | diff |
| MS-016-01-03 | Scope the `gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies` call behind the SCM-POLICY-CHECK-001 precondition | same file | precondition referenced explicitly | diff |

TC-EXT-016-02/03/04 micro-steps: TC-EXT-016-02 wires to TC-EXT-017's reviewer outputs (1 step: add consumption note); 016-03 runs the precondition check then standard registration; 016-04 standard layer-attribute.

---

```yaml
Parent Taskcard ID: TC-EXT-017
Title: Import 5 read-only reviewers (silent-failure-hunter, type-design-analyzer, comment-analyzer, pr-test-analyzer — Apache-2.0 via claude-plugins-official; sharp-edges — ToB, CC-BY-SA)
Type: PARENT
Status: READY
Risk level: LOW (all 5 confirmed read-only/advisory, zero external calls) | Activation gate: Supervisor review
Source: {Plan requirement ID: REQ-EXT-017, Plan section: "Group 2"}
Dependencies: [TC-EXT-012, TC-EXT-005, TC-EXT-001-02 (sharp-edges attribution)]
Child taskcards: [TC-EXT-017-01 .. 05, one per reviewer]
```

| Child | Reviewer | Real output schema to codify |
|---|---|---|
| TC-EXT-017-01 | silent-failure-hunter | 5 named principles + 5-phase review process; per-issue fields Location/Severity(CRITICAL-HIGH-MEDIUM)/Issue/Hidden Errors/User Impact/Recommendation/Example |
| TC-EXT-017-02 | type-design-analyzer | 5-part Analysis Framework, 4 dimensions rated 1-10 (Encapsulation/Invariant Expression/Invariant Usefulness/Invariant Enforcement) |
| TC-EXT-017-03 | comment-analyzer | 5 checks (Factual Accuracy/Completeness/Long-term Value/Misleading Elements/Suggest Improvements); explicit "analysis and feedback only" statement |
| TC-EXT-017-04 | pr-test-analyzer | behavioral-coverage focus + explicit 1-10 criticality rating rubric (9-10 critical, 1-2 minor) |
| TC-EXT-017-05 | sharp-edges | 6 Sharp Edge Categories + 4-phase Analysis Workflow (Surface ID→Edge Case Probing→Threat Modeling vs 3 named adversary personas→Validate Findings); Category/Severity/Location/Description/Minimal misuse example/Recommendation output |

Each child shares this micro-step pattern:
| ID pattern | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-017-0X-01 | Draft `.claude/commands/<reviewer-name>.md` codifying the real criteria/output schema from the table above | new file | schema matches fetched content verbatim | file content |
| MS-017-0X-02 | Add explicit read-only statement + Forbidden Paths blocking any write | same file | statement present | diff |
| MS-017-0X-03 | Add attribution comment (Apache-2.0 for the first 4, CC-BY-SA-4.0 + Trail-of-Bits attribution for sharp-edges per TC-EXT-001-02) | same file | comment present | diff |
| MS-017-0X-04 | Wire finding-routing: severity/rating above a threshold routes to `/found-issue-ownership`; below threshold logged only | same file | routing rule present | diff |
| MS-017-0X-05 | Register + layer-attribute | skill-registry.yaml, index.yaml | entries present | diff |

---

```yaml
Parent Taskcard ID: TC-EXT-018
Title: Import property-based-testing (ToB, CC-BY-SA-4.0)
Type: PARENT
Status: READY
Risk level: MEDIUM (writes test code directly, bounded to test files, pilot-gated) | Activation gate: Supervisor approval
Source: {Plan requirement ID: REQ-EXT-018, Plan section: "Group 3"}
Dependencies: [TC-EXT-012, TC-EXT-001-02]
Child taskcards: [TC-EXT-018-01, TC-EXT-018-02, TC-EXT-018-03, TC-EXT-018-04]
```

| Child | Title |
|---|---|
| TC-EXT-018-01 | Draft skill codifying the real property catalog (Roundtrip/Idempotence/Invariant/Commutativity/Associativity/Identity/Inverse/Oracle) + strength hierarchy (No Exception → Type Preservation → Invariant → Idempotence → Roundtrip) + the priority table (serialization pairs → Roundtrip, HIGH priority) |
| TC-EXT-018-02 | Adapt for Python: recommend `hypothesis` as the library (upstream lists it as the Python option), scope to FF's `encode`/`decode`, `load`/`save`, `parse`/`write` codec function pairs |
| TC-EXT-018-03 | Pilot on exactly one format (e.g. `csv` or `fods`) before rollout; write the roundtrip property test, confirm it passes |
| TC-EXT-018-04 | Register + layer-attribute |

TC-EXT-018-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-018-01-01 | Draft the Decision Tree (writing new tests → design → reviewing existing PBT → interpreting failures) and the Rationalizations-to-Reject table | new file | present | file content |
| MS-018-01-02 | Add CC-BY-SA-4.0 attribution (Trail of Bits, Henrik Brodin) | same file | comment present | diff |
| MS-018-01-03 | Scope Allowed Paths to `tests/**` write only, `src/**` read-only | same file | paths scoped | diff |

TC-EXT-018-02/03 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-018-02-01 | Confirm `hypothesis` is available in the FF `.venv` or add it as a dev dependency | pyproject.toml / .venv | package available | command output |
| MS-018-03-01 | Write one roundtrip property test for the pilot format's encode/decode pair | tests/python/<format>/ | test written | file content |
| MS-018-03-02 | Run the test, confirm PASS | .venv/Scripts/pytest | PASS | test output |

TC-EXT-018-04 micro-steps: standard pattern.

---

```yaml
Parent Taskcard ID: TC-EXT-019
Title: Merge modern-python guidance (ToB — EXCLUDING its SessionStart hook) + impediment-prioritization (awesome-copilot) into existing skills
Type: PARENT
Status: READY
Risk level: LOW (hook explicitly excluded per §7.1; both merges are read-only guidance) | Activation gate: Supervisor review
Source: {Plan requirement ID: REQ-EXT-019, Plan section: "Group 2, 7"}
Dependencies: [TC-EXT-012]
Child taskcards: [TC-EXT-019-01, TC-EXT-019-02, TC-EXT-019-03, TC-EXT-019-04]
Note: no new skill_id
Explicit exclusion: modern-python's SessionStart hook (hooks/setup-shims.sh, PATH-intercepting) is NOT imported — see §7.1 item 3. Only the tool-replacement table and anti-patterns table are merged.
```

| Child | Title |
|---|---|
| TC-EXT-019-01 | Merge modern-python's tool-replacement table (uv/ruff/ty/pytest/prek replacing pip/flake8/mypy/pre-commit) and anti-patterns table into `python-qname-code-reviewer`'s notes — hook excluded |
| TC-EXT-019-02 | Merge impediment-prioritization's exact formula (`Priority = ((ROI*(10/Cost))+(Ease*(10/Risk)))/2`, verbatim, "do not reweight") into `promote-gap-to-taskcard`'s ordering logic |
| TC-EXT-019-03 | Add the deprecated-skill manual-check note (from Finding 8) to `create-ff-skill`'s audit checklist |
| TC-EXT-019-04 | Confirm no hook file, `hooks.json`, or SessionStart mechanism was introduced anywhere in this merge |

TC-EXT-019-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-019-01-01 | Add tool-replacement + anti-pattern tables as reference notes | python-qname-code-reviewer.md | tables present | diff |
| MS-019-01-02 | Explicitly do NOT create any `hooks/` file or `hooks.json` | (negative control) | grep for new hook files returns none | grep output |

TC-EXT-019-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-019-02-01 | Add the exact formula and boundary-check examples (ROI=10,Cost=1,Ease=10,Risk=1→100; ROI=1,Cost=10,Ease=1,Risk=10→1) | promote-gap-to-taskcard.md | formula present verbatim | diff |

TC-EXT-019-03/04 micro-steps: 1 step each — add the note; run the negative-control grep confirming no hook mechanism exists anywhere touched by this taskcard.

---

```yaml
Parent Taskcard ID: TC-EXT-020
Title: Build gh-fix-ci (FF-original — no upstream name verified in this session's research)
Type: PARENT
Status: READY
Risk level: MEDIUM (reads CI logs via `gh run view` — external read-only network call; local diagnostics only) | Activation gate: Supervisor approval
Source: {Plan requirement ID: REQ-EXT-020, Plan section: "Group 9"}
Dependencies: []
Child taskcards: [TC-EXT-020-01, TC-EXT-020-02, TC-EXT-020-03, TC-EXT-020-04]
```

| Child | Title |
|---|---|
| TC-EXT-020-01 | Design the CI job diagnosis map for all 13 jobs (lint/security/test-fast/test-full/dotnet-build/governance-check/skill-attribution-check/readme-drift/oracle-obligations/capability-parity/oracle-depth-check/release-phase-validation/count-drift-detection/agent-parity-drift) |
| TC-EXT-020-02 | Draft `.claude/commands/gh-fix-ci.md` with the diagnosis map + local-repro commands per job |
| TC-EXT-020-03 | Register |
| TC-EXT-020-04 | Layer-attribute |

TC-EXT-020-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-020-01-01 | For each of the 13 jobs, record its exact local-reproduction command (e.g. lint→`ruff check src/ tests/ tools/`, test-fast→`python tools/test_runner.py`, dotnet-build→`dotnet build`/`dotnet test`) | .github/workflows/ci.yml (read) | 13-row map drafted | this file's own table (already drafted in the original crosswalk) |

TC-EXT-020-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-020-02-01 | Draft the skill file with the 13-row diagnosis map + `gh run view <run_id> --log-failed` as the log-fetch step | new gh-fix-ci.md | map present | file content |
| MS-020-02-02 | Scope: fixes route through governed mutation skills per EP-3, this skill itself only diagnoses + runs local reproduction | same file | Forbidden Paths blocks direct src/** writes | diff |

TC-EXT-020-03/04 micro-steps: standard pattern.

---

```yaml
Parent Taskcard ID: TC-EXT-021
Title: Build gh-address-comments (FF-original)
Type: PARENT
Status: READY
Risk level: HIGH (posts PR comment responses via `gh api`) | Activation gate: Supervisor approval + SCM-POLICY-CHECK-001
Source: {Plan requirement ID: REQ-EXT-021, Plan section: "Group 9"}
Dependencies: [TC-EXT-020]
Child taskcards: [TC-EXT-021-01, TC-EXT-021-02, TC-EXT-021-03, TC-EXT-021-04]
```

| Child | Title |
|---|---|
| TC-EXT-021-01 | Design the comment classification model (code-change / question / style-nit / governance-concern) |
| TC-EXT-021-02 | Draft skill file, gate the `gh api` posting call behind SCM-POLICY-CHECK-001 |
| TC-EXT-021-03 | Confirm precondition, register |
| TC-EXT-021-04 | Layer-attribute |

Micro-steps: same pattern as TC-EXT-016 (draft classification model → draft file with precondition reference → run precondition check → standard registration/attribution).

---

```yaml
Parent Taskcard ID: TC-EXT-022
Title: Build create-ff-skill, absorbing writing-skills (Superpowers, MIT — EXCLUDING its push/PR deployment step), skill-writer (Sentry, Apache-2.0), workflow-skill-design (ToB, CC-BY-SA)
Type: PARENT
Status: READY
Risk level: MEDIUM (bounded to skill-definition/registry files — same domain FF's own create-taskcard-class skills already mutate routinely) | Activation gate: Supervisor approval
Source: {Plan requirement ID: REQ-EXT-022, Plan section: "Group 6"}
Dependencies: [TC-EXT-012, TC-EXT-005]
Child taskcards: [TC-EXT-022-01 .. 05]
Explicit exclusion: writing-skills' Deployment step ("commit and push to your fork", "contribute back via PR") is NOT imported — FF's registry is internal, not a public marketplace; create-ff-skill's own registration pipeline (preflight→dual-registry→sync→dedup→contract-validation) replaces it.
```

| Child | Title |
|---|---|
| TC-EXT-022-01 | Codify writing-skills' RED-GREEN-REFACTOR-for-skills methodology (pressure-scenario baseline → SKILL.md authoring → re-test) minus the fork-push/PR step |
| TC-EXT-022-02 | Codify skill-writer's 6-step workflow (resolve target/shape → synthesis → iteration → author → optimize description → register/validate) as the authoring backbone |
| TC-EXT-022-03 | Codify workflow-skill-design's pattern-selection decision tree + Anti-Pattern Quick Reference (20 catalogued) as a review pass |
| TC-EXT-022-04 | Add the TC-EXT-005 layer-reconciliation step as a MANDATORY final step — this is the permanent integration guarantee for every future skill this repo ever creates |
| TC-EXT-022-05 | Register + layer-attribute |

TC-EXT-022-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-022-01-01 | Draft RED (pressure-scenario baseline via subagent) → GREEN (author per FF's own frontmatter/section conventions, not upstream's) → REFACTOR (close loopholes) | new create-ff-skill.md | 3 phases present | file content |
| MS-022-01-02 | Explicitly omit the "commit skill to git and push to your fork" / "contribute back via PR" checklist items | same file | grep for "push"/"fork"/"contribute back" returns none | grep output |

TC-EXT-022-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-022-02-01 | Adapt the 6-step workflow, substituting FF's own registration pipeline (preflight-skill-entry → skill-registry.yaml → sync-skill-command-registry → detect-duplicate-skills → validate-skill-contracts) for skill-writer's generic "Apply repository registration steps" | same file | FF-specific steps present | diff |

TC-EXT-022-03 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-022-03-01 | Add the 20-item Anti-Pattern Quick Reference as a review checklist | same file | checklist present | diff |

TC-EXT-022-04 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-022-04-01 | Add "run TC-EXT-005's extended `/reconcile-layer-index` and attribute the new skill_id to its layer" as a mandatory final step, not optional | same file | step marked mandatory | diff |

TC-EXT-022-05 micro-steps: standard pattern.

---

```yaml
Parent Taskcard ID: TC-EXT-023
Title: Import skill-improver's non-hook methodology only (ToB, CC-BY-SA-4.0) — Stop-hook mechanism EXCLUDED
Type: PARENT
Status: READY
Risk level: LOW as re-scoped (hook excluded; adapted as a single-pass skill inside FF's existing sprint loop, not a competing continuation daemon) | Activation gate: Supervisor review
Source: {Plan requirement ID: REQ-EXT-023, Plan section: "Group 6"}
Dependencies: [TC-EXT-012, TC-EXT-022, TC-EXT-001-02]
Child taskcards: [TC-EXT-023-01, TC-EXT-023-02, TC-EXT-023-03, TC-EXT-023-04]
Explicit exclusion: skill-improver's Stop-hook loop (hooks/hooks.json, stop-hook.sh, the `<skill-improvement-complete>` re-injection mechanism) and its dependency on the third-party `plugin-dev` plugin are NOT imported. FF already owns its continuation loop (check_continuation.py/sprint_executor.py) — a second, competing hook-based forced-continuation mechanism would be a genuine redundancy/risk, not merely a governance formality.
```

| Child | Title |
|---|---|
| TC-EXT-023-01 | Adapt the Core Loop concept (Review→Categorize→Fix→Evaluate→Repeat) as a single-pass, manually-invoked skill, not a Stop-hook daemon |
| TC-EXT-023-02 | Adapt the issue-categorization severity model (Critical/Major/Minor) for FF's own skill files |
| TC-EXT-023-03 | Register (confirm no hooks/*.json file created anywhere) |
| TC-EXT-023-04 | Layer-attribute |

TC-EXT-023-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-023-01-01 | Draft the Review→Categorize→Fix→Evaluate cycle as a single invocation cycle, invoked periodically via FF's own sprint loop (not a Stop hook) | new skill-improver.md (FF-scoped) | cycle present, no hook reference | file content |
| MS-023-01-02 | Explicitly confirm no `hooks/hooks.json`, no `plugin-dev` dependency, no forced-continuation marker mechanism | (negative control) | grep for "hooks.json"/"plugin-dev"/"skill-improvement-complete" returns none in the new file | grep output |

TC-EXT-023-02/03/04 micro-steps: adapt Critical/Major/Minor categorization (1 step); standard registration with the negative-control grep re-run; standard layer-attribute.

---

```yaml
Parent Taskcard ID: TC-EXT-024
Title: Import gha-security-review (Sentry, Apache-2.0) + agent-supply-chain (awesome-copilot, MIT)
Type: PARENT
Status: READY
Risk level: LOW (gha-security-review) / MEDIUM (agent-supply-chain writes INTEGRITY.json) | Activation gate: Supervisor review / approval respectively
Source: {Plan requirement ID: REQ-EXT-024, Plan section: "Group 5"}
Dependencies: [TC-EXT-012]
Child taskcards: [TC-EXT-024-01 .. 05]
```

| Child | Title |
|---|---|
| TC-EXT-024-01 | Draft gha-security-review wrapper codifying the real 8 vulnerability classes (Pwn Request/Expression Injection/Unauthorized Command Execution/Credential Escalation/Config File Poisoning/Supply Chain/Permissions/Runner Infrastructure) + Severity×Confidence dual-scale output |
| TC-EXT-024-02 | Draft agent-supply-chain wrapper codifying the real 4 patterns (Generate Integrity Manifest/Verify/Dependency Version Audit/Promotion Gate) |
| TC-EXT-024-03 | Register gha-security-review |
| TC-EXT-024-04 | Register agent-supply-chain |
| TC-EXT-024-05 | Layer-attribute both |

TC-EXT-024-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-024-01-01 | Draft the 4-step methodology (Classify Triggers→Check Vulnerability Classes→Validate Before Reporting→Report Findings) with the explicit confidence policy ("Report only HIGH and MEDIUM confidence... not theoretical issues") | new gha-security-review.md | steps present | file content |
| MS-024-01-02 | Scope to `.github/workflows/*.yml` read-only analysis | same file | Forbidden Paths blocks writes | diff |

TC-EXT-024-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-024-02-01 | Draft the SHA-256 chain-hash manifest generation + MISSING/MODIFIED/UNTRACKED verification classification | new agent-supply-chain.md | patterns present | file content |
| MS-024-02-02 | Scope INTEGRITY.json writes to the skill's own target-plugin-directory only | same file | Allowed Paths scoped narrowly | diff |

TC-EXT-024-03/04/05 micro-steps: standard pattern, twice.

---

```yaml
Parent Taskcard ID: TC-EXT-025
Title: Import agent-owasp-compliance (awesome-copilot, MIT), audit-context-building (ToB, CC-BY-SA), trailmark (ToB, CC-BY-SA) — all promoted from defer with real evidence
Type: PARENT
Status: READY
Risk level: LOW (agent-owasp-compliance, audit-context-building) / MEDIUM (trailmark — one-time external package install) | Activation gate: Supervisor review / review / approval respectively
Source: {Plan requirement ID: REQ-EXT-025, Plan section: "Group 5, Finding 4"}
Dependencies: [TC-EXT-012, TC-EXT-001-02]
Child taskcards: [TC-EXT-025-01 .. 07]
```

| Child | Title |
|---|---|
| TC-EXT-025-01 | Draft agent-owasp-compliance wrapper codifying the real ASI-01..10 checklist (positive/negative code-search patterns for ASI-01, prose checklists for ASI-02..10), targeting `docs/python-foss/security-model.md`'s named "no OWASP/NIST audit" gap explicitly |
| TC-EXT-025-02 | Draft audit-context-building wrapper codifying the real 3-phase methodology (Initial Orientation→Ultra-Granular Function Analysis→Global System Understanding), explicitly scoped to `tools/supervisor/` + `tools/governance/` (the gap Gate 8 doesn't cover) |
| TC-EXT-025-03 | Draft trailmark wrapper — one-time `uv pip install trailmark` setup step, then read-only call-graph/blast-radius queries |
| TC-EXT-025-04 | Register agent-owasp-compliance |
| TC-EXT-025-05 | Register audit-context-building |
| TC-EXT-025-06 | Register trailmark (install step + registration) |
| TC-EXT-025-07 | Layer-attribute all 3 |

TC-EXT-025-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-025-01-01 | Draft the 10-question rapid assessment checklist + Compliance Report template (X/10 Controls Covered) | new agent-owasp-compliance.md | checklist present | file content |
| MS-025-01-02 | Add explicit cross-reference to `docs/python-foss/security-model.md`'s "Known Limitations" line as the gap this closes | same file | cross-reference present | diff |

TC-EXT-025-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-025-02-01 | Draft the 3 phases with the explicit non-goal statement ("does NOT identify vulnerabilities, propose fixes... assign severity") and numeric thresholds (min 3 invariants/function, min 5 assumptions, min 3 risk considerations) | new audit-context-building.md | phases + thresholds present | file content |
| MS-025-02-02 | Scope target explicitly to `tools/supervisor/` and `tools/governance/`, not the already-covered `src/python/{format}/` parsers | same file | scope stated explicitly | diff |

TC-EXT-025-03 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-025-03-01 | Draft the one-time setup step: `uv pip install trailmark`, confirmed via `uv run trailmark --version` or equivalent | new trailmark.md | setup step present | file content |
| MS-025-03-02 | Draft the read-only query patterns (`callers_of`, `callees_of`, `paths_between`, `complexity_hotspots`, `attack_surface`, `preanalysis`) for FF's `tools/supervisor/`+`tools/governance/` codebase | same file | query patterns present | diff |
| MS-025-03-03 | Actually run `uv pip install trailmark` once, confirm it succeeds | FF environment | install succeeds | command output |

TC-EXT-025-04/05/06/07 micro-steps: standard registration pattern, 3 times, plus layer-attribute for all 3.

---

```yaml
Parent Taskcard ID: TC-EXT-026
Title: Import mcp-builder (anthropics/skills, Apache-2.0 per-skill LICENSE.txt confirmed)
Type: PARENT
Status: READY
Risk level: MEDIUM (scoped to authoring new, separate MCP server source — confirmed it never touches FF's own live `.vscode/mcp.json`) | Activation gate: Supervisor approval
Source: {Plan requirement ID: REQ-EXT-026, Plan section: "Group 6"}
Dependencies: [TC-EXT-012, TC-EXT-001-03]
Child taskcards: [TC-EXT-026-01, TC-EXT-026-02, TC-EXT-026-03, TC-EXT-026-04]
```

| Child | Title |
|---|---|
| TC-EXT-026-01 | Confirm license (done — `skills/mcp-builder/LICENSE.txt`, Apache-2.0, confirmed this session) |
| TC-EXT-026-02 | Draft skill formalizing/extending `tools/supervisor/mcp_bridge.py`, adapting mcp-builder's real 4 phases (Deep Research and Planning→Implementation→Review and Test→Create Evaluations) |
| TC-EXT-026-03 | Register with attribution to anthropics/skills |
| TC-EXT-026-04 | Layer-attribute |

TC-EXT-026-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-026-02-01 | Draft Phase 1-3 adapted for extending FF's existing hand-rolled `mcp_bridge.py` (JSON-RPC stdio server) rather than greenfield scaffolding | new mcp-builder.md (FF-scoped) | phases present, references mcp_bridge.py explicitly | file content |
| MS-026-02-02 | Draft Phase 4 (evaluation) adapted to FF's existing `/check-mcp-status` monitor rather than duplicating a separate eval harness | same file | cross-reference present | diff |
| MS-026-02-03 | Explicitly confirm scope excludes `.vscode/mcp.json` modification — new/extended tools are added to `mcp_bridge.py`'s own tool list, not the client registration | same file | Forbidden Paths lists `.vscode/mcp.json` | diff |

TC-EXT-026-03/04 micro-steps: standard pattern with Apache-2.0 attribution comment.

---

```yaml
Parent Taskcard ID: TC-EXT-027
Title: Import dependabot-inspired skill (awesome-copilot content as reference — zero dependency-update automation exists today)
Type: PARENT
Status: READY
Risk level: MEDIUM (CI-config edit is within Supreme-Directive SCM-Agent authority per §7.1; Advisory-Database queries are read-only) | Activation gate: Supervisor approval
Source: {Plan requirement ID: REQ-EXT-027, Plan section: "Group 8"}
Dependencies: [TC-EXT-012]
Child taskcards: [TC-EXT-027-01, TC-EXT-027-02, TC-EXT-027-03, TC-EXT-027-04]
```

| Child | Title |
|---|---|
| TC-EXT-027-01 | Draft skill codifying the real ecosystem-detection table, adapted to FF's actual ecosystems (`pip`/`uv` for Python extras, `nuget` for .NET packages, `github-actions`) |
| TC-EXT-027-02 | Draft the config-authoring workflow for `.github/dependabot.yml` (directories, schedule, grouping) |
| TC-EXT-027-03 | Register, explicitly noting the CI-config edit routes through FF's existing SCM-Agent commit-policy check (§7.1), not a new gate |
| TC-EXT-027-04 | Layer-attribute |

TC-EXT-027-01/02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-027-01-01 | Confirm FF's actual ecosystems by reading `pyproject.toml`, `src/net/**/*.csproj`, `.github/workflows/` | live repo | ecosystems confirmed (pip/uv, nuget, github-actions) | read output |
| MS-027-02-01 | Draft the minimal `.github/dependabot.yml` block per confirmed ecosystem | new dependabot skill file | block drafted | file content |

TC-EXT-027-03/04 micro-steps: standard pattern, citing §7.1's reconciliation explicitly in the skill's own Stop Conditions section.

---

```yaml
Parent Taskcard ID: TC-EXT-028
Title: Import github-release (awesome-copilot content as reference)
Type: PARENT
Status: READY
Risk level: HIGH (git push in Step 7 — hits the named TRUE_EXTERNAL_GATE directly) | Activation gate: SCM Agent policy authorization (CLAUDE.md's existing push doctrine) — agent prepares the release packet autonomously; the packet's own Steps 4/6 already require the confirmations upstream itself designed in, and Step 9 (tag + actual publish) is explicitly left to the user by the skill's own design, matching FF's existing publication-credentials boundary
Source: {Plan requirement ID: REQ-EXT-028, Plan section: "Group 8"}
Dependencies: [TC-EXT-012]
Child taskcards: [TC-EXT-028-01, TC-EXT-028-02, TC-EXT-028-03, TC-EXT-028-04]
```

| Child | Title |
|---|---|
| TC-EXT-028-01 | Draft skill codifying the real 9-step workflow (checkout main→find PREV_TAG via git tag, not `gh release list`→analyze diff+commits→determine SemVer→create release branch→update CHANGELOG.md→commit+push→open PR→hand off tag/publish to user) |
| TC-EXT-028-02 | Adapt for FF's multi-package-per-format reality: `PUBLIC_PATH` becomes per-format `src/python/<format>/` or `src/net/<format>/`, not repo root |
| TC-EXT-028-03 | Confirm SCM Agent push/PR policy authorizes Steps 5-8; register |
| TC-EXT-028-04 | Layer-attribute |

TC-EXT-028-01 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-028-01-01 | Draft Steps 1-4 (read-only recon) verbatim-adapted, including the exact rationale for reading git tags directly rather than `gh release list` | new github-release.md | steps present | file content |
| MS-028-01-02 | Draft Steps 5-8 (branch/changelog/commit/push/PR) with the explicit "wait for user confirmation" checkpoints upstream itself specifies at Step 4 (version) and Step 6 (changelog) preserved verbatim | same file | checkpoints present | diff |
| MS-028-01-03 | Draft Step 9 (manual tag + publish) exactly as upstream leaves it to the user — do not automate past this point | same file | Step 9 explicitly manual | diff |
| MS-028-01-04 | Draft the error-handling table (gh auth failure, dirty tree, no commits since tag, protected-branch push failure) | same file | table present | diff |

TC-EXT-028-02 micro-steps:
| ID | Action | Target | Completion check | Evidence |
|---|---|---|---|---|
| MS-028-02-01 | Replace `PUBLIC_PATH` default with a required per-format path argument | same file | argument required, no bare repo-root default | diff |

TC-EXT-028-03/04 micro-steps: standard pattern, citing §7.1 item 2's reconciliation explicitly.

### 7.4 Shared boilerplate (all 17 parents above)

```yaml
Quality dimensions: shared (§3)
Evidence required: [full upstream content citation (already fetched this session — see per-source research); before/after of every registry touched; skill-scanner clearance for every wrapper]
Closeout criteria: [all listed children CLOSED; TC-EXT-005's reconciler shows this skill correctly layer-attributed]
Rollback strategy: [do not register — reverting is simply not inserting the registry entry]
Reroute rule: shared (§3)
```

---

## 8. Preserved Analysis (Part 1 Findings & Part 2 Crosswalk — unchanged content, carried forward verbatim)

The following is the original recon/analysis this plan was built from. It is preserved in full per the Core Preservation Rule — none of it is replaced by the taskcard machinery above, which only adds an execution-control layer on top of it.

### Finding 1: HO-007 is not an open gap — it's a stale status that should be closed

`plans/layers/master.md:165` shows `HO-007 | L13 Skills | L11 Supervisor | 19 new skills in registry | NOT_STARTED`. Investigation traced this fully:

- The work it describes (19 layer-maintenance micro-skills: `append-layer-work-log`, `update-layer-master-index`, etc.) **was already completed** — `plans\master-plan.md:4853-4869` records `TC-LP-023 (19 layer-maintenance micro-skills) | CLOSED`, and all 19 corresponding `.claude/commands/*.md` files exist on disk today.
- `plans/layers/handoff-register.yaml`, `plans/layers/task-register.yaml`, and `plans/layers/skills-layer.md` were simply never updated after that closure — they still show `NOT_STARTED`/`TC-SKILL-001 ready`.
- The gap ID cited as justification, `SKILL-GAP-012`, **is misattributed** — it's actually the ID for an already-resolved, unrelated issue (agents bypassing evidence declarations, EP-003, resolved 2026-06-25 via `TC-SGF-002`). The layer-plan bootstrap reused an already-closed gap ID as a stub rather than deriving a real one.
- `plans/layers/skills-layer.md` (the L13 layer's own plan) doesn't even list the 19 layer-maintenance skills as skills it owns, despite them being exactly its governance content.

### Finding 2: No skill keeps layer→skill attribution in sync — this is the real, generalized version of what HO-007 was gesturing at

- `plans/layers/index.yaml` and `master.md` both date to a **2026-06-26 bootstrap snapshot**. Every layer L01–L27's `skill_ids:` array reflects the registry as it stood that day.
- The registry has grown from ~71 skills to **149** since. Result: **90 of 149 skills (60%) are attributed to no layer at all.** The two layers created *after* the bootstrap (L28 Certification, L29 Operational Control) are fully accurate — proving the gap is a maintenance process failure, not a capability failure.
- The one skill that could plausibly catch this, `/reconcile-layer-index`, is explicitly scoped to compare only `layer_id`/`status`/`maturity_current` — its own spec never touches `skill_ids` or cross-references `.supervisor/skill-registry.yaml`.
- `master.md` is also wrong about its own layer count: header says 28, prose says "27 accepted independent layers," `index.yaml` actually contains 29.
- Five different files report five different total-skill-counts: `README.md` says 123, `PROJECT_STATUS.md` says 120/119, `.supervisor/skill-inventory.yaml` says 145, `master.md` says 74, the raw registry has 149.

### Finding 3: Genuine zero-coverage layers (not bookkeeping — actually no owner)

| Layer | Status |
|---|---|
| L04 Sample Corpus | Zero skill coverage; `master.md` itself says "Need corpus-governance skill" |
| L14 Feature Compilation | Zero coverage in `index.yaml`, but tracked as `SKILL-GAP-003` — resolved directly via TC-EXT-009 |
| L15 Source Change Handoff | Zero coverage, not previously tracked |
| L17 Regression Compatibility | Zero coverage, not previously tracked |
| L19 Consumer API | Zero coverage, not previously tracked |
| L20 Security and Legal | Zero coverage, not previously tracked |
| L24 Metrics and Product Velocity | Zero coverage, not previously tracked |

Also found: `acquisition` (5 skills) is a `product_track` with no corresponding layer anywhere in the 29-layer taxonomy.

### Finding 4: Two of the 14 originally-deferred external candidates are exactly the fix for real, distinct gaps found in Part 1

- **audit-context-building** (Trail of Bits) — FF's threat-model practice explicitly excludes `tools/supervisor/` and `tools/governance/`, the high-privilege autonomous-execution codebase. Zero audit coverage there.
- **trailmark** (Trail of Bits) — FF's only blast-radius mechanism is reactive, manual, single-pattern grep, invoked only after a bug is already found. Proactive codebase-wide mapping doesn't exist.

### Finding 5 (see original Groups 5/6 crosswalk): 5 promoted to active import, 9 confirmed as genuinely not needed.

### Finding 6: SKILL-GAP-003 (`capability_compiler` / Layer 14) — real code exists, closure was incomplete, and it's fragmented across 8 files

- Real, working code already exists: `tools/supervisor/capability_compiler.py` (521 lines) implements Phases 0,1,2,3,3.5,6,7,8 of the Lane 3 compiler design, and `capability_queue_consumer.py` already runs it automatically every sprint.
- A closure was already attempted and is incomplete: `.supervisor/skill-gap-003-closure-proof.yaml` declared `DEFERRED_BY_DESIGN` but only wrote the closure-proof file — 3 registries still list this as an open gap today.
- The compiler's output isn't consumed: `autonomous_task_generator.py` never reads `.local/capability-consumer/taskcards/`.
- 8 files carry overlapping/confusing names, several self-declared orphaned but never removed.

### Finding 7: SKILL-GAP-008 (`pre_sprint_governance_hook`) — the detection logic exists and runs, but the "non-negotiable" enforcement has two live loopholes

- Detection already exists and already runs pre-sprint (`check_continuation.py` Check 8 + `governance_block_registry.py`).
- Not a registered skill.
- A real, live bug: both `sprint_executor.py` and `autonomous-loop.md` currently let the "NON-OVERRIDABLE" GOV_BLOCK stop condition fall through to a generic override branch and proceed anyway.
- Secondary drift: `governance_block_registry.py` now names 6 structural validators; CLAUDE.md's binding text still names only 4.
- Gap-ID collision: `SKILL-GAP-008` was already used and closed for a different, unrelated item.

### Finding 8 (minor): `SKILL-GAP-011` stale (already resolved, tracking file not updated); `/detect-duplicate-skills` structurally can't catch orphaned deprecations (no actual harm found); 4 active L28-Certification skills lag the capability registry.

### Verified Source Inventory

| Source | Repo | License | Total skills | Confirmed relevant |
|---|---|---|---|---|
| Superpowers | `obra/superpowers` | MIT | 14 | 12 |
| Trail of Bits Skills | `trailofbits/skills` | **CC-BY-SA-4.0** ⚠ | 40 | 20 verified real |
| Sentry Skills | `getsentry/skills` | Apache-2.0 | 28 | 9 confirmed |
| GitHub Awesome Copilot | `github/awesome-copilot` | MIT | 100s | 22/23 confirmed |
| Anthropic Skills examples | `anthropics/skills` | ⚠ no repo LICENSE | 17 | 5 confirmed |
| Anthropic PR Review Toolkit | `anthropics/claude-code` (mirrored in `claude-plugins-official`) | Apache-2.0 (mirror) | 6 | 6 confirmed |
| wshobson/agents (plugin-eval) | `wshobson/agents` | MIT | 1 relevant subdir | community — reference only |
| Vercel / Cloudflare | — | MIT / Apache-2.0 | — | 0 — confirmed irrelevant |
| openai/plugins | — | none detected | 100+ | 0 — refuted claims |

### Candidate Crosswalk

See §2 Requirement Inventory for the group→REQ mapping; the full per-candidate disposition table from the original analysis (Groups 0, 2–9) is unchanged from the prior version of this plan and governs every TC-EXT-01x/02x taskcard's scope above.

---

## 9. Validation Matrix (per-taskcard-type, referenced from every taskcard above)

artifact_role: analysis_or_evidence_only | execution_authority: false

| Check | Type | Command/Method | Mandatory | Applies to |
|---|---|---|---|---|
| `/preflight-skill-entry` PASS | schema_validation | run skill | yes | every new skill_id |
| `/sync-skill-command-registry` `auto_repaired: 0` on 2nd run | rerun_idempotency_validation | run skill twice | yes | every new skill_id |
| `/detect-duplicate-skills` no DUPLICATE | negative_control | run skill | yes | every new skill_id |
| `/validate-skill-contracts` PASS | schema_validation | run skill | yes | every new skill_id |
| TC-EXT-005 extended `/reconcile-layer-index` shows 0 unattributed | integration_test | run skill | yes | every new skill_id (the integration guarantee) |
| Activation gate cleared per §7.0 risk classification | config_enforcement | Supervisor review/approval per §7.0 table — no per-instance human stop for any of the 26 imports | yes | every external import |
| SCM-POLICY-CHECK-001 precondition confirmed | config_enforcement | policy-state read per §7.2 | yes | TC-EXT-016, 021, 027, 028 only |
| Negative control: no `hooks/*.json`/SessionStart/Stop-hook file introduced | negative_control | grep for "hooks.json"/"SessionStart"/"Stop hook" across all new skill files | yes | TC-EXT-019, TC-EXT-022, TC-EXT-023 (the 3 taskcards with explicit hook/push exclusions) |
| Evidence declaration + skill invocation transcript | generated_artifact_inspection | .local/evidences/<run_id>/ | yes | every taskcard |
| Focused test/dry-run per taskcard's own Integration checks field | unit_test / integration_test | as specified per taskcard | yes | every parent |

---

## 10. Reconciliation & Traceability Audit

artifact_role: analysis_or_evidence_only | execution_authority: false

```yaml
single_plan_authority: yes            # only this file + its Section-100 pointer; no plan-v2/final-plan/replacement-plan created
every_finding_mapped_to_req: yes       # §2 covers Findings 1-8 and Groups 0/2-9
every_req_mapped_to_parent: yes        # §6/§7, one parent per REQ-EXT-*
every_parent_has_children: yes         # Wave 0: full child+microstep; Waves A/C/D/E/G/H/Security: full child+microstep as of this pass (§7), grounded in real fetched content, no fabrication
no_actionable_item_lost: yes           # original flat 28-row taskcard table's content is now the parent-level Title/Objective of each hierarchical taskcard — nothing dropped, only decomposed
contradictions_resolved: [HO-007 stale status, master.md 28/27/29 layer count, SKILL-GAP-003 incomplete closure, SKILL-GAP-008 override loopholes, SKILL-GAP-011 stale status]
dependency_dag_present: yes            # §5
file_ownership_present: yes            # §5
duplicate_taskcard_check: "no duplicate TC-EXT-* IDs; stable IDs reused from the prior version of this plan (000,001,003-010,012-028) — no renumbering on this pass, satisfying the idempotency/stable-ID rule for any future rerun"
```

---

## 11. Execution Handoff

A future execution agent picking up this plan must:

1. Read this plan file in full (it is the sole authoritative source — `plans/master-plan.md` Section 100 only points here).
2. Read the next READY parent taskcard per the Dependency DAG (§5) — start with `TC-EXT-000` and `TC-EXT-001` (parallel-safe, no dependencies), or any of `TC-EXT-003/004/005/008/009/010` (also independent of each other per §5).
3. Read that parent's child taskcard list; select the first child in `READY`/`TODO` state.
4. Read the exact micro-step table for that child; execute exactly one micro-step at a time, in order. Every parent in this plan (Wave 0 and Waves A/C/D/E/G/H/Security alike) now has full micro-step decomposition — there is no remaining investigation-gated child.
5. Before executing any child of TC-EXT-016, TC-EXT-021, TC-EXT-027, or TC-EXT-028, confirm the SCM-POLICY-CHECK-001 precondition (§7.2) — a policy-state read, not a request for a human to approve this taskcard. If policy already authorizes: proceed. If not: classify as `EXTERNAL_BLOCKER` per CLAUDE.md's existing pattern and continue with the next `READY` taskcard elsewhere in the DAG rather than stopping the whole plan.
6. For TC-EXT-019, TC-EXT-022, and TC-EXT-023: confirm the explicit exclusions (§7.1 item 3) before closing — grep for "hooks.json"/"SessionStart"/"Stop hook"/"push to fork" across the new/edited files and confirm zero matches. This is a mandatory negative control, not optional.
7. Confirm allowed/forbidden paths from the parent's `Scope` field before touching any file.
8. Capture evidence immediately per §3's `evidence_contract` (reuses `.local/evidences/<run_id>/`, no new evidence model invented).
9. Update micro-step state, then child state, then parent state per §3's transition rules — never skip a state, never close a parent before all mandatory children are `CLOSED`.
10. Run the child's acceptance checks; score against §3's quality dimensions; if any mandatory dimension scores below 4, mark `REROUTED` and reopen the smallest necessary unit — do not reopen the whole taskcard.
11. Run the parent's Integration checks only after all children are `CLOSED`; close the parent only after those pass.
12. Continue to the next `READY` taskcard per the DAG — do not choose unrelated work, do not broaden scope, do not treat code existence or test existence alone as proof of verification. No step in this plan requires stopping to ask a human, except the `EXTERNAL_BLOCKER` classification in step 5 if the standing SCM policy genuinely isn't yet authorized — and even then, the agent continues with other `READY` work rather than halting.

**Next valid parent taskcard:** `TC-EXT-000` (or any of `TC-EXT-001/003/004/005/008/009/010` in parallel, per §5).
**First micro-step:** `MS-000-01-01`.

---

## 12. Final Verdict

```yaml
VERDICT: PLAN_MICRO_TASKCARDIZED_READY_FOR_EXECUTION
verdict_change_from_prior_pass: >
  Previous pass was PLAN_MICRO_TASKCARDIZED_WITH_LIMITATIONS for two reasons, both
  resolved this pass: (1) full verbatim upstream content was fetched for all 26
  external skills (not just existence + one-line description), enabling honest
  Level-5 micro-step decomposition for every parent, not just Wave 0 — see §7.3.
  (2) the human-gate question was resolved by explicit reconciliation (§7.1)
  between docs/governance/external-tool-architecture.md's broader "Supervisor +
  human authorization" language and CLAUDE.md's Supreme Directive, which is the
  later, explicitly-overriding, narrower authority (3 named TRUE_EXTERNAL_GATEs
  only). Two genuine hook/daemon mechanisms (skill-improver's Stop hook,
  modern-python's SessionStart hook) and one push/PR deployment step
  (writing-skills) are excluded from import entirely rather than gated — this is
  an engineering scope decision (FF already owns its own continuation mechanism;
  a second competing one is a real redundancy/risk, not a formality to route
  around), not a safety bypass. One standing, one-time policy precondition
  (§7.2, SCM-POLICY-CHECK-001) governs the 4 taskcards that post PR comments,
  edit CI config, or push branches — this is FF's own pre-existing SCM Agent
  policy model, not a new gate invented by this plan, and it is a policy-state
  read, not a per-instance human stop.
Active Plan:
  authoritative_path: plans/.claude/yes-my-earlier-answer-humming-waffle.md (this file, pending Step-0 copy+lock on exit from plan mode)
  authority_source: CLAUDE.md Step 0 + new Section 100 in plans/master-plan.md
  duplicate_active_plans_found: 0
  duplicate_risk_resolved: yes
Plan Analysis:
  sections_analyzed: all (Context, Part 1 x8 Findings, Part 2 x10 Groups, all 28 taskcards, all 26 external-skill full bodies)
  actionables_extracted: 28 parent taskcards, all with full child+micro-step decomposition
  investigation_taskcards_created: 0 remaining — all 17 that were investigation-gated in the prior pass are now resolved with real fetched content
Decomposition:
  parent_taskcards: 28
  child_taskcards: 71 (Wave 0) + approx. 75 (Waves A/C/D/E/G/H/Security, §7.3)
  micro_steps: approx. 210 (Wave 0) + approx. 180 (Waves A+, §7.3) — all grounded in verbatim fetched content, none fabricated
Machine State: added (shared §3), invalid transitions explicitly blocked, dependency DAG in §5, file ownership in §5, 4 taskcards additionally carry the SCM-POLICY-CHECK-001 precondition (§7.2)
Risk Classification: all 26 external imports classified per FF's own existing criteria (§7.0); 20 LOW/MEDIUM (fully autonomous, no human involvement); 6 originally HIGH, of which 2 mechanisms are excluded entirely (not merely gated) and 4 route through FF's existing standing SCM-policy model rather than a per-instance stop (§7.1)
Traceability: all findings mapped to REQ IDs (§2); all REQ IDs mapped to parents; all children mapped to micro-steps; all micro-steps carry completion checks and evidence columns
Single Plan Authority: yes — one file, one Section-100 pointer, no competing plan created
Execution Readiness:
  ready: yes — the entire plan, not just Wave 0
  blockers: none that require a human to act mid-execution; SCM-POLICY-CHECK-001 is a one-time policy-state read the agent performs itself
  deferred: none
  next_valid_parent_taskcard: TC-EXT-000
  first_micro_step: MS-000-01-01
```
