<!--plan_identity:
  schema_version: "1.0"
  plan_id: "capability-fact-to-feature-production-plan"
  mission_id: "FF-CAPABILITY-LAYER-001"
  native_plan_path: "plans/capability-fact-to-feature-production-plan.md"
  native_plan_filename: "capability-fact-to-feature-production-plan.md"
  created_by_agent: "autonomous-agent"
  created_during_plan_mode: false
  created_at: "2026-06-16"
  repository: "format-factory"
  branch: "main"
  parent_plan_id: null
  successor_plan_id: null
  ownership_status: "ACTIVE"
  plan_type: "capability_layer_supplement"
  ledger_entry: null
  current_revision: "1.0"
  terminal_lock: false
  terminal_lock_reason: null
  terminal_locked_at: null
  run_id: "capability-fact-to-feature-forensics-20260616-f607c78"
  notes: >
    Governed supplement to plans/spec-to-feature-radical-correction-plan.md.
    Lives in the repository plans/ directory. Not in .claude/plans/.
-->
# Capability Layer — Fact-to-Feature Production Plan

## Authority Declaration

- **Plan type:** Focused Capability Layer production plan (Lane 2, 3, 6 execution supplement)
- **Upstream authority:** `plans/spec-to-feature-radical-correction-plan.md` (master plan)
- **Related authoritative docs:**
  - `docs/commercial-product-capability-model.md` — defines C0-C10 capability levels and Gate 11 requirements (normative)
  - `docs/governance/requirement-capability-authority-layer.md` — RCAL proof graph design (18 node types, 19 edge types, 8 invariants) — status: PLAN_HEALED_READY_FOR_MWP_EXECUTION
  - `docs/capability-layer-design.md` — Operational capability layer design (18-state taxonomy, validator suite)
- **Relationship:** Governed supplement — does not replace master plan; provides detailed diagnostic evidence, root causes, stage-by-stage architecture, and executable taskcards for Capability Layer work
- **Run ID:** `capability-fact-to-feature-forensics-20260616-f607c78`
- **Evidence root:** `.local/evidences/capability-fact-to-feature-forensics-20260616-f607c78/capability-fact-to-feature/`
- **Date:** 2026-06-16
- **HEAD:** f607c78

---

## 1. Executive Summary

The Capability Layer is the bridge between specification truth (SAL facts) and product implementation. It contains **4,022 capability records** (3,897 FOSS + 125 commercial) *(2026-06-17 generation; current 2026-06-23 generation: **1,779 records** — schema/filtering change; see Appendix C §D-02)*, a **1,469-entry gap ledger** (1,435 closed, 34 open — all commercial, 0 FOSS open) *(current 2026-06-23: **927 entries**, 89 open [81 FOSS + 8 commercial], 838 closed — see Appendix C §D-03)*, a **9-phase capability compiler** (513 lines), and a **gap-to-taskcard queue consumer**. All of these exist and have tests.

*(Statistics updated 2026-06-17: original 2026-06-16 values were 2375 records / 1326-entry gap ledger / 1281 closed. Count reconciliation for 2026-06-23 generation added in Appendix C.)*

**None of them are wired into the active production pipeline.**

The active execution path is: `generate_next_worker_prompt.py` → Claude Code reads `next-sprint.md` → implements functions → `supervisor_loop.py` grades. This path partially reads the gap ledger (via `autonomous_task_generator.py`) but completely bypasses the capability compiler, action queue, queue consumer, test obligation matrix, evidence obligation matrix, and gate readiness projections.

The result is a system that generates impressive capability infrastructure artifacts which are never consumed by the process that actually builds product features.

---

## 2. Current-State Evidence Summary

### Working Components (Active Production Use)

| Component | Location | Status |
|-----------|----------|--------|
| SAL master runner | `tools/specification-authority-layer/sal_master_runner.py` | ACTIVE — 14,309 facts, 23 formats *(current 2026-06-23; prior 2026-06-17: 14,432 / 22 formats)*; FODS: 4,987; FODT: 4,961; ZST: 109 |
| SAL facts output | `.local/sal-output/sal-facts-latest.json` | ACTIVE — 14,309 facts; last regen: 2026-06-23 |
| Capability map generator | `tools/capability_layer/capability_map_generator.py` | ACTIVE — generates maps + gap ledger |
| Unified capability map | `reports/capability-layer/unified-capability-map.json` | ACTIVE — 1,779 records *(current 2026-06-23 generation; prior 2026-06-17: 4,022 — schema/filtering change; see Appendix C §D-02)* |
| Gap ledger | `reports/capability-layer/gap-ledger.json` | ACTIVE — 927 entries, 838 closed, 89 open (81 FOSS + 8 commercial) *(current 2026-06-23; prior 2026-06-17: 1,469 / 34 open)* |
| Capability map validator | `tools/capability_layer/validate_capability_map.py` | ACTIVE |
| Gap-ledger → task generator bridge | `autonomous_task_generator.py:_load_gap_ledger_goals()` | PARTIAL — primary source since Lane 6 repair |
| Supervisor loop | `tools/supervisor/supervisor_loop.py` | ACTIVE — grades declarations |
| Next-worker-prompt generator | `tools/supervisor/generate_next_worker_prompt.py` | ACTIVE — reads poc-targets, gap extraction fixtures |

### Dormant Components (Exist, Have Tests, Zero Production Callers)

| Component | Location | Lines | Tests | Production Callers |
|-----------|----------|-------|-------|--------------------|
| Capability compiler | `tools/supervisor/capability_compiler.py` | 513 | `test_capability_compiler.py` | **CONDITIONAL** *(2026-06-23: called via subprocess chain for mainstream/product streams; non-mainstream still ZERO)* |
| Queue consumer | `tools/supervisor/capability_queue_consumer.py` | 260 | `test_capability_queue_consumer.py` | **CONDITIONAL** *(2026-06-23: TC-WIRE-001 — `_run_capability_consumer()` at generate_next_worker_prompt.py:1037 subprocess-invokes consumer for mainstream stream; non-mainstream ZERO)* |
| Action queue | `reports/capability-layer/action-queue.json` | 27 lines | N/A | **ZERO** |
| System healing gate | `tools/supervisor/check_system_healing_gate.py` | ~250 | N/A | File-existence checks only |

### Quantified Pipeline State

- **SAL facts:** 14,309 total, across 23 formats *(current 2026-06-23; prior 2026-06-17: 14,432 / 22 formats)*; FODS: 4,987; FODT: 4,961; ZST: 109
- **Capability records:** 1,779 total *(current 2026-06-23 generation; prior 2026-06-17: 4,022 — see Appendix C §D-02 for reconciliation)*
- **Gap ledger:** 927 total (89 open: 81 FOSS + 8 commercial; 838 closed) *(current 2026-06-23; prior 2026-06-17: 1,469 / 34 open — see Appendix C §D-03)*
- **Action queue:** 24 items (all have per-item advisory_only=true — TC-ADVQ-001 fix claimed but not persisted; CAP-GEN-011 field-presence diagnosis was INCORRECT per 2026-06-23 verification)
*(Statistics updated 2026-06-17: original 2026-06-16 values were 268 SAL facts / 2375 records / 1326 total gaps / 45 open. Further updated 2026-06-23 — see Appendix C.)*
- **Compiler invocations in production:** Conditional — mainstream/product streams invoke via TC-WIRE-001; non-mainstream streams: 0 *(updated 2026-06-23)*
- **Queue consumer invocations in production:** Conditional — mainstream/product streams: called via subprocess; non-mainstream: 0 *(updated 2026-06-23)*
- **Features compiled through capability pipeline:** 0 *(compiler outputs not yet injected into sprint prompt)*
- **Taskcards generated by compiler in production:** 0 *(compiler output not yet consumed by sprint flow)*

---

## 3. Problem Statement

### The Pipeline Breaks at Stage 8 (Compiler)

```
SAL Facts → Capability Map Generator → Capability Records → Gap Ledger → [BREAK] → Compiler → Feature IR → Taskcard
                                                                  ↓
                                                         [PARALLEL PATH]
                                                                  ↓
                                              _EXPANSION_GOALS + gap-ledger goals → autonomous_task_generator → function impl
```

Stages 1-6 work: SAL facts exist, capabilities are generated, gaps are detected, gap ledger is partially consumed by task generation.

Stages 7-12 are broken: The action queue is advisory-only and unread. The compiler exists but is orphaned. The queue consumer exists but is never called. Taskcards are generated by the parallel `generate_next_worker_prompt.py` path, not by the compiler.

### Five Root Causes

**RC-1: Authority Inversion.** Capabilities are derived from `poc-targets.yaml` + source introspection, with SAL facts attached as post-hoc enrichment. The design intent (SAL facts → capabilities) is reversed in practice (source code → capabilities, then facts decoratively attached).

> **Update (2026-06-17):** SAL enrichment is now active — 14,432 facts across 22 formats are loaded and `spec_refs` fields are populated in capability records. The remaining inversion is at the granularity level: `spec_refs` are bulk-attached per format (all format facts added to every capability in that format), not per-capability (specific facts that authorize that operation). RC-1 is **PARTIALLY MITIGATED**. The outstanding work is in Stage 5 (TC-C5-001 through TC-C5-004).

**RC-2: Compiler Orphaning.** The 513-line, 9-phase capability compiler (`capability_compiler.py`) has zero production callers. `supervisor_loop.py` does not import it. `generate_next_worker_prompt.py` does not call it. No automated pipeline invokes it. It exists in isolation with its own test suite but no production integration.

> **Update (2026-06-17):** The system uses **subprocess dispatch**, not library imports. The fix is NOT to add `import capability_compiler` to `supervisor_loop.py` (which would break the subprocess pattern). The correct fix is to add a subprocess invocation of `capability_queue_consumer.py` from within the supervisor pipeline. Additionally, `capability_queue_consumer.py` (260 lines) already imports `capability_compiler` directly at line 33 — the consumer IS wired to the compiler; the missing link is the supervisor calling the consumer. Stage 1 taskcards (TC-C1-001, TC-C1-002) target subprocess invocation, not library import.
>
> **Update (2026-06-23, velvet-hatching-lark):** TC-WIRE-001 is **COMPLETE** for the mainstream stream. `_run_capability_consumer()` at `generate_next_worker_prompt.py:1037` IS called with conditional guard: `effective_stream in ("mainstream", "product", None) AND _product_groups_allowed`. This function subprocess-invokes `capability_queue_consumer.py`, which imports `capability_compiler.py` at line 33. RC-2 status: **PARTIALLY RESOLVED** — mainstream stream is fully wired; non-mainstream streams (e.g., "analytics") do NOT invoke the consumer. Gate C4: FAIL → **PARTIAL**. TC-C1-001 and TC-C1-002 are PARTIALLY_DONE (mainstream wired; non-mainstream extension remains). Evidence: `.local/evidences/capability-fact-to-feature-forensics-20260623-06f0ea05/capability-fact-to-feature/compiler-invocation-chain.md`

**RC-3: Parallel Task Path.** The actual autonomous execution path bypasses the compiler entirely. Work items come from `_EXPANSION_GOALS` (hardcoded, ~100 entries) + gap-ledger-derived goals, NOT from compiled feature IRs. The compiler's test obligation matrix, evidence obligation matrix, and gate readiness projections are never used.

> **Update (2026-06-17):** Lane 6 repair is confirmed. As of line 1564 of `autonomous_task_generator.py`, gap-ledger goals are loaded FIRST as primary authority. `_EXPANSION_GOALS` are used only as fallback for functions not in the gap-ledger. RC-3 is **PARTIALLY MITIGATED**.
>
> **NEW RISK — FOSS closure regression:** With FOSS gaps 100% closed (0 open FOSS entries in gap-ledger), the gap-ledger generates ZERO FOSS task candidates. This means the `_EXPANSION_GOALS` fallback re-becomes the de facto primary FOSS task source — the exact inversion RC-3 addressed. This is documented in Stage 2 TC-C2-005 (new taskcard, see §8).

**RC-4: Advisory-Only Action Queue + Queue Fragmentation.** All items in `reports/capability-layer/action-queue.json` have `advisory_only: true`. Additionally, there are TWO separate action queues: the capability layer's `reports/capability-layer/action-queue.json` (1 advisory item) and the supervisor's `.local/supervisor/action-queue.jsonl` (consumed by `autonomous_orchestrator.py`). These are completely disconnected — the supervisor orchestrator reads only its own JSONL queue, never the capability layer's JSON queue.

> **Update (2026-06-17):** Sprint TC-ADVQ-001 claimed to change `advisory_only` true→false in `action-queue.json` but the file was not actually modified (contradiction confirmed). Gate C5 remains FAIL. Fix requires: (1) actually modify `advisory_only` in `action-queue.json`, AND (2) wire a subprocess consumer call in the pipeline — making the flag false without a consumer is a false-fix. See Stage 3 TC-C3-001 and TC-C3-002.
>
> **Update (2026-06-23, velvet-hatching-lark):** VERIFIED — all 24 items in `reports/capability-layer/action-queue.json` already have **per-item** `advisory_only: true` (set in `capability_map_generator.py` line 1015 with comment "until queue consumer wired (Stage 3)"). The original CAP-GEN-011 diagnosis (which claimed items were *missing* per-item advisory_only) was **INCORRECT**. The real Stage 3 fix (TC-C3-001) is to change the VALUE of `advisory_only` from `True` to `False` for items satisfying `machine_executable: true AND commercial_impact == "NONE" AND priority in ("P0","P1","P2")`. The per-item field is already present on all items. CAP-GEN-011 as originally described is **INVALIDATED** — see Appendix C §CAP-GEN-011.

**RC-5: Implicit Closure.** Gap closure happens via source introspection (capability_map_generator scans for function existence), not via spec-backed contract verification. A gap closes when a function named correctly appears in source — regardless of whether it satisfies the original SAL facts or capability contract.

**RC-6: Evidence Capture Structure Mismatch.** The supervisor's materialization engine requires explicit `evidence_paths: []` fields in evidence declarations pointing to resolvable file paths. Sprint `ff-idempotent-spec-to-feature-swarm-20260617-8656416` declared 6 work items as `completed_verified` but provided zero resolvable evidence paths, resulting in all items being graded OVERCLAIMED. The 9 QName YAML files existed physically but could not be verified because the declaration did not point to them. Root cause: evidence declaration authors are not using the evidence path format required by the materialization engine. Addressed by TC-C0-006: evidence path baseline diagnostic.

**RC-7: Authority Integration Fabric Not Wired.** `tools/supervisor/authority_integration_fabric.py` (462 lines) connects SAL, `tools/requirements_authority/` (17 modules), and supervisor decision-making. It is imported in 43 repo files. But `supervisor_loop.py` does NOT import or subprocess-call it. The supervisor makes grading and continuation decisions without authority fabric input. This is the same orphaning pattern as RC-2 but at a higher architectural level. Addressed by Stage 8 (authority fabric wiring — future, after Stage 7). Priority: P3 (after Stages 1-7).

**RC-8: Capability Closure Not Integrated into Autonomous Cycle.** *(Added 2026-06-23, velvet-hatching-lark)*

Gap closure is performed by one-off manual scripts (`tools/close_comm_gaps.py`, `tools/close_fods_fodt_ppm_gaps.py`, `tools/close_xcf_zst_gaps.py`) that write `status='closed'` directly to `gap-ledger.json`. These scripts are NOT called by the autonomous cycle after a PASS-graded work item. Additionally, `capability_map_generator.py` **regenerates** `gap-ledger.json` from scratch on each run — potentially overwriting any manual closure writes. The autonomous cycle has no closure feedback loop: completed gaps re-appear in every sprint's gap selection, causing infinite re-selection of already-implemented capabilities.

- **Severity:** HIGH — structural; invalidates the gap-ledger as a dynamic capability inventory
- **Current state:** **PARTIALLY RESOLVED** *(updated 2026-06-24)* — `gap_closure_engine.py` (158 lines) IS wired into `autonomous_cycle.py` Step 3a-closure. `update_gap_status()` API added to `capability_map_generator.py`. Generator's merge code preserves `closed_by_sprint` and `closed_at` on regeneration. **Remaining gap:** zero production closures because declarations lack `gap_ledger_ref` entries — the engine's matcher finds no qualifying items. Manual `close_*.py` scripts still account for all 969 closed gaps.
- **Consequence:** Same gaps re-selected every sprint until declarations include `gap_ledger_ref`
- **Fix Target:** Stage 7 (TC-C7-001 through TC-C7-004) — Capability Closure Wiring
- **Evidence:** `.local/evidences/capability-fact-to-feature-forensics-20260623-06f0ea05/capability-fact-to-feature/closure-feedback-analysis.md`, `tests/capability_layer/test_update_gap_status.py` (7 tests), `tests/supervisor/test_gap_closure_engine.py` (18 tests)

---

## 4. Relationship to SAL and Master Plan

### SAL (Specification Authority Layer)
- SAL produces verified spec facts (14,309 across 23 formats; current 2026-06-23; prior 2026-06-17: 14,432 / 22 formats)
- The Capability Layer is intended to consume these facts and derive capabilities
- In practice, capabilities are derived from poc-targets + source code; SAL facts are decorative
- This plan addresses the SAL→Capability consumption gap

### Master Plan Lanes
- **Lane 1 (SAL Pipeline):** Produces concept inventories — upstream input to this plan
- **Lane 2 (Capability Reintegration):** This plan's primary scope
- **Lane 3 (Capability-to-Feature Compiler):** This plan's primary scope
- **Lane 6 (QName-to-Code Ontology):** Produces QName maps consumed by compiler Phase 3.5
- **Lane 4 (Skills/Prompts):** Downstream consumer of compiler output format
- **Lane 5 (Validators/Gates):** Consumes compiler-generated evidence obligations

---

## 5. Capability Contract

### What Is a Capability?

A capability is an **atomic, independently verifiable behavior** that a format implementation provides, derived from one or more specification facts and representing a single testable contract.

### Capability Lifecycle

```
discovered → candidate → normalized → authority-linked → proof-incomplete →
gap → selected → compiled → implementation-ready → in-progress →
implemented → verified → consumed → closed
```

Regression: `closed → regressed → reopened → gap`

### Capability Identity Schema

```yaml
capability_id: "{FORMAT}-{PRODUCT}-{OPERATION}-{SEQ}"
canonical_name: Human-readable operation name
format_id: Target format (FODS, FODT, ZST, etc.)
platform: python | dotnet | both
capability_category: parsing | mutation | serialization | query | validation | export | preservation
source_fact_refs: List of SAL fact QNames that authorize this capability
authority_state: spec_fact | implementation_derived | goal_derived | ai_draft
current_state: One of STATE_ORDER values
```

### Key Distinctions

| Concept | Definition | Example |
|---------|-----------|---------|
| Spec fact | Verified statement from authoritative specification | "ODF cells have office:value-type attribute" |
| Capability | Atomic testable behavior derived from facts | "Parse cell value types from FODS" |
| Feature | Implementation-scoped unit compiled from capability | "fods_cell_value_type() returns typed value" |
| API operation | Public function/method exposed to consumers | `fods_cell_value_type(workbook, sheet, row, col)` |
| Test obligation | Required test derived from capability contract | "File-based input test for fods_cell_value_type" |

### Closure Requirements

A capability is closed when:
1. Source implementation exists and matches expected module path
2. Function is exported in `__init__.py`
3. Tests pass covering all test obligation types
4. Ledger entry exists in product-code-change-ledger
5. If spec-backed: SAL fact references are traceable from test→implementation→capability→fact
6. Gap ledger gap status changed to `closed`

---

## 6. Confirmed Symptoms and Root Causes

### Symptoms (Observable)

| # | Symptom | Evidence |
|---|---------|----------|
| S1 | Compiler has zero production callers | `grep -r capability_compiler supervisor_loop.py` → 0 matches *(PARTIALLY RESOLVED 2026-06-23: TC-WIRE-001 wires mainstream stream via subprocess chain; non-mainstream streams still 0 callers)* |
| S2 | Action queue is advisory-only | `action-queue.json` line 6: `advisory_only: true` |
| S3 | Queue consumer is never invoked | Not imported by supervisor_loop, check_continuation, sprint_executor |
| S4 | Gap ledger consumption is partial | Only `autonomous_task_generator` reads it; `supervisor_loop` does not |
| S5 | System healing gate checks file existence, not consumption | `check_lane_2_capability()` checks `_file_exists()` only |
| S6 | _EXPANSION_GOALS still exist as fallback | `autonomous_task_generator.py` line 1572: `for hardcoded_goal in _EXPANSION_GOALS:` |
| S7 | Capability records lack spec-concept granularity | One capability per function, not per spec concept |

### Root Causes (Diagnosed)

| # | Root Cause | Impact | Evidence |
|---|-----------|--------|----------|
| RC-1 | Authority inversion | Capabilities are source-derived, not fact-derived | `capability_map_generator.py` line 6: "poc-targets.yaml (primary authority source)" |
| RC-2 | Compiler orphaning (PARTIALLY RESOLVED 2026-06-23) | Mainstream stream now wired via TC-WIRE-001; non-mainstream streams still bypassed | `generate_next_worker_prompt.py:1037` calls `_run_capability_consumer()` for mainstream/product streams |
| RC-3 | Parallel task path | Execution bypasses compiler entirely | `generate_next_worker_prompt.py` reads poc-targets directly |
| RC-4 | Advisory-only queue (two-queue architecture) | All 24 JSON items have per-item `advisory_only: true`; JSONL operational queue is separate and not connected | `action-queue.json` line 1015 in generator: hardcoded True; fix is changing VALUE not adding field |
| RC-5 | Implicit closure | Gaps close on function existence, not contract verification | `capability_map_generator.py` introspects source AST for function names |

---

## 6b. RCAL Proof Graph — Dormant but Comprehensive

The Requirement & Capability Authority Layer (`docs/governance/requirement-capability-authority-layer.md`) defines a comprehensive proof graph model:
- **18 node types** (ProductRequirement, CapabilityClaim, ImplementationArtifact, TestArtifact, etc.)
- **19 edge types** (derives_from, claims_support_for, implemented_by, tested_by, etc.)
- **8 graph invariants** for claim sufficiency
- **11 subsystems** (ProductRequirementRegistry, CapabilityClaimRegistry, OverclaimDetector, etc.)
- **10 proof sufficiency levels**

**Status: DORMANT.** The RCAL model is comprehensively designed but the proof graph has never been populated from actual capability data. The node types and edge types exist as specifications, not as populated data structures.

**Key insight:** The RCAL design already answers many questions this forensic investigation raises — it defines what "proven" means, what evidence is required, what graph invariants must hold, and how overclaims are detected. The problem is not design but activation.

**Integration with this plan:** Stage 5 (Fact-Driven Derivation) should use RCAL proof sufficiency levels as the closure standard. Stage 4 (Contract-Based Closure) should adopt RCAL's proof requirements per capability type (Load/parse → minimum: ImplementationArtifact + TestArtifact + EvidencePackage).

Also discovered:
- `tools/requirements_authority/` contains **17 files** implementing RCAL subsystems (graph_store.py, coverage_evaluator.py, overclaim_detector.py, staleness_invalidator.py, poc_readiness.py, mainstream_gap_queue.py, etc.)
- `tools/supervisor/authority_integration_fabric.py` imports ALL of these tools and provides an integration layer
- `authority_integration_fabric.py` is referenced in 43 files across the repo
- **BUT `supervisor_loop.py` does NOT import `authority_integration_fabric`** — same orphaning pattern as the capability compiler

**This reveals a systemic orphaning pattern:** comprehensive capability/authority infrastructure is built, tested, and referenced in reports — but the central orchestrator (`supervisor_loop.py`) imports none of it. The supervisor operates on a simpler parallel path (evidence grading → next-sprint generation) that bypasses all capability, RCAL, and proof graph infrastructure.

**RC-7: Authority Integration Fabric Not Wired (2026-06-17 finding).** `tools/supervisor/authority_integration_fabric.py` (462 lines) connects SAL, `tools/requirements_authority/` (17 modules), and supervisor decision-making. It IS imported in 43 repo files. But `supervisor_loop.py` does NOT import or subprocess-call it. The supervisor makes grading and continuation decisions without authority fabric input. This is the same orphaning pattern as RC-2 but at a higher architectural level. Stage 8 (future — authority fabric wiring) addresses this. Priority: P3 (after Stages 1-7).

---

## 7. Target Architecture

### Integrated Pipeline (Goal State)

```
SAL Facts (14,309 across 23 formats; current 2026-06-23)
  │
  ▼
Fact Eligibility Filter (explicit accept/reject/quarantine per fact)
  │
  ▼
Capability Derivation (SAL facts → atomic capabilities)
  │                    (poc-targets as SECONDARY validation, not primary source)
  ▼
Capability Normalization + Deduplication
  │
  ▼
Proof Graph Population (SAL authority → arch mapping → source → tests → consumer)
  │
  ▼
Gap Detection (denominator: all spec-derived capabilities; numerator: proof-sufficient ones)
  │
  ▼
Gap Ledger Publication (typed gaps: missing_implementation, missing_tests, missing_spec_coverage)
  │
  ▼
Gap Selection + Prioritization (by dependency readiness, spec authority, product value)
  │
  ▼
Capability Compiler (9 phases: SAL validation → Feature IR → Taskcard → Test/Evidence/Gate obligations)
  │
  ▼
Supervisor Integration (supervisor_loop.py imports compiler, generates taskcards from compiler output)
  │
  ▼
Execution (Claude Code executes compiler-generated taskcards with evidence obligations)
  │
  ▼
Verification (test pass + spec-fact reverse trace + proof-graph update)
  │
  ▼
Closure (capability status → closed; proof graph gains edges; gap ledger resolves gap)
  │
  ▼
Feedback (closed capabilities removed from future selection; regressions reopen)
```

### Key Architecture Decisions

1. **SAL facts become primary derivation input.** poc-targets.yaml becomes validation reference, not capability source.
2. **Compiler becomes production caller.** supervisor_loop.py imports and invokes capability_compiler for taskcard generation.
3. **Action queue becomes executable.** Items with sufficient authority_state get `advisory_only: false` and are picked up by queue consumer.
4. **Closure becomes contract-verified.** Gap closure requires test pass + spec-fact traceability, not just function existence.
5. **_EXPANSION_GOALS are removed.** All task selection goes through gap-ledger → compiler → taskcard path.

---

## 8. Diagnostic Gates (C0-C8)

### C0: SAL Input Availability
- **Test:** `sal-facts-latest.json` exists, is parseable, contains facts for target format
- **Current:** PASS (14,309 facts, 23 formats; FODS: 4,987; FODT: 4,961; ZST: 109) *(updated 2026-06-23; prior 2026-06-17: 14,432 / 22 formats)*
- **Command:** `python tools/specification-authority-layer/sal_master_runner.py --format FODS`

### C1: Fact-to-Capability Traceability
- **Test:** Every capability record has `source_fact_refs` populated with verified SAL fact QNames
- **Current:** PARTIAL — records have `spec_refs` but these are bulk-attached per format, not per-capability
- **Verification:** For each capability, check that spec_refs are specific to that operation, not the entire format fact set

### C2: Capability Granularity
- **Test:** Each capability is independently implementable and testable; no "support FODS"-level monoliths
- **Current:** PASS for FOSS (one function = one capability); NEEDS REVIEW for spec-concept alignment

### C3: Gap-Ledger Consumption
- **Test:** Gap ledger is read by task generation AND compiler pipeline; no advisory-only bypass
- **Current:** PARTIAL (IMPROVED — gap-ledger is now PRIMARY source since Lane 6 repair at line 1564 of `autonomous_task_generator.py`; `_EXPANSION_GOALS` are fallback only. **Warning:** FOSS gap-ledger is now empty (0 open FOSS); fallback re-activates for all FOSS work.) *(updated 2026-06-17)*
- **Target:** Compiler invoked by supervisor_loop, producing executable taskcards from gap records

### C4: Compiler Production Integration
- **Test:** `supervisor_loop.py` or `generate_next_worker_prompt.py` subprocess-invokes `capability_queue_consumer.py` which in turn calls `capability_compiler`
- **Current:** **PARTIAL** *(updated 2026-06-23, velvet-hatching-lark)* — TC-WIRE-001 COMPLETE for mainstream stream. `_run_capability_consumer()` at `generate_next_worker_prompt.py:1037` IS called when `effective_stream in ("mainstream","product",None) AND _product_groups_allowed`. Non-mainstream streams (e.g., "analytics") do NOT invoke the consumer. Evidence: `.local/evidences/capability-fact-to-feature-forensics-20260623-06f0ea05/capability-fact-to-feature/compiler-invocation-chain.md`
- **Target:** All production streams invoke `capability_queue_consumer.py` (not just mainstream)

### C5: Action Queue Executability
- **Test:** At least one action queue item has `advisory_only: false` AND a downstream executor
- **Current:** FAIL — all items advisory_only=true, zero consumers
- **Target:** Queue items with authority_state >= spec_verified become executable

### C6: Contract-Based Closure
- **Test:** Gap closure requires passing tests + spec-fact traceability, not just function existence
- **Current:** FAIL — closure is AST-scan-based (function name exists in source)
- **Target:** Closure requires test_verified + spec_refs validated against SAL facts

### C7: _EXPANSION_GOALS Elimination
- **Test:** `_EXPANSION_GOALS` hardcoded list removed or reduced to zero entries
- **Current:** PARTIAL — ~100 hardcoded goals demoted to fallback as of 2026-06-17 (`autonomous_task_generator.py` line 1564). However, with FOSS gaps 100% closed, the fallback re-activates as de facto primary for all FOSS work. Full gate pass requires: `_EXPANSION_GOALS` emptied OR replaced by FOSS-capable gap regeneration strategy. *(updated 2026-06-17)*
- **Target:** All task selection through gap-ledger → compiler → taskcard

### C8: End-to-End Reverse Trace
- **Test:** Pick any implemented function → trace back through taskcard → feature IR → capability → SAL fact → specification section
- **Current:** FAIL — no implemented function was generated through the compiler pipeline
- **Target:** At least 10 functions per format have complete reverse trace

### C9: Capability Closure Feedback *(Added 2026-06-23, velvet-hatching-lark)*
- **Test:** After a PASS-graded work item with `gap_ledger_ref`, the corresponding gap-ledger entry has `status='closed'`; same gap does NOT appear in next sprint's gap selection
- **Current:** **PARTIAL** *(updated 2026-06-24, convergence iteration 1)* — `gap_closure_engine.py` EXISTS and IS WIRED into `autonomous_cycle.py` Step 3a-closure (line 1108). Engine matches graded items to `gap_ledger_ref`, evaluates closure criteria (ACCEPTED grade + test evidence + no failures), and writes `closed` status. **However:** zero production closures have occurred (`gap-closure-log.json` is empty; 0 gaps have `closed_by_engine=true`). Root cause: declarations do not include `gap_ledger_ref` in `planned_work_items` — the engine's `_match_grades_to_gaps()` finds zero matches. Also: `update_gap_status()` standalone API added to `capability_map_generator.py` (TC-C7-001). 25 tests pass (18 engine + 7 API).
- **Target:** TC-C7-001 through TC-C7-004 implemented and passing
- **Remaining:** Declarations must include `gap_ledger_ref` for the engine to activate. This is a process/tooling gap, not a code gap.

---

## 9. Implementation Stages

### Stage 0: Diagnostic Baseline (No Code Changes)
**Objective:** Run existing pipeline, measure current break points, produce diagnostic evidence.

**Taskcards:**
- TC-C0-001: Run `capability_map_generator.py` and inspect output structure
- TC-C0-002: Run `capability_compiler.py` with a sample gap record and inspect output
- TC-C0-003: Run `capability_queue_consumer.py --max-gaps 3` and inspect output
- TC-C0-004: Trace one FODS capability from gap-ledger through compiler to feature IR
- TC-C0-005: Verify SAL fact counts per format against capability spec_refs
- TC-C0-006: Run materialized evidence review against one known-complete work item to establish the evidence path format baseline. Inspect how the materialization engine resolves declared paths. Produce `evidence-path-format-guide.md`. **REQUIRED before any sprint declaration for Capability Layer work.** (Addresses RC-6.)

### Stage 1: Compiler Production Wiring (RC-2 Fix)
**Objective:** Wire the existing compiler into the active supervisor pipeline.

**Taskcards:**
- TC-C1-001: Add subprocess invocation of `capability_queue_consumer.py` to `generate_next_worker_prompt.py` (NOT a library import — system uses subprocess dispatch pattern)
- TC-C1-002: Wire subprocess output (feature IR, test obligations, evidence obligations) into sprint prompt template via consumer→compiler chain
- TC-C1-003: Add test: `test_supervisor_invokes_compiler.py` — verify supervisor pipeline subprocess-invokes `capability_queue_consumer.py`
- TC-C1-004: End-to-end smoke test: gap record → consumer subprocess call → compiler output → taskcard in sprint prompt

**Gate:** C4 passes — supervisor pipeline subprocess-invokes `capability_queue_consumer.py` in at least one code path.

### Stage 2: Gap-Ledger Primary Source (RC-1 + RC-3 Fix)
**Objective:** Make gap ledger the exclusive source of task selection; remove _EXPANSION_GOALS.

**Taskcards:**
- TC-C2-001: In `autonomous_task_generator.py`, remove _EXPANSION_GOALS fallback loop (lines 1572-1575)
- TC-C2-002: Verify all existing _EXPANSION_GOALS entries have equivalent gap-ledger records
- TC-C2-003: Add test: verify `generate_task_candidates()` produces 0 tasks when gap-ledger is empty
- TC-C2-004: Add test: verify tasks come exclusively from gap-ledger, not hardcoded goals
- TC-C2-005: Address FOSS closure regression — with gap-ledger empty for FOSS, `_EXPANSION_GOALS` fallback re-activates as de facto primary. Strategy options: (a) regenerate FOSS gaps at a higher-difficulty tier, (b) extend gap-ledger to include spec-concept gaps not yet mapped to functions, (c) disable fallback entirely and allow gap-ledger to drive zero FOSS work until new gaps are generated. Produce analysis report before implementation. (Addresses RC-3 FOSS regression risk.)

**Gate:** C7 passes — _EXPANSION_GOALS eliminated or empty; all task selection through gap-ledger.

### Stage 3: Action Queue Activation (RC-4 Fix)
**Objective:** Convert advisory-only action queue items to executable items where authority is sufficient.

> **Human Gate Policy (velvet-hatching-lark session decision, 2026-06-23):** Compiled gap taskcards for FOSS capabilities enter the autonomous queue **WITHOUT** a per-taskcard human approval gate. The `advisory_only: false` flag is the execution gate — NOT a human gate. Human gates (`external_gate: true`) apply ONLY to Gate 11 G11-G commercial release execution (Babar Raza only), git push requiring credentials, and package publication. This is consistent with AGENTS.md §AG1 and §AG5. **For Stage 3 implementation:** change `advisory_only` True→False for items satisfying `machine_executable: true AND commercial_impact == "NONE" AND priority in ("P0","P1","P2")`. Do NOT add `external_gate: true` for FOSS items. The `advisory_only` flag already exists per-item on all 24 current queue items — only the VALUE needs changing.

**Taskcards:**
- TC-C3-001: In `capability_map_generator.py`, change `advisory_only` VALUE: items with `machine_executable: true AND commercial_impact == "NONE" AND priority in ("P0","P1","P2")` get `advisory_only: False`. (Note: the per-item field already exists on all items — change the value, do not add the field. See RC-4 update 2026-06-23.)
- TC-C3-002: Wire `capability_queue_consumer.py` as a callable from the supervisor pipeline (not just standalone)
- TC-C3-003: Add test: verify queue consumer processes non-advisory items and produces taskcards

**Gate:** C5 passes — at least one queue item is executable and has a downstream consumer.

### Stage 4: Contract-Based Closure (RC-5 Fix)
**Objective:** Replace implicit AST-scan closure with contract verification.

**Taskcards:**
- TC-C4-001: In `capability_map_generator.py`, change gap closure logic: require `test_verified` state (test file exists AND all tests pass) in addition to function existence
- TC-C4-002: Add spec_refs validation to closure: verify capability's spec_refs are still present and verified in SAL facts
- TC-C4-003: Add test: gap does NOT close when function exists but tests fail
- TC-C4-004: Add test: gap does NOT close when function exists but spec_refs are invalid

**Gate:** C6 passes — closure requires test pass + spec-ref traceability.

### Stage 5: Fact-Driven Capability Derivation (Authority Correction)
**Objective:** Shift capability derivation from poc-targets-first to SAL-facts-first.

**Taskcards:**
- TC-C5-001: Add new capability derivation mode to `capability_map_generator.py`: read SAL facts, group by semantic category, generate capability candidates per fact group
- TC-C5-002: Cross-validate SAL-derived capabilities against existing poc-targets-derived capabilities
- TC-C5-003: Produce fact-eligibility-ledger per format: each fact classified as accepted/rejected/quarantined with reason
- TC-C5-004: Add test: SAL-derived capabilities have per-capability (not per-format) spec_refs

**Gate:** C1 passes — every capability has operation-specific (not bulk) spec_refs.

### Stage 6: System Healing Gate Hardening
**Objective:** Replace file-existence checks with consumption-verified checks.

**Taskcards:**
- TC-C6-001: In `check_system_healing_gate.py:check_lane_2_capability()`, add checks: gap-ledger consumed by task generator (import trace), compiler has production caller (import trace)
- TC-C6-002: In `check_lane_3_compiler()`, add checks: compiler output is consumed (not just exists), at least one compiled taskcard was executed
- TC-C6-003: Add end-to-end trace check: pick random capability → verify reverse path to SAL fact exists

**Gate:** C8 passes for at least one format.

### Stage 7: Capability Closure Wiring (RC-8 Fix) *(Added 2026-06-23, velvet-hatching-lark)*
**Objective:** Wire gap closure into the autonomous cycle so that PASS-graded work items close their corresponding gap-ledger entries, preventing infinite re-selection of implemented capabilities.

**Status:** *(updated 2026-06-24, convergence iteration 3)* **ALL 5 TASKCARDS COMPLETE.** Full code path + data path implemented. `gap_closure_engine.py` wired at Step 3a-closure. `update_gap_status()` standalone API in `capability_map_generator.py`. Step 3a-pre in `autonomous_cycle.py` merges `gap_ledger_ref` from work items into declarations. 32 tests pass (18 engine + 7 API + 7 injection). Production closures will activate on next sprint with gap-ledger-sourced work items.

**Taskcards:**
- TC-C7-001: ~~Design and implement `update_gap_status()`~~ **DONE** (2026-06-24). Implemented in `capability_map_generator.py`. Idempotent. Regeneration-safe (generator merge code preserves `closed_by_sprint`, `closed_at`). 7 tests in `tests/capability_layer/test_update_gap_status.py`.
- TC-C7-002: ~~Wire into `autonomous_cycle.py` post-grade step~~ **ALREADY DONE** (prior sprint). `gap_closure_engine.py` wired at Step 3a-closure (line 1108). 18 tests in `tests/supervisor/test_gap_closure_engine.py`.
- TC-C7-003: ~~Test: closed gap absent from next sprint~~ **DONE** (2026-06-24). `TestClosedGapAbsentFromSelection` in `test_update_gap_status.py`.
- TC-C7-004: ~~Idempotency test~~ **DONE** (2026-06-24). `TestIdempotency` in `test_update_gap_status.py` + `TestIdempotentRerun` in `test_gap_closure_engine.py`.
- TC-C7-005: ~~Inject `gap_ledger_ref` into work item declarations~~ **DONE** (2026-06-24, convergence iteration 3). Three-pronged fix: (1) `autonomous_cycle.py` Step 3a-pre merges `gap_ledger_ref` from canonical `next-work-items.json` into declaration items before closure engine runs. (2) `gap_ledger_to_work_items.py` now includes `gap_ledger_ref` field in output. (3) `capability_feature_compiler.py` now includes `gap_ledger_ref` in compiled work items. 7 tests in `tests/supervisor/test_gap_ledger_ref_injection.py`. End-to-end test verifies closure engine activates after merge.

**Gate:** C9 ~~PARTIAL~~ **READY** — code path + data path complete; production closures will activate on next gap-ledger-sourced sprint.

---

## 10. Dependency DAG

```
Stage 0 (Diagnostics) → required by all stages
  │
  ├─→ Stage 1 (Compiler Wiring)         ← RC-2 fix
  │     │
  │     ├─→ Stage 2 (Gap-Ledger Primary) ← RC-1, RC-3 fix (depends on Stage 1)
  │     │
  │     └─→ Stage 3 (Queue Activation)   ← RC-4 fix (depends on Stage 1)
  │
  ├─→ Stage 4 (Contract Closure)         ← RC-5 fix (independent of Stage 1)
  │
  ├─→ Stage 5 (Fact-Driven Derivation)   ← Authority correction (independent)
  │     │
  │     └─→ Stage 6 (Gate Hardening)     ← Depends on Stages 1-5
  │
  └─→ Stage 7 (Closure Wiring)           ← RC-8 fix (depends on Stage 1)
```

### Execution Order
1. Stage 0 (diagnostic baseline) — no dependencies
2. Stage 1 (compiler wiring) — depends on Stage 0
3. Stage 2 + Stage 3 (gap-ledger + queue) — depend on Stage 1, can run in parallel
4. Stage 4 (contract closure) — depends on Stage 0, can run parallel with Stage 1
5. Stage 5 (fact-driven derivation) — depends on Stage 0
6. Stage 6 (gate hardening) — depends on all others
7. Stage 7 (closure wiring) — depends on Stage 1; can run in parallel with Stages 2-6

---

## 11. Taskcards (Summary)

| ID | Stage | Description | Dependencies |
|----|-------|-------------|-------------|
| TC-C0-001 | 0 | Run capability_map_generator diagnostic | None |
| TC-C0-002 | 0 | Run capability_compiler with sample gap | None |
| TC-C0-003 | 0 | Run capability_queue_consumer --max-gaps 3 | None |
| TC-C0-004 | 0 | Trace FODS capability through compiler | None |
| TC-C0-005 | 0 | Verify SAL fact counts vs capability spec_refs | None |
| TC-C0-006 | 0 | Evidence path format baseline + guide (RC-6) | None |
| TC-C1-001 | 1 | Import capability_compiler in prompt generator | TC-C0-002 |
| TC-C1-002 | 1 | Add compiler invocation path in supervisor | TC-C1-001 |
| TC-C1-003 | 1 | Test: supervisor invokes compiler | TC-C1-002 |
| TC-C1-004 | 1 | Wire compiler output into sprint prompt | TC-C1-002 |
| TC-C2-001 | 2 | Remove _EXPANSION_GOALS fallback | TC-C1-002 |
| TC-C2-002 | 2 | Verify gap-ledger covers all _EXPANSION_GOALS | TC-C2-001 |
| TC-C2-003 | 2 | Test: zero tasks when gap-ledger empty | TC-C2-001 |
| TC-C2-004 | 2 | Test: tasks from gap-ledger exclusively | TC-C2-001 |
| TC-C2-005 | 2 | FOSS closure regression strategy (RC-3 risk) | TC-C0-001 |
| TC-C3-001 | 3 | Activate non-advisory queue items | TC-C1-002 |
| TC-C3-002 | 3 | Wire queue consumer as supervisor callable | TC-C3-001 |
| TC-C3-003 | 3 | Test: queue consumer processes items | TC-C3-002 |
| TC-C4-001 | 4 | Replace AST-scan closure with contract check | TC-C0-001 |
| TC-C4-002 | 4 | Add spec_refs validation to closure | TC-C4-001 |
| TC-C4-003 | 4 | Test: gap stays open when tests fail | TC-C4-001 |
| TC-C4-004 | 4 | Test: gap stays open when spec_refs invalid | TC-C4-002 |
| TC-C5-001 | 5 | SAL-fact-first capability derivation mode | TC-C0-005 |
| TC-C5-002 | 5 | Cross-validate SAL vs poc-targets capabilities | TC-C5-001 |
| TC-C5-003 | 5 | Produce fact-eligibility-ledger per format | TC-C5-001 |
| TC-C5-004 | 5 | Test: per-capability (not per-format) spec_refs | TC-C5-001 |
| TC-C6-001 | 6 | Harden Lane 2 gate: consumption checks | TC-C1-003, TC-C2-004 |
| TC-C6-002 | 6 | Harden Lane 3 gate: compiler output consumed | TC-C1-003 |
| TC-C6-003 | 6 | End-to-end reverse trace check | TC-C5-004 |
| TC-C7-001 | 7 | ~~Implement update_gap_status()~~ DONE 2026-06-24 | TC-C1-002 |
| TC-C7-002 | 7 | ~~Wire gap closure into autonomous_cycle.py~~ DONE (prior sprint) | TC-C7-001 |
| TC-C7-003 | 7 | ~~Test: closed gap absent from selection~~ DONE 2026-06-24 | TC-C7-002 |
| TC-C7-004 | 7 | ~~Idempotency test~~ DONE 2026-06-24 | TC-C7-001 |
| TC-C7-005 | 7 | ~~Inject gap_ledger_ref into work item declarations~~ DONE 2026-06-24 | TC-C7-002 |

---

## 12. Evidence Contract

Every taskcard completion must produce:

1. **Source diff** — git diff showing exact changes
2. **Test results** — pytest output with pass/fail counts
3. **Gate status** — which diagnostic gate (C0-C8) advances
4. **Reverse trace** — for stages 1+: trace from changed artifact back to capability → SAL fact
5. **Consumer proof** — evidence that the output is consumed by the next pipeline stage

---

## 13. Anti-Patterns (Prohibited)

1. **Do not add more capability records to prove progress.** Record count is not the metric; consumption is.
2. **Do not mark compiler as "active" because it has tests.** Active means production callers invoke it.
3. **Do not close gaps by scanning for function names.** Closure requires contract verification.
4. **Do not create a new parallel pipeline.** Wire the existing compiler into the existing supervisor.
5. **Do not attach all format facts to every capability.** Per-capability spec_refs must be operation-specific.
6. **Do not make advisory_only=false without consumption verification.** Executable items need executors.

---

## 14. Critical File Map

| File | Role | Modification Scope |
|------|------|-------------------|
| `tools/capability_layer/capability_map_generator.py` | Capability generation + gap detection | Stages 4, 5 |
| `tools/supervisor/capability_compiler.py` | 9-phase compiler | Stage 0 (diagnostic), Stage 1 (wiring) |
| `tools/supervisor/capability_queue_consumer.py` | Gap→taskcard bridge | Stage 3 |
| `tools/supervisor/autonomous_task_generator.py` | Task selection | Stage 2 (_EXPANSION_GOALS removal) |
| `tools/supervisor/generate_next_worker_prompt.py` | Sprint prompt generation | Stage 1 (compiler integration) |
| `tools/supervisor/supervisor_loop.py` | Main orchestrator | Stage 1 (compiler import) |
| `tools/supervisor/check_system_healing_gate.py` | Gate checks | Stage 6 |
| `reports/capability-layer/gap-ledger.json` | Gap state | Read by Stages 2-6 |
| `reports/capability-layer/action-queue.json` | Action items | Stage 3 |
| `.local/sal-output/sal-facts-latest.json` | SAL facts | Read by Stages 0, 5 |

---

## 15. Execution-Readiness Criteria

This plan is ready for execution when:

1. Evidence root directory exists
2. Stage 0 diagnostic taskcards can be run without error
3. All critical files listed in Section 14 exist and are readable
4. SAL facts file is present and parseable
5. No blocking contradictions in `reports/supervisor/contradictions.md`

**Current assessment:** READY FOR STAGE 0.

Stage 0 requires only read operations and diagnostic command runs. No source mutation.
Stages 1-6 require source modification and are gated by Stage 0 completion.

---

## 16. Tradeoffs and Risks

| Risk | Mitigation |
|------|-----------|
| Compiler wiring may break existing sprint flow | Stage 1 adds compiler as ADDITIONAL path, not replacement; existing path remains until verified |
| _EXPANSION_GOALS removal may leave format gaps | TC-C2-002 verifies all goals have gap-ledger equivalents before removal |
| SAL fact quality varies by format | Stage 5 produces fact-eligibility-ledger with explicit accept/reject/quarantine per fact |
| Contract-based closure may reopen thousands of gaps | Stage 4 is phased: first add tests, then retroactively verify existing closures |

---

## 17. Pilot Selection

### Primary Deep Pilot: FODS
- 98 SAL facts (FODS-specific + ODF base)
- Existing implementation with analytics functions
- Capability records exist with spec_refs
- Best candidate for end-to-end reverse trace

### Shared-Spec Pilot: FODT
- Tests format-specific fact filtering (ODF spreadsheet facts should not become FODT capabilities)
- Validates shared vs format-specific capability handling

### Non-XML Pilot: ZST
- RFC-based spec facts (algorithmic, not document object model)
- Tests compiler with non-ODF capability types
- Compression/decompression capabilities

### Negative Pilot: A format with insufficient SAL facts
- Must refuse to fabricate capabilities
- Must produce a governed gap indicating missing authority
- Must not silently fall back to hardcoded expectations

---

## Appendix A: Existing Assumption Register

| ID | Claim | Evidence | Result | Consequence if False |
|----|-------|----------|--------|---------------------|
| A-01 | Gap ledger is consumed by task generation | `autonomous_task_generator.py` line 1564 | CONFIRMED PRIMARY (2026-06-17 + 2026-06-23 update) — gap-ledger goals load first; `_EXPANSION_GOALS` are fallback only. **2026-06-23:** 81 open FOSS gaps — fallback NOT currently active. Fallback risk remains if all 81 close. | Tasks for FOSS formats revert to hardcoded goals if gap-ledger FOSS becomes empty. |
| A-02 | Compiler is functional | `test_capability_compiler.py` passes | CONFIRMED — works in isolation | Compiler produces valid output but nobody reads it |
| A-03 | SAL facts drive capabilities | `capability_map_generator.py` line 6: "poc-targets.yaml (primary)" | PARTIALLY MITIGATED (2026-06-17) — SAL enrichment now active (14,432 facts; `spec_refs` populated). But derivation still source-first: poc-targets → capabilities, then SAL facts bulk-attached per format. Per-capability fact authorization is the remaining gap. | Capabilities have spec_refs but at wrong granularity; not per-operation authorized. |
| A-04 | Action queue drives execution | `action-queue.json` line 6: `advisory_only: true` | CONTRADICTED — all items advisory, zero consumers | Queue is decorative |
| A-05 | System healing gate verifies consumption | `check_lane_2_capability()` | CONTRADICTED — checks file existence only | Gate passes when files exist even if nobody reads them |
| A-06 | Gap closure is contract-based | `capability_map_generator.py` source introspection | CONTRADICTED — still function-name AST scan (2026-06-17). TC-ADVQ-001 claimed fix not persisted. 1,435 already-closed gaps were closed by implicit scan. | Gaps close when function name appears, regardless of spec correctness or test pass. |
| A-07 | Capabilities are atomic and testable | Record structure | CONFIRMED — one function = one capability | Granularity is acceptable for current FOSS work |
| A-08 | 4,022 capability records (3,897 FOSS + 125 commercial) represent real capabilities | Source introspection + poc-targets (updated 2026-06-17) | **STALE COUNT (2026-06-23):** 4,022 was the 2026-06-17 generation count. Current 2026-06-23 generation: 1,779 records. See Appendix C §D-02. | Plan was overstating current capability coverage by 2,243 records. |
| A-09 | Evidence declarations correctly reference materialization-engine-resolvable paths | Sprint `ff-idempotent-spec-to-feature-swarm-20260617-8656416` review | CONTRADICTED — 6 items OVERCLAIMED because evidence_paths field was absent or unresolvable, even though work was done. | Future capability layer sprint declarations will also be OVERCLAIMED unless RC-6 (TC-C0-006 evidence path guide) is resolved. |
| A-10 | `authority_integration_fabric.py` is wired into supervisor decision-making | `tools/supervisor/authority_integration_fabric.py` (462 lines) | CONTRADICTED — supervisor_loop.py does NOT import or subprocess-call it (RC-7). It is imported in 43 other repo files but the central orchestrator bypasses it. | Supervisor makes grading decisions without authority fabric; RCAL proof graph is never consulted. |

---

## Appendix B: FOSS Closure Regression Risk Analysis (Added 2026-06-17)

### Context

All FOSS gaps were 100% closed as of 2026-06-17 (0 open FOSS entries). This created a structural regression risk.

> **Update (2026-06-23, velvet-hatching-lark):** FOSS gap-ledger is NOT empty. The 2026-06-23 gap-ledger generation shows **81 open FOSS gaps** (`product_type=foss_reduced`, `status=open`). Fallback is currently **NOT active** for FOSS. The RC-3 risk remains FUTURE risk only. Evidence: `_expansion_goal_fallback = len(gap_ledger_goals) == 0` at `autonomous_task_generator.py:1610` — with 81 FOSS gaps, this evaluates to `False`. Evidence file: `.local/evidences/capability-fact-to-feature-forensics-20260623-06f0ea05/capability-fact-to-feature/hardcoded-goal-bypass-analysis.md`

### The Regression Mechanism

Lane 6 repair demoted `_EXPANSION_GOALS` to fallback in `autonomous_task_generator.py` (line 1564). The intent was: gap-ledger drives tasks, hardcoded goals are backup. However, when the gap-ledger becomes empty:

1. Gap-ledger FOSS items = 0 (all closed)
2. Gap-ledger commercial items = 8 (agent cannot execute commercial work autonomously)
3. Therefore, `autonomous_task_generator.py` finds 0 actionable gap-ledger items for FOSS
4. Fallback activates: `_EXPANSION_GOALS` (~100 hardcoded entries) re-become the de facto FOSS task source
5. Lane 6 repair is logically undone at runtime despite the code change being correct

### Risk Classification

- **Type:** Structural / architectural regression
- **Severity:** HIGH — undermines the core fix that RC-3 was meant to address
- **Detectability:** LOW — the code change is correct; regression is only visible at runtime when gap-ledger is empty
- **Current status (2026-06-23):** LATENT (not active) — 81 open FOSS gaps prevent fallback activation. Risk activates when all 81 are closed or the `close_*.py` scripts close them manually.

### Mitigation Options (see TC-C2-005 for implementation)

| Option | Description | Trade-offs |
|--------|-------------|-----------|
| A | Regenerate FOSS gaps at higher-difficulty tier (spec-concept not yet mapped) | Requires new SAL fact analysis; may produce weak gaps |
| B | Extend gap-ledger to include spec-concept coverage gaps (not function-level) | Correct approach; requires gap-ledger schema extension |
| C | Disable fallback entirely when gap-ledger is authoritative | Zero FOSS work until new gaps generated; honest but disruptive |
| D | Add "gap regeneration sprint" trigger when FOSS gap count hits zero | Automated; requires supervisor trigger logic |

**Recommended:** Option B + D in combination. Short-term: Option C (honest) until Option B is ready.

---

## Appendix C: Forensic Session Findings — velvet-hatching-lark (2026-06-23)

**Session ID:** velvet-hatching-lark | **Date:** 2026-06-23 | **Run ID:** capability-fact-to-feature-forensics-20260623-06f0ea05
**Evidence root:** `.local/evidences/capability-fact-to-feature-forensics-20260623-06f0ea05/capability-fact-to-feature/`
**Mode:** EXISTING_PLAN_SURGICAL_ENHANCEMENT (MODE A confirmed — single authoritative plan)

### Discrepancy Resolutions

| # | Original Claim | Verified Finding | Resolution |
|---|----------------|-----------------|------------|
| D-01 | RC-2: "ZERO production callers" | TC-WIRE-001 COMPLETE for mainstream stream — `_run_capability_consumer()` at `generate_next_worker_prompt.py:1037` | PARTIALLY RESOLVED — see RC-2 update §3 |
| D-02 | 4,022 capability records | 2026-06-23 generation: 1,779 records | Schema/filtering change between generations; 4,022 = 2026-06-17 generation using older schema |
| D-03 | 1,469-entry gap ledger | 2026-06-23 generation: 927 entries, 89 open (81 FOSS + 8 commercial), 838 closed | Gap regeneration with updated closure tracking; plan counts updated in §1 and §2 |
| D-04 | Single action queue (advisory) | TWO architecturally distinct queues: static advisory JSON + operational JSONL | Confirmed two-queue architecture; RC-4 updated; see §3 RC-4 |
| D-05 | CAP-GEN-011: 16/24 items missing per-item advisory_only | ALL 24 items already have per-item advisory_only:true | CAP-GEN-011 INVALIDATED — see §CAP-GEN-011 below |
| D-06 | CAP-NETPBM-CLEANUP-001: 100+ stub files to delete | Only 3 r374 netpbm test files exist; all are real analytics tests | Deletion approach WRONG — see §CAP-NETPBM-CLEANUP-001 below |
| D-07 | PGM function implementations missing | pgm_dark_pixel_ratio (line 491) and pgm_bright_pixel_ratio (line 19) EXIST in pgm_analytics.py | Already resolved by cap-layer-hardening-exe sprint; 761 PGM tests pass |

### New Root Cause

**RC-8** added — Capability Closure Not Integrated into Autonomous Cycle. See §3 RC-8 and Stage 7 (TC-C7-001 through TC-C7-004).

### Gate Status Changes

| Gate | Prior Status | New Status (2026-06-23) |
|------|-------------|------------------------|
| C4 (Compiler Production Integration) | FAIL | PARTIAL — mainstream stream wired via TC-WIRE-001 |
| C9 (Capability Closure Feedback) | — (not defined) | FAIL — gap-ledger never mutated post-grade (RC-8) |

### Human Gate Policy

Compiled gap taskcards for FOSS capabilities enter the autonomous queue WITHOUT a per-taskcard human approval gate. See Stage 3 policy block above TC-C3-001.

### §CAP-GEN-011: INVALIDATED (velvet-hatching-lark) → CORRECTED AND EXECUTED (cap-layer-hardening-exe)

**Original diagnosis (Appendix E intent):** Generator emitting advisory_only=False in some code paths, violating VAL-009 invariant.
**velvet-hatching-lark forensic scan finding:** All 24 items in `reports/capability-layer/action-queue.json` have per-item `advisory_only: true`. Led to conclusion: "field already exists, fix not needed."
**CORRECTION (2026-06-23, cap-layer-hardening-exe):** The velvet-hatching-lark scan read the ALREADY-REGENERATED file. The GENERATOR SOURCE CODE had 3 buggy sites that would emit advisory_only=False on any fresh `capability_map_generator.py` run:
- Site 1 (hardcoded action): `"advisory_only": False` → `True`
- Site 2 (per-gap actions): `"advisory_only": not is_machine_executable` → `True`
- Site 3 (top-level queue): `"advisory_only": not any_machine_executable` → `True`

**Status: EXECUTED AND ACCEPTED** — cap-layer-hardening-exe sprint fixed all 3 sites; action-queue regenerated; validate() passes with 0 errors; supervisor ACCEPTED_WITH_LIMITATIONS (code correct; evidence declaration did not list 7 updated test files).
**VAL-009 status:** PASSING — no errors.
**Do NOT re-diagnose or re-implement.** The fix is complete.

### §CAP-NETPBM-CLEANUP-001: SUPERSEDED

**Original diagnosis:** 100+ netpbm analytics test stubs need deletion; massive collection error count.
**Verification finding (2026-06-23):** Only 3 netpbm test files exist for r374 analytics tests (`tests/python/pbm/`, `tests/python/pgm/`, `tests/python/ppm/`). All 3 are real comprehensive analytics test suites. Current state: 0 collection errors (resolved by cap-layer-hardening-exe sprint).
**Status:** SUPERSEDED — the 100+ collection errors were resolved by the prior sprint. No deletion needed. No stub files found.
**If collection errors recur:** Run `pytest --collect-only tests/python/pbm/ tests/python/pgm/ tests/python/ppm/` to identify root cause. Do NOT delete test files before root cause is confirmed.

### Count Reconciliation Notes

**Capability records (D-02):** The 4,022 figure (2026-06-17) used schema version 1.0 with looser filtering. The 1,779 figure (2026-06-23) uses the same schema version but a different capability_map_generator.py generation run with updated `_FORMAT_SOURCE_MAP`. The reduction is due to stricter per-format filtering, not lost capabilities. Both generations cover the same FOSS formats.

**Gap ledger (D-03):** The 1,469 figure (2026-06-17) included commercial gaps reopened by the regenerator. The 927 figure (2026-06-23) reflects the current generation. 838 gaps are closed (many by `close_*.py` scripts run manually). 81 open FOSS gaps remain as of 2026-06-23.

**SAL facts:** 14,432 (2026-06-17) vs 14,309 (2026-06-23). Difference of 123 facts: one new format added (bringing total to 23), but some format fact counts were refined by the updated SAL pipeline.

### Assumption Register Updates

| Assumption | Prior Verdict | Updated Verdict (2026-06-23) |
|------------|--------------|------------------------------|
| A-01 (Gap ledger consumed) | CONFIRMED PRIMARY | CONFIRMED (81 FOSS open; _expansion_goal_fallback=False) |
| A-03 (SAL facts drive capabilities) | PARTIALLY MITIGATED | PARTIAL (per-capability spec_refs still missing) |
| A-08 (4,022 capability records) | CONFIRMED for existence | STALE COUNT — current: 1,779 records (see D-02) |

### Next Actions from This Session

1. **Stage 0 Diagnostics** (TC-C0-001 through TC-C0-006) — run capability tools in diagnostic mode
2. **Stage 1 Extension** (TC-C1-001/TC-C1-002) — extend TC-WIRE-001 to non-mainstream streams
3. **Stage 7** (TC-C7-001) — design capability closure wiring (highest-priority new RC-8 fix)

### Change Ledger (velvet-hatching-lark)

| Item | Change |
|------|--------|
| §3 RC-2 | Added 2026-06-23 update: TC-WIRE-001 COMPLETE for mainstream; RC-2 → PARTIALLY RESOLVED |
| §3 RC-4 | Added 2026-06-23 update: all 24 items have per-item advisory_only; CAP-GEN-011 invalidated |
| §3 RC-7 | Stage 7 reference updated → Stage 8 (authority fabric = future work) |
| §3 RC-8 | NEW ROOT CAUSE ADDED: Capability Closure Not Integrated |
| §6b | Stage 7 reference updated → Stage 8 |
| §8 Gates | C4: FAIL → PARTIAL; C9: FAIL (new) added |
| §8 Stage 3 | Human Gate Policy added before TC-C3-001; TC-C3-001 description updated |
| §9 Stage 7 | NEW STAGE: Capability Closure Wiring (TC-C7-001 through TC-C7-004) |
| §10 DAG | Stage 7 added to dependency graph |
| §11 Taskcards | TC-C7-001 through TC-C7-004 rows added |
| §2 Tables | Counts updated: 14,309 facts / 23 formats / 1,779 records / 927 gaps / 89 open |
| §2 Dormant | Compiler + consumer status: ZERO → CONDITIONAL (mainstream stream) |
| §3 Symptoms | S1 updated: partial resolution noted |
| §3 Root Causes | RC-2, RC-4 table entries updated |
| §4 SAL | Count updated: 14,309 / 23 formats |
| §7 Architecture | SAL fact count updated |
| §8 Gate C0 | Count updated: 14,309 / 23 formats / FODS: 4,987 |
| Appendix A | A-01, A-03, A-08 verdicts updated |
| Appendix B | Context + Risk Classification updated: ACTIVE → LATENT (81 FOSS open) |
| Appendix C | THIS APPENDIX — forensic session summary |
| Appendix D | Plan File Hardening — velvet-hatching-lark post-audit (2026-06-23) |

---

## Appendix D: Plan File Hardening — velvet-hatching-lark Post-Audit (2026-06-23)

### D.0 Plan File Hardening Change Log

| Rev | Date | Author | Change |
|-----|------|--------|--------|
| H-1.0 | 2026-06-23 | PLAN_FILE_HARDENING_MODE | Post-sprint evidence-based audit incorporated: grader rejections (TC-VHL-001/006/010 OVERCLAIMED) converted to taskcards; gap-ledger regeneration risk (new), RCAL unwired (A-10), declaration evidence-tagging mismatch (A-09) all taskcardsed; continuation block root cause documented; hardening sections added; required verification matrix, gate contract, evidence contract, repair loop, anti-overclaim rules, closeout criteria, remaining blockers |

---

### D.1 Audit Findings Incorporated

Source: Evidence-based sprint review of `velvet-hatching-lark-forensics-20260623`, run `capability-fact-to-feature-forensics-20260623-06f0ea05`. Supervisor grade: `ACCEPTED_WITH_REWORK` — 0 accepted, 3 OVERCLAIMED, autonomous_continue=False.

| Finding ID | Finding | Severity | Taskcard | Status |
|------------|---------|----------|----------|--------|
| FIND-VHL-001 | TC-VHL-001/006/010 evidence artifacts do not tag parent item IDs — grader cannot match evidence to planned items; all 3 graded OVERCLAIMED | CRITICAL (blocks continuation) | TC-VHL-REWORK-001 | READY |
| FIND-VHL-002 | Plan modifications from velvet-hatching-lark are in working tree only — NOT committed; `git clean -f` destroys them | HIGH | TC-VHL-REWORK-002 | READY |
| FIND-VHL-003 | Gap-ledger regeneration risk: `capability_map_generator.py` may overwrite the 838 manually-closed gaps on next generation run — not yet verified | HIGH | TC-VHL-REWORK-003 | READY |
| FIND-VHL-004 | A-10 contradicted: `authority_integration_fabric.py` is not imported or called by `supervisor_loop.py`; RCAL proof graph never consulted in sprint grading; no plan stage targets this | HIGH | TC-C8-001 (new stage) | READY |
| FIND-VHL-005 | A-09 structural pattern: evidence artifacts must tag parent item IDs (not just sub-item IDs) for the grader to accept planned items; this will recur in every future sprint that uses sub-item numbering | MEDIUM | TC-VHL-REWORK-004 | READY |
| FIND-VHL-006 | A-06 updated: `close_*.py` scripts close gaps by file-existence check, NOT test-pass verification; 838 closed gaps may not have verified test coverage | MEDIUM | TC-C4-AUDIT-001 (new) | READY |
| FIND-VHL-007 | CAP-GEN-011 is an invalid diagnosis — field already present in all 24 items — but it may still be listed as an open task in execution queues; must be formally removed | LOW | TC-VHL-REWORK-005 | READY |
| FIND-VHL-008 | Continuation signal is blocked (`autonomous_continue=False`, `hard_stops_detected=[critical_rework_blocks_continuation]`); 3 rework items (TC-VHL-001, TC-VHL-006, TC-VHL-010) must be re-submitted before autonomous loop resumes | CRITICAL | TC-VHL-REWORK-001 | READY |

---

### D.2 Resolved / Preserved Work

The following work from prior sessions is confirmed complete and must NOT be re-executed:

| Item | Evidence | Classification |
|------|----------|----------------|
| D-05: CAP-GEN-011 invalid diagnosis confirmed | All 24 action-queue.json items have per-item advisory_only:true; VAL-009 passes | COMPLETED_AND_VERIFIED |
| D-06: CAP-NETPBM-CLEANUP-001 superseded | 0 collection errors; only 3 real test files exist; no stubs | COMPLETED_AND_VERIFIED |
| D-07: PGM function implementations confirmed | pgm_dark_pixel_ratio (line 491) and pgm_bright_pixel_ratio (line 19) exist; 761 PGM tests pass | COMPLETED_AND_VERIFIED |
| TC-WIRE-001: Mainstream compiler invocation chain live | `_run_capability_consumer()` at `generate_next_worker_prompt.py:1037` confirmed; chain diagram in evidence | COMPLETED_BUT_WEAKLY_VERIFIED (code-inspection; no runtime trace) |
| SAL fact count corrected to 14,309 / 23 formats | sal-input-census.json; plan §1/§2/§4 updated | COMPLETED_AND_VERIFIED |
| Capability record count corrected to 1,779 | unified-capability-map.json 2026-06-23 generation; plan §1/§2 updated | COMPLETED_AND_VERIFIED |
| Gap ledger count corrected to 927 / 89 open / 838 closed | gap-ledger.json 2026-06-23 generation; plan §1/§2 updated | COMPLETED_AND_VERIFIED |
| RC-8 new root cause documented | closure-feedback-analysis.md; Stage 7 taskcards added (TC-C7-001 through TC-C7-004) | COMPLETED_AND_VERIFIED (finding documented; implementation NOT started) |
| A-04/05/06/08/09/10 contradicted in assumption register | capability-plan-assumption-register.yaml; Appendix A updated | COMPLETED_AND_VERIFIED |

---

### D.3 Unresolved Work Register

| Item | Why Unresolved | Required to Unblock |
|------|----------------|---------------------|
| TC-VHL-001/006/010 grader rejection | Evidence artifacts tagged sub-item IDs only; parent item IDs not found | TC-VHL-REWORK-001 — re-submit declaration with parent-ID-tagged artifacts |
| Plan working-tree changes not committed | 11 plan corrections in working tree only | TC-VHL-REWORK-002 — commit before next generator or clean run |
| Gap-ledger regeneration risk | Whether generator preserves or overwrites manual closures is unverified | TC-VHL-REWORK-003 — run generator with snapshot; compare before/after |
| A-10: RCAL proof graph unwired | `supervisor_loop.py` bypasses `authority_integration_fabric.py` | TC-C8-001 — new Stage 8 |
| A-06: 838 closed gaps not test-verified | close_*.py scripts check file existence, not test execution | TC-C4-AUDIT-001 — audit closure evidence quality |
| CAP-GEN-011 task in execution queues | Invalid diagnosis may still appear in next-sprint task lists | TC-VHL-REWORK-005 — remove from queues |
| Non-mainstream stream compiler coverage | TC-WIRE-001 complete for mainstream only; analytics and other streams still zero callers | TC-C1-EXTEND-001 (was TC-C1-002) |
| Compiler output injection into sprint prompt | Chain runs but output not confirmed consumed by sprint work selection | TC-C1-003 |
| Stage 7 implementation | TC-C7-001 through TC-C7-004 in taskcard table but no implementation started | TC-C7-001 → TC-C7-004 |

---

### D.4 Taskcard Register (Post-Hardening)

#### Immediate Unblock Tasks (must complete before autonomous cycle resumes)

---

**TC-VHL-REWORK-001: Re-Substantiate TC-VHL-001/006/010 Evidence Tags**

- **Status:** READY (CRITICAL BLOCKER — autonomous_continue=False until resolved)
- **Priority:** P0 — blocks all continuation
- **Lane:** capability_layer_forensics
- **Source finding:** FIND-VHL-001, FIND-VHL-008
- **Why it matters:** All 3 graded items OVERCLAIMED because evidence_artifacts only tag sub-item IDs (e.g., TC-VHL-001-02) not parent IDs (TC-VHL-001). The grader cannot match evidence to planned items. Continuation signal has `hard_stops_detected: [critical_rework_blocks_continuation]`.
- **Required work:**
  1. Add a new evidence artifact entry for TC-VHL-001 directly: path=`recon-intake.md`, description="Evidence directory exists and session context established", `related_work_items: [TC-VHL-001]`
  2. Add a new evidence artifact for TC-VHL-006: path=`plans/capability-fact-to-feature-production-plan.md`, type=source_change, description="11 surgical corrections applied — counts corrected, RC-2/RC-4/RC-8 updated", `related_work_items: [TC-VHL-006]`
  3. Add a new evidence artifact for TC-VHL-010: path=`evidence-declaration.yaml`, description="Evidence declaration written and validated with sprint_executor_validate.py", `related_work_items: [TC-VHL-010]`
  4. Re-run supervisor pipeline: `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/capability-fact-to-feature-forensics-20260623-06f0ea05/capability-fact-to-feature/evidence-declaration.yaml`
- **Required verification:** Supervisor output shows 0 OVERCLAIMED, 3 accepted; `autonomous_continue` returns to true
- **Required evidence:** Supervisor-review.md from the re-submission showing TC-VHL-001/006/010 as accepted; continuation-signal.json with `autonomous_continue: true`
- **Acceptance criteria:** All three items accepted; continuation signal unblocked
- **Stop conditions:** If resubmission fails, inspect the actual grader rejection message; do not resubmit more than twice without understanding root cause
- **Allowed actions:** Edit evidence-declaration.yaml; run supervisor pipeline
- **Forbidden actions:** Do NOT delete existing evidence artifacts; do NOT change completed_work_items list
- **Dependencies:** TC-VHL-REWORK-002 must complete first (plan changes committed before referencing the plan file as an evidence artifact)
- **Closeout rules:** Item is closed when supervisor accepts all 3 and `autonomous_continue=true` in continuation signal

---

**TC-VHL-REWORK-002: Commit Plan Working-Tree Modifications**

- **Status:** READY
- **Priority:** P0 — plan modifications at risk; required before TC-VHL-REWORK-001
- **Lane:** capability_layer_forensics
- **Source finding:** FIND-VHL-002
- **Why it matters:** 11 corrections to `plans/capability-fact-to-feature-production-plan.md` (including this Appendix D) exist only in the working tree. A `git clean -f` or rebase would destroy them. The plan file is referenced as evidence artifact for TC-VHL-006 — it must be committed before the evidence resubmission.
- **Required work:**
  1. `git add plans/capability-fact-to-feature-production-plan.md`
  2. `git commit -m "docs(plans): velvet-hatching-lark forensic corrections + plan hardening (11 corrections + Appendix D)"`
- **Required verification:** `git log --oneline -1 -- plans/capability-fact-to-feature-production-plan.md` shows the commit; `git diff HEAD -- plans/...` returns empty
- **Required evidence:** Git commit hash; `git show --stat HEAD` confirming the plan file
- **Acceptance criteria:** Plan file committed; working tree clean for this file
- **Forbidden actions:** Do NOT use `--no-verify`; do NOT amend a prior commit
- **Dependencies:** None
- **Closeout rules:** Closed when git log shows the commit

---

**TC-VHL-REWORK-003: Verify Gap-Ledger Regeneration Behavior**

- **Status:** READY
- **Priority:** P1
- **Lane:** capability_layer_forensics
- **Source finding:** FIND-VHL-003
- **Why it matters:** 838 gaps are currently marked closed by manual `close_*.py` scripts. If `capability_map_generator.py` regenerates gap-ledger.json from scratch (overwriting closed-status entries), those 838 closures are ephemeral. This would silently re-open all closed gaps on the next generator run.
- **Required work:**
  1. Read the gap-ledger.json generation code: `python -c "from pathlib import Path; txt = Path('tools/capability_layer/capability_map_generator.py').read_text(); print('merge' if 'merge' in txt.lower() or 'existing' in txt.lower() else 'OVERWRITES')" `
  2. If the generator overwrites: add a snapshot/merge step — before generation, read existing closed-status entries; after generation, re-apply closures from the snapshot. Record as TC-C4-REGEN-001.
  3. If the generator merges: document the merge logic location and add a regression test.
- **Required verification:** Run generator; compare `gap-ledger.json` closed-gap count before and after. Count must not decrease.
- **Required evidence:** Before-count and after-count of `jq '[.[] | select(.status=="closed")] | length' reports/capability-layer/gap-ledger.json`; generator run log
- **Acceptance criteria:** Either (a) generator proved to preserve closures with regression test added, OR (b) merge step implemented and tested
- **Stop conditions:** If generator run modifies other plan-critical files unexpectedly, STOP and investigate
- **Forbidden actions:** Do NOT run the generator without first capturing the before-count; do NOT delete existing closed-gap entries as a workaround
- **Dependencies:** None
- **Closeout rules:** Closed when verification evidence shows closed count preserved; regression test committed

---

**TC-VHL-REWORK-004: Establish Parent-ID Evidence Tagging Pattern for All Future Sprints**

- **Status:** READY
- **Priority:** P2
- **Lane:** governance
- **Source finding:** FIND-VHL-005 (A-09 structural pattern)
- **Why it matters:** The grader matches evidence to planned items by `related_work_items` in `evidence_artifacts`. Sprints that use sub-item numbering (TC-VHL-001-01, etc.) must ALSO tag the parent ID (TC-VHL-001) in at least one artifact. This failure pattern will recur in every future sprint using hierarchical task decomposition.
- **Required work:**
  1. Add a rule to `docs/automation/supervisor-worker-contract.md`: "If a planned_work_item has sub-items, at least one evidence artifact MUST include the parent item ID in related_work_items."
  2. Add a check to `tools/supervisor/sprint_executor_validate.py`: for each planned_work_item ID, verify at least one evidence_artifact has it in related_work_items; warn (not fail) if parent ID is absent.
- **Required verification:** Run `sprint_executor_validate.py` against the velvet-hatching-lark declaration and confirm it would now warn about TC-VHL-001/006/010
- **Required evidence:** Updated supervisor-worker-contract.md; sprint_executor_validate.py diff; validator output showing warning
- **Acceptance criteria:** New check in validator; documentation updated; no existing tests broken
- **Forbidden actions:** Do NOT make the check a hard FAIL until at least one sprint has verified it works correctly
- **Dependencies:** None
- **Closeout rules:** Closed when validator check exists and documentation updated

---

**TC-VHL-REWORK-005: Reconcile CAP-GEN-011 Diagnosis History**

- **Status:** SUPERSEDED — CAP-GEN-011 was VALIDLY EXECUTED in cap-layer-hardening-exe sprint (2026-06-23)
- **Priority:** P2 (informational only — no blocking action required)
- **Lane:** governance
- **Source finding:** FIND-VHL-007 (SUPERSEDED by FIND-HARDEN-001 in Appendix E)
- **Why it matters (HISTORICAL):** The velvet-hatching-lark forensic scan found 24/24 items with advisory_only=True in the ALREADY-REGENERATED action-queue.json. This was misread as "the field already exists" = fix not needed. In reality, the GENERATOR SOURCE CODE had 3 buggy sites that would emit advisory_only=False on any fresh regeneration. The cap-layer-hardening-exe sprint correctly identified and fixed those 3 generator sites.
- **Corrected understanding:** CAP-GEN-011 was NOT an invalid diagnosis at the generator code level. The invalidation in Appendix C §CAP-GEN-011 referred to the ALREADY-GENERATED FILE content, not the generator's code behavior on re-run.
- **Resolved by:** cap-layer-hardening-exe sprint (run-id: cap-layer-hardening-exe-20260623-06f0ea). Generator now emits advisory_only=True unconditionally. action-queue.json regenerated with 24/24 True. validate() passes.
- **Required work:** None — COMPLETE
- **Required evidence (already exists):** `tools/capability_layer/capability_map_generator.py` (3 sites fixed); `reports/capability-layer/action-queue.json` (24/24 advisory_only=True); supervisor review ACCEPTED_WITH_LIMITATIONS
- **Acceptance criteria:** MET — fix executed and accepted
- **Closeout rules:** CLOSED — documented as SUPERSEDED; no further work required

---

#### Stage Extension Tasks (existing stage coverage gaps)

---

**TC-C1-EXTEND-001: Extend Compiler Invocation to Non-Mainstream Streams**

- **Status:** PARTIALLY_DONE (mainstream complete via TC-WIRE-001; non-mainstream streams have zero callers)
- **Priority:** P2
- **Lane:** stage_1_compiler_wiring
- **Source finding:** Discrepancy D-01 residual gap; compiler-invocation-chain.md §Remaining Gap
- **Why it matters:** Non-mainstream streams (e.g., "analytics") skip `_run_capability_consumer()`. Any sprint run with a non-mainstream stream configuration bypasses the compiler entirely.
- **Required work:**
  1. Read `generate_next_worker_prompt.py` lines 1030-1045 — understand the stream guard condition
  2. Determine which non-mainstream streams are active in production (check `.supervisor/policies.yaml` stream config)
  3. For each active non-mainstream stream: extend the `effective_stream in ("mainstream", "product", None)` condition OR add a separate consumer call without the stream guard
  4. Add test: `test_compiler_called_for_all_active_streams.py`
- **Required verification:** Run supervisor cycle with `stream="analytics"` and confirm compiler is invoked; test passes
- **Required evidence:** Code diff; test output; supervisor cycle log showing consumer subprocess invoked
- **Acceptance criteria:** All production-active streams invoke the compiler consumer; test covers each stream
- **Dependencies:** TC-WIRE-001 (COMPLETE for mainstream)
- **Closeout rules:** Closed when test passes for all streams and no stream bypasses consumer

---

**TC-C4-AUDIT-001: Audit Closed Gap Evidence Quality**

- **Status:** READY
- **Priority:** P2
- **Lane:** stage_4_contract_closure
- **Source finding:** FIND-VHL-006; A-06 updated verdict
- **Why it matters:** 838 gaps are marked closed by `close_*.py` scripts that check FILE EXISTENCE (not test execution). The gap-ledger may overstate verified closed work. Before Stage 4 (contract-based closure) proceeds, we need to know how many of the 838 closures have real test backing.
- **Required work:**
  1. Sample 20 closed gaps from gap-ledger.json: read `closed_by` field (should be a test file path)
  2. For each sampled gap: check if the test file exists AND run the test to confirm it passes
  3. Count: (a) closed_by test file exists AND passes, (b) closed_by test file exists but test fails, (c) closed_by test file is absent
  4. If >10% of sample falls into category (b) or (c): escalate to TC-C4-AUDIT-002 (full audit)
- **Required verification:** 20-gap sample with test-execution results for each
- **Required evidence:** Sample results table (gap_id, closed_by, test_exists, test_result); conclusion on closure quality
- **Acceptance criteria:** Sample completed; quality classification documented; escalation decision made
- **Dependencies:** None
- **Closeout rules:** Closed when sample is completed and escalation decision is documented

---

#### New Stage 8: Authority Fabric Integration

**TC-C8-001: Wire authority_integration_fabric.py into supervisor_loop.py**

- **Status:** READY
- **Priority:** P3
- **Lane:** stage_8_authority_fabric (NEW STAGE)
- **Source finding:** FIND-VHL-004; A-10 CONTRADICTED
- **Why it matters:** `supervisor_loop.py` does NOT import or invoke `authority_integration_fabric.py`. This means sprint grading decisions bypass the RCAL proof graph (18 node types, 19 edge types, 8 invariants defined in `docs/governance/requirement-capability-authority-layer.md`). Every sprint grade is currently made without authority validation.
- **Required work:**
  1. Read `tools/supervisor/authority_integration_fabric.py` — identify the primary API entry point (consult function list; likely `evaluate_requirement_authorization()` or similar)
  2. Read `tools/supervisor/supervisor_loop.py` — identify where grade decisions are finalized
  3. Determine integration pattern: library import vs. subprocess call (follow the subprocess pattern used by TC-WIRE-001)
  4. Add a subprocess invocation of the authority fabric to the grading pipeline — at minimum: log when authority consultation is skipped vs. invoked
  5. Add test: `test_supervisor_loop_invokes_authority_fabric.py`
- **Required verification:** Run `supervisor_loop.py autonomous-cycle` with a test declaration and confirm authority fabric is invoked (subprocess or import); test passes
- **Required evidence:** Code diff; test output; supervisor cycle log showing authority fabric invocation
- **Acceptance criteria:** `supervisor_loop.py` invokes the authority fabric for PRODUCT_SOURCE items at minimum; no existing tests broken
- **Stop conditions:** If authority fabric invocation causes grade results to change dramatically (>10% item grade change), STOP and investigate before proceeding
- **Forbidden actions:** Do NOT force-patch grade results to match authority fabric without understanding why they differ; do NOT remove existing grading logic
- **Dependencies:** TC-C1-003 (compiler output consumed), TC-C6-001 (lane gate hardening)
- **Closeout rules:** Closed when test passes and no existing test regressions

---

### D.5 Lane Ownership

| Lane | Owner | Taskcards |
|------|-------|-----------|
| capability_layer_forensics | autonomous agent (current session) | TC-VHL-REWORK-001, TC-VHL-REWORK-002, TC-VHL-REWORK-003, TC-VHL-REWORK-004, TC-VHL-REWORK-005 |
| stage_1_compiler_wiring | autonomous agent | TC-C1-EXTEND-001, TC-C1-003 |
| stage_4_contract_closure | autonomous agent | TC-C4-AUDIT-001 |
| stage_7_closure_wiring | autonomous agent | TC-C7-001, TC-C7-002, TC-C7-003, TC-C7-004 |
| stage_8_authority_fabric | autonomous agent | TC-C8-001 |
| governance | autonomous agent | TC-VHL-REWORK-004, TC-VHL-REWORK-005 |
| external (Gate 11 execution) | Babar Raza | — |

---

### D.6 Gate Contract

| Gate | Condition | Blocking? | Evidence Required |
|------|-----------|-----------|-------------------|
| GATE-UNBLOCK-001 | TC-VHL-001/006/010 grader acceptance | YES — blocks autonomous_continue | Supervisor review showing 0 OVERCLAIMED; continuation-signal with autonomous_continue=true |
| GATE-COMMIT-001 | Plan file committed to git | YES — blocks GATE-UNBLOCK-001 | git log showing commit; git diff HEAD empty for plan file |
| GATE-REGEN-001 | Gap-ledger regeneration behavior verified | YES — blocks Stage 7 execution | Before/after closed-gap count comparison; test or documented merge logic |
| GATE-CLOSURE-AUDIT-001 | Closed gap evidence quality sampled (TC-C4-AUDIT-001) | YES — blocks Stage 4 contract closure | 20-gap sample with test execution results |
| GATE-AUTHORITY-001 | Authority fabric invoked in supervisor loop | NO — improvement only for now | Test proving invocation; no grade regressions |
| GATE-C0 through GATE-C8 | Per-stage gates from §8 | YES per stage | See §8 for each gate's evidence requirements |

---

### D.7 Evidence Contract (Updated)

Every taskcard completion in this plan must produce all of the following:

1. **Source diff** — `git diff HEAD -- <file>` showing exact changes
2. **Test results** — pytest output with pass/fail/skip counts; zero failures required
3. **Gate status** — which gate (C0-C8, GATE-UNBLOCK, GATE-COMMIT, GATE-REGEN, etc.) advances
4. **Parent-ID evidence tagging (MANDATORY):** Every `planned_work_item` ID must appear in at least one `evidence_artifact.related_work_items` list — both parent AND sub-item IDs must be explicitly tagged
5. **Consumer proof** — for Stage 1+: evidence that output is consumed by the next pipeline stage; not just that the output file exists
6. **Continuation signal check** — after each sprint cycle, confirm `autonomous_continue` status and `hard_stops_detected` is empty
7. **Supervisor round-trip** — every sprint must end with `supervisor_loop.py autonomous-cycle` completing with exit code 0 and 0 OVERCLAIMED items

**Anti-pattern:** Tagging only sub-item IDs (TC-VHL-001-02) while omitting the parent (TC-VHL-001) is PROHIBITED. The grader rejects planned items with no directly-tagged evidence artifact.

---

### D.8 Verification Matrix

| Capability | Required verification method | Current status |
|---|---|---|
| Evidence tagging — parent IDs | `sprint_executor_validate.py` check (TC-VHL-REWORK-004) | NOT VERIFIED — check does not exist yet |
| Gap-ledger closure durability | Generator before/after comparison (TC-VHL-REWORK-003) | NOT VERIFIED |
| Mainstream compiler invocation | `compiler-invocation-chain.md` code inspection | VERIFIED at code level (PL-2); runtime not demonstrated |
| Non-mainstream compiler invocation | Test with stream="analytics" (TC-C1-EXTEND-001) | NOT VERIFIED — zero callers |
| 838 closed gaps are test-backed | 20-gap sample with test execution (TC-C4-AUDIT-001) | NOT VERIFIED |
| Authority fabric invoked in grading | Test (TC-C8-001) | NOT VERIFIED — not wired |
| Compiler output consumed by sprint | TC-C1-003 end-to-end trace | NOT VERIFIED — chain runs but output destination unconfirmed |
| Stage 7 gap closure integration | TC-C7-001 through TC-C7-004 | NOT STARTED |
| Continuation signal unblocked | Supervisor resubmission (TC-VHL-REWORK-001) | BLOCKED — 3 overclaimed items pending |

---

### D.9 Repair Loop

If any step below fails, STOP at that step and resolve before proceeding:

1. Commit plan file (TC-VHL-REWORK-002) → verify `git diff HEAD` is empty for plan
2. Re-tag evidence declaration (TC-VHL-REWORK-001) → verify supervisor accepts 0 OVERCLAIMED
3. Verify gap-ledger regeneration behavior (TC-VHL-REWORK-003) → verify closed count preserved
4. Audit closed gap evidence quality (TC-C4-AUDIT-001) → document quality classification
5. Remove CAP-GEN-011 from queues (TC-VHL-REWORK-005) → verify no open references
6. Add parent-ID tagging rule to validator (TC-VHL-REWORK-004) → verify check exists
7. Extend compiler to non-mainstream streams (TC-C1-EXTEND-001) → test passes
8. Implement gap closure integration (TC-C7-001 → TC-C7-004) → idempotency test passes
9. Wire authority fabric (TC-C8-001) → no grade regressions

If TC-VHL-REWORK-001 re-submission fails after 2 attempts: investigate the grader's actual rejection message (not the template message); do NOT retry with the same evidence.

If gap-ledger regeneration (TC-VHL-REWORK-003) reveals generator overwrites closures: STOP Stage 7 work until a merge/snapshot mechanism is implemented and tested.

---

### D.10 Anti-Overclaim Rules

The following claims from this sprint must not be repeated as-is:

| Incorrect claim | Correct statement |
|-----------------|-------------------|
| "TC-VHL-001/006/010 COMPLETE" (in declaration) | "TC-VHL-001/006/010 work performed but grader requires parent-ID evidence tagging — items require re-declaration" |
| "Compiler has zero production callers" | "Compiler has CONDITIONAL callers for mainstream/product streams; zero callers for non-mainstream streams; compiler output not yet confirmed consumed by sprint flow" |
| "838 gaps are verified closed" | "838 gaps are marked closed by manual scripts that check file existence; test-execution verification has not been performed on a representative sample" |
| "System healing gate confirms integration" | "System healing gate confirms output files exist; does not verify consumer behavior" |
| "Authority integration fabric is wired" | "authority_integration_fabric.py exists and has 43 callers in the repo but supervisor_loop.py is NOT one of them; RCAL proof graph is not consulted in sprint grading" |
| "Gap closure is automatic after sprint PASS" | "Gap closure is entirely manual via one-off scripts; autonomous cycle never updates gap status post-grade" |
| "CAP-GEN-011 needs to be fixed" | "CAP-GEN-011 fix was VALID and EXECUTED — generator had 3 buggy code paths emitting advisory_only=False on fresh regeneration; all fixed; action-queue regenerated with 24/24 advisory_only=True; supervisor ACCEPTED_WITH_LIMITATIONS (evidence gap in declaration, not code gap)" |

**Additional anti-overclaim requirements for all future sprint declarations:**
- Do NOT tag only sub-item IDs in evidence_artifacts — always include parent item ID
- Do NOT claim a compiler chain is "end-to-end proven" until output is traced to sprint prompt consumption
- Do NOT claim gap closure is verified without showing test execution results (not file existence)
- Do NOT claim a gate passes if the gate only checks file existence and not consumer behavior

---

### D.11 Closeout Criteria

This plan may proceed to Stage 1+ execution only when ALL of the following are true:

1. `plans/capability-fact-to-feature-production-plan.md` is committed to git (TC-VHL-REWORK-002)
2. Supervisor accepts TC-VHL-001, TC-VHL-006, TC-VHL-010 — 0 OVERCLAIMED — and `autonomous_continue=true` (TC-VHL-REWORK-001)
3. Gap-ledger regeneration behavior is verified (either generator preserves closures, or a snapshot/merge mechanism is implemented and tested) (TC-VHL-REWORK-003)
4. CAP-GEN-011 references removed from all execution queues (TC-VHL-REWORK-005)
5. Evidence tagging parent-ID rule documented in supervisor-worker-contract.md (TC-VHL-REWORK-004)
6. For Stage 7 execution specifically: TC-C4-AUDIT-001 closed-gap quality sample completed
7. For Stage 8 execution specifically: TC-C8-001 authority fabric wired and tested

The plan must NOT be declared TERMINAL_CLOSED until Stage 7 (gap closure integration) is implemented, tested, and the autonomous cycle demonstrates at least one post-grade gap status update.

---

### D.12 Remaining True Blockers

| Blocker | Type | Resolved by |
|---------|------|-------------|
| TC-VHL-001/006/010 grader rejection — `autonomous_continue=False` | Declaration mechanics | TC-VHL-REWORK-001 (after TC-VHL-REWORK-002) |
| Plan file uncommitted — loss risk | Repository hygiene | TC-VHL-REWORK-002 |
| Gap-ledger regeneration risk — 838 closures may be ephemeral | Architectural | TC-VHL-REWORK-003 |
| Authority fabric unwired in supervisor_loop.py | Architectural | TC-C8-001 |
| Gap closure not integrated into autonomous cycle | Structural (RC-8) | TC-C7-001 through TC-C7-004 |
| Non-mainstream stream compiler still zero callers | Coverage gap | TC-C1-EXTEND-001 |

---

## Appendix E: Plan File Hardening — cap-layer-hardening-exe Post-Audit (2026-06-23)

### E.0 Plan File Hardening Change Log

| Rev | Date | Author | Change |
|-----|------|--------|--------|
| H-2.0 | 2026-06-23 | PLAN_FILE_HARDENING_MODE | Post-sprint evidence-based audit of cap-layer-hardening-exe-20260623-06f0ea incorporated: 3 completed taskcards status-updated; Appendix C CAP-GEN-011 INVALIDATED corrected to EXECUTED; Appendix C CAP-NETPBM-CLEANUP-001 SUPERSEDED corrected to COMPLETE; D.10 anti-overclaim CAP-GEN-011 entry corrected; TC-VHL-REWORK-005 updated to SUPERSEDED; new taskcards TC-SIGNAL-RESET-001, TC-EVIDENCE-QUAL-001 added; remaining P2 items CAP-COMPILE-TRACK-001, CAP-UNPROVEN-001 registered as not_attempted |

---

### E.1 Audit Findings Incorporated

**Source:** Evidence-based sprint review of `cap-layer-hardening-exe-20260623-06f0ea`.
**Supervisor grade:** ACCEPTED (Global Status: ACCEPTED, Autonomous Continue: True per sprint exit 0).
**Review package SHA-256:** `66cd1f4a39de062fa072452bfa227a9da5b38c9d55d0a31b1790db201382a615`

| Finding ID | Finding | Severity | Taskcard | Status |
|------------|---------|----------|----------|--------|
| FIND-HARDEN-001 | Appendix C CAP-GEN-011 "INVALIDATED" was incorrect — generator had 3 buggy code sites emitting advisory_only=False on regeneration; velvet-hatching-lark read the ALREADY-REGENERATED file not the code paths | HIGH | TC-VHL-REWORK-005 (SUPERSEDED) | RESOLVED |
| FIND-HARDEN-002 | continuation-signal.json overwritten by different session (FF-PLAN-GOV-001, session 60766799b1eb); current signal shows GOV_BLOCKs and autonomous_continue=false belonging to different sprint | CRITICAL | TC-SIGNAL-RESET-001 | READY |
| FIND-HARDEN-003 | CAP-GEN-011 evidence gap: 7 updated test files not in evidence_paths for the item; LLM reviewer downgraded to ACCEPTED_WITH_LIMITATIONS despite valid code fix | MEDIUM | TC-EVIDENCE-QUAL-001 | READY |
| FIND-HARDEN-004 | D.10 anti-overclaim "CAP-GEN-011 is INVALID_DIAGNOSIS — do not implement" was wrong; corrected in D.10 in place | MEDIUM | Corrected in D.10 | RESOLVED |
| FIND-HARDEN-005 | Loop-decision quality scorer (test_coverage=1) produces STRUCTURED_NOT_GREEN for GOVERNANCE_TASKCARDs where N/A by design; supervisor grader correctly ACCEPTS via file-content validation | LOW | Document in E.7 | RESOLVED |
| FIND-HARDEN-006 | TC-COMPILE-TRACK-001 and TC-UNPROVEN-001 from planned Appendix E work remain NOT_ATTEMPTED | MEDIUM | TC-COMPILE-TRACK-001, TC-UNPROVEN-001 | not_attempted |

---

### E.2 Resolved / Preserved Work

Work completed in cap-layer-hardening-exe sprint — confirmed by git diff, artifact inspection, and supervisor ACCEPTED grade:

| Item | Evidence | Classification | Supervisor Grade |
|------|----------|----------------|-----------------|
| CAP-NETPBM-LEDGER-001: Fix 2 PGM test expectation bugs | git diff: method rename + assertion 0.25->0.5 in test_r256 and test_r258; 2409 tests pass | completed_verified | ACCEPTED_VERIFIED |
| CAP-NETPBM-CLEANUP-001: Remove 99 netpbm stub files | netpbm-cleanup-verification.log: 2409 passed, 9 skipped, 0 collection errors | completed_verified | ACCEPTED_VERIFIED |
| CAP-GEN-011: Fix generator advisory_only invariant (3 sites) | git diff 3 sites False->True; action-queue.json 24/24 advisory_only=True; validate() 0 errors; 106 capability_layer tests pass | completed_but_weakly_verified (evidence declaration missing 7 test files) | ACCEPTED_WITH_LIMITATIONS |
| TC-VHL-REWORK-005: CAP-GEN-011 queue removal | SUPERSEDED — fix was validly executed; the "invalid diagnosis" conclusion was wrong at the generator code level | SUPERSEDED | N/A |

---

### E.3 Unresolved Work Register (Post-cap-layer-hardening-exe)

| Item | Why Unresolved | Priority | Required to Unblock |
|------|----------------|----------|---------------------|
| continuation-signal.json stale/cross-session | Signal from FF-PLAN-GOV-001 (session 60766799b1eb) overwrote cap-layer-hardening-exe exit-0 result | CRITICAL | TC-SIGNAL-RESET-001 |
| CAP-GEN-011 evidence gap (7 test files not declared) | Pattern will recur for future fix sprints; supervisor will downgrade | MEDIUM | TC-EVIDENCE-QUAL-001 |
| TC-COMPILE-TRACK-001 (compiler invocation tracking) | Not attempted | P2 | TC-COMPILE-TRACK-001 |
| TC-UNPROVEN-001 (12 CLAIMED_UNPROVEN gap upgrades) | Not attempted | P2 | TC-UNPROVEN-001 |
| TC-VHL-REWORK-001 through TC-VHL-REWORK-004 (Appendix D) | Still pending from velvet-hatching-lark | P0-P2 | See Appendix D |

---

### E.4 Taskcard Register (Post-cap-layer-hardening-exe)

---

**TC-SIGNAL-RESET-001: Investigate and Resolve Cross-Session Continuation Signal**

- **Status:** READY — CRITICAL BLOCKER for autonomous continuation
- **Priority:** P0 — autonomous loop cannot resume until resolved
- **Lane:** governance
- **Source finding:** FIND-HARDEN-002
- **Why it matters:** The live `continuation-signal.json` belongs to `FF-PLAN-GOV-001-sprint-001` (session `60766799b1eb`), not the current work. It shows `autonomous_continue: false` with `rework_items` containing TC-PG-001 through TC-PG-009 and two GOV_BLOCKs. The GOV_BLOCKs may be from a crashed/abandoned session (stale) or from real currently-failing source files (actionable). The two cases require different responses.
- **Required work:**
  1. Read `.local/supervisor/continuation-signal.json` — confirm session_id is `60766799b1eb`
  2. Read `.local/supervisor/plan-locks/` — check if a lock for session `60766799b1eb` exists and its status
  3. **If plan-lock is COMPLETE or missing:** signal is orphaned — run `python tools/supervisor/reset_track_signal.py --track product`
  4. **If plan-lock is IN_PROGRESS:** that session's plan may be active — read it and determine if still valid
  5. **If GOV_BLOCK:monolith_detection_validator is present:** run `python tools/validators/source_structure_validator.py --json` to verify if any real source file currently exceeds the LOC cap
  6. **If real GOV_BLOCK:** execute analytics separation per CLAUDE.md GOV_BLOCK Exception before proceeding to anything else
  7. After reset or resolution: run `python tools/supervisor/check_continuation.py` and confirm CONTINUE
- **Required verification:** `check_continuation.py` returns exit 0 + verdict=CONTINUE with no GOV_BLOCKs
- **Required evidence:** Plan-lock inspection; reset or resolution command output; check_continuation.py CONTINUE output
- **Acceptance criteria:** check_continuation.py returns CONTINUE; no GOV_BLOCKs; session_id matches current
- **Stop conditions:** If GOV_BLOCK confirmed real (current source file exceeds LOC cap) STOP and execute analytics separation first
- **Allowed actions:** Read plan-locks; run reset_track_signal.py; run check_continuation.py; run source_structure_validator.py
- **Forbidden actions:** Do NOT reset if GOV_BLOCK is from a real currently-failing file; do NOT skip GOV_BLOCK resolution per CLAUDE.md
- **Dependencies:** None
- **Closeout rules:** Closed when check_continuation.py returns CONTINUE with 0 rework items and 0 GOV_BLOCKs

---

**TC-EVIDENCE-QUAL-001: Update Evidence Contract for Fix Sprints Involving Test Updates**

- **Status:** READY
- **Priority:** P1 — will recur in every future fix sprint
- **Lane:** governance
- **Source finding:** FIND-HARDEN-003
- **Why it matters:** CAP-GEN-011 was code-complete and test-verified but received ACCEPTED_WITH_LIMITATIONS because 7 updated test files were absent from `evidence_paths`. The LLM semantic verifier requires test files in evidence_paths to validate that behavioral changes are tested. This pattern will downgrade every future sprint that updates tests without listing them as evidence for the relevant work item.
- **Required work:**
  1. Add to `docs/automation/supervisor-worker-contract.md` under Evidence Contract: "FSE-001 — Fix Sprint Evidence Completeness: When a work item fixes a behavior AND updates test files, ALL updated test files MUST appear in evidence_paths for that work item."
  2. Add check to `tools/supervisor/sprint_executor_validate.py`: warn (not fail) when a GOVERNANCE_TASKCARD or PRODUCT_SOURCE item has test files in `changed_files` but none in `evidence_paths`
  3. Update D.7 Evidence Contract in this plan: add FSE-001 as a required rule
- **Required verification:** sprint_executor_validate.py warns when test files omitted from evidence_paths; no existing tests broken
- **Required evidence:** supervisor-worker-contract.md diff; sprint_executor_validate.py diff; validator warning shown
- **Acceptance criteria:** Rule documented; validator warns; no regressions
- **Forbidden actions:** Do NOT make the check a hard FAIL — warn only
- **Dependencies:** None
- **Closeout rules:** Closed when documentation updated and validator check exists

---

**TC-COMPILE-TRACK-001: Trace Compiler Output to Consumer (P2 — deferred)**

- **Status:** not_attempted
- **Priority:** P2
- **Lane:** stage_1_compiler_wiring
- **Source finding:** Original capability-fact-to-feature Appendix E intent; not executed in cap-layer-hardening-exe sprint
- **Why it matters:** TC-WIRE-001 confirms compiler invocation at `generate_next_worker_prompt.py:1037` (mainstream stream). But the compiler output file destination and whether it is subsequently read by any pipeline stage is unconfirmed. An unread compiler output means the chain is a no-op at runtime.
- **Required work:**
  1. Read `capability_to_feature_compiler.py` — find the default output path (`--output` default or `COMPILED_OUTPUT_PATH`)
  2. Grep `tools/supervisor/` and `tools/` for reads of that output path
  3. Document: consumer identified (with file + line) OR absence confirmed
  4. If no consumer: register TC-C1-003 for consumer wiring
- **Required verification:** A documented call chain from compiler invocation to compiler output read, or a documented absence with TC-C1-003 registered
- **Required evidence:** Grep output; call chain prose or absence documentation
- **Acceptance criteria:** Chain documented; consumer identified or TC-C1-003 created
- **Forbidden actions:** Do NOT modify compiler or consumers until chain is documented
- **Dependencies:** TC-WIRE-001 (complete)
- **Closeout rules:** Closed when consumer identified and documented OR TC-C1-003 created

---

**TC-UNPROVEN-001: Upgrade 12 CLAIMED_UNPROVEN Gap-Audit Entries (P2 — deferred)**

- **Status:** not_attempted
- **Priority:** P2
- **Lane:** stage_4_contract_closure
- **Source finding:** investigation-matrix-2026-06-23.md; 12 of 25 sampled gaps CLAIMED_UNPROVEN
- **Why it matters:** 12 gaps are marked closed without direct test-execution proof — only file-existence checks. These cannot be treated as verified closures. Upgrading requires per-gap test execution.
- **Required work:**
  1. Read `reports/capability-layer/investigation-matrix-2026-06-23.md` — identify the 12 CLAIMED_UNPROVEN gap IDs
  2. For each gap: run the associated test; record pass/fail
  3. For passing gaps: update gap-ledger entry with test reference; change status to verified_closed
  4. For failing gaps: re-open the gap; add to open gap register
- **Required verification:** 12 gaps each have a test execution result (not file-existence)
- **Required evidence:** Test run output per gap (12 entries); updated gap-ledger entries
- **Acceptance criteria:** All 12 have test-execution evidence; failing gaps re-opened
- **Forbidden actions:** Do NOT mark verified_closed based on file-existence alone
- **Dependencies:** TC-C4-AUDIT-001 (may provide additional context)
- **Closeout rules:** Closed when all 12 have test-execution evidence and statuses updated

---

### E.5 Lane Ownership (Updated)

| Lane | Owner | Taskcards |
|------|-------|-----------|
| capability_layer_forensics | autonomous agent | TC-VHL-REWORK-001, TC-VHL-REWORK-002, TC-VHL-REWORK-003, TC-VHL-REWORK-004 |
| stage_1_compiler_wiring | autonomous agent | TC-C1-EXTEND-001, TC-C1-003, TC-COMPILE-TRACK-001 |
| stage_4_contract_closure | autonomous agent | TC-C4-AUDIT-001, TC-UNPROVEN-001 |
| stage_7_closure_wiring | autonomous agent | TC-C7-001, TC-C7-002, TC-C7-003, TC-C7-004 |
| stage_8_authority_fabric | autonomous agent | TC-C8-001 |
| governance | autonomous agent | TC-SIGNAL-RESET-001, TC-EVIDENCE-QUAL-001, TC-VHL-REWORK-005 (SUPERSEDED) |
| external (Gate 11 execution) | Babar Raza | — |

---

### E.6 Gate Contract (Updated)

| Gate | Condition | Blocking? | Status | Evidence Required |
|------|-----------|-----------|--------|-------------------|
| GATE-SIGNAL-001 | continuation-signal.json current + autonomous_continue=true | YES | BLOCKED (cross-session) | TC-SIGNAL-RESET-001; check_continuation.py CONTINUE |
| GATE-UNBLOCK-001 | TC-VHL-001/006/010 grader acceptance | YES | BLOCKED (requires signal reset first) | Supervisor review 0 OVERCLAIMED |
| GATE-COMMIT-001 | Plan file committed to git | YES | BLOCKED (TC-VHL-REWORK-002) | git log showing commit |
| GATE-REGEN-001 | Gap-ledger regeneration verified | YES | OPEN | Before/after closed-gap count |
| GATE-CLOSURE-AUDIT-001 | 20-gap evidence quality sample | YES | OPEN | Sample with test execution results |
| GATE-EVIDENCE-QUAL-001 | FSE-001 fix-sprint evidence contract | NO | OPEN | supervisor-worker-contract.md update |
| GATE-C0 through GATE-C8 | Per-stage gates from section 8 | YES per stage | Per Appendix D | See section 8 |

---

### E.7 Evidence Contract Addendum (FSE-001 and FSE-002)

Additions to D.7 Evidence Contract:

**FSE-001 — Fix Sprint Evidence Completeness:** When a work item fixes a behavior AND updates test files to match the corrected behavior, ALL updated test files MUST appear in `evidence_paths` for that specific work item. Omitting test files causes the LLM semantic verifier to downgrade the item to ACCEPTED_WITH_LIMITATIONS regardless of code correctness.

**FSE-002 — Loop-Decision vs. Supervisor Grade Disambiguation:** The `review/loop-decision.json` quality scorer (STRUCTURED_NOT_GREEN when test_coverage=1) and `supervisor/work-item-grades.md` grader are separate assessment layers. For GOVERNANCE_TASKCARDs where test coverage is N/A by design (cleanup, config fixes, stub deletion), the supervisor grader overrides the quality scorer via file-content validation. STRUCTURED_NOT_GREEN in loop-decision does NOT override ACCEPTED_VERIFIED in work-item-grades.md. The canonical acceptance authority is `work-item-grades.md`.

---

### E.8 Verification Matrix (Updated)

| Capability | Required verification | Status |
|---|---|---|
| Continuation signal current + CONTINUE | check_continuation.py CONTINUE | BLOCKED (TC-SIGNAL-RESET-001) |
| CAP-GEN-011 generator fix persists on regeneration | Re-run capability_map_generator.py; verify 24/24 advisory_only=True | VERIFIED (last run 24/24 True) |
| CAP-NETPBM-CLEANUP-001 stub deletion permanent | pytest --collect-only tests/python/pbm|pgm|ppm/ shows 0 errors | VERIFIED (2409 pass, 0 errors) |
| CAP-NETPBM-LEDGER-001 test fixes correct | PGM threshold contracts documented; tests match | VERIFIED (git diff confirmed; ACCEPTED_VERIFIED) |
| Fix sprint evidence includes all test files | sprint_executor_validate.py FSE-001 check | NOT VERIFIED (TC-EVIDENCE-QUAL-001) |
| GOV_BLOCKs in current signal are real or stale | source_structure_validator.py --json | NOT VERIFIED (TC-SIGNAL-RESET-001) |
| Compiler output consumed by sprint pipeline | Grep trace of compiler output path | NOT VERIFIED (TC-COMPILE-TRACK-001) |
| 12 CLAIMED_UNPROVEN gaps have test evidence | Per-gap test execution | NOT VERIFIED (TC-UNPROVEN-001) |

---

### E.9 Repair Loop (Updated)

Execute in order. STOP at each step on failure before proceeding:

1. **[P0]** Investigate continuation-signal.json (TC-SIGNAL-RESET-001) — confirm CONTINUE or resolve GOV_BLOCKs; if real GOV_BLOCK: execute analytics separation first per CLAUDE.md
2. **[P0]** Commit plan file (TC-VHL-REWORK-002) — verify git diff HEAD empty for plan
3. **[P1]** Re-tag evidence for TC-VHL-001/006/010 (TC-VHL-REWORK-001) — supervisor accepts 0 OVERCLAIMED
4. **[P1]** Verify gap-ledger regeneration (TC-VHL-REWORK-003) — closed count preserved
5. **[P1]** Update evidence contract FSE-001 (TC-EVIDENCE-QUAL-001) — rule documented; validator warns
6. **[P2]** Add parent-ID tagging rule to validator (TC-VHL-REWORK-004) — check exists
7. **[P2]** Trace compiler output to consumer (TC-COMPILE-TRACK-001) — consumer identified or TC-C1-003 created
8. **[P2]** Upgrade 12 CLAIMED_UNPROVEN gaps (TC-UNPROVEN-001) — per-gap test evidence

---

### E.10 Anti-Overclaim Rules (Updated — supersedes conflicting D.10 entries)

| Incorrect claim | Correct statement |
|-----------------|-------------------|
| "CAP-GEN-011 is INVALID_DIAGNOSIS — do not implement" | "CAP-GEN-011 was validly diagnosed and EXECUTED — generator had 3 code paths emitting False on regeneration; all fixed; supervisor ACCEPTED_WITH_LIMITATIONS (code correct; evidence declaration gap)" |
| "CAP-NETPBM-CLEANUP-001 was SUPERSEDED — no stubs found" | "CAP-NETPBM-CLEANUP-001 was EXECUTED — 99 stub files deleted; verified by 0 collection errors; ACCEPTED_VERIFIED" |
| "Continuation is unblocked — hardening sprint exited 0" | "Hardening sprint exited 0 but continuation-signal.json was overwritten by a different session; current signal shows GOV_BLOCKs from FF-PLAN-GOV-001" |
| "Test files do not need to be in evidence_paths if they are listed in changed_files" | "ALL updated test files must appear in evidence_paths for the specific work item — changed_files alone is insufficient for semantic verification" |
| "STRUCTURED_NOT_GREEN in loop-decision overrides supervisor ACCEPTED grade" | "loop-decision quality scorer and supervisor grader are separate layers; work-item-grades.md is canonical; GOVERNANCE_TASKCARD file-content validation overrides test_coverage=1" |

---

### E.11 Closeout Criteria (Updated)

This plan may proceed to Stage 1+ autonomous execution only when ALL are true:

1. TC-SIGNAL-RESET-001 resolved — check_continuation.py returns CONTINUE, 0 GOV_BLOCKs
2. plans/capability-fact-to-feature-production-plan.md committed to git (TC-VHL-REWORK-002)
3. Supervisor accepts TC-VHL-001, TC-VHL-006, TC-VHL-010 with 0 OVERCLAIMED (TC-VHL-REWORK-001)
4. Gap-ledger regeneration behavior verified (TC-VHL-REWORK-003)
5. Evidence contract updated with FSE-001 fix-sprint rule (TC-EVIDENCE-QUAL-001)
6. For Stage 7 execution: TC-C4-AUDIT-001 closed-gap quality sample completed
7. For Stage 8 execution: TC-C8-001 authority fabric wired and tested

The plan must NOT be declared TERMINAL_CLOSED until Stage 7 (gap closure integration) demonstrates at least one post-grade gap status update in the autonomous cycle.

---

### E.12 Remaining True Blockers (Updated)

| Blocker | Type | Status | Resolved by |
|---------|------|--------|-------------|
| continuation-signal.json cross-session — GOV_BLOCKs from FF-PLAN-GOV-001 | State management | ACTIVE — CRITICAL | TC-SIGNAL-RESET-001 |
| TC-VHL-001/006/010 grader rejection | Declaration mechanics | ACTIVE (after signal reset) | TC-VHL-REWORK-001 |
| Plan file uncommitted | Repository hygiene | ACTIVE | TC-VHL-REWORK-002 |
| Gap-ledger regeneration risk | Architectural | OPEN | TC-VHL-REWORK-003 |
| Evidence contract missing FSE-001 | Process quality | OPEN | TC-EVIDENCE-QUAL-001 |
| Authority fabric unwired in supervisor_loop.py | Architectural | OPEN | TC-C8-001 |
| Gap closure not integrated into autonomous cycle | Structural (RC-8) | **RESOLVED** *(2026-06-24, iter 3)* — code path + data path complete. All 5 Stage 7 taskcards DONE. 32 tests pass. Production closures will activate on next gap-ledger-sourced sprint. | TC-C7-001 through TC-C7-005 |
| Non-mainstream stream compiler zero callers | Coverage gap | OPEN | TC-C1-EXTEND-001 |
| SAL spec_refs bulk-attached per format (RC-1 remaining) | Data granularity | **OPEN** *(2026-06-24, Stage 0 corrected)* — ALL format SAL facts bulk-attached to EVERY capability (e.g., 5,013 FODS facts per capability). Case normalization works; join is functional but non-specific. | TC-C5-001 (per-capability spec_refs) |
| Compiler CLI gap field mapping bug | Tool usability | **FIXED** *(2026-06-24, convergence iteration 2)* — `compile_gap_to_feature_ir()` now accepts both consumer-mapped fields (`format_id`/`function_name`) and raw gap-ledger fields (`format`/`capability_name`). 34 compiler tests pass. | TC-C1-005 (CLOSED) |

---

## Appendix D: Stage 0 Diagnostic Baseline Results (2026-06-24, convergence iteration 1)

**Run date:** 2026-06-24 | **Evidence directory:** `.local/stage0-diagnostics/`

### TC-C0-001: Capability Map Generator
- Output: 1,782 records (125 commercial + 1,657 FOSS), 910 gaps, 20 action items
- **Finding:** Counts drift between runs (last read: 1,003 gaps in production ledger vs 910 regenerated)
- Generator preserves closed status on regeneration (merge code lines 1280-1288)

### TC-C0-002: Capability Compiler (standalone CLI)
- **Bug found and FIXED (iteration 2):** CLI passed raw gap-ledger fields directly to `compile_gap_to_feature_ir()` without mapping `format→format_id`, `capability_name→function_name`. Result: `format_id=UNKNOWN`.
- **Fix applied:** `compile_gap_to_feature_ir()` now accepts both consumer-mapped and raw gap-ledger field names. Falls back to `format` when `format_id` absent; derives `function_name` from `capability_name`. 34 compiler tests pass.

### TC-C0-003: Queue Consumer
- Successfully compiled 3 gaps to taskcards (priority-ordered, deterministic selection)
- Output: `TC-94EE382C.json` (XCF), `TC-9306CA32.json` (ABW), `TC-A15E2748.json` (CSV)
- All taskcards have `advisory_only: True`

### TC-C0-004: FODS Trace Through Compiler
- Traced GAP-FODS-COMM-LOAD-001 through compiler (with consumer field mapping)
- Feature IR and taskcard correctly generated: `format_id=FODS, function_name=fods_load`
- **Finding:** `spec_qnames` has 5,009 entries — ALL FODS SAL facts bulk-attached to every capability. Confirms RC-1 remaining issue.

### TC-C0-005: SAL Fact Counts vs Capability spec_refs
- SAL facts use lowercase format IDs (`fods`, `fodt`); capabilities use uppercase (`FODS`, `FODT`). Both generator and compiler normalize to `.upper()` internally — the case difference does NOT break the join.
- **Corrected finding:** SAL facts ARE successfully attached as `spec_refs` (FODS capabilities have 5,013 spec_refs). However, ALL format facts are **bulk-attached** to EVERY capability in that format (RC-1 remaining issue). Spec_refs are format-level, not per-capability operation-level.
- 14,486 SAL facts across 25 formats; 1,782 capabilities across 18 formats.

### TC-C0-006: Evidence Path Format Baseline
- Evidence paths use relative paths from repo root (e.g., `.local/evidences/<run_id>/<subdir>/<filename>`)
- All 15 artifacts from velvet-hatching-lark evidence declaration resolve correctly
- Changed files also use relative paths and resolve correctly

### Gate Status Summary (post-Stage 0)

| Gate | Status | Evidence |
|------|--------|----------|
| C0 (SAL Input) | PASS | 14,486 facts, 25 formats |
| C1 (Fact-to-Capability) | PARTIAL — join works but bulk-attached (RC-1) | All format facts attached to every capability |
| C2 (Capability Granularity) | PASS | One function = one capability |
| C3 (Gap-Ledger Consumption) | PARTIAL | Read by task generator; 0 open FODS |
| C4 (Compiler Integration) | PARTIAL | Mainstream stream wired |
| C5 (Queue Executability) | FAIL | All items advisory_only=true |
| C6 (Contract Closure) | FAIL | AST-scan only |
| C7 (_EXPANSION_GOALS) | PARTIAL | Fallback only, but re-activates for FOSS |
| C8 (End-to-End Trace) | FAIL | No function through compiler pipeline |
| C9 (Closure Feedback) | **READY** | Code + data path complete (TC-C7-005 done); awaiting first production closure |
