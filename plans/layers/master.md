# Format Factory Permanent Layer Master Plan

```yaml
control_plane_binding:
  mission_id: FORMAT-FACTORY-LAYER-MASTER-20260626
  repository: c:\Users\prora\OneDrive\Documents\GitHub\format-factory
  branch: main
  head: a7744cf6
  layer_root: plans/layers/
  master_path: plans/layers/master.md
  index_path: plans/layers/index.yaml
  task_register_path: plans/layers/task-register.yaml
  handoff_register_path: plans/layers/handoff-register.yaml
  dependency_register_path: plans/layers/dependency-register.yaml
  decision_register_path: plans/layers/decision-register.yaml
  change_ledger_path: plans/layers/change-ledger.jsonl
  bootstrap_session: "923e237958c1"
  bootstrap_sprint: "lp-bootstrap"
  bootstrap_date: "2026-06-26"
  total_layers: 30
  total_permanent_files: 36
```

---

## 1. Purpose and Authority

This document is the **permanent, continuously maintained master plan** for the
Format Factory layer architecture. It is the entry point for every assistant,
autonomous agent, and supervisor that needs to understand the system.

**Authority hierarchy:**
1. `CLAUDE.md` — session instructions (highest authority)
2. `AGENTS.md` — agent governance
3. `plans/master-plan.md` — strategic project plan
4. `plans/strategic/spec-to-feature-radical-correction-plan.md` — lane architecture authority
5. `plans/layers/master.md` (this file) — layer architecture and execution state
6. Individual layer files — detailed per-layer state and tasks
7. `reports/supervisor/next-sprint.md` — current sprint prompt (advisory)

**This file summarizes** the complete architecture.
**Detailed logs** remain in individual permanent layer files.

## 2. Current Repository Binding

- **HEAD:** a7744cf6 (branch: main)
- **Python formats:** 20 packages (fods, fodt, ods, odt, fodg, fodp, xcf, zst, ndjson, toml, csv, tsv, abw, dif, gnumeric, sylk, qoi, pbm, pgm, ppm)
- **.NET formats:** 10+ packages
- **Governance validators:** 85 (V1-V82 + SAL validators)
- **Registered skills:** 151 (148 active, 2 deprecated, 1 deferred) — reconciled 2026-07-14 via TC-EXT-007 against `.supervisor/skill-registry.yaml`; other figures in this binding block (HEAD, validator count, test count, SAL facts) remain the original 2026-06-26 bootstrap snapshot and are out of this taskcard's scope
- **Tests passing:** 1,609
- **SAL facts:** 14,441 (6/20 formats covered)
- **QName coverage:** 99.4% (65/66 active entries)
- **Oracle status:** ALL 20 Python formats VERIFIED (73/73 PASS)

## 3. Governance Contract

```
EVERY GOVERNED TASK MUST HAVE:
1. ONE PRIMARY LAYER → plans/layers/index.yaml
2. ONE PERMANENT LAYER PLAN → plans/layers/{slug}.md
3. ONE REGISTERED TASKCARD → plans/layers/task-register.yaml
4. REGISTERED SKILLS AND COMMANDS → .supervisor/skill-registry.yaml
5. A PRE-WORK LOG → layer file §34 Work Log
6. LIVE PROGRESS LOGS → layer file §34 Work Log (append per event)
7. VERIFICATION EVIDENCE → layer file §35 Verification Log
8. A POST-WORK UPDATE → layer file §29-§32 taskcards, §9 current state
9. A CURRENT SESSION HANDOFF → layer file §36

NO PRIMARY LAYER → NO WORK
NO PERMANENT LAYER FILE → NO WORK
NO PRE-WORK PLAN UPDATE → NO WORK
NO TASKCARD → NO WORK
NO REGISTERED SKILL → NO WORK
NO WORK LOG → NO CONTINUATION
NO VERIFICATION LOG → NO CLOSURE
NO MASTER/INDEX SYNC → NO SPRINT CLOSURE
```

## 4. Canonical Layer Taxonomy

30 accepted independent layers across 4 architecture planes. See `plans/layers/decision-register.yaml`
for full taxonomy decisions (DEC-001 through DEC-028; L30 Format Contract Layer added by DEC-038,
mission FCL-MACHINERY-2026-07-16).

**Merged:** `taskcard-work-queue-layer` → merged into L10 plan-prompt-authority-layer (DEC-015)

## 5. Architecture Planes

| Plane | Layer IDs | Purpose |
|-------|-----------|---------|
| SYSTEM_HEALING | L01, L02, L03, L04, L14, L27, L30 | Spec pipeline: SAL → QName → Contract → Capability → Feature |
| PRODUCT | L06, L07, L15, L16, L17, L18, L19 | Product source, tests, release |
| GOVERNANCE | L08, L09, L10, L11, L12, L13, L20, L21, L22, L23, L24, L25, L26 | Execution control, policy, evidence |
| ORACLE | L05 | Conformance verification |

## 6. Permanent Layer Index

| Layer | Permanent Plan | Status | Maturity | Target | Next Task | Blockers |
|-------|---------------|--------|----------|--------|-----------|---------|
| L01 SAL | specification-authority-layer.md | HARDENING_REQUIRED | 2/5 | 4 | TC-SAL-001 | None |
| L02 QName | qname-hierarchy-layer.md | GOVERNED_OPERATIONAL | 3/5 | 4 | TC-QN-001 | TC-SAL-001 |
| L03 Capability | capability-layer.md | HARDENING_REQUIRED | 3/5 | 4 | TC-CAP-001 | None |
| L04 Corpus | corpus-layer.md | NOT_ASSESSED | 2/5 | 3 | TC-CORP-001 | None |
| L05 Oracle | oracle-layer.md | GOVERNED_OPERATIONAL | 4/5 | 4 | TC-ORC-004 | None |
| L06 Product | product-architecture-layer.md | EXECUTION_IN_PROGRESS | 4/5 | 5 | Continue S141+ | Gate 11 |
| L07 Tests | test-infrastructure-layer.md | GOVERNED_OPERATIONAL | 4/5 | 5 | TC-TEST-001 | None |
| L08 Evidence | evidence-review-layer.md | GOVERNED_OPERATIONAL | 4/5 | 4 | TC-EV-001 | None |
| L09 State | state-continuation-layer.md | GOVERNED_OPERATIONAL | 4/5 | 4 | TC-STATE-001 | None |
| L10 Plan | plan-prompt-authority-layer.md | HARDENING_REQUIRED | 3/5 | 4 | TC-PLAN-001 | None |
| L11 Supervisor | supervisor-sprint-layer.md | GOVERNED_OPERATIONAL | 5/5 | 5 | TC-SUP-001 | None |
| L12 Validation | validation-policy-layer.md | GOVERNED_OPERATIONAL | 4/5 | 5 | TC-VAL-001 | None |
| L13 Skills | skills-layer.md | GOVERNED_OPERATIONAL | 4/5 | 5 | TC-SKILL-001 | None |
| L14 Feature | feature-compilation-layer.md | NOT_ASSESSED | 0/5 | 4 | TC-FEAT-001 | TC-CAP-001 |
| L15 Handoff | source-change-handoff-layer.md | NOT_ASSESSED | 1/5 | 3 | TC-SCH-001 | None |
| L16 Dogfood | product-output-dogfood-layer.md | NOT_ASSESSED | 1/5 | 3 | TC-DOG-001 | None |
| L17 Regression | regression-compatibility-layer.md | NOT_ASSESSED | 1/5 | 3 | TC-REG-001 | None |
| L18 Release | package-release-layer.md | NOT_ASSESSED | 1/5 | 3 | TC-PKG-001 | Gate 11 |
| L19 ConsumerAPI | consumer-api-layer.md | NOT_ASSESSED | 1/5 | 3 | TC-CAPI-001 | None |
| L20 Security | security-legal-layer.md | NOT_ASSESSED | 1/5 | 3 | TC-SEC-001 | None |
| L21 AIBoundary | ai-acceleration-boundary-layer.md | NOT_ASSESSED | 2/5 | 4 | TC-AIB-001 | Gate 11 |
| L22 ExtTools | external-tool-governance-layer.md | NOT_ASSESSED | 1/5 | 3 | TC-EXT-001 | None |
| L23 Knowledge | knowledge-discoverability-layer.md | NOT_ASSESSED | 1/5 | 3 | TC-KNOW-001 | None |
| L24 Metrics | metrics-product-velocity-layer.md | NOT_ASSESSED | 1/5 | 3 | TC-MET-001 | None |
| L25 Recovery | recovery-rollback-layer.md | NOT_ASSESSED | 1/5 | 3 | TC-REC-001 | None |
| L26 Provenance | provenance-artifact-identity-layer.md | NOT_ASSESSED | 2/5 | 4 | TC-PROV-001 | None |
| L27 Obligation | format-language-obligation-layer.md | NOT_ASSESSED | 1/5 | 3 | TC-OBL-001 | None |
| L28 CertAudit | certification-audit-layer.md | GOVERNED_OPERATIONAL | 4/5 | 4 | TC-CERT-L-003 | None |
| L29 OpControl | operational-control-record-layer.md | GOVERNED_OPERATIONAL | 4/5 | 5 | Extend trust_registry | None |
| L30 FormatContract | format-contract-layer.md | GOVERNED_OPERATIONAL | 3/5 | 4 | TC-FCL-090 | None |

## 7. Layer Dependency Graph

```
External Specs
    ↓
[L01 SAL] ──────────────────────→ [L02 QName] → [L30 Format Contract] → [L03 Capability] → [L14 Feature Compiler]
                                       (L27 Obligation → L30 when mature)
    ↓                                                                        ↓
    └────────────────────────────��─────────────────────────��───→ [L06 Product Architecture]
                                                                             ↓
[L04 Corpus] ──────────────────────────��──→ [L05 Oracle] ←──────────────────┘
                                                 ↓
[L06 Product] ──→ [L07 Tests] ──→ [L08 Evidence] ──→ [L11 Supervisor]
     ↓                                                       ↑
[L15 Handoff]                                          [L09 State]
[L16 Dogfood]                                          [L10 Plan]
[L17 Regression]                                       [L12 Validation]
     ↓                                                  [L13 Skills]
[L18 Release] (BLOCKED: Gate 11)
     ↓
[L19 Consumer API]

Cross-cutting (governance plane, run in parallel):
L20 Security, L21 AIBoundary, L22 ExtTools, L23 Knowledge, L24 Metrics, L25 Recovery, L26 Provenance, L27 Obligation, L28 CertAudit, L29 OpControl
```

## 8. Cross-Layer Handoff Matrix

See `plans/layers/handoff-register.yaml` for full records.

| HO ID | Producer | Consumer | Artifact | Status |
|-------|----------|----------|---------|--------|
| HO-001 | L01 SAL | L02 QName | sal-facts-latest.json | PENDING |
| HO-002 | L01 SAL | L03 Capability | sal-facts-latest.json | PENDING |
| HO-003 | L03 Capability | L14 Feature | gap-ledger.json | NOT_STARTED |
| HO-004 | L05 Oracle | L07 Tests | oracle-package.yaml VERIFIED | ACTIVE |
| HO-005 | L10 Plan | L11 Supervisor | plans/layers/index.yaml | PENDING |
| HO-006 | L12 Validation | L08 Evidence | primary_layer_id field | NOT_STARTED |
| HO-007 | L13 Skills | L11 Supervisor | 19 new skills in registry | CLOSED |

## 9. Current Maturity Matrix

| Layer | Current L | Target L | Gap |
|-------|-----------|----------|-----|
| L01 SAL | 2 | 4 | 17 tools dormant, 14 formats with 0 facts |
| L02 QName | 3 | 4 | 99.4% coverage; 4 new formats pending |
| L03 Capability | 3 | 4 | Task generator doesn't read gap-ledger |
| L04 Corpus | 2 | 3 | No governance, unknown coverage |
| L05 Oracle | 4 | 4 | At cap (execute_oracle.py 1428/1428) |
| L06 Product | 4 | 5 | Gate 11 execution blocked |
| L07 Tests | 4 | 5 | Some formats < 3 tests |
| L08 Evidence | 4 | 4 | provenance_chain not enforced |
| L09 State | 4 | 4 | Layer control plane not in signal |
| L10 Plan | 3 | 4 | 6 hardening addenda (fragmentation) |
| L11 Supervisor | 5 | 5 | Overclaim detector never called |
| L12 Validation | 4 | 5 | V83-V86 not yet created |
| L13 Skills | 4 | 5 | 19 layer-maintenance skills missing |
| L14 Feature | 0 | 4 | Does not exist |
| L15-L27 | 1-2 | 3-4 | NOT_ASSESSED |
| L28 CertAudit | 4 | 4 | None — at target (execute_oracle-style cap) |
| L29 OpControl | 4 | 5 | Extend trust_registry population; add quarantine lifecycle transitions |

## 10. Target Maturity Matrix

Target state when all gaps are closed:
- L01: 4 (all formats have SAL facts)
- L02: 4 (100% coverage)
- L03: 4 (gap-ledger drives task selection)
- L04: 3 (governed manifest per format)
- L05: 4 (execute_oracle.py refactored)
- L06: 5 (Gate 11 executed, commercial release)
- L07: 5 (all formats ≥3 roundtrip tests)
- L08: 4 (provenance_chain enforced)
- L09: 4 (layer tracking in continuation)
- L10: 4 (addenda merged, task register consumed)
- L11: 5 (overclaim detector called, layer index consumed)
- L12: 5 (V83-V86 active)
- L13: 5 (all skill gaps closed, V46 FAIL)
- L14: 4 (9-phase compiler implemented)

## 11. Global Gap Summary

**Critical system gaps (block downstream work):**
1. L01-SAL: 14/20 formats have ZERO spec facts → breaks spec parity chain
2. L03-Capability: task generator hardcoded → capability layer output not consumed
3. L14-Feature: does not exist → missing bridge capability → product
4. L11-Supervisor: overclaim detector never called → false ACCEPTED_VERIFIED verdicts possible

**Significant gaps (reduce quality):**
5. L12-Validation: V83-V86 missing → no layer-plan enforcement in declarations
6. L13-Skills: 19 layer-maintenance skills missing → layer operations lack canonical skill paths
7. L06-Product: Gate 11 execution blocked → commercial release blocked
8. L10-Plan: 6 addenda fragments authority

**Infrastructure gaps:**
9. L04-Corpus: no governance
10. L15-L27: NOT_ASSESSED (13 layers)

## 12. Critical Machinery Gaps

| Gap | Layer | Severity | Root Cause | Blocker |
|-----|-------|----------|------------|---------|
| SAL facts missing | L01 | CRITICAL | 17 tools dormant since 2026-05-06 | None (run TC-SAL-001) |
| Capability disconnect | L03 | CRITICAL | Hardcoded _EXPANSION_GOALS in task generator | None (run TC-CAP-001) |
| Feature compiler absent | L14 | CRITICAL | Lane 3 not started | TC-CAP-001 |
| Overclaim detector uncalled | L11 | HIGH | Prompt-only enforcement | None |

## 13. Critical Product Gaps

| Gap | Layer | Severity | Blocker |
|-----|-------|----------|---------|
| Gate 11 execution | L06, L18 | CRITICAL | Babar Raza sign-off (TRUE_EXTERNAL_GATE) |
| .NET deepening S141+ | L06 | MEDIUM | None (continue per next-sprint.md) |
| Oracle LOC cap refactor | L05 | LOW | None |

## 14. Active Layer Work

**TC-LP-001** (L10, IN_PROGRESS, this session): Create permanent layer control plane

## 15. Ready Layer Work

After TC-LP-001 completes:

**Wave 1 (parallel, system healing):**
- TC-SAL-001 (L01): Activate dormant tools, run extraction
- TC-CAP-001 (L03): Wire gap-ledger to task generator
- TC-VAL-001 (L12): Add V83-V86 validators
- TC-SKILL-001 (L13): Register 19 micro-skills

**Wave 2 (after Wave 1):**
- TC-SUP-001 (L11): Code-enforce lane ownership
- TC-SUP-002 (L11): Consume layer index
- TC-FEAT-001 (L14): Design 9-phase compiler

## 16. Blocked Layer Work

- TC-PKG-001 (L18): Gate 11 execution (TRUE_EXTERNAL_GATE — Babar Raza)
- TC-FEAT-001 (L14): depends on TC-CAP-001
- TC-QN-001 (L02): depends on TC-SAL-001

## 17. Recently Verified Work

- Oracle layer: ALL 20 Python formats VERIFIED (73/73 PASS) — 2026-06-26
- QName coverage: 99.4% — 2026-06-26
- Governance validators: 138 tests PASS — 2026-06-26
- FODS Gate 11 G11-G APPROVED — 2026-06-05

## 18. Current Execution Waves

**Wave 0 (COMPLETE):** Layer control plane bootstrap (TC-LP-001)

**Wave 1 (NEXT, parallel):**
- TC-SAL-001: SAL pipeline activation
- TC-CAP-001: Capability reconnection
- TC-VAL-001: Layer validators
- TC-SKILL-001: Layer maintenance skills

**Wave 2 (after Wave 1):**
- TC-SUP-001: Supervisor lane enforcement
- TC-FEAT-001: Feature compiler design

**Wave 3 (ongoing):**
- L06 Product deepening (S141+ per next-sprint.md)
- L05 Oracle refactor (TC-ORC-004)
- L10 Plan hardening (TC-PLAN-001)

## 19. Parallel Work Lanes

Layers that can run in parallel (no dependency conflicts):
- L01+L03 (both need no upstream)
- L12+L13 (no dependency between them)
- L06 product deepening + any governance work
- L05 oracle refactor + all other layers

## 20. Shared Mutation Ownership

| Shared Path | Primary Owner | Secondary |
|-------------|--------------|-----------|
| tools/supervisor/ | L11 | L12 |
| .supervisor/skill-registry.yaml | L13 | L11 |
| plans/layers/ | L10 | L11 (reads) |
| registry/ | L06 | L02, L27 |
| oracle/ | L05 | L27 |

## 21. Skill and Command Coverage

| Layer | Skills | Commands | Gaps |
|-------|--------|---------|------|
| L01 SAL | 2 | 2 | None |
| L02 QName | 2 | 2 | None |
| L03 Capability | 2 | 2 | None |
| L04 Corpus | 0 | 0 | Need corpus-governance skill |
| L05 Oracle | 1 | 1 | None |
| L06 Product | 6 | 6 | None |
| L07 Tests | 2 | 2 | None |
| L08 Evidence | 3 | 3 | None |
| L09 State | 0 | 0 | None |
| L10 Plan | 3 | 3 | None |
| L11 Supervisor | 3 | 3 | None |
| L12 Validation | 3 | 3 | None |
| L13 Skills | 29 | 25 | None — 19 layer-maintenance skills closed via TC-LP-023 (HO-007 CLOSED, see master-plan.md:4853-4869) |
| L14 Feature | 0 | 0 | SKILL-GAP-003 |
| L15-L27 | 1-3 | 1-3 | Most NOT_ASSESSED |
| L28 CertAudit | 13 | 13 | None |
| L29 OpControl | 10 | 10 | None |

## 22. Supervisor Work-Selection Contract

The autonomous supervisor MUST:

1. **Load** `plans/layers/master.md` (this file)
2. **Load** `plans/layers/index.yaml`
3. **Load** `plans/layers/task-register.yaml`
4. **Validate** index.yaml consistency with layer files
5. **Find** ready tasks (status=TODO, dependencies met)
6. **Select** task with highest priority from ready set
7. **Read** the permanent layer plan file for that task
8. **Read** §36 Current Session Handoff
9. **Claim** task: update task-register.yaml status=IN_PROGRESS
10. **Execute** using registered skills from .supervisor/skill-registry.yaml
11. **Log** progress to layer file §34 Work Log
12. **Verify** per layer file §38 completion gate
13. **Update** layer file §9, §29-§31, §35, §36
14. **Update** master.md §14-§17 (active, ready, blocked, recently verified)
15. **Update** index.yaml layer status
16. **Close** task in task-register.yaml

**GAP-SUP-002 (CONFIRMED, DEFERRED — 2026-07-13):**
- `generate_next_worker_prompt.py` reads: POC targets, gap fixtures, review grades.
- It does NOT read `plans/layers/task-register.yaml`.
- G1-G8 train groups are hardcoded in GROUP_DEFS (lines 104-113 of generate_next_worker_prompt.py).
- A G9 layer-task group would require modifying `synthesize_trains()` (lines 181-440).
- This is a separate sprint. Until TC-SUP-002 is implemented, layer tasks are INVISIBLE
  to the autonomous supervisor. They must be manually scheduled in next-sprint.md.
- Affected tasks: TC-CERT-L-003 (now CLOSED), TC-SAL-001, TC-QN-001, TC-SUP-001,
  TC-FEAT-001, and all other TODO tasks in task-register.yaml.
- See `docs/governance/layer-promotion-guide.md` for the manual scheduling workaround.

## 23. Current Session Summary

**Session:** 923e237958c1
**Sprint:** lp-bootstrap
**Objective:** Create permanent layer control plane (TC-LP-001)
**Status:** TC-LP-001 IN_PROGRESS
**Files created:** 34 (7 registers + 27 layer files)
**Last updated:** 2026-06-26

## 24. Global Session Handoff

```yaml
global_session_handoff:
  handoff_id: GSH-001
  generated_at: "2026-06-26T00:00:00Z"
  repository_revision: a7744cf6
  session_id: "923e237958c1"
  active_work: TC-LP-001 (lp-bootstrap)
  status: IN_PROGRESS
  completed_files: 34
  pending_tasks:
    - TC-LP-023: Register 19 layer-maintenance micro-skills
    - TC-LP-024: Add governance validators V83-V86
    - TC-LP-025: Idempotency verification and evidence
  next_session_priority: >
    Complete TC-LP-023 (skills) and TC-LP-024 (validators) as highest priority.
    Then begin Wave 1: TC-SAL-001, TC-CAP-001 in parallel.
  resume_instructions: >
    READ plans/layers/master.md (this file) → READ plans/layers/index.yaml →
    FIND ready tasks → READ permanent layer plan → EXECUTE.
    DO NOT start from session-resume.md when a per-chat plan is active.
```

## 25. Exact Next Dependency-Valid Work

**Immediately executable (no blockers):**
1. TC-SKILL-001 (L13): Register 19 layer-maintenance micro-skills
2. TC-VAL-001 (L12): Add V83-V86 governance validators
3. TC-SAL-001 (L01): Activate dormant SAL tools (run /sal-pipeline-heal)
4. TC-CAP-001 (L03): Wire gap-ledger.json to autonomous task generator

**After TC-SAL-001:**
- TC-QN-001 (L02): Add QName entries for new formats

**After TC-CAP-001:**
- TC-FEAT-001 (L14): Design 9-phase feature compiler

**External gate (cannot unblock autonomously):**
- TC-PKG-001 (L18): Awaiting Babar Raza Gate 11 execution sign-off

## 26. Layer Completion Accounting

| Plane | Layers | At Target | In Progress | Not Started |
|-------|--------|-----------|-------------|------------|
| SYSTEM_HEALING | 6 | 0 | 2 (L01, L03) | 4 |
| PRODUCT | 7 | 0 | 1 (L06) | 6 |
| GOVERNANCE | 15 | 2 (L11, L28) | 5 (L08, L09, L12, L13, L29) | 8 |
| ORACLE | 1 | 1 (L05) | 0 | 0 |
| **TOTAL** | **29** | **3** | **8** | **18** |

## 27. Master Change History

| Date | Session | Change | Files Affected |
|------|---------|--------|----------------|
| 2026-06-26 | 923e237958c1 | Bootstrap: created permanent layer control plane | 34 files in plans/layers/ |

---

## Startup Sequence for Every Assistant

Before any work:

```
READ plans/layers/master.md  ← YOU ARE HERE
→ READ plans/layers/index.yaml  (layer statuses)
→ IDENTIFY PRIMARY LAYER for your task
→ READ the permanent layer plan file (plans/layers/{slug}.md)
→ READ §36 Current Session Handoff in that file
→ VERIFY the taskcard in plans/layers/task-register.yaml
→ UPDATE the layer file §34 Work Log (pre-work entry)
→ RESOLVE skills from .supervisor/skill-registry.yaml
→ BEGIN WORK
→ LOG meaningful progress to layer file §34
→ VERIFY per layer file §38 completion gate
→ UPDATE layer file §9, §29-§31, §35, §36
→ UPDATE plans/layers/index.yaml (layer status)
→ UPDATE plans/layers/master.md §14-§17
→ CLOSE task in plans/layers/task-register.yaml
```

**NEVER start work without identifying the primary layer and reading its permanent plan.**


## 2026-06-29 layer completion pass

All individual layer markdown files were expanded from stub/shallow state into the standard 39-section governed layer plan pattern. The pass preserves existing metadata shape where possible and adds authority, scope, gaps, contracts, evidence, rollback, taskcard, handoff, next-action, and completion-gate details for each layer.
