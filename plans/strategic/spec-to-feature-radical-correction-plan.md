# Format Factory — Hardened Spec-to-Feature System Correction Plan (with System-Healed Spec-Literal Regeneration)

## Context

A Gate 11 review + prior plan revealed products far below commercial grade. This hardened plan goes deeper: it audits the Specification Authority Layer, the Capability/Feature Extraction Layer, and the Supervisor/Governance system forensically, diagnoses exactly where each pipeline stage broke, and produces a concrete, multi-lane remediation plan with autonomous iteration gates.

**The prior plan was NOT strong enough.** It identified symptoms (shallow products, manual facts, missing compiler) but did not audit the full integration state of the Specification Authority Layer (which is ghost infrastructure — built but dormant), the Capability Layer (which generates output nobody consumes), or the Task Generation system (which uses hardcoded goals instead of the capability map). This hardened plan corrects all three.

**SYSTEM HEALING ENHANCEMENT (Prompt 4):** The system must be healed FIRST so that spec-literal hierarchy is enforced everywhere, THEN products are regenerated through governed channels. Spec-literal parity is not a product refactoring task — it is a system governance rule. The naming rules must be wired into skills, prompts, validators, taskcard schemas, evidence schemas, and supervisor gates that govern all future agent work. Without system healing, agents follow prompt instructions once and then forget.

Gate 11 is NOT approved. Babar Raza is the only approver.

**Run ID:** `spec-to-feature-radical-correction-plan-20260612-8e45224`
**Output root:** `.local/evidences/spec-to-feature-radical-correction-plan-20260612-8e45224/`

---

## FINAL PLAN HEALING SPRINT — Execution Plan

### Mission

Convert this entire plan into an executable swarm plan without information loss. The original plan (Sections 1-26 below) is preserved as the canonical input. This section describes the healing sprint that normalizes it into taskcards.

### Execution Approach

1. **Determine run ID** from current date + repo short SHA
2. **Create output directory** under `.local/evidences/<run_id>/`
3. **Create preservation ledger** — map every plan section to its output location
4. **Extract requirements** — scan Sections 1-26, assign stable `REQ-<DOMAIN>-<###>` IDs
5. **Generate taskcards** — one YAML per taskcard, organized by lane (16 lanes, 100+ taskcards)
6. **Build execution DAG** — dependency graph across waves 0-7
7. **Build swarm infrastructure** — lane registry, file ownership, validation matrix, repair policy
8. **Build no-information-loss audit** — prove nothing was silently dropped
9. **Write ready-to-execute swarm prompt** — the main deliverable

### 75 Required Artifacts

All under `.local/evidences/final-plan-healing-swarm-execution-<date>-<sha>/`:

**Swarm Infrastructure (1-33)**
1. `evidence-declaration.yaml`
2. `original-plan-preservation-ledger.md`
3. `normalized-requirements-inventory.yaml`
4. `requirements-to-taskcards-traceability.csv`
5. `execution-dag.yaml`
6. `swarm-lane-registry.yaml`
7. `taskcards/index.yaml`
8-23. `taskcards/lane-00-coordinator/*.yaml` through `taskcards/lane-15-autonomous-healing-learning/*.yaml`
24. `autonomous-supervision-dispatch-plan.md`
25. `lane-supervisor-checklists.md`
26. `wave-execution-plan.md`
27. `repair-loop-policy.md`
28. `file-ownership-and-locks.yaml`
29. `validation-command-matrix.md`
30. `evidence-obligation-matrix.yaml`
31. `no-information-loss-audit.md`
32. `healed-executable-master-plan.md`
33. `ready-to-execute-swarm-prompt.md`

**Lane 14 Audit Artifacts (34-40)**
34. `autonomous-supervision-layer-integration-audit.md` (Lane 14 — Section 20)
35. `autonomous-supervision-component-inventory.md`
36. `autonomous-supervision-enforcement-gap-table.md`
37. `autonomous-supervision-wiring-plan.md`
38. `autonomous-supervision-acceptance-criteria.md`
39. `continuation-state-machine-diagram.md`
40. `lane-enforcement-proof-matrix.md`

**Lane 15 Audit Artifacts (41-49)**
41. `autonomous-healing-learning-layer-integration-audit.md` (Lane 15 — Section 21)
42. `healing-loop-model.md`
43. `learning-propagation-matrix.md`
44. `failure-taxonomy.yaml`
45. `durable-learning-loop-design.md`
46. `skill-propagation-wiring-plan.md`
47. `failure-memory-schema.yaml`
48. `healing-learning-acceptance-criteria.md`
49. `healing-learning-validator-design.md`

**Deep-Dive Addendum Artifacts (50-75) — Section 20B/21B/22-26**
50. `plan-gap-review.md`
51. `no-information-loss-audit-v2.md`
52. `plan-preservation-diff.md`
53. `section-to-requirement-map.csv`
54. `requirement-to-taskcard-map.csv`
55. `dropped-or-merged-content-ledger.yaml`
56. `autonomy-layer-deep-dive-addendum.md`
57. `autonomous-supervision-call-graph.md`
58. `autonomous-supervision-state-machine.yaml`
59. `autonomous-supervision-enforcement-proof.md`
60. `autonomous-supervision-bypass-analysis.md`
61. `autonomous-supervision-rectification-backlog.yaml`
62. `autonomous-supervision-integration-tests-plan.md`
63. `taskcards/lane-14-autonomous-supervision-hardening/*.yaml`
64. `autonomous-healing-learning-call-graph.md`
65. `failure-taxonomy-v2.yaml`
66. `healing-learning-state-machine.yaml`
67. `learning-propagation-proof-matrix.md`
68. `healing-learning-bypass-analysis.md`
69. `healing-learning-rectification-backlog.yaml`
70. `healing-learning-integration-tests-plan.md`
71. `taskcards/lane-15-autonomous-healing-learning-hardening/*.yaml`
72. `product-acquisition-readiness-gate.md`
73. `updated-execution-dag-v2.yaml`
74. `updated-swarm-lane-registry-v2.yaml`
75. `updated-ready-to-execute-swarm-prompt-v2.md`

### Wave Structure

- **Wave 0:** Intake, preservation, normalization (no source mutation)
- **Wave 1A:** Autonomy/supervision/healing RESEARCH first (Lanes 14A, 15A) — must complete before governance wiring
- **Wave 1B:** Governance wiring WITH autonomy findings (Lanes 1, 4, 5, 14B-14D, 15B-15E)
- **Wave 2:** Capability and compiler integration (Lanes 2, 3, 6 in parallel; depends on Wave 1B contracts)
- **Wave 3:** System-healing gate check — HARDENED: autonomy call graphs complete, enforcement proofs complete, BLOCKER rectification items resolved, each lane is implemented_and_tested or patch_ready or blocked_external
- **Wave 4:** Architecture/regeneration planning (Lanes 7, 8, 11; skeletons marked architecture_only)
- **Wave 5:** Product rebuild execution (Lanes 9, 10, 11; only after Wave 3 passes; behavior gates not skeleton gates)
- **Wave 6:** CI, package, evidence hardening (Lane 12)
- **Wave 7:** Post-regeneration recompute and closeout (Lane 13)

### Swarm Roles

1. **Coordinator Agent** — owns DAG, file locks, lane scheduling, supervision checkpoints
2. **Lane Supervisor Agents** (one per lane) — owns lane taskcards, validators, evidence
3. **Worker Agents** — execute one taskcard at a time, no cross-file-boundary work
4. **Independent Verification Agent** — reviews completed lanes, checks no overclaim/loss
5. **Repair Agent** — executes rework taskcards, does not broaden scope

### Key Files to Read During Execution

- `reports/supervisor/session-resume.md`
- `.supervisor/state/`
- `.local/supervisor/continuation-signal.json`
- `tools/supervisor/autonomous_cycle.py`
- `tools/supervisor/supervisor_loop.py`
- `tools/supervisor/generate_next_worker_prompt.py`

### Verification

After all 75 artifacts are created:
- Every plan section maps to requirements and taskcards (no-information-loss audit)
- Taskcards are small enough for weak agents (< 1 objective each)
- Lane dependencies are explicit in execution-dag.yaml
- System healing lanes (1-6, 14, 15) precede product regeneration (7-13)
- Gate 11 remains blocked in every taskcard
- File ownership prevents lane collisions
- Autonomous supervision enforcement verified (Lane 14 audit outputs present)
- Autonomous healing/learning durability verified (Lane 15 audit outputs present)

---

## 1. EXECUTIVE FINDING

The current system produced low-grade products because the spec-to-feature pipeline has **three critical disconnections**:

1. **The Specification Authority Layer is ghost infrastructure.** 20+ tools were built (parser, normalizer, indexer, digestor, requirement extractor, verifier, graph builder, vault ingest, cache tools, normalization tools). Only 3 are actively used (spec_source_registry, context_pack_builder, spec_governance_runtime). The other 17+ modules produce artifacts that are NEVER read by any production pipeline. Fact extraction ran ONCE (run030, 2026-05-06), produced 10 FODS facts, then stopped permanently. Normalized spec text (57,803 lines for FODS alone) sits unused.

2. **The Capability Layer generates output that nobody consumes.** 800+ capability records and a 398-gap ledger are generated but: gap-ledger.json is NEVER read by task generation; action-queue.json has `advisory_only: true` on ALL items; the autonomous task generator (`autonomous_task_generator.py`) uses a HARDCODED `_EXPANSION_GOALS` catalog of ~20 manually curated goals instead of reading the capability map. The Requirements Authority proof graph model (18 node types, 19 edge types) is comprehensively defined but DORMANT — never populated from capability data.

3. **No capability-to-feature compiler exists.** There is no tool that converts a capability record into a source skeleton, test template, architecture blueprint, or executable taskcard. The `FeatureFactory` in `product_feature_factory.py` is a code generation helper (6 patterns), not a task generator. It is never called by autonomous loops. The pipeline from spec → capability simply ENDS at capability map generation with no downstream consumer.

These three disconnections mean: specs never become rich capabilities, capabilities never become implementation plans, and agents do minimum viable work because prompts say "close these gaps" with no depth requirements.

### Why Spec-Literal Parity Must Be Healed Into the System First

Beyond the three disconnections above, a **fourth systemic failure** exists: the system has 67+ wiring points across 35+ files where spec-literal rules need to be inserted. Without system healing:
- Agents follow prompt instructions once, then forget
- Taskcards don't require `spec_qname` fields
- Evidence declarations don't record canonical class mappings
- Validators don't reject flat or arbitrary architecture
- Base prompts don't mention spec-prefix hierarchy
- Skills don't enforce QName-to-code mapping
- Gate 11 criteria don't require namespace tree validation

The system must enforce `SPEC QNAME → CODE NAMESPACE → CLASS → PROPERTIES → CONTAINMENT → TESTS → EVIDENCE` as a durable governance chain, not a one-time prompt instruction.

### Fifth Systemic Risk: Autonomous Supervision May Be Partially Wired

Autonomous Supervision may be a partially wired control layer rather than a real execution authority. It may generate prompts, read declarations, or run validators, but not actually enforce lane ownership, dependency DAGs, continuation state, repair loops, no-overclaim gates, and product-progress selection. The plan references `autonomous_cycle.py`, `supervisor_loop.py`, `generate_next_worker_prompt.py`, continuation signals, and evidence declarations — but does not yet deeply prove whether these components actually control worker agents, enforce lane boundaries, generate executable rework, or prevent unsafe product regeneration. This is a risk to investigate, not an assumption.

### Sixth Systemic Risk: Autonomous Healing and Learning May Be Prompt-Only

Autonomous Healing and Learning may be present only as prompts or repair policies, not as a durable learning loop. It may repair one sprint but fail to update skills, rules, validators, taskcard templates, failure memory, continuation state, or future prompt generation. If the system cannot learn from failures and propagate corrections into durable machinery (skills, schemas, validators), then the swarm will repeat the same mistakes indefinitely. This is a risk to investigate, not an assumption.

---

## 2. SPECIFICATION AUTHORITY LAYER INTEGRATION AUDIT

### Component Inventory (Forensically Verified)

| Component | File | Intended Role | Actual Role | Downstream Consumer | Status |
|-----------|------|--------------|------------|-------------------|--------|
| spec_source_registry.py | tools/specification-authority-layer/ | Register & manage spec sources | Authority source for spec citations | authority_conveyor.py, authority_gate_validation.py, validate_spec_fact_refs.py | **ACTIVE** |
| context_pack_builder.py | tools/specification-authority-layer/ | Build deterministic context packs | Context bundles for agent use | autonomous_cycle.py, capability_layer | **ACTIVE** (read-only) |
| spec_governance_runtime.py | tools/specification-authority-layer/ | Anti-bypass enforcement, usage ledger | Governance gate for spec citations | validate_spec_fact_refs.py | **ACTIVE** |
| spec_parser.py | tools/specification-authority-layer/ | Parse spec sections from text | Produces ParsedSpec objects | NONE (test imports only) | **DEAD** |
| spec_normalizer.py | tools/specification-authority-layer/ | Normalize parsed specs to canonical form | Output: `-normalized.json` | NONE (test imports only) | **DEAD** |
| spec_indexer.py | tools/specification-authority-layer/ | Build searchable term/section index | Output: `-index.json` | NONE (test imports only) | **DEAD** |
| spec_digestor.py | tools/specification-authority-layer/ | Compute SHA-256 digests for staleness | Output: `-digest.json` | NONE (never checked) | **DEAD** |
| requirement_extractor.py | tools/specification-authority-layer/ | Extract RFC 2119 requirements | Output: `-requirements.json` (QUARANTINED) | NONE (test imports only) | **DEAD** |
| spec_verifier.py | tools/specification-authority-layer/ | Verify requirements against source | Anti-hallucination gate | NONE (test imports only) | **DEAD** |
| requirement_graph.py | tools/specification-authority-layer/ | Build requirement linkage graph | Output: `-req-graph.json` | NONE (test imports only) | **DEAD** |
| spec_vault_ingest.py | tools/specification-authority-layer/ | Ingest raw snapshots with SHA-256 | Snapshot registry | NONE (test imports only) | **DEAD** |
| acquire_spec.py | tools/spec-cache/ | Download specs from URLs | DRY-RUN only; --allow-network never used | NONE | **DEAD** |
| spec_index.py | tools/spec-cache/ | Index .local/spec-cache/ | Library; never imported externally | NONE | **DEAD** |
| build_spec_workbench.py | tools/spec-normalize/ | Bundle normalized artifacts into workbench | Ran ONCE (run030); produced auto-seed facts | NEVER updated again | **RAN ONCE** |
| build_section_index.py | tools/spec-normalize/ | Detect section headings from pages.jsonl | Output: sections.jsonl | NEVER called | **DEAD** |
| build_chunk_index.py | tools/spec-normalize/ | Split specs into addressable chunks | Output: chunks.jsonl | NEVER called | **DEAD** |
| normalize_pdf.py | tools/spec-normalize/ | Extract text & pages from PDF | Output: pages.jsonl | NEVER called | **DEAD** |
| build_citation_map.py | tools/spec-normalize/ | Build section-citation mapping | — | NEVER called | **DEAD** |
| query_normalized_spec.py | tools/spec-normalize/ | Query interface for normalized spec | — | NEVER called | **DEAD** |
| validate_normalized_spec.py | tools/spec-normalize/ | Validate normalized artifact structure | — | NEVER called | **DEAD** |

**Summary:** 3 ACTIVE, 17+ DEAD. The SAL is a **Museum of Good Intentions** — fully architected, extensively documented, beautifully implemented, but replaced by a simpler reality where facts are manually verified once and checked into git.

### Produced-But-Never-Consumed Artifacts

```
.local/spec-artifacts/ (34 files):
  FODS-SPEC-001-normalized.json    <- NEVER READ
  FODS-SPEC-001-index.json         <- NEVER READ
  FODS-SPEC-001-digest.json        <- NEVER READ
  FODS-SPEC-001-req-graph.json     <- NEVER READ
  FODS-SPEC-001-requirements.json  <- QUARANTINED
  [Similar for DIF, FODT, GNUMERIC, NETPBM, ZST]

.local/spec-cache/{format}/{version}/normalized/:
  text.txt      <- EXISTS (57,803 lines for FODS), NEVER QUERIED
  pages.jsonl   <- EXISTS, NEVER QUERIED
  sections.jsonl <- NOT CREATED (build_section_index never runs)
  chunks.jsonl   <- NOT CREATED (build_chunk_index never runs)
```

### What Actually Works (Fact Flow)

```
acquisition-packs/{format}/verified-facts.yaml  (GIT, canonical authority)
    | (copy to .local/ at test/runtime)
.local/spec-cache/{format}/{version}/workbench/verified-facts-review.yaml
    | (read by 3 consumers)
    +-- capability_map_generator.py: _load_spec_facts() [lines 141-155]
    +-- validate_spec_fact_refs.py: blocking gate on work item declarations
    +-- authority_gate_validation.py: authority level P0-P6 computation
```

### Fact Count by Format

| Format | Verified Facts | Source | Evidence |
|--------|---------------|--------|---------|
| FODS | 10 (9 verified, 1 quarantined: FACT-FODS-002) | acquisition-packs/fods/verified-facts.yaml | Hardcoded in build_spec_workbench.py lines 115-137 |
| FODT | Unknown (likely similar to FODS) | acquisition-packs/fodt/verified-facts.yaml | No verified-facts-review.yaml found in workbench |
| ZST | 2 (both verified) | .local/spec-cache/zst/rfc8878/... | FACT-ZST-001, FACT-ZST-002 |

### Integration Failure Root Cause

The pipeline was designed as: `spec_discovery -> normalization -> section_indexing -> chunk_indexing -> fact_extraction -> fact_verification -> requirement_graph -> capability_derivation`.

It STOPPED after step 2 (normalization). Steps 3-8 exist as code but were never executed in production. Facts were instead created manually in run030 (2026-05-06) and never regenerated.

**No orchestrator chains these tools.** Each is a standalone CLI. No scheduler, no cron, no master runner connects them.

### Required Correction

The SAL does NOT need to be rebuilt. The infrastructure EXISTS. It needs to be:
1. **WIRED**: Connect the dormant tools into a running pipeline
2. **ORCHESTRATED**: Create a master runner that chains spec_discovery -> normalization -> section_index -> chunk_index -> fact_extraction -> fact_verification
3. **CONSUMED**: Make the downstream capability layer actually read the generated facts
4. **ITERATED**: Run the pipeline for FODS/FODT/ZST with product-scope filtering
5. **VALIDATED**: Add validators that reject formats with < N verified facts

---

## 3. CAPABILITY AND FEATURE EXTRACTION LAYER AUDIT

### Layer Health Assessment

| Component | Status | Risk | Evidence |
|-----------|--------|------|---------|
| Capability map generation | OPERATIONAL | MEDIUM | `capability_map_generator.py`: reads poc-targets.yaml + source introspection; produces 500+ records |
| Capability map validation | DEFINED | MEDIUM | `validate_capability_map.py`: 10 validators (VAL-001..010), unknown if recently run |
| Gap ledger generation | OPERATIONAL | **HIGH** | Generated (398 gaps) but **NEVER CONSUMED** by task generation |
| Action queue | OPERATIONAL | **HIGH** | `advisory_only: true` on ALL items; not actionable |
| Feature Factory | OPERATIONAL | LOW | `product_feature_factory.py`: 6 code patterns; manual-use only, never called by autonomous loops |
| Task generation | OPERATIONAL | **HIGH** | `autonomous_task_generator.py`: uses **HARDCODED** `_EXPANSION_GOALS` catalog, NOT capability map |
| Requirements Authority proof graph | **DORMANT** | **CRITICAL** | 18 node types + 19 edge types defined; NO population pipeline; NO consumption |
| Capability verifier | OPERATIONAL | LOW | `capability_verifier.py`: 4-bucket sync check (read-only) |

### The Disconnection Chain

```
poc-targets.yaml --> capability_map_generator.py --> unified-capability-map.json --> [DEAD END]
                                                  +-> gap-ledger.json --> [DEAD END]
                                                  +-> action-queue.json --> [advisory_only: true]

autonomous_task_generator.py --reads--> HARDCODED _EXPANSION_GOALS (20+ manual entries)
                             --ignores-> unified-capability-map.json
                             --ignores-> gap-ledger.json
```

### Capability Record Schema (Actual)

```json
{
  "capability_id": "ZST-FOSS-COMPRESS_BYTES-001",
  "format": "ZST",
  "format_family": "compression",
  "product_type": "foss_reduced",
  "capability_name": "Compress Bytes",
  "operation_kind": "compress_bytes",
  "current_state": "example_verified",
  "authority_state": "spec_fact",
  "spec_refs": ["FACT-ZST-001", "FACT-ZST-002"],
  "spec_fact_refs": ["FACT-ZST-001", "FACT-ZST-002"],
  "implementation_refs": ["src/python/zst/zst_codec.py::compress_bytes"],
  "test_refs": ["tests/python/zst/test_r104_...py"],
  "confidence_level": "high",
  "gaps": []
}
```

### Gap Ledger Record Schema (Actual — generated but never consumed)

```json
{
  "gap_id": "GAP-FODS-COMM-LOAD-001",
  "format": "FODS",
  "product_type": "commercial",
  "capability_name": "Load",
  "current_state": "implementation_verified",
  "gap_type": "missing_test_coverage",
  "blocks_poc": true,
  "priority": "P0",
  "suggested_taskcard": ""
}
```

### Required Correction

1. **REINTEGRATE** gap-ledger.json into `autonomous_task_generator.py` — replace hardcoded `_EXPANSION_GOALS` with capability-map-driven task selection
2. **POPULATE** the Requirements Authority proof graph from capability records (18 node types exist; wire them)
3. **CONSUME** action-queue.json by making items machine-executable (not advisory_only)
4. **ADD** a capability-to-feature compiler (Phase 0-8 design in Section 6)
5. **VALIDATE** with feedback loop: implementation changes -> capability map reconciliation

---

## 4. SUPERVISOR AND GOVERNANCE FAILURE AUDIT

### What the Supervisor ACTUALLY Checks (Process Only)

| Validator | Exists? | What It Checks | Checks Product Depth? |
|-----------|---------|---------------|----------------------|
| Execution method validation | YES | Valid execution_method field | NO |
| Item type validation | YES | Valid item_type field | NO |
| Claim classification | YES | Consistent claim vs evidence | NO |
| Forbidden jump detection | YES | No skipping gate levels | NO |
| Taskcard state machine | YES | Valid status transitions | NO |
| Anti-skip checker (17-23 detectors) | YES | Process errors, lost files, stale gaps; test count regression (shallow); evidence quality score (indirect) | WEAKLY |
| LLM semantic verification | ADVISORY ONLY | Defaults to `adequate: True` | WEAKLY |
| Implementation depth validator | **NO** | — | — |
| Capability coverage percentage | **NO** | — | — |
| Spec fact coverage validator | **NO** | — | — |
| Tier completeness validator | **NO** | — | — |
| .NET/Python parity validator | **NO** | — | — |
| Shallow code detector | **NO** | — | — |
| Overclaim pattern #5 | SKELETON ONLY | `_pattern_5_commercial_ready_helpers_only()` not implemented | NO |
| **Spec-parity QName validator** | **NO** | — | — |
| **Namespace tree validator** | **NO** | — | — |
| **Containment graph validator** | **NO** | — | — |
| **Skeleton progress validator** | **NO** | — | — |

### Gate 11 Definition (The Entire Spec)

From `plans/master-plan.md` S14 lines 244-246:
```
| 11 | Commercial Readiness | 4 | Commercial review, legal review |
```

That's it. No depth criteria, no test coverage thresholds, no architecture standards, no spec-parity requirements.

### Evidence Declaration Schema Gaps

The schema requires: `completed_work_items`, `test_results`, `evidence_artifacts`, timestamps, git state. It does NOT require: `implementation_depth_score`, `spec_fact_coverage`, `feature_tier_achieved`, `class_count_delta`, `capability_refs_covered`, `spec_qname_refs`, `canonical_classes_added`, `containment_edges`, `spec_parity_validator_results`.

### System Wiring Points for Spec-Literal Rules (67+ locations, 35+ files)

| Category | File | Lines | Required Change | Priority |
|----------|------|-------|----------------|----------|
| **Skill Registry** | `.supervisor/skill-registry.yaml` | 47-180 | Add `spec_qname_required` to product skills | HIGH |
| **Skill Schema** | `.supervisor/schemas/skill-registry.schema.json` | 57-123 | Validate product_track triggers spec_qname requirement | HIGH |
| **Command Definitions** | `.claude/commands/add-dotnet-api.md` + 9 others | ALL | Add "Spec-Literal Hierarchy Required" section | HIGH |
| **Base Prompt** | `.supervisor/prompts/mega-train-template.md` | 31-42, 66-80 | Add spec_qname rules to Mandatory Evidence Rules and Hard Prohibitions | HIGH |
| **Worker Prompt Generator** | `tools/supervisor/generate_next_worker_prompt.py` | ~100-150, ~500-550 | Inject spec-authority advisory and per-item QName audit | HIGH |
| **Taskcard Schema** | `schemas/governance/product-mutation-taskcard-state-machine.schema.json` | ADD | Add `spec_qname`, `canonical_namespace`, `canonical_class` fields | HIGH |
| **Evidence Schema** | `.supervisor/schemas/evidence-declaration.schema.json` | 30-42 | Add `spec_qname_refs`, `canonical_classes_added`, `containment_edges` | HIGH |
| **Spec Fact Validator** | `tools/supervisor/validate_spec_fact_refs.py` | ALL | **ALREADY EXISTS** (493 lines, complete enforcement) | -- |
| **Governance Validators** | `tools/supervisor/governance_validators.py` | 200+ | Add `validate_spec_parity_enforcement()` call | HIGH |
| **Anti-Skip Checker** | `tools/supervisor/anti_skip_checker.py` | ADD | Detector 19: spec-parity authority gaps | MEDIUM |
| **Authority Gate** | `tools/supervisor/authority_gate_validation.py` | ~140 | Require QName map for READINESS gate | HIGH |
| **Format Registry** | `registry/format-registry.yaml` | ALL | Add `spec_literal_hierarchy: true` to ODF formats | MEDIUM |
| **Autonomous Cycle** | `tools/supervisor/autonomous_cycle.py` | ~200-450 | Integrate spec-parity enforcement gates | HIGH |
| **Product Source Executor** | `tools/supervisor/product_source_executor.py` | ADD | Pre-flight spec_qname validation | HIGH |
| **Source Constants** | `src/python/fods/constants.py`, `src/python/fodt/constants.py` | 57-70 | Add FACT-FODS/FACT-FODT comments to QName constants | MEDIUM |
| **.NET Parsers** | `src/net/fods/FodsParser.cs`, `src/net/fodt/FodtParser.cs` | 136-229 | Migrate S-references to FACT-* identifiers | MEDIUM |

### Required Correction

1. Add concrete Gate 11 criteria (see Section 13 below — C1-C20, P1-P11)
2. Implement 5 original depth validators + 8 spec-parity validators in governance_validators.py
3. Implement overclaim pattern #5
4. Add depth fields AND spec-parity fields to evidence declaration schema
5. Add .NET CI pipeline (currently Python-only)
6. Wire spec-literal rules into all 67+ wiring points

---

## 5. PRODUCT ARCHITECTURE ASSESSMENT (Corrected from Prior Plan)

### Key Correction: .NET Architecture Is Better Than Previously Assessed

The prior plan graded .NET at 3/5 (prototype). **Forensic audit reveals 4/5 (professional SDK, incomplete).** The architecture IS professional — dual-mode (streaming + DOM), typed wrappers, security-hardened, sealed classes, proper exception hierarchy. The issue is SCOPE, not QUALITY.

| Product | Track | Files | Classes | Public Methods | LOC | Largest File | Arch Grade | SDK Professional? |
|---------|-------|-------|---------|---------------|-----|-------------|-----------|------------------|
| FODS .NET | Commercial | 7 src | 19 | 40+ | 2,408 | FodsDocument.cs (1,386) | **4/5** | YES |
| FODT .NET | Commercial | 7 src | 18 | 25+ | 1,905 | FodtDocument.cs (977) | **4/5** | YES |
| FODS Python | FOSS | 7 src | **0** | 29 exports | 2,725 | neutral_model.py (1,670) | **2.5/5** | NO |
| FODT Python | FOSS | 7 src | **0** | 31 exports | 2,986 | neutral_model.py (1,875) | **2.5/5** | NO |
| ZST Python | FOSS | 2 src | 4 | 24 | 1,062 | zst_codec.py (986) | **4/5** | YES |

### FODS .NET — What's Missing (Scope Gaps, Not Architecture Gaps)

| Missing Feature | Spec Concept | Impact | Evidence |
|----------------|-------------|--------|---------|
| Typed cell values | `office:value-type`, `office:value`, `office:date-value`, `office:boolean-value` | Numeric cells export as EMPTY in CSV | FodsCell.cs: `Value` is `string?` only (line 22); FodsCsvExporter.cs uses only `text:p` display value |
| Formula object model | `table:formula` | "formula results not available without evaluation engine... deferred" | FodsCsvExporter.cs line 31 comment |
| Style objects | `style:style`, `office:automatic-styles` | Preserved by DOM but NOT exposed to callers | No FodsStyle.cs exists |
| Named ranges | `table:named-range` | Not modeled | No API surface |
| Data validation | `table:content-validation` | Not modeled | No API surface |

### FODT .NET — What's Missing

| Missing Feature | Spec Concept | Impact | Evidence |
|----------------|-------------|--------|---------|
| List object model | `text:list`, `text:list-item` | Lists counted but not accessible as typed objects | FodtParser.cs line 193: detected, no wrapper |
| Table object model | `table:table`, `table:table-row`, `table:table-cell` | Tables detected but only `HasTables` boolean | No FodtTable.cs exists |
| Text span | `text:span` | Inline formatting lost at paragraph level | No FodtTextSpan.cs |
| Footnote/endnote | `text:footnote`, `text:endnote` | Detected, not modeled | No FodtFootnote.cs |
| Style objects | `style:style` | Preserved by DOM, not exposed | No FodtStyle.cs |

### Python FODS/FODT — Architectural Problem

Both products have ZERO classes. All logic is in top-level functions operating on nested dicts. This is:
- Not aligned with .NET typed model
- Not maintainable at scale (1,670-1,875 LOC monoliths)
- Not a professional SDK

However, for FOSS track, it WORKS. The neutral model schema is explicit and testable. The question is whether Python must mirror .NET structure or can remain functional.

**Decision for plan:** Python keeps functional API as backward-compatible wrappers but adds a class-based model layer for important concepts. Python DOES NOT need to be a clone of .NET; it needs to be coherent enough that the product family makes sense. After spec-literal healing, Python modules must follow spec-prefix hierarchy where implemented.

---

## 6. PRODUCTION CAPABILITY-TO-FEATURE COMPILER DESIGN

### Design Principles

1. **Deterministic:** Same inputs -> same output (no random IDs, no timestamp-dependent logic)
2. **Idempotent:** Running twice produces identical output
3. **Format-family plugins:** Spreadsheet-like, word-processing-like, compression-like, image-like
4. **Multi-language targets:** .NET commercial + Python reduced (same concept graph, different depth)
5. **Intermediate representation:** Normalized feature IR between capability records and source generation

### Compiler Phases

**Phase 0 — Input validation**
- Validate spec facts (schema, references, quarantine status)
- Validate capability records (required fields, authority_state)
- Validate product scope (commercial vs FOSS)
- Reject capabilities with `authority_state: manual` unless explicitly marked `manual_override: true`

**Phase 1 — Concept graph construction**
- Input: verified facts from `verified-facts-review.yaml`
- Group facts into spec concepts (e.g., all `table:table-cell` facts -> `Cell` concept)
- Classify concept types: `model`, `attribute`, `operation`, `validation`, `preservation`, `export`, `metadata`, `style`, `formula`, `binary_frame`, `streaming`, `security`, `error_condition`
- Detect parent/child relationships (Document -> Sheet -> Row -> Cell)
- Output: `spec_concept_graph.yaml`

**Phase 2 — Capability graph construction**
- Input: concept graph + unified-capability-map.json
- Convert concepts to capabilities where missing
- Attach scope (`commercial`, `foss`, `both`)
- Attach track targets (`.NET`, `Python`, `both`)
- Attach dependencies (e.g., `FODS-TYPED-CELL-VALUE` depends on `FODS-CELL-VALUE-TYPE-ATTRIBUTE`)
- Attach implementation depth target (0-5)
- Output: `capability_graph.yaml`

**Phase 3 — Feature graph construction**
- Convert capabilities into implementable features
- Feature types: `model_class`, `parser_support`, `writer_support`, `public_api`, `operation_service`, `export_support`, `validation`, `error_handling`, `roundtrip`, `fixture`, `negative_test`, `package`, `evidence`
- Assign each feature to target files/classes/tests
- Output: `feature_graph.json`

**Phase 3.5 — QName-to-Code Ontology Generation (SYSTEM HEALING ADDITION)**
- Input: concept graph + ODF namespace registry
- Map each spec QName to canonical namespace/module/class/property
- Generate `qname-to-code-map.yaml`, `namespace-tree.yaml`, `canonical-class-inventory.yaml`
- Generate `containment-graph.yaml` from spec parent/child relationships
- Generate `attribute-property-map.yaml` from spec attribute -> typed property mappings
- Generate `naming-exceptions.yaml` and `legacy-alias-map.yaml`
- Validate: no orphan QNames, no unmapped in-scope elements
- Output: All 9 ontology artifacts (see Section 7A)

**Phase 4 — Architecture blueprint generation**
- Generate namespace/module plan per product/track
- Generate class inventory (MUST match QName-to-code map from Phase 3.5)
- Generate file placement plan
- Generate public API map
- Generate refactor/migration plan if current source conflicts with blueprint
- Output: `architecture_blueprint.yaml`

**Phase 5 — Taskcard generation**
- One taskcard per feature or coherent feature group
- Include: source targets, forbidden files, tests required, fixture requirements, evidence required, validation commands, done criteria, depth target, **spec_qname**, **canonical_namespace**, **canonical_class**
- Output: `taskcards/generated/*.yaml`

**Phase 6 — Test obligation generation**
- For every feature: positive parse, edit/mutate, save/write, roundtrip, malformed/negative, boundary, export, public API, package/import, regression, spec trace assertion
- Output: `test_obligation_matrix.csv`

**Phase 7 — Evidence obligation generation**
- Every completed feature must produce: source diff map, spec fact refs covered, capability refs covered, tests added, tests passed, sample outputs, supervisor declaration item, **spec_qname_refs**, **canonical_classes_added_or_modified**, **containment_edges_implemented**
- Output: `evidence_obligation_matrix.csv`

**Phase 8 — Gate readiness calculation**
- Compute gate status from evidence (NOT manually claimed)
- Compare completed features vs total features per product/track
- **Require spec-parity validator pass for Gate 11 candidates**
- Output: `gate_readiness_projection.yaml`

### Compiler Outputs

| Output | Purpose |
|--------|---------|
| `spec_concept_graph.yaml` | Spec concepts grouped from facts |
| `capability_graph.yaml` | Capabilities with dependencies and scope |
| `feature_graph.json` | Machine-readable implementable features |
| `qname-to-code-map.yaml` | Canonical QName -> namespace/class mappings (NEW) |
| `namespace-tree.yaml` | Target namespace hierarchy per format per track (NEW) |
| `containment-graph.yaml` | Spec parent/child -> code containment (NEW) |
| `architecture_blueprint.yaml` | Target class/file structure per product/track |
| `taskcards/generated/*.yaml` | Executable taskcards |
| `test_obligation_matrix.csv` | Tests required per feature |
| `traceability_matrix.csv` | fact -> capability -> feature -> source -> test -> evidence |
| `gap_queue.yaml` | Missing work queue |
| `gate_readiness_projection.yaml` | Computed readiness (not approval) |

### Scaling for Hundreds of Formats

- **Batching:** Process formats independently (no cross-format state)
- **Caching:** Cache concept graph and capability graph per format; invalidate on fact change
- **Deterministic IDs:** `{FORMAT}-{CONCEPT}-{TRACK}-{SEQ}` (no UUIDs)
- **Incremental reruns:** Diff new facts vs cached facts; regenerate only changed subtrees
- **Format-family plugins:** Spreadsheet plugin produces Sheet/Row/Cell concepts; WP plugin produces Paragraph/List/Table concepts; Compression plugin produces Frame/Block concepts
- **Schema versioning:** `schema_version` field in all outputs
- **Failure isolation:** One format's failure doesn't block others
- **Stale artifact detection:** Compare output hash vs prior run; flag unchanged
- **Supervisor integration:** Compiler produces evidence declarations consumed by `autonomous_cycle.py`

---

## 7. .NET COMMERCIAL SDK ARCHITECTURE AUDIT AND TARGET

### Current Assessment (Corrected)

The .NET architecture is already **professional SDK grade (4/5)**. It does NOT need a "radical redesign." It needs **scope expansion** — adding the missing spec concepts as new classes in the existing well-designed framework.

### FODS .NET — Current File/Class Inventory

| File | LOC | Public Types | Spec Concept | Correct Placement? | Problem |
|------|-----|-------------|-------------|-------------------|---------|
| FodsDocument.cs | 1,386 | FodsDocument, FodsDocumentException | office:document (orchestrator) | YES | Too large (1,386 LOC); should extract operation methods |
| FodsParser.cs | 286 | FodsParser, FodsParseResult, FodsSheetInfo, FodsParseException | Streaming parse | YES | Good |
| FodsWriter.cs | 56 | FodsWriter | Serialize to XML | YES | Good (thin) |
| Model/FodsCell.cs | 74 | FodsCell | table:table-cell | YES | Missing: typed value, formula |
| Model/FodsSheet.cs | 49 | FodsSheet | table:table | YES | Good |
| Model/FodsRow.cs | 48 | FodsRow | table:table-row | YES | Good |
| FodsCsvExporter.cs | 291 | FodsCsvExporter, FodsCsvExportResult, FodsCsvExportException | Export to CSV | YES | Uses display text only; should use typed values |
| FodsHtmlExporter.cs | 201 | FodsHtmlExporter | Export to HTML | YES | Good |
| FodsJsonExporter.cs | 188 | FodsJsonExporter | Export to JSON | YES | Good |

### FODS .NET — Classes to ADD (Scope Expansion)

| Spec QName | Canonical Class | Canonical File | Facade Alias | Depends On |
|-----------|----------------|---------------|-------------|-----------|
| `office:value-type` (+ subtypes: string, float, date, time, boolean) | `Table.TypedValue` | Table/TypedValue.cs | `FodsTypedValue` (Compat/) | — |
| `table:formula` | `Table.Formula` | Table/Formula.cs | `FodsFormula` (Compat/) | `Table.TypedValue` (cached result) |
| `style:style` | `Style.Style` | Style/Style.cs | `FodsStyle` (Compat/) | — |
| `table:table-column` | `Table.TableColumn` | Table/TableColumn.cs | `FodsColumnDefinition` (Compat/) | `Style.Style` |
| `table:covered-table-cell` span | `Table.CoveredTableCell` | Table/CoveredTableCell.cs | `FodsMergedCellRange` (Compat/) | `Table.TableCell` |
| `table:content-validation` | `Validation.ContentValidation` | Validation/ContentValidation.cs | `FodsDataValidation` (Compat/) | — |

### FODT .NET — Classes to ADD

| Spec QName | Canonical Class | Canonical File | Facade Alias | Depends On |
|-----------|----------------|---------------|-------------|-----------|
| `text:list` | `Text.List` | Text/List.cs | `FodtList` (Compat/) | — |
| `text:list-item` | `Text.ListItem` | Text/ListItem.cs | `FodtListItem` (Compat/) | `Text.List` |
| `table:table` | `Table.Table` | Table/Table.cs | `FodtTable` (Compat/) | — |
| `table:table-row` | `Table.TableRow` | Table/TableRow.cs | `FodtTableRow` (Compat/) | `Table.Table` |
| `table:table-cell` | `Table.TableCell` | Table/TableCell.cs | `FodtTableCell` (Compat/) | `Table.TableRow` |
| `text:span` | `Text.Span` | Text/Span.cs | `FodtTextSpan` (Compat/) | `Text.Paragraph` |
| `text:h` | `Text.Heading` | Text/Heading.cs | `FodtHeading` (Compat/) | — |
| `text:footnote` | `Text.Footnote` | Text/Footnote.cs | `FodtFootnote` (Compat/) | — |
| `style:style` | `Style.Style` | Style/Style.cs | `FodtStyle` (Compat/) | — |
| `text:section` | `Text.Section` | Text/Section.cs | `FodtSection` (Compat/) | — |

### Architecture Rule

**Do not preserve bad architecture merely because it exists.** But the current .NET architecture is NOT bad — it is professional and incomplete. The rule becomes: **Extend the existing architecture with new spec-shaped classes. Extract operation methods from FodsDocument.cs (1,386 LOC) into dedicated operation classes only if it exceeds 1,500 LOC after expansion.**

---

## 7A. QNAME-TO-CODE ONTOLOGY DESIGN (SYSTEM HEALING ADDITION)

### ODF Namespace Registry (Verified from Codebase)

The codebase already defines these ODF namespaces as constants:

| Prefix | URI | Used In | Evidence |
|--------|-----|---------|---------|
| office | `urn:oasis:names:tc:opendocument:xmlns:office:1.0` | FODS, FODT | `constants.py` lines 48-51 |
| table | `urn:oasis:names:tc:opendocument:xmlns:table:1.0` | FODS, FODT | `constants.py` lines 48-51 |
| text | `urn:oasis:names:tc:opendocument:xmlns:text:1.0` | FODS, FODT | `constants.py` lines 48-51 |
| draw | `urn:oasis:names:tc:opendocument:xmlns:drawing:1.0` | FODS, FODT | `constants.py` lines 48-51 |
| style | (not yet in constants) | FODS, FODT | Preserved in DOM but not explicit |
| dc | `http://purl.org/dc/elements/1.1/` | FODS, FODT | Metadata |
| meta | `urn:oasis:names:tc:opendocument:xmlns:meta:1.0` | FODT | Metadata |

### QName-to-Code Mapping Rules

**Rule 1: Prefix -> Namespace/Module**
- `office:` -> `.NET: FormatFactory.Fods.Office` / `Python: fods.office`
- `table:` -> `.NET: FormatFactory.Fods.Table` / `Python: fods.table`
- `text:` -> `.NET: FormatFactory.Fodt.Text` / `Python: fodt.text`
- `style:` -> `.NET: FormatFactory.Fods.Style` / `Python: fods.style`
- `draw:` -> `.NET: FormatFactory.Fodt.Draw` / `Python: fodt.draw`

**Rule 2: Local Name -> Class Name**
- `document` -> `Document`
- `spreadsheet` -> `Spreadsheet`
- `table` -> `Table`
- `table-row` -> `TableRow`
- `table-cell` -> `TableCell`
- `covered-table-cell` -> `CoveredTableCell`
- `table-column` -> `TableColumn`
- `p` -> `Paragraph`
- `h` -> `Heading`
- `list` -> `List`
- `list-item` -> `ListItem`
- `span` -> `Span`
- `style` -> `Style`
- `automatic-styles` -> `AutomaticStyles`
- `frame` -> `Frame`

**Rule 3: Attribute -> Typed Property**
- `office:value-type` -> `ValueType` (enum: string, float, date, time, boolean, currency, percentage)
- `office:value` -> `NumericValue` (double?)
- `office:boolean-value` -> `BooleanValue` (bool?)
- `office:date-value` -> `DateValue` (DateTimeOffset?)
- `table:formula` -> `Formula` (string?)
- `table:name` -> `Name` (string)
- `text:outline-level` -> `OutlineLevel` (int)
- `text:style-name` -> `StyleName` (string?)

**Rule 4: Parent/Child -> Containment**
- `office:document` contains `office:body`
- `office:body` contains `office:spreadsheet` (FODS) or `office:text` (FODT)
- `office:spreadsheet` contains `table:table`*
- `table:table` contains `table:table-row`*
- `table:table-row` contains `table:table-cell`*
- `office:text` contains `text:p`* / `text:h`* / `text:list`* / `table:table`*
- `text:list` contains `text:list-item`*
- `text:list-item` contains `text:p`* / `text:list`*

### Existing Class Classification

| Existing Type | Product | Track | Spec QName | Canonical Full Type Required | Classification | Migration Action |
|--------------|---------|-------|-----------|---------------------------|---------------|-----------------|
| `FodsDocument` | FODS | .NET | `office:document` | `FormatFactory.Fods.Office.Document` | `facade_alias` | Create canonical `Office.Document`; keep `FodsDocument` as facade delegating to it |
| `FodsSheet` | FODS | .NET | `table:table` | `FormatFactory.Fods.Table.Table` | `facade_alias` | Create canonical `Table.Table`; keep `FodsSheet` as facade |
| `FodsRow` | FODS | .NET | `table:table-row` | `FormatFactory.Fods.Table.TableRow` | `facade_alias` | Create canonical `Table.TableRow`; keep `FodsRow` as facade |
| `FodsCell` | FODS | .NET | `table:table-cell` | `FormatFactory.Fods.Table.TableCell` | `facade_alias` | Create canonical `Table.TableCell`; keep `FodsCell` as facade |
| `FodtDocument` | FODT | .NET | `office:document` | `FormatFactory.Fodt.Office.Document` | `facade_alias` | Create canonical; keep facade |
| `FodtBody` | FODT | .NET | `office:text` | `FormatFactory.Fodt.Office.Text` | `facade_alias` | Create canonical; keep facade |
| `FodtParagraph` | FODT | .NET | `text:p` / `text:h` | `FormatFactory.Fodt.Text.Paragraph` + `FormatFactory.Fodt.Text.Heading` | `migration_target` | Split into two canonical classes; keep `FodtParagraph` as facade |
| `FodsParser` | FODS | .NET | (streaming tool) | `FormatFactory.Fods.IO.Parser` | `facade_alias` | Move to IO namespace |
| `FodsWriter` | FODS | .NET | (streaming tool) | `FormatFactory.Fods.IO.Writer` | `facade_alias` | Move to IO namespace |
| `FodsCsvExporter` | FODS | .NET | (export tool) | `FormatFactory.Fods.Export.CsvExporter` | `facade_alias` | Move to Export namespace |

### Python Existing Function Classification

| Existing Function/Module | Spec QName Scope | Canonical Target | Classification | Wrapper Retained? |
|-------------------------|-----------------|-----------------|---------------|------------------|
| `neutral_model.py` (1670 LOC) | Multiple | Split into `fods.office.document`, `fods.table.*` | `migration_target` | Functions become wrappers calling class methods |
| `parser.py` | N/A (tool) | `fods.io.parser` | `facade_alias` | Keep as functional API |
| `writer.py` | N/A (tool) | `fods.io.writer` | `facade_alias` | Keep as functional API |
| `workbook_stats()` etc. | Multiple | Methods on canonical classes | `legacy_wrapper` | Keep in compat module |

---

## 8. PYTHON REDUCED PRODUCT ARCHITECTURE STRATEGY

### Design Decision

Python does NOT need to clone .NET. Python keeps its functional API as the public interface. But Python MUST:
1. Add a model layer with classes for core concepts (Workbook/Sheet/Row/Cell for FODS; Document/Paragraph/List/Table for FODT)
2. Refactor neutral_model.py monoliths into concept-grouped modules
3. Keep existing function exports as backward-compatible wrappers
4. Produce a parity matrix declaring what Python has vs what .NET has
5. **After spec-literal healing: Python modules follow spec-prefix hierarchy where implemented** (SYSTEM HEALING ADDITION)

### FODS Python Target Structure (Pre-Spec-Literal)

```
src/python/fods/
+-- __init__.py          (public exports -- backward compatible)
+-- model.py             (NEW: FodsWorkbook, FodsSheet, FodsRow, FodsCell, FodsTypedValue)
+-- parser.py            (existing: streaming parser)
+-- writer.py            (existing: XML serializer)
+-- neutral_model.py     (REFACTORED: delegates to model.py; keeps old function signatures)
+-- operations.py        (NEW: extracted analytics/accessors from neutral_model.py)
+-- csv_exporter.py      (existing)
+-- exceptions.py        (existing)
+-- constants.py         (existing)
```

### FODS Python Target Structure (Post-Spec-Literal Regeneration)

```
src/python/fods/
+-- __init__.py             (public exports -- backward compatible)
+-- office/
|   +-- __init__.py
|   +-- document.py         (canonical: Document class)
|   +-- spreadsheet.py      (canonical: Spreadsheet class)
+-- table/
|   +-- __init__.py
|   +-- table.py            (canonical: Table class)
|   +-- table_row.py        (canonical: TableRow class)
|   +-- table_cell.py       (canonical: TableCell class)
+-- text/
|   +-- __init__.py
|   +-- paragraph.py        (canonical: Paragraph class)
+-- style/
|   +-- __init__.py         (future gate)
+-- io/
|   +-- parser.py           (moved from parser.py)
|   +-- writer.py           (moved from writer.py)
+-- compat/
|   +-- neutral_model.py    (compatibility: old functional API wrapping canonical classes)
|   +-- csv_exporter.py     (moved from csv_exporter.py)
+-- exceptions.py
+-- constants.py
```

### FODT Python Target Structure (Post-Spec-Literal Regeneration)

```
src/python/fodt/
+-- __init__.py             (public exports -- backward compatible)
+-- office/
|   +-- __init__.py
|   +-- document.py         (canonical: Document class)
|   +-- text.py             (canonical: office:text body container)
+-- text/
|   +-- __init__.py
|   +-- paragraph.py        (canonical: Paragraph class)
|   +-- heading.py          (canonical: Heading class)
|   +-- span.py             (canonical: Span class)
|   +-- list.py             (canonical: List class)
|   +-- list_item.py        (canonical: ListItem class)
+-- table/
|   +-- __init__.py
|   +-- table.py            (canonical: Table class)
|   +-- table_row.py        (canonical: TableRow class)
|   +-- table_cell.py       (canonical: TableCell class)
+-- draw/
|   +-- frame.py            (canonical: Frame class)
+-- io/
|   +-- parser.py
|   +-- writer.py
+-- compat/
|   +-- neutral_model.py    (compatibility wrapper)
+-- exceptions.py
+-- constants.py
```

### Migration Strategy (Staged, Non-Breaking)

**Stage 1:** Create model.py with class stubs. Classes wrap the existing dict model internally.
**Stage 2:** Move logic from neutral_model.py into class methods. Keep neutral_model.py as thin wrappers calling class methods.
**Stage 3:** Add parity matrix YAML (`docs/architecture/{format}-python-parity-matrix.yaml`)
**Stage 4:** Add validators: fail if complex Python product has zero domain classes; fail if parity matrix missing
**Stage 5 (POST SYSTEM HEALING):** Migrate model.py classes into spec-prefix submodules (office/, table/, text/, etc.). Keep model.py as re-export layer.

### Parity Matrix Format

```yaml
format: fods
track: python
versus: net
items:
  - spec_qname: "office:document"
    concept: Document
    net_canonical: Office.Document           # FormatFactory.Fods.Office.Document
    net_facade: FodsDocument                 # Compat/FodsDocument.cs
    python_canonical: office.document.Document  # fods.office.document.Document
    python_facade: FodsWorkbook              # fods.compat (backward compat)
    python_status: implemented
  - spec_qname: "office:value-type"
    concept: TypedValue
    net_canonical: Table.TypedValue          # FormatFactory.Fods.Table.TypedValue
    net_facade: FodsTypedValue               # Compat/FodsTypedValue.cs
    python_canonical: table.typed_value.TypedValue
    python_facade: FodsTypedValue
    python_status: partial
    scope_note: "string + float only; date/bool deferred"
  - spec_qname: "table:formula"
    concept: Formula
    net_canonical: Table.Formula
    net_facade: FodsFormula
    python_canonical: null
    python_facade: null
    python_status: not_implemented
    scope_note: "formula evaluation out of scope for FOSS track"
```

---

## 8A. FODS .NET TARGET CANONICAL STRUCTURE (Post-Spec-Literal Regeneration)

```
src/net/fods/
+-- Office/
|   +-- Document.cs         (canonical: office:document)
|   +-- Spreadsheet.cs      (canonical: office:spreadsheet)
|   +-- AutomaticStyles.cs  (canonical: office:automatic-styles)
+-- Table/
|   +-- Table.cs            (canonical: table:table)
|   +-- TableRow.cs         (canonical: table:table-row)
|   +-- TableCell.cs        (canonical: table:table-cell)
|   +-- CoveredTableCell.cs (canonical: table:covered-table-cell)
|   +-- TableColumn.cs      (canonical: table:table-column)
+-- Text/
|   +-- Paragraph.cs        (canonical: text:p)
+-- Style/
|   +-- Style.cs            (canonical: style:style -- future gate)
+-- IO/
|   +-- Parser.cs           (streaming Tier 0)
|   +-- Reader.cs           (DOM loading)
|   +-- Writer.cs           (DOM serialization)
+-- Export/
|   +-- CsvExporter.cs
|   +-- HtmlExporter.cs
|   +-- JsonExporter.cs
+-- Compat/
|   +-- FodsDocument.cs     (facade -> Office.Document)
|   +-- FodsSheet.cs        (facade -> Table.Table)
|   +-- FodsRow.cs          (facade -> Table.TableRow)
|   +-- FodsCell.cs         (facade -> Table.TableCell)
|   +-- FodsParser.cs       (facade -> IO.Parser)
|   +-- FodsWriter.cs       (facade -> IO.Writer)
+-- FormatFactory.Fods.csproj
```

### FODT .NET Target Canonical Structure (Post-Spec-Literal Regeneration)

```
src/net/fodt/
+-- Office/
|   +-- Document.cs         (canonical: office:document)
|   +-- Text.cs             (canonical: office:text -- body container)
+-- Text/
|   +-- Paragraph.cs        (canonical: text:p)
|   +-- Heading.cs          (canonical: text:h)
|   +-- Span.cs             (canonical: text:span)
|   +-- List.cs             (canonical: text:list)
|   +-- ListItem.cs         (canonical: text:list-item)
+-- Table/
|   +-- Table.cs            (canonical: table:table)
|   +-- TableRow.cs         (canonical: table:table-row)
|   +-- TableCell.cs        (canonical: table:table-cell)
+-- Draw/
|   +-- Frame.cs            (canonical: draw:frame)
+-- Style/
|   +-- Style.cs            (canonical: style:style -- future gate)
+-- IO/
|   +-- Parser.cs
|   +-- Reader.cs
|   +-- Writer.cs
+-- Export/
|   +-- HtmlExporter.cs
|   +-- MarkdownExporter.cs
|   +-- TxtExporter.cs
+-- Compat/
|   +-- FodtDocument.cs     (facade -> Office.Document)
|   +-- FodtBody.cs         (facade -> Office.Text)
|   +-- FodtParagraph.cs    (facade -> Text.Paragraph + Text.Heading)
|   +-- FodtParser.cs       (facade -> IO.Parser)
|   +-- FodtWriter.cs       (facade -> IO.Writer)
+-- FormatFactory.Fodt.csproj
```

### Migration Table (FODS .NET)

| Existing Type | Current File | Spec QName | Canonical Type | Canonical File | Classification | Migration Action | Wrapper? |
|--------------|-------------|-----------|---------------|---------------|---------------|-----------------|----------|
| FodsDocument | FodsDocument.cs | office:document | Office.Document | Office/Document.cs | facade_alias | Extract canonical class; facade delegates | YES |
| FodsSheet | Model/FodsSheet.cs | table:table | Table.Table | Table/Table.cs | facade_alias | Create canonical; facade delegates | YES |
| FodsRow | Model/FodsRow.cs | table:table-row | Table.TableRow | Table/TableRow.cs | facade_alias | Create canonical; facade delegates | YES |
| FodsCell | Model/FodsCell.cs | table:table-cell | Table.TableCell | Table/TableCell.cs | facade_alias | Create canonical with typed value; facade delegates | YES |
| FodsParser | FodsParser.cs | (tool) | IO.Parser | IO/Parser.cs | facade_alias | Move; keep facade | YES |
| FodsWriter | FodsWriter.cs | (tool) | IO.Writer | IO/Writer.cs | facade_alias | Move; keep facade | YES |
| FodsCsvExporter | FodsCsvExporter.cs | (export) | Export.CsvExporter | Export/CsvExporter.cs | facade_alias | Move; keep facade | YES |
| (missing) | -- | table:table-column | Table.TableColumn | Table/TableColumn.cs | `reduced_scope_absent` | Create when scope expands | NO |
| (missing) | -- | style:style | Style.Style | Style/Style.cs | `future_gate` | Create when style support added | NO |

---

## 9. GOVERNED SKILLS DESIGN (SYSTEM HEALING ADDITION)

### New Skills to Add

**Skill 1: `spec-literal-qname-to-code-mapping`**
- Purpose: Convert spec QNames into canonical namespace/module/class/property mappings
- When: Before any product architecture work
- Inputs: Verified facts YAML, spec prefix registry, product scope
- Outputs: `qname-to-code-map.yaml`, `namespace-tree.yaml`, `canonical-class-inventory.yaml`
- Validators: No orphan QNames, no unmapped in-scope elements
- Location: `.claude/commands/spec-literal-qname-to-code-mapping.md`

**Skill 2: `spec-shaped-product-architecture-blueprint`**
- Purpose: Generate product source architecture from QName-to-code ontology
- When: After QName map exists, before source generation
- Inputs: `qname-to-code-map.yaml`, feature graph, product scope
- Outputs: Architecture blueprint with canonical file paths
- Validators: Namespace tree matches spec prefixes
- Location: `.claude/commands/spec-shaped-product-architecture-blueprint.md`

**Skill 3: `spec-parity-source-regeneration-and-migration`**
- Purpose: Regenerate/rename source according to canonical spec hierarchy
- When: After system healing gates pass
- Inputs: Migration plan, QName map, existing source
- Outputs: Canonical classes, facade wrappers, updated tests
- Validators: All canonical classes have behavior + tests + spec_qname
- Location: `.claude/commands/spec-parity-source-regeneration-and-migration.md`

**Skill 4: `python-reduced-spec-parity-model`**
- Purpose: Ensure Python follows same canonical concept graph as .NET with explicit reduced scope
- When: During Python product work
- Inputs: .NET canonical class inventory, Python parity matrix
- Outputs: Python spec-prefix modules, parity matrix YAML
- Validators: No missing Python class without `reduced_scope_absent` reason
- Location: `.claude/commands/python-reduced-spec-parity-model.md`

**Skill 5: `spec-parity-verification`**
- Purpose: Validate namespace tree, class inventory, attribute map, containment graph
- When: After any product source change
- Inputs: Source tree, QName map, containment graph
- Outputs: Validator results (PASS/FAIL per check)
- Location: `.claude/commands/spec-parity-verification.md`

### Base Prompt Update Plan

**File:** `.supervisor/prompts/mega-train-template.md`

Add to "Mandatory Evidence Rules" (after existing rule 5):
```
6. Every PRODUCT_SOURCE work item creating or modifying model classes MUST reference
   spec_qname mappings from qname-to-code-map.yaml. No arbitrary class names for spec concepts.
7. Canonical classes derive names from spec local names. Format-prefixed names (FodsSheet,
   FodtParagraph) are facades/wrappers that delegate to canonical spec-literal classes.
8. Source namespace/module hierarchy MUST follow spec prefix hierarchy where implemented.
```

Add to "Hard Prohibitions":
```
- No creation of model classes without spec_qname mapping or explicit naming_exception.
- No flat namespace for ODF products where spec defines prefix hierarchy.
- No product-progress claims for skeleton-only spec-shaped files.
- No Gate 11 candidate without QName-to-code validator pass.
```

### Taskcard Schema Extension

Add to `schemas/governance/product-mutation-taskcard-state-machine.schema.json`:
```json
"spec_parity_fields": {
  "spec_qname": {"type": "string", "description": "e.g. table:table-cell"},
  "canonical_namespace": {"type": "string", "description": "e.g. FormatFactory.Fods.Table"},
  "canonical_module": {"type": "string", "description": "e.g. fods.table.table_cell"},
  "canonical_class": {"type": "string", "description": "e.g. TableCell"},
  "canonical_file_path": {"type": "string"},
  "containment_parent": {"type": "string"},
  "containment_children": {"type": "array", "items": {"type": "string"}},
  "attributes_to_map": {"type": "array", "items": {"type": "string"}},
  "facade_aliases": {"type": "array", "items": {"type": "string"}},
  "naming_exceptions": {"type": "array", "items": {"type": "string"}}
}
```

### Evidence Schema Extension

Add to `.supervisor/schemas/evidence-declaration.schema.json` work item properties:
```json
"spec_qname_refs": {"type": "array", "items": {"type": "string"}},
"qname_to_code_map_refs": {"type": "array", "items": {"type": "string"}},
"canonical_classes_added_or_modified": {"type": "array", "items": {"type": "string"}},
"attributes_mapped": {"type": "array", "items": {"type": "string"}},
"containment_edges_implemented": {"type": "array", "items": {"type": "string"}},
"aliases_added_or_preserved": {"type": "array", "items": {"type": "string"}},
"spec_parity_validator_results": {"type": "object"}
```

---

## 10. SPEC-PARITY VALIDATORS (SYSTEM HEALING ADDITION)

### 1. SpecParityQNameValidator

**Fails if:**
- A model class exists without a `spec_qname` mapping entry
- An in-scope spec QName has no canonical class or explicit exclusion
- A class name does not derive from the spec local name
- A namespace/module does not derive from the spec prefix
- Facade aliases exist without canonical types
- Flat names replace spec hierarchy without naming exception

**Location:** `tools/supervisor/spec_parity_validators.py` (NEW)

### 2. NamespaceTreeValidator

**Fails if:**
- Complex ODF products have all source in one flat folder
- FODS lacks `Office/`, `Table/`, `Text/` namespace folders (.NET) or `office/`, `table/`, `text/` modules (Python) where in scope
- FODT lacks `Office/`, `Text/`, `Table/`, `Style/`, `Draw/` where in scope
- Python and .NET namespace trees diverge without reduced-scope reason

### 3. AttributePropertyMapValidator

**Fails if:**
- Spec attributes used by implemented elements are not mapped to typed properties
- `office:value-type` is string-only where typed value is required by product scope
- Formula/style attributes are preserved in XML but not exposed where scope requires editability

### 4. ContainmentGraphValidator

**Fails if:**
- `table:table` does not contain `table:table-row`
- `table:table-row` does not contain `table:table-cell`
- `text:list` does not contain `text:list-item`
- `office:spreadsheet` does not expose `table:table` children

### 5. AliasCompatibilityValidator

**Fails if:**
- Old classes/functions are removed without wrappers
- Aliases don't delegate to canonical classes
- Compatibility wrappers become the canonical implementation

### 6. SkeletonProgressValidator

**Fails product-progress claims if:**
- Class exists but has no behavior (empty body)
- Class exists but has no spec_qname mapping
- Class exists but has no tests
- Class exists but is not wired into parser/writer/model flow

### 7. SpecParityGateValidator (Gate 11 extension)

**Fails any Gate 11 candidate if:**
- QName-to-code map is incomplete
- Canonical namespace tree is missing
- Attribute-property map is missing for implemented elements
- Containment graph is missing
- Python parity matrix is stale or missing
- Naming exceptions are unreviewed

### 8. SkillWiringValidator

**Fails if:**
- New spec-literal rules are not referenced in governed skills
- Product-source task templates omit QName fields
- Base prompts don't include spec parity rules
- Execution prompts can still create arbitrary class names

---

## 11. MULTI-LANE RADICAL REMEDIATION PLAN (Enhanced with System Healing)

### Lane Sequencing (System Healing FIRST, then Product Regeneration)

```
SYSTEM HEALING (must pass before product regeneration):
  Lane 1 (SAL Pipeline Wiring)
  Lane 2 (Capability Reintegration)           <- gap-ledger consumed, _EXPANSION_GOALS replaced
  Lane 3 (Compiler Build)                     <- includes Phase 3.5 QName Ontology
  Lane 4 (Skills and Prompt Wiring)           <- 67+ wiring points, 5 new skills
  Lane 5 (Validators and Gate Hardening)      <- 8 spec-parity + 5 depth validators + 20 gate criteria
  Lane 6 (QName-to-Code Ontology Layer)       <- maps for FODS/FODT/ZST
  Lane 14 (Autonomous Supervision Integration) <- audit + wire autonomous_cycle, supervisor_loop, continuation, DAG enforcement
  Lane 15 (Autonomous Healing/Learning Integration) <- audit + wire durable learning loops, failure memory, skill propagation

SYSTEM HEALING GATE CHECK: All validators implementable. Skills wired. Schemas extended. QName maps exist.
  Autonomous supervision enforcement verified (Lane 14). Healing/learning loops durable (Lane 15).

PRODUCT REGENERATION (only after system healing):
  Lane 7 (.NET Architecture Blueprint + Spec-Literal Regeneration)
  Lane 8 (Python Blueprint + Spec-Literal Migration)
  Lane 9 (FODS Product Rebuild)
  Lane 10 (FODT Product Rebuild)
  Lane 11 (ZST Product Hardening)
  Lane 12 (CI, Package, and Evidence Hardening)
  Lane 13 (Post-Regeneration Recompute)
```

### Lane 0 — Coordinator and Autonomous Supervision

**Objective:** Orchestrate lanes without mixing responsibilities.

**Lane ownership:** Each lane owns specific files/directories. No cross-lane writes without coordinator approval.

**Must enforce (SYSTEM HEALING):**
- No product rename before system healing validators exist
- No source regeneration before QName-to-code map exists
- No agent may use arbitrary class names for spec concepts
- No taskcard may omit `spec_qname` for product model classes
- No product-progress claim may omit spec parity evidence
- No Gate 11 candidate without spec parity validators
- No product regeneration before Lane 14 (Autonomous Supervision) audit proves enforcement is real
- No product regeneration before Lane 15 (Autonomous Healing/Learning) audit proves learning loops are durable
- Autonomous supervision must enforce lane ownership, DAG ordering, continuation state, repair loops, and no-overclaim gates
- Autonomous healing must propagate corrections into skills, schemas, validators, failure memory, and future prompt generation

**Iteration gates (replace time estimates):**
- Repeat any lane until its validators pass
- Repeat product implementation until target score reached
- Repeat supervisor cycle until no OVERCLAIMED/REWORK remains
- Stop only on: real external blocker, impossible contradiction, or Babar-only approval

### Lane 1 — SAL Pipeline Wiring

**Objective:** Wire the dormant SAL tools into a running pipeline. Do NOT rebuild — CONNECT.

**Execution steps:**
1. Create `tools/specification-authority-layer/run_spec_pipeline.py` — master runner that chains:
   - `normalize_pdf.py` (if raw PDF not yet normalized)
   - `build_section_index.py` -> sections.jsonl
   - `build_chunk_index.py` -> chunks.jsonl
   - `build_spec_workbench.py` -> verified-facts-auto-seed.yaml (extended, not 10 hardcoded)
   - `spec_verifier.py` -> verify new facts against normalized text
2. Run pipeline for FODS, FODT, ZST
3. Generate product-scope spec concept inventory (not arbitrary fact counts):
   - Extract all reachable in-scope top-level and second-level concepts
   - Every excluded concept must have explicit exclusion reason: `out_of_scope`, `not_reachable`, `external_dependency`, `future_gate`, `unsupported_by_product_scope`, `duplicate`
4. Update `verified-facts-review.yaml` for all three formats

**Must produce:**
- `spec-authority-integration-audit.md` (20-component table)
- Master runner: `tools/specification-authority-layer/run_spec_pipeline.py`
- Updated workbenches for FODS (50+ facts), FODT (40+ facts), ZST (verified)
- Product-scope concept inventories with exclusion reasons

**Key files:** `tools/specification-authority-layer/*.py`, `tools/spec-normalize/*.py`, `.local/spec-cache/`

**Validation:** `spec_verifier.py --format fods --require-concept-inventory`

**Iteration gate:** Pipeline runs end-to-end for FODS/FODT/ZST; concept inventories produced.

### Lane 2 — Capability Reintegration

**Objective:** Make capabilities derived from spec facts AND consumed by task generation.

**Execution steps:**
1. Extend `capability_map_generator.py` to read from newly generated concept inventories (Lane 1 output)
2. Replace `_EXPANSION_GOALS` hardcoded catalog in `autonomous_task_generator.py` with capability-map-driven task selection:
   - Read `gap-ledger.json`
   - Filter to P0/P1 gaps with `blocks_readiness` or `required_for_poc`
   - Generate IMPLEMENT_CAPABILITY or TEST_COVERAGE tasks from gaps
3. Remove `advisory_only: true` from action queue items that have sufficient authority_state
4. Add feedback loop: after each sprint, reconcile actual source exports vs capability records
5. **Require capabilities to reference spec facts and QName concepts** (SYSTEM HEALING)
6. **No capability accepted without fact/concept source** (SYSTEM HEALING)
7. **No feature accepted without canonical source target** (SYSTEM HEALING)

**Key files:** `tools/capability_layer/capability_map_generator.py`, `tools/supervisor/autonomous_task_generator.py`, `reports/capability-layer/*.json`

**Iteration gate:** gap-ledger.json consumed by task generator AND task generator produces at least 10 spec-backed tasks per format.

### Lane 3 — Capability-to-Feature Compiler

**Objective:** Build the compiler described in Section 6 above (including Phase 3.5 QName Ontology).

**Execution steps:**
1. Create `tools/capability_layer/capability_to_feature_compiler.py` implementing Phases 0-8 (including Phase 3.5)
2. Format-family plugins: `spreadsheet_plugin.py` (FODS), `wordprocessing_plugin.py` (FODT), `compression_plugin.py` (ZST)
3. Run compiler for FODS/FODT/ZST
4. Produce all output artifacts listed in Section 6

**Key files:** `tools/capability_layer/capability_to_feature_compiler.py` (CREATE), `tools/capability_layer/plugins/` (CREATE)

**Must support:** Hundreds of formats through deterministic IDs, idempotent output, format-family plugins, incremental reruns, schema versioning.

**Iteration gate:** traceability_matrix.csv has no orphan facts, no orphan capabilities, and no features without fact references.

### Lane 4 — Skills and Prompt Wiring (SYSTEM HEALING)

**Objective:** Wire spec-literal rules into 67+ locations across 35+ files.

**Key files to modify:**
1. `.supervisor/skill-registry.yaml` — add spec_qname_required to product skills
2. `.supervisor/prompts/mega-train-template.md` — add 3 mandatory rules + 4 hard prohibitions
3. `tools/supervisor/generate_next_worker_prompt.py` — inject spec-authority advisory
4. `.claude/commands/*.md` — add "Spec-Literal Hierarchy Required" to 10 command files
5. `schemas/governance/product-mutation-taskcard-state-machine.schema.json` — add QName fields
6. `.supervisor/schemas/evidence-declaration.schema.json` — add spec parity fields

**Must add 5 new skills:** spec-literal-qname-to-code-mapping, spec-shaped-product-architecture-blueprint, spec-parity-source-regeneration-and-migration, python-reduced-spec-parity-model, spec-parity-verification

**Iteration gate:** Every skill registered; base prompts updated; schemas extended; governance validators wired.

### Lane 5 — Validators and Gate Hardening (SYSTEM HEALING)

**Objective:** Implement 8 spec-parity validators + 5 depth validators and extend Gate 11.

**Must implement in `tools/supervisor/spec_parity_validators.py` (NEW):**
1. SpecParityQNameValidator
2. NamespaceTreeValidator
3. AttributePropertyMapValidator
4. ContainmentGraphValidator
5. AliasCompatibilityValidator
6. SkeletonProgressValidator
7. SpecParityGateValidator
8. SkillWiringValidator

**Must implement in `tools/supervisor/governance_validators.py` (EXTEND):**
1. `validator_implementation_depth_score()` — reject if not declared or < 3
2. `validator_spec_fact_traceability()` — reject PRODUCT_SOURCE items with no spec_fact_refs
3. `validator_class_count_minimum()` — warn if < 5 new public classes for format library
4. `validator_monolith_detection()` — warn if any .py/.cs file > 1,200 LOC
5. `validator_no_stub_tests()` — reject tests containing only `assert True` or `pass`

**Implement overclaim pattern #5:** `_pattern_5_commercial_ready_helpers_only()` in overclaim_detector.py

**Must extend `plans/master-plan.md` S14** with C1-C20 and P1-P11 (see Section 13).

**Iteration gate:** All validators pass against current codebase (even if at lower gate level).

### Lane 6 — QName-to-Code Ontology Layer (SYSTEM HEALING)

**Objective:** Create the canonical map from spec concepts to code architecture.

**Must produce:**
- `prefix-namespace-registry.yaml`
- `qname-to-code-map.yaml` (per format)
- `namespace-tree.yaml` (per format per track)
- `canonical-class-inventory.yaml`
- `attribute-property-map.yaml`
- `containment-graph.yaml`
- `naming-exceptions.yaml`
- `legacy-alias-map.yaml`
- `migration-plan.yaml`

**Iteration gate:** Maps cover all in-scope QNames; no orphan concepts.

### Lane 7 — .NET Architecture Blueprint + Spec-Literal Regeneration Plan

**Objective:** Document target architecture for FODS and FODT .NET scope expansion with spec-literal canonical structures.

**Do NOT execute regeneration until Lanes 1-6 system healing gates pass.**

**Execution steps:**
1. Write `docs/architecture/fods-net-sdk-blueprint.md` — class inventory, namespace plan, spec-concept mappings, new classes to add (Section 7)
2. Write `docs/architecture/fodt-net-sdk-blueprint.md` — same
3. Complete migration table (all existing types classified per Section 8A)
4. Canonical file path plan (per Section 8A target structures)
5. Facade wrapper plan
6. Test migration plan
7. Rollback notes
8. Generate class skeleton files for all NEW classes (signatures only, no implementation)
9. Write architecture conformance test: count expected classes, fail if missing

**Key files:** `docs/architecture/*.md` (CREATE), `src/net/fods/` (ADD skeletons), `src/net/fodt/` (ADD skeletons)

**Iteration gate:** Blueprint passes review; skeleton files compile (`dotnet build` succeeds).

### Lane 8 — Python Blueprint + Spec-Literal Migration Plan

**Objective:** Document Python migration strategy, parity matrix, and spec-prefix module plan.

**Execution steps:**
1. Write `docs/architecture/fods-python-parity-matrix.yaml`
2. Write `docs/architecture/fodt-python-parity-matrix.yaml`
3. Write `docs/architecture/python-migration-strategy.md` — describes staged migration from monolith to spec-prefix modules
4. Module hierarchy plan (fods.office, fods.table, fods.text, etc.)
5. Class migration plan (neutral_model.py functions -> class methods)
6. Compatibility wrapper plan
7. Explicit reduced-scope declarations
8. Create `src/python/fods/model.py` and `src/python/fodt/model.py` with class stubs

**Key files:** `docs/architecture/*.yaml` (CREATE), `src/python/fods/model.py` (CREATE), `src/python/fodt/model.py` (CREATE)

**Iteration gate:** model.py classes importable; existing tests still pass; parity matrix complete.

### Lane 9 — FODS Product Rebuild

**Objective:** Expand FODS to target grade. **Only after system healing gates pass.**

**FODS .NET scope expansion (spec-literal canonical targets):**
- P1: `office:value-type` → `Table.TypedValue` (+ subtypes) + refactor `Table.TableCell` to use typed values
- P1: `table:formula` → `Table.Formula` (string representation, cached `Table.TypedValue` result)
- P2: `style:style` → `Style.Style` + `office:automatic-styles` → `Office.AutomaticStyles`
- P3: `table:covered-table-cell` → `Table.CoveredTableCell`; `table:table-column` → `Table.TableColumn`; `table:content-validation` → `Validation.ContentValidation`
- P3: Extract operations from `Office.Document` if canonical class exceeds 1,500 LOC
- Facade wrappers (`FodsTypedValue`, `FodsFormula`, `FodsStyle`, etc.) created in Compat/ delegating to canonical classes

**FODS Python model migration (spec-literal canonical targets):**
- P1: `office.document.Document`, `table.table.Table`, `table.table_row.TableRow`, `table.table_cell.TableCell` classes
- P1: `table.typed_value.TypedValue` (string + float)
- P2: Refactor neutral_model.py to delegate to canonical model classes
- P2: operations.py extracted from neutral_model.py
- Compat wrappers (`FodsWorkbook`, `FodsSheet`, `FodsRow`, `FodsCell`) in fods.compat module

**Tests per new class:** Minimum 5 tests (positive, negative, roundtrip, edge case, spec trace).

**Iteration gate:** Score reaches 20/25 (.NET) and 18.5/25 (Python).

### Lane 10 — FODT Product Rebuild

**Objective:** Expand FODT to target grade. **Only after system healing gates pass.**

**FODT .NET scope expansion (spec-literal canonical targets):**
- P1: `text:list` → `Text.List` + `text:list-item` → `Text.ListItem` (with nested list support)
- P1: `table:table` → `Table.Table` + `table:table-row` → `Table.TableRow` + `table:table-cell` → `Table.TableCell`
- P1: `text:span` → `Text.Span`
- P2: `text:h` → `Text.Heading` (separate from `Text.Paragraph`, typed)
- P2: `text:footnote` → `Text.Footnote`; `text:endnote` → `Text.Endnote`; `draw:frame` → `Draw.Frame`; `text:section` → `Text.Section`
- P3: `style:style` → `Style.Style`
- Facade wrappers (`FodtList`, `FodtTable`, `FodtTextSpan`, `FodtHeading`, etc.) created in Compat/ delegating to canonical classes

**FODT Python model migration (spec-literal canonical targets):**
- P1: `office.document.Document`, `text.paragraph.Paragraph`, `text.list.List`, `table.table.Table` classes
- P2: Refactor neutral_model.py to delegate to canonical model classes
- Compat wrappers (`FodtDocument`, `FodtParagraph`, `FodtList`, `FodtTable`) in fodt.compat module

**Iteration gate:** Score reaches 20/25 (.NET) and 18.5/25 (Python).

### Lane 11 — ZST Product Strategy

**Objective:** Confirm ZST scope; deepen Python to 20/25.

**Decision:** Record `DEC-ZST-NET-TRACK` — ZST remains Python-only FOSS. .NET track is `intentionally_absent`.

**ZST Python hardening:**
- Fix collection errors
- Add malformed frame tests (corrupt magic, truncated, wrong checksum)
- Add window size boundary tests
- Add streaming compression test for large inputs

**Iteration gate:** 0 collection errors; 670+ tests passing; score 20/25.

### Lane 12 — CI, Package, and Evidence Hardening

**Objective:** Make .NET build/test unavoidable; verify Python packages; add coverage audit.

**Execution steps:**
1. Add .NET CI job to `.github/workflows/ci.yml`: `dotnet build` + `dotnet test` for FODS and FODT
2. Add Python wheel build step: `python -m build --wheel` for fods/fodt/zst
3. Add capability coverage audit step
4. Verify pyproject.toml includes fods/fodt/zst packages

**Iteration gate:** CI passes with .NET and Python steps; wheels buildable; NuGet buildable.

### Lane 13 — Post-Regeneration Recompute

**Regenerate ALL derived artifacts after product regeneration.** No old map trusted.

Must regenerate:
- Spec concept graph
- QName-to-code map
- Capability graph
- Feature graph
- Taskcards
- Test obligation matrix
- Evidence obligation matrix
- Traceability matrix
- Gap queue
- Gate readiness projection
- Product architecture report
- Python reduced parity matrix
- .NET commercial SDK audit
- Supervisor evidence declaration

### Lane 14 — Autonomous Supervision Layer Integration Audit (SYSTEM HEALING)

**Objective:** Forensically audit whether the Autonomous Supervision Layer actually controls worker agents, enforces lane boundaries, generates executable rework, and prevents unsafe product regeneration. Produce a wiring plan to close any gaps found. This is NOT about building new infrastructure — it is about proving whether the EXISTING infrastructure (autonomous_cycle.py, supervisor_loop.py, generate_next_worker_prompt.py, continuation signals, evidence declarations) actually functions as an integrated enforcement authority or is partially wired ghost infrastructure.

**Systemic risk addressed:** 5th systemic risk (Section 1) — Autonomous Supervision may be a partially wired control layer rather than a real execution authority.

**Investigation questions (26 minimum):**

*Lane Ownership & Boundary Enforcement:*
1. Does `autonomous_cycle.py` enforce that a worker agent can only modify files owned by its assigned lane?
2. Is there a file-ownership registry that maps lanes to allowed file paths?
3. What happens if a worker writes to a file outside its lane? Is the write rejected, warned, or silently accepted?
4. Does `generate_next_worker_prompt.py` inject lane-specific file restrictions into worker prompts?

*DAG Ordering Enforcement:*
5. Does `autonomous_cycle.py` read an execution DAG and refuse to schedule a lane whose dependencies haven't completed?
6. Is there a DAG file that the system reads, or is ordering determined by ad-hoc logic?
7. Can Wave 5 lanes (product regeneration) actually be started before Wave 3 (system healing gate check) passes?
8. What prevents a worker from executing Lane 9 work when Lane 1 hasn't completed?

*Continuation State Machine:*
9. Does `continuation-signal.json` actually control whether the next sprint starts, or is it advisory?
10. Can a worker ignore the continuation signal and proceed anyway?
11. What states does the continuation state machine support? Are they documented?
12. Does `classify_continuation_state()` in autonomous_cycle.py check governance validators or only process state?

*Repair Loop Enforcement:*
13. When `autonomous_cycle.py` returns exit 3 (OVERCLAIMED), does the system actually generate rework taskcards?
14. Are rework taskcards machine-generated or do they require manual intervention?
15. Does the repair loop have a maximum iteration count before escalating?
16. Can the system repair itself when a lane fails, or does it just report the failure?

*No-Overclaim Gate:*
17. Does `overclaim_detector.py` actually run as part of the autonomous cycle, or is it a standalone tool?
18. Are overclaim results consumed by `grade_declared_work.py` or by `autonomous_cycle.py`?
19. Can a work item be marked ACCEPTED when overclaim patterns are detected?
20. Is Pattern #5 (`_pattern_5_commercial_ready_helpers_only()`) implemented or skeleton-only?

*Product-Progress Selection:*
21. Does `autonomous_task_generator.py` actually select the next best work item based on product state?
22. Does it read the gap-ledger, capability map, or action queue — or does it use hardcoded goals?
23. Can the task generator produce zero-product-work loops indefinitely?
24. Is there a circuit breaker for repeated no-progress cycles?

*Evidence Declaration Authority:*
25. Does `autonomous_cycle.py` reject evidence declarations that reference non-existent files?
26. Can a worker self-declare PASS on items that haven't been tested?

**Required tables:**

| Component | File | Lines | Intended Role | Actual Role | Enforces? | Gap |
|-----------|------|-------|---------------|-------------|-----------|-----|
| (one row per autonomous supervision component) |

| Enforcement Point | Expected Behavior | Actual Behavior | Wired? | Fix Required |
|-------------------|-------------------|-----------------|--------|-------------|
| (one row per enforcement boundary) |

| Continuation State | Condition | Next Action | Actually Enforced? |
|-------------------|-----------|-------------|-------------------|
| (one row per state transition) |

**Must produce:**
- `autonomous-supervision-layer-integration-audit.md` — full 26-question investigation with evidence
- `autonomous-supervision-component-inventory.md` — component table with actual vs intended roles
- `autonomous-supervision-enforcement-gap-table.md` — every enforcement point with wired/not-wired status
- `autonomous-supervision-wiring-plan.md` — concrete steps to close every gap found
- `autonomous-supervision-acceptance-criteria.md` — criteria for declaring Lane 14 complete
- `continuation-state-machine-diagram.md` — all states, transitions, and enforcement points
- `lane-enforcement-proof-matrix.md` — for each lane pair, proof that ordering is enforced

**Key files to audit:**
- `tools/supervisor/autonomous_cycle.py` (~817 LOC)
- `tools/supervisor/supervisor_loop.py`
- `tools/supervisor/generate_next_worker_prompt.py`
- `tools/supervisor/grade_declared_work.py` (~625 LOC)
- `tools/supervisor/autonomous_task_generator.py` (~1,084 LOC)
- `tools/supervisor/governance_validators.py` (~1,170 LOC)
- `tools/supervisor/anti_skip_checker.py` (~1,241 LOC)
- `tools/requirements_authority/overclaim_detector.py` (~300 LOC)
- `.local/supervisor/continuation-signal.json`
- `.supervisor/state/current-run.json`
- `.supervisor/state/watcher.json`

**Iteration gate:** All 26 investigation questions answered with file:line evidence. Gap table complete. Wiring plan actionable. No unanswered "partially wired" claims remain.

### Lane 15 — Autonomous Healing and Learning Layer Integration Audit (SYSTEM HEALING)

**Objective:** Forensically audit whether the system can learn from failures and propagate corrections into durable machinery (skills, schemas, validators, taskcard templates, failure memory, continuation state, future prompt generation). Produce a wiring plan to make learning loops durable. This is NOT about building a new AI learning system — it is about proving whether corrections made in one sprint actually persist into future sprints through governed channels, or whether they evaporate when the context window closes.

**Systemic risk addressed:** 6th systemic risk (Section 1) — Autonomous Healing and Learning may be present only as prompts or repair policies, not as a durable learning loop.

**Investigation questions (26 minimum):**

*Failure Memory:*
1. When a sprint fails, where is the failure recorded? Is it in a durable file or only in the conversation context?
2. Does `autonomous_cycle.py` read past failure records when planning the next sprint?
3. Is there a failure taxonomy (categories of failures) or is every failure treated as unique?
4. Can the system detect that the same failure has occurred 3+ times and escalate?
5. Is there a `failure-memory.json` or equivalent persistent store?

*Skill Propagation:*
6. When a new pattern is discovered (e.g., "evidence_artifacts requires type field"), does it get written to a skill or validator?
7. Does `generate_next_worker_prompt.py` inject lessons learned from prior sprints?
8. Are `.claude/commands/*.md` skill files ever updated by the autonomous system, or only by humans?
9. Does the skill registry (`skill-registry.yaml`) track version history or update timestamps?
10. Can the system create a new skill from a repeated pattern without human intervention?

*Validator Evolution:*
11. When a validator catches a new class of error, does the system add a new check for it?
12. Are `governance_validators.py` checks ever auto-generated from observed failure patterns?
13. Does `anti_skip_checker.py` learn new skip patterns, or is its detector list static?
14. Can the system promote an ad-hoc fix into a permanent validator?

*Taskcard Template Evolution:*
15. When a taskcard schema is extended (e.g., adding `spec_qname`), do existing taskcards get migrated?
16. Are taskcard templates ever regenerated based on execution outcomes?
17. Does the system track which taskcard fields most often cause rework?

*Continuation State Learning:*
18. Does `continuation-signal.json` capture WHY a sprint stopped, not just THAT it stopped?
19. Can the system distinguish between "stopped because of a real blocker" and "stopped because of a false positive"?
20. Does `stop_reason_adjudicator.py` learn from prior adjudication decisions?

*Prompt Generation Learning:*
21. Does `generate_next_worker_prompt.py` incorporate feedback from grading results?
22. Are prompts that led to OVERCLAIMED results flagged and modified for future use?
23. Is there a prompt quality feedback loop (grade result -> prompt modification)?
24. Does the mega-train template evolve based on execution evidence?

*Schema Evolution:*
25. When evidence declarations repeatedly fail validation, does the system propose schema changes?
26. Are schema migrations tracked and versioned?

**Failure Taxonomy (Required Output):**

| Failure Category | Example | Current Response | Durable? | Learning Propagated? |
|-----------------|---------|-----------------|----------|---------------------|
| Schema validation | Missing `type` in evidence_artifacts | Fix in current sprint | NO — next sprint may repeat | NO |
| Grading false positive | LLM grader claims function missing when it exists | Rework item (advisory) | PARTIAL — grader context not updated | NO |
| Import path error | `from csv import` collides with stdlib | sys.path fix | YES — in MEMORY.md | PARTIALLY — only in auto-memory |
| API signature mismatch | Function takes path not model | Fix call site | NO — next sprint may repeat | PARTIALLY — only in auto-memory |
| Governance validator false trigger | no_wrong_stream on rework items | Reorder evidence | NO — must be rediscovered | NO |
| Continuation state stuck | iteration >= max_iterations | Manual reset or governed rollover | YES — governed rollover exists | YES |

**Healing Loop Model (Required Output):**

```
FAILURE OCCURS
    |
    v
DETECTED BY: grade_declared_work / governance_validators / anti_skip_checker / autonomous_cycle
    |
    v
CLASSIFIED AS: [schema_error | grading_error | api_mismatch | governance_false_positive | real_blocker]
    |
    v
RECORDED IN: [continuation-signal.json | rework items | ???]
    |
    v
CORRECTION APPLIED IN: [current sprint fix | prompt update | validator addition | skill creation | schema migration]
    |
    v
PROPAGATED TO: [??? — THIS IS THE GAP TO INVESTIGATE]
    |
    v
VERIFIED DURABLE: [??? — DOES THE CORRECTION SURVIVE CONTEXT WINDOW CLOSURE?]
```

**Learning Propagation Matrix (Required Output):**

| Correction Type | Where Applied | Survives Context Close? | Consumed by Future Sprint? | Evidence |
|----------------|---------------|------------------------|---------------------------|---------|
| auto-memory entry | MEMORY.md | YES | YES (if loaded) | MEMORY.md loaded at start |
| prompt text fix | generate_next_worker_prompt.py | YES | YES | Code persists |
| schema fix | evidence-declaration.schema.json | YES | YES | Schema loaded at validation |
| skill file update | .claude/commands/*.md | YES | CONDITIONAL (must be invoked) | Only if skill selected |
| validator addition | governance_validators.py | YES | YES | Always run |
| rework item | rework_items in signal | NO — single sprint | NO | Consumed once |
| grading context | LLM grader system prompt | NO — per call | NO | Reconstructed each time |
| taskcard field addition | taskcard schema | YES | CONDITIONAL | Only if new taskcards use schema |

**Must produce:**
- `autonomous-healing-learning-layer-integration-audit.md` — full 26-question investigation
- `healing-loop-model.md` — flow diagram with gap analysis at each stage
- `learning-propagation-matrix.md` — every correction type with durability analysis
- `failure-taxonomy.yaml` — machine-readable failure categories with current/target responses
- `durable-learning-loop-design.md` — concrete design for making transient corrections durable
- `skill-propagation-wiring-plan.md` — how skills evolve from observed patterns
- `failure-memory-schema.yaml` — schema for persistent failure records
- `healing-learning-acceptance-criteria.md` — criteria for declaring Lane 15 complete
- `healing-learning-validator-design.md` — validators that ensure learning persists

**Key files to audit:**
- `tools/supervisor/autonomous_cycle.py` (continuation state, failure handling)
- `tools/supervisor/generate_next_worker_prompt.py` (prompt evolution)
- `tools/supervisor/grade_declared_work.py` (grading feedback)
- `tools/supervisor/stop_reason_adjudicator.py` (stop classification)
- `tools/supervisor/governance_validators.py` (validator evolution)
- `tools/supervisor/anti_skip_checker.py` (pattern learning)
- `.supervisor/skill-registry.yaml` (skill versioning)
- `.supervisor/prompts/mega-train-template.md` (template evolution)
- `.local/supervisor/continuation-signal.json` (failure persistence)
- `C:\Users\prora\.claude\projects\c--Users-prora-OneDrive-Documents-GitHub-format-factory\memory\MEMORY.md` (auto-memory durability)

**Iteration gate:** All 26 investigation questions answered with file:line evidence. Failure taxonomy complete. Healing loop model has no unresolved "???" gaps. Learning propagation matrix shows no "NO" entries without a wiring plan to fix them.

---

## 12. AUTONOMOUS SUPERVISION OPERATING MODEL

### Coordinator Agent

- Reads `session-resume.md` at start
- Assigns lane work per priority sequence
- After each lane: runs `autonomous_cycle.py` with lane-specific declaration
- Collects rework items; repairs before advancing
- Stops on: exit code 3 (OVERCLAIMED), Gate 11 (Babar Raza), iteration >= max_iterations
- **System healing lanes (1-6, 14, 15) MUST pass before product regeneration lanes (7-13)**

### Iteration-Based Acceptance (Replaces Time Estimates)

**NO time estimates appear in this plan.** Acceptance is ONLY through validated repo state:
- Lane complete when its specific validators pass
- Product complete when score reaches target
- Sprint complete when `autonomous_cycle.py` returns exit 0 with no OVERCLAIMED items

### Repair Loop

If any lane returns exit 3 or REWORK_REQUIRED:
1. Coordinator reads rework items
2. Assigns rework to responsible lane
3. Lane re-executes with smaller scope
4. Repeat until validators pass

### Done Criteria

| Product | Track | Target Score | Required Validators |
|---------|-------|-------------|-------------------|
| FODS | .NET | 20/25 | C1-C20 all pass |
| FODS | Python | 18.5/25 | P1-P11 all pass |
| FODT | .NET | 20/25 | C1-C20 all pass |
| FODT | Python | 18.5/25 | P1-P11 all pass |
| ZST | Python | 20/25 | P1-P5 all pass |
| ZST | .NET | N/A | DEC-ZST-NET-TRACK recorded |

### No-Human-Blocker Rule

NOT human blockers: Adding classes, tests, validators, blueprints, CI steps, refactoring, wiring SAL tools, wiring skills, extending schemas.
HUMAN blockers: Gate 11 final approval (Babar Raza), PyPI/NuGet publication credentials, legal sign-off.

---

## 13. EXTENDED GATE 11 CRITERIA

### .NET Commercial (C1-C20)

**Original depth criteria (C1-C10):**
```
C1: implementation_depth_score >= 4/5 verified by independent reviewer
C2: capability_coverage_percentage >= 80%
C3: Every public method has >= 1 spec_fact_ref
C4: class_count >= 15 for complex formats (FODS/FODT)
C5: .NET CI pipeline: dotnet build AND dotnet test must pass
C6: >= 3 roundtrip tests with XML-level verification
C7: >= 1 negative test per public method
C8: NuGet package buildable
C9: No single class exceeds 1,500 LOC without justification
C10: Babar Raza sign-off (final human gate)
```

**Spec-parity criteria (C11-C20, SYSTEM HEALING ADDITION):**
```
C11: QName-to-code map complete for all in-scope implemented spec concepts
C12: Canonical namespace tree exists and passes NamespaceTreeValidator
C13: Every canonical model class has spec_qname metadata
C14: Every facade/legacy class maps to a canonical spec-literal class
C15: Attribute-property map covers implemented elements' in-scope attributes
C16: Containment graph matches spec hierarchy for implemented concepts
C17: No flat model architecture for ODF commercial products unless formally excepted
C18: Spec parity skills wired into task generation, implementation, evidence, verification
C19: Regeneration generated from QName-to-code map, not ad hoc manual edits
C20: Post-regeneration traceability matrices regenerated and pass
```

### Python FOSS (P1-P11)

**Original depth criteria (P1-P5):**
```
P1: Class-based model exists (no monolithic function-only modules for complex formats)
P2: Parity matrix exists and is up to date
P3: capability_coverage_percentage >= 60%
P4: Wheel buildable from pyproject.toml
P5: 0 collection errors in test suite
```

**Spec-parity criteria (P6-P11, SYSTEM HEALING ADDITION):**
```
P6: Python modules follow same spec-prefix hierarchy where implemented
P7: Python reduced parity matrix generated from same QName-to-code map
P8: Every missing Python class has explicit reduced-scope reason
P9: Dict/function API is compatibility layer only after model migration
P10: Python wrappers delegate to canonical spec-literal model classes
P11: Python parity validators wired into supervisor verification
```

---

## 14. SCORING TARGETS

| Product | Track | Current /25 | Target /25 | Classification After Remediation |
|---------|-------|------------|-----------|--------------------------------|
| FODS | .NET | 13 (incomplete scope) | 20 | GATE_11_APPROVAL_CANDIDATE |
| FODS | Python | 16 (monolith) | 18.5 | REVIEWABLE_WITH_LIMITATIONS |
| FODT | .NET | 13 (incomplete scope) | 20 | GATE_11_APPROVAL_CANDIDATE |
| FODT | Python | 16 (monolith) | 18.5 | REVIEWABLE_WITH_LIMITATIONS |
| ZST | Python | 19 (near-complete) | 20 | REVIEWABLE_WITH_LIMITATIONS |
| ZST | .NET | 0 (absent by design) | N/A | SCOPE_DECISION_RECORDED |

"GATE_11_APPROVAL_CANDIDATE" means candidate for Babar Raza's review, NOT approved.

---

## 15. PLAN HARDENING DIFF (vs Prior Plan)

| Area | Prior Plan | Hardened Plan | Why |
|------|-----------|--------------|-----|
| SAL assessment | "Facts manually seeded" | Full 20-component audit: 3 ACTIVE, 17 DEAD, ghost infrastructure | Prior plan didn't diagnose WHY facts were manual |
| Capability layer | "Come from POC targets" | Full disconnection chain: gap-ledger NEVER consumed, task generator uses HARDCODED goals | Prior plan didn't trace the break point |
| .NET architecture grade | 3/5 (prototype) | **4/5 (professional SDK, incomplete)** | Forensic audit revealed proper dual-mode design, typed wrappers, security hardening |
| Compiler design | "Create capability_to_taskcard_compiler.py" | 9-phase production compiler with IR, format-family plugins, Phase 3.5 QName Ontology, scaling for hundreds of formats | Prior plan was a single script, not a production subsystem |
| Python strategy | "Refactor to class-based" | Staged migration preserving backward compatibility; parity matrix; validator for zero-class detection; spec-prefix module hierarchy | Prior plan didn't address migration safety or spec-literal parity |
| Gate 11 criteria | Not specified | 20 .NET criteria (C1-C20) + 11 Python criteria (P1-P11) | Prior plan had no concrete criteria |
| Time estimates | "3 days", "2 days" | **REMOVED** -- iteration gates only | Time estimates are not acceptance logic |
| Anti-fake-progress | Not present | 10 hard constraint rules | Prior plan allowed skeleton-only progress |
| Supervisor validators | Listed 5 new validators | 5 depth + 8 spec-parity + overclaim pattern #5 | Prior plan didn't include spec-parity validators |
| System healing | Not present | **67+ wiring points, 5 new skills, schema extensions, base prompt updates** | Prior plan treated spec-literal as product refactoring, not governance |
| Spec-literal hierarchy | Not present | QName-to-code ontology, namespace tree, containment graph, canonical class inventory | Prior plan allowed arbitrary class naming |
| Lane count | 10 lanes | **16 lanes** (8 system healing + 7 product regeneration + 1 coordinator) | System healing lanes (1-6, 14, 15) added before product work |
| Autonomous supervision | Not audited | **Lane 14**: full integration audit of autonomous_cycle, supervisor_loop, continuation, DAG enforcement | 5th systemic risk: may be partially wired |
| Autonomous healing/learning | Not audited | **Lane 15**: full integration audit of durable learning loops, failure memory, skill propagation | 6th systemic risk: may be prompt-only |

---

## 16. OUTPUT ARTIFACTS

All under `.local/evidences/spec-to-feature-radical-correction-plan-20260612-8e45224/`:

### Diagnostic Artifacts (from prior plan)
1. `evidence-declaration.yaml` — mode: planning_only, source_mutation_performed: false, gate11_approved_by_agent: false
2. `system-failure-analysis.md` — pipeline stage table, root causes, executive finding
3. `spec-authority-integration-audit.md` — 20-component SAL audit with consumption proof
4. `capability-feature-layer-audit.md` — disconnection chain, schema comparison, health verdicts
5. `capability-to-feature-compiler-design.md` — 9-phase compiler with IR and scaling design
6. `product-architecture-gap-report.md` — per product/track current vs expected architecture
7. `dotnet-commercial-sdk-audit.md` — file/class inventory, spec-concept mapping, scope gaps
8. `python-reduced-architecture-strategy.md` — migration stages, parity matrix format, validators
9. `spec-to-capability-to-feature-trace.md` — traceability chain per format
10. `radical-remediation-master-plan.md` — 16-lane plan with iteration gates
11. `autonomous-supervision-operating-model.md` — coordinator, repair loops, done criteria
12. `implementation-depth-gate-spec.md` — proposed validators
13. `plan-hardening-diff.md` — explicit changes from prior plan

### System Healing Artifacts (ADDED)
14. `system-healing-plan.md`
15. `skill-wiring-audit.md`
16. `skill-wiring-update-plan.md`
17. `base-prompt-update-plan.md`
18. `taskcard-schema-qname-extension.md`
19. `evidence-schema-spec-parity-extension.md`
20. `spec-literal-hierarchy-rules.md`
21. `prefix-namespace-registry.yaml`
22. `qname-to-code-map-design.md`
23. `namespace-tree-design.md`
24. `canonical-class-inventory-design.md`
25. `attribute-property-map-design.md`
26. `containment-graph-design.md`
27. `naming-exceptions-design.md`
28. `legacy-alias-map-design.md`
29. `migration-plan-design.md`
30. `spec-parity-validator-design.md`
31. `skill-wired-validator-integration-plan.md`
32. `regeneration-and-renaming-execution-plan.md`
33. `post-regeneration-recompute-plan.md`
34. `hardened-next-execution-prompt.md`

### Autonomous Supervision Audit Artifacts (ADDENDUM — Lane 14)
35. `autonomous-supervision-layer-integration-audit.md`
36. `autonomous-supervision-component-inventory.md`
37. `autonomous-supervision-enforcement-gap-table.md`
38. `autonomous-supervision-wiring-plan.md`
39. `autonomous-supervision-acceptance-criteria.md`
40. `continuation-state-machine-diagram.md`
41. `lane-enforcement-proof-matrix.md`

### Autonomous Healing/Learning Audit Artifacts (ADDENDUM — Lane 15)
42. `autonomous-healing-learning-layer-integration-audit.md`
43. `healing-loop-model.md`
44. `learning-propagation-matrix.md`
45. `failure-taxonomy.yaml`
46. `durable-learning-loop-design.md`
47. `skill-propagation-wiring-plan.md`
48. `failure-memory-schema.yaml`
49. `healing-learning-acceptance-criteria.md`

---

## 17. ANTI-FAKE-PROGRESS RULES (Hard Constraints)

1. Skeleton-only source files do NOT count as product progress
2. Architecture-only files MUST be labeled architecture-only
3. Generated taskcards do NOT count as implemented features
4. Capability maps do NOT count as source progress
5. Passing smoke tests do NOT count as implementation depth
6. Public exports without deep tests count as overclaim risk
7. No model class without spec_qname mapping
8. No product-progress claim without spec parity evidence
9. No time estimates as acceptance logic — iteration gates only
10. Every product-progress claim MUST include source + tests + spec_qname refs + evidence

---

## 18. VERIFICATION

### System Healing Verification (Before Product Regeneration)

```bash
# Verify skills wired
python tools/supervisor/spec_parity_validators.py --check skill-wiring
# Verify base prompt updated
grep "spec_qname" .supervisor/prompts/mega-train-template.md
# Verify taskcard schema extended
python -c "import json; s=json.load(open('schemas/governance/product-mutation-taskcard-state-machine.schema.json')); assert 'spec_qname' in str(s)"
# Verify evidence schema extended
python -c "import json; s=json.load(open('.supervisor/schemas/evidence-declaration.schema.json')); assert 'spec_qname_refs' in str(s)"
# Verify QName map exists
test -f .local/evidences/*/qname-to-code-map.yaml
# Verify namespace tree exists
test -f .local/evidences/*/namespace-tree.yaml
# Verify containment graph exists
test -f .local/evidences/*/containment-graph.yaml
# Verify Lane 14 (Autonomous Supervision) audit outputs
test -f .local/evidences/*/autonomous-supervision-layer-integration-audit.md
test -f .local/evidences/*/autonomous-supervision-enforcement-gap-table.md
test -f .local/evidences/*/lane-enforcement-proof-matrix.md
# Verify Lane 15 (Autonomous Healing/Learning) audit outputs
test -f .local/evidences/*/autonomous-healing-learning-layer-integration-audit.md
test -f .local/evidences/*/failure-taxonomy.yaml
test -f .local/evidences/*/learning-propagation-matrix.md
test -f .local/evidences/*/failure-memory-schema.yaml
```

### Product Regeneration Verification (After)

```bash
# .NET builds
dotnet build src/net/fods/FormatFactory.Fods.csproj
dotnet build src/net/fodt/FormatFactory.Fodt.csproj
# Python imports (post-spec-literal)
python -c "from fods.office.document import Document; print('OK')"
python -c "from fodt.text.paragraph import Paragraph; print('OK')"
# All tests pass
.local/venv/Scripts/python -m pytest tests/python/fods/ tests/python/fodt/ -v --continue-on-collection-errors
dotnet test tests/net/fods/ tests/net/fodt/
# Validators pass
python tools/supervisor/spec_parity_validators.py --format fods --format fodt
```

---

## 19. CONSTRAINTS

- System healing BEFORE product regeneration (Lanes 1-6, 14, 15 before Lanes 7-13)
- Spec-literal rules wired into governed skills, NOT just docs
- No ad hoc manual renaming — all renames from QName-to-code map
- No skeleton-only files counted as progress
- No Gate 11 approval — Babar Raza only
- All prior prompt requirements remain active
- Iteration gates, NOT time estimates
- DO NOT approve Gate 11
- DO NOT mutate source code during this planning sprint
- DO NOT treat this plan as evidence of product readiness
- DO NOT skip spec-fact tracing when implementing features
- DO NOT write tests that just call a function and assert it returns something
- DO NOT say "this will take X days" as acceptance logic
- DO NOT count skeleton files as product progress
- DO NOT count capability maps as source progress
- ALWAYS produce focused evidence with specific assertions
- ALWAYS run validators before declaring any lane complete
- NEVER call a Python module "professional" if it has zero class definitions
- DO NOT declare system healing complete until Lane 14 (Autonomous Supervision) audit proves enforcement is real
- DO NOT declare system healing complete until Lane 15 (Autonomous Healing/Learning) audit proves learning loops are durable
- DO NOT start product regeneration with unresolved "partially wired" or "prompt-only" supervision findings
- DO NOT treat autonomous supervision or healing/learning as working without file:line evidence
- ALWAYS answer all 26 investigation questions per lane with traceable evidence before marking complete

---

## 20. AUTONOMOUS SUPERVISION LAYER INTEGRATION AUDIT

### Purpose

This section defines the deep forensic investigation required by Lane 14. The Autonomous Supervision Layer is referenced throughout the plan (autonomous_cycle.py, supervisor_loop.py, generate_next_worker_prompt.py, continuation signals, evidence declarations, grade_declared_work.py, governance validators) but has NOT been proven to function as an integrated enforcement authority.

**The 5th systemic risk (Section 1) states:** "Autonomous Supervision may be a partially wired control layer rather than a real execution authority. It may generate prompts, read declarations, or run validators, but not actually enforce lane ownership, dependency DAGs, continuation state, repair loops, no-overclaim gates, and product-progress selection."

This audit answers: **Does the supervision layer ACTUALLY enforce, or does it merely ADVISE?**

### Component Inventory (To Be Verified)

| Component | File | LOC (approx) | Intended Role | To Investigate |
|-----------|------|-------------|---------------|----------------|
| autonomous_cycle.py | tools/supervisor/ | ~817 | Orchestrate sprint lifecycle, classify continuation state | Does it enforce lane ordering? DAG? File ownership? |
| supervisor_loop.py | tools/supervisor/ | ~500 | Subprocess wrapper for autonomous_cycle | Does it add enforcement beyond subprocess timeout? |
| generate_next_worker_prompt.py | tools/supervisor/ | ~700 | Generate worker prompts with lane context | Does it inject file restrictions? Lane boundaries? |
| grade_declared_work.py | tools/supervisor/ | ~625 | Grade evidence declarations | Does it reject overclaimed items? Or default to adequate? |
| autonomous_task_generator.py | tools/supervisor/ | ~1,084 | Select next work items | Does it read gap-ledger or hardcoded goals? Circuit breaker? |
| governance_validators.py | tools/supervisor/ | ~1,170 | Validate process compliance | Does it check product depth? Or process only? |
| anti_skip_checker.py | tools/supervisor/ | ~1,241 | Detect skip patterns | Are detectors static or learning? |
| overclaim_detector.py | tools/requirements_authority/ | ~300 | Detect overclaim patterns | Is Pattern #5 implemented? All 5 patterns real? |
| stop_reason_adjudicator.py | tools/supervisor/ | ~200 | Classify stop reasons | Does it distinguish real vs false blockers? |
| authority_gate_validation.py | tools/supervisor/ | ~250 | Compute authority levels | Does it require QName map for READINESS? |
| continuation-signal.json | .local/supervisor/ | N/A | Persist continuation state | Advisory or mandatory? |
| current-run.json | .supervisor/state/ | N/A | Track current sprint | Does it enforce single-sprint exclusion? |

### Enforcement Boundary Analysis (To Be Produced)

For each enforcement boundary below, the audit must determine: **Is it enforced by code, or merely advised by prompts?**

1. **Lane file ownership** — Can worker A write files owned by lane B?
2. **DAG ordering** — Can Lane 9 start when Lane 1 hasn't completed?
3. **Continuation gating** — Can a worker ignore continuation-signal.json?
4. **Rework generation** — Does exit 3 produce machine-readable rework taskcards?
5. **Overclaim rejection** — Does overclaim detection block acceptance?
6. **Product depth requirement** — Can a shallow product be declared ACCEPTED?
7. **Evidence file existence** — Can a declaration reference non-existent files?
8. **Spec fact traceability** — Can a PRODUCT_SOURCE item have zero spec_fact_refs?
9. **Test count regression** — Can test count decrease without detection?
10. **Zero-progress circuit breaker** — Is there a limit on no-product-work cycles?
11. **Max iteration enforcement** — Does iteration >= max actually stop execution?
12. **Grading authority** — Can LLM grading override governance validator FAIL?

### Acceptance Criteria for Lane 14

1. All 26 investigation questions answered with `file:line` evidence
2. Component inventory table complete with actual vs intended roles (no "unknown" cells)
3. Enforcement boundary table complete with wired/not-wired status and gap classification
4. Every "NOT WIRED" enforcement boundary has a concrete wiring plan with target file and implementation sketch
5. Continuation state machine fully documented with all transitions
6. Lane enforcement proof matrix shows evidence for every lane-pair ordering constraint
7. No remaining "partially wired" claims without specific file:line gap identification

---

## 21. AUTONOMOUS HEALING AND LEARNING LAYER INTEGRATION AUDIT

### Purpose

This section defines the deep forensic investigation required by Lane 15. The system's ability to learn from failures is referenced in repair loops, rework items, prompt generation, grading feedback, and auto-memory — but has NOT been proven to constitute a durable learning system.

**The 6th systemic risk (Section 1) states:** "Autonomous Healing and Learning may be present only as prompts or repair policies, not as a durable learning loop. It may repair one sprint but fail to update skills, rules, validators, taskcard templates, failure memory, continuation state, or future prompt generation."

This audit answers: **Do corrections persist beyond the current context window, or do they evaporate?**

### Failure Mode Analysis (To Be Verified)

The system encounters the following failure categories. For each, the audit must trace: (a) how it's detected, (b) how it's corrected, (c) whether the correction persists, (d) whether future sprints benefit.

| Failure Mode | Detection Mechanism | Current Correction | Persists? | Future Benefit? | To Investigate |
|-------------|--------------------|--------------------|-----------|-----------------|----------------|
| Schema validation error | evidence-declaration.schema.json | Fix YAML in current sprint | NO | NO | Can schema be auto-extended from observed patterns? |
| LLM grading false positive | Manual rework review | Advisory rework item | NO | NO | Can grader context be updated with corrections? |
| Import path collision | Python import error | sys.path fix | PARTIAL | PARTIAL (MEMORY.md) | Can a validator detect this before sprint starts? |
| API signature mismatch | Test failure | Fix call site | NO | PARTIAL (MEMORY.md) | Can API contracts be machine-validated? |
| Governance false trigger | no_wrong_stream on valid items | Reorder evidence | NO | NO | Can false triggers update validator thresholds? |
| Continuation state stuck | iteration >= max | Governed rollover | YES | YES | Working correctly — verify |
| Prompt quality failure | prompt_quality_gate | stop_reason_adjudicator | YES | PARTIAL | Does adjudicator learn from prior decisions? |
| Missing evidence artifacts | Validator rejection | Add missing files | NO | NO | Can obligation matrix prevent this? |
| Taskcard field omission | Schema validation | Fix YAML | NO | NO | Can taskcard templates be auto-generated from schema? |
| Test count regression | anti_skip_checker | Alert (no block) | YES | YES | Should this block, not just alert? |

### Learning Channel Inventory (To Be Verified)

| Channel | Mechanism | Durability | Scope | Consumed By | To Investigate |
|---------|-----------|-----------|-------|------------|----------------|
| Auto-memory (MEMORY.md) | Write tool | Survives context close | Per-project | Conversation context load | Does it reach 200-line limit? Is it pruned? Stale entries? |
| Prompt code changes | Edit to .py files | Permanent (git) | Global | Every future sprint | How often does generate_next_worker_prompt.py actually change? |
| Validator code changes | Edit to .py files | Permanent (git) | Global | Every validation run | How many validators were added from observed failures? |
| Schema changes | Edit to .json files | Permanent (git) | Global | Every declaration | How many schema fields were added from observed errors? |
| Skill file updates | Edit to .md files | Permanent (git) | Per-skill invocation | Workers using that skill | Are skills ever auto-updated? |
| Rework items | continuation-signal.json | Single sprint | Current sprint | Next sprint only | Lost after consumption |
| Grader system prompt | Constructed per call | Per-call | Single grading | One grading call | Reconstructed from scratch each time |
| Session resume | session-resume.md | Survives context close | Per-session | Next session start | How much learning survives here? |
| Repair loop policy | repair-loop-policy.md (planned) | Permanent (git) | Global | Repair agent | Does not exist yet |
| Failure memory | (does not exist) | N/A | N/A | N/A | CRITICAL GAP — must design |

### Healing Loop Model (To Be Verified and Completed)

The audit must trace each step of the healing loop and identify where learning is lost:

```
STEP 1: FAILURE OCCURS during sprint execution
  ├── Detected by: test runner / validator / grading / anti-skip
  └── To verify: Are all failure types detected, or do some pass silently?

STEP 2: FAILURE CLASSIFIED
  ├── By: grade_declared_work.py (ACCEPTED/REWORK/OVERCLAIMED/REJECTED)
  ├── By: governance_validators.py (PASS/WARN/FAIL per check)
  ├── By: stop_reason_adjudicator.py (agent-repairable / external-blocker / terminal)
  └── To verify: Is there a unified failure taxonomy, or 3 separate classification systems?

STEP 3: CORRECTION APPLIED
  ├── In current sprint: fix code, fix declaration, reorder evidence
  ├── In repair loop: rework item consumed, re-executed
  └── To verify: Is the correction applied to ROOT CAUSE or SYMPTOM?

STEP 4: CORRECTION PROPAGATED (THE GAP)
  ├── To auto-memory: sometimes (depends on MEMORY.md rules)
  ├── To prompt code: rarely (requires code edit, not just prompt text)
  ├── To validator code: very rarely (requires new detector)
  ├── To skill files: never automatically
  ├── To schema files: never automatically
  ├── To taskcard templates: never automatically
  └── To verify: What % of corrections reach durable storage?

STEP 5: CORRECTION VERIFIED DURABLE
  ├── Survives context window close: only if in git or auto-memory
  ├── Consumed by future sprint: only if in code path or loaded context
  └── To verify: Can we prove a correction from sprint N prevents the same failure in sprint N+5?
```

### Learning Propagation Design (Required Output)

The audit must produce a concrete design for making learning durable. At minimum:

1. **Failure Memory Store** — persistent JSON/YAML file recording:
   - Failure category (from taxonomy)
   - Root cause classification
   - Correction applied
   - Files modified
   - Verification command
   - Sprint where discovered
   - Sprint where last verified still working

2. **Skill Auto-Evolution** — mechanism for:
   - Detecting repeated patterns (same failure 3+ times)
   - Generating skill file updates from patterns
   - Routing updates through governance review (not arbitrary edits)
   - Versioning skill files with changelog

3. **Validator Auto-Extension** — mechanism for:
   - Proposing new validators from observed failure patterns
   - Adding detectors to anti_skip_checker.py from failure memory
   - Adding governance checks from repeated schema errors

4. **Prompt Evolution Feedback Loop** — mechanism for:
   - Feeding grading results back into prompt generation
   - Updating mega-train template from observed overclaim patterns
   - Injecting "lessons learned" sections into worker prompts from failure memory

5. **Schema Migration Pipeline** — mechanism for:
   - Tracking schema versions
   - Generating migration scripts when schemas change
   - Ensuring all existing artifacts conform to new schema

### Acceptance Criteria for Lane 15

1. All 26 investigation questions answered with `file:line` evidence
2. Failure mode analysis table complete (all 10+ failure modes traced through detection → correction → persistence → future benefit)
3. Learning channel inventory verified (all channels assessed for durability and scope)
4. Healing loop model has no unresolved "???" gaps
5. Learning propagation matrix shows no "NO" entries without a concrete wiring plan
6. Failure memory schema designed and documented
7. Skill auto-evolution mechanism designed (even if implementation deferred to execution phase)
8. At least 3 concrete examples showing where past failures WOULD have been prevented by the designed learning loop
9. Validator auto-extension mechanism designed
10. No remaining "prompt-only" healing claims without specific persistence gap identification

---

## 20B. AUTONOMOUS SUPERVISION FORENSIC DEEP DIVE AND RECTIFICATION PLAN

### Mission

Determine whether autonomous supervision is a real hard-gated execution-control layer or a partially wired / advisory-only layer. This must be proven through repo research, not assumed.

### Forensic Research Findings (From Codebase Audit)

The following findings are based on file:line evidence from `autonomous_cycle.py` (1047 LOC), `supervisor_loop.py`, `generate_next_worker_prompt.py` (1700+ LOC), `autonomous_task_generator.py` (1633 LOC), `grade_declared_work.py` (625 LOC), `overclaim_detector.py` (400 LOC), and 12+ supporting files.

#### Verified Hard Gates (Enforced by Code)

| Gate | File:Line | Exit Code | Enforcement Type | Bypass Possible? |
|------|-----------|-----------|-----------------|-----------------|
| Declaration validation | autonomous_cycle.py:209-216 | Exit 1 | Blocks cycle immediately | NO |
| Overclaimed items present | autonomous_cycle.py:85-86, 831-832 | Exit 3 | classify_continuation_state → NO_UNSAFE_SOURCE_STATE | NO |
| Anti-skip critical block | autonomous_cycle.py:502-505 | Exit 3 | Sets critical_rework_count | NO |
| Requirements authority FAIL | autonomous_cycle.py:306-310, 373 | Exit 3 | _ra_failure_blocks → critical_rework_count | NO |
| Route decision PRESENCE (V11) | governance_validators.py V11, docs line 63-68 | Exit 3 if blocks_sprint=True | Current-run PRODUCT_SOURCE items need route_decision_id | NO |
| Route decision CONTENT (dispatch) | next_action_runner.py:89-116 | Action BLOCKED | Fail-closed at dispatch; ImportError also blocks | NO (except manual/skill bypass) |

#### Verified Advisory-Only Controls (NOT Enforced by Code)

| Control | Mechanism | Evidence | Can Worker Ignore? |
|---------|-----------|---------|-------------------|
| Lane assignment | Prompt text in generate_next_worker_prompt.py | No lane enforcement code in autonomous_cycle.py; grep "lane" finds only advisory data structures | YES |
| DAG ordering | Prompt text; line 339 of generate_next_worker_prompt.py: "Prerequisite: {gap.get('prerequisite', 'none')}" | No DAG validation code in autonomous_cycle.py; no wave/prerequisite enforcement | YES |
| File ownership per lane | No code exists | grep "file_ownership\|allowed_path\|forbidden_path" finds only queue-item-v2 schema fields, not enforcement | YES |
| Rework items | Advisory in continuation-signal.json | rework_items in signal; YES_WITH_REWORK allows safe lane continuation | YES (safe lanes can skip) |
| Next-sprint prompt content | generate_next_worker_prompt.py output | Worker can override prompt instructions based on own code analysis | YES |
| Governance WARN verdicts | governance_validators.py WARN results | WARN doesn't set blocks_sprint; doesn't increase critical_rework_count | YES |

#### Verified Gaps (NOT Wired)

| Gap ID | Description | File:Line Evidence | Severity |
|--------|-------------|-------------------|----------|
| SUP-GAP-001 | Lane ownership not enforced by code — only prompt text | autonomous_cycle.py: no "lane" enforcement; generate_next_worker_prompt.py: no path restrictions injected | BLOCKER |
| SUP-GAP-002 | DAG ordering not enforced by code — only prompt text | autonomous_cycle.py: no wave/prerequisite check; no dependency validation | BLOCKER |
| SUP-GAP-003 | Overclaim detector (10 patterns, Pattern #5 implemented) is NEVER CALLED by autonomous_cycle or grade_declared_work | overclaim_detector.py:228-253 implemented; not imported by autonomous_cycle.py or grade_declared_work.py | HIGH |
| SUP-GAP-004 | grade_declared_work.py defaults to {"adequate": True} with confidence 0.0 when no evidence found | grade_declared_work.py:143-144, 151 | HIGH |
| SUP-GAP-005 | grade_declared_work.py overrides LLM "inadequate" verdict if confidence < 0.80 → forces "adequate" | grade_declared_work.py:223-225 | HIGH |
| SUP-GAP-006 | semantic_verify_item() reads only first 300 lines of test files; large files truncated | grade_declared_work.py:166-168 | HIGH |
| SUP-GAP-007 | No circuit breaker for zero-task / no-progress loops in autonomous_task_generator.py | autonomous_task_generator.py: no stall detection code found | HIGH |
| SUP-GAP-008 | _EXPANSION_GOALS is frozen hardcoded list (lines 29-1372, ~100+ entries); never regenerated from capability data | autonomous_task_generator.py:29 | HIGH |
| SUP-GAP-009 | Gap-ledger is read (line 1374, 1401-1460) but returns [] if file missing; capability map NOT read at all | autonomous_task_generator.py:1374, 1410-1420 | MEDIUM |
| SUP-GAP-010 | Manual/skill execution bypasses dispatch-time route enforcement (Layer 2) | docs/governance/autonomy-default-routing-policy.md:77-80 | MEDIUM |
| SUP-GAP-011 | continuation-signal.json is advisory; no code prevents worker from ignoring it | autonomous_cycle.py:755-862 writes; no read-enforcement in supervisor_loop.py | MEDIUM |
| SUP-GAP-012 | Governance blocks_sprint=True downgrades verdict to REWORK but may not always trigger exit 3 | autonomous_cycle.py:417-424 — verdict downgrade, not direct critical_rework_count increment | MEDIUM |
| SUP-GAP-013 | product_source_executor.py has _HARD_FORBIDDEN paths (line 39-46) but this is pre-flight only, not post-execution validation | product_source_executor.py:39-46 | MEDIUM |
| SUP-GAP-014 | Stale queue repair is disabled by default (dry_run=True, enabled=False) | autonomous_cycle.py:198 | LOW |

### Required Research Method for Lane 14 Execution

The agent executing Lane 14 MUST follow this exact research method for each component. No component may be marked "audited" without completing all steps:

1. **Read entire file** — not first 100 lines, not summary
2. **Document entry points** — CLI, function calls, imports
3. **Document inputs** — what files/state it reads, with paths
4. **Document outputs** — what files/state it writes, with paths
5. **Document downstream consumers** — who reads its output? Prove with grep.
6. **Document exit codes** — every sys.exit() and return code
7. **Document hard gates** — code that BLOCKS execution (not just warns)
8. **Document advisory warnings** — code that WARNS but allows continuation
9. **Document bypass paths** — how a worker could ignore this component
10. **Document tests** — existing test files for this component
11. **Document prior run evidence** — examples of this component being invoked in real sprints
12. **Produce call-graph fragment** — entry → validators → state writes → verdict

### Required Commands (Exact)

The agent MUST run these commands (or equivalent) and include raw output in evidence:

```bash
grep -rn "autonomous_cycle" tools/ .supervisor/ reports/ --include="*.py" --include="*.yaml" --include="*.md" | head -100
grep -rn "continuation.signal\|continuation-signal" tools/ .supervisor/ .local/ --include="*.py" --include="*.json" | head -50
grep -rn "generate_next_worker_prompt" tools/ .supervisor/ reports/ --include="*.py" --include="*.yaml" | head -50
grep -rn "OVERCLAIMED\|REWORK_REQUIRED\|exit.3\|exit.1\|exit.9" tools/supervisor/ --include="*.py" | head -50
grep -rn "lane\|allowed_path\|forbidden_path\|file_ownership" tools/supervisor/ .supervisor/ schemas/ --include="*.py" --include="*.yaml" --include="*.json" | head -100
grep -rn "wave\|prerequisite\|depends_on\|dag\|dependency_order" tools/supervisor/ .supervisor/ --include="*.py" --include="*.yaml" | head -50
grep -rn "overclaim_detector\|detect_all\|OverclaimReport" tools/supervisor/ --include="*.py" | head -30
grep -rn "circuit.breaker\|stall\|no.progress\|zero.task\|empty.queue" tools/supervisor/ --include="*.py" | head -30
```

### Required Outputs for Section 20B

#### 1. `autonomous-supervision-call-graph.md`

Must show the actual validated call flow:

```
Worker runs sprint
  → Worker writes evidence-declaration.yaml
  → Worker calls: python tools/supervisor/autonomous_cycle.py --declaration <path>
    → STEP 0: stale_queue_repair (DISABLED, dry_run=True) [autonomous_cycle.py:197-204]
    → STEP 1: validate_declaration() [autonomous_cycle.py:209] → EXIT 1 if invalid
    → STEP 2: inspect_declaration() [autonomous_cycle.py:226]
    → STEP 2b: evidence_manifest_validation [autonomous_cycle.py:232-248]
    → STEP 2c: materialize_declared_evidence [autonomous_cycle.py:250-257]
    → STEP 2d: adoption_compliance_validation [autonomous_cycle.py:259-275]
    → STEP 2d2: requirements_authority_validation [autonomous_cycle.py:277-321] → EXIT 3 if FAIL
    → STEP 2e: governance_validators (10 validators) [autonomous_cycle.py:323-347]
      → V11: route_decision_required → blocks_sprint=True if missing
    → ENFORCEMENT BOUNDARY NOTE [autonomous_cycle.py:349-354]
    → STEP 3: grade_all() via grade_declared_work.py [autonomous_cycle.py:356-386]
      → semantic_verify_item(): reads 300 lines max, fallback={"adequate":True}
      → OVERCLAIMED if claimed complete + no evidence
      → REWORK_REQUIRED if paths missing or tests failed
    → STEP 3b: anti_skip_checks (17 detectors) [autonomous_cycle.py:435-515]
      → Critical block → EXIT 3 [autonomous_cycle.py:502-505]
    → STEP 4: generate_next_worker_prompt [autonomous_cycle.py:517-524]
    → STEP 5: manifest + review outputs [autonomous_cycle.py:525-620]
    → STEP 8: classify_continuation_state() [autonomous_cycle.py:750-899]
      → Writes continuation-signal.json (ADVISORY)
      → 17+ states: YES, YES_WITH_REWORK, NO_UNSAFE_SOURCE_STATE, NO_MAX_ITERATIONS, etc.
  → Exit code: 0 (continue) or 3 (critical rework) or 1 (invalid) or 9 (error)
```

**NOT CALLED ANYWHERE IN THIS FLOW:**
- overclaim_detector.py (10 patterns implemented, never invoked)
- lane ownership validation (does not exist)
- DAG ordering validation (does not exist)
- file ownership enforcement (does not exist)
- Wave ordering enforcement (does not exist)

#### 2. `autonomous-supervision-state-machine.yaml`

Must define all 17+ continuation states with transitions:

```yaml
states:
  YES:
    condition: "auto_continue_value truthy, no overclaimed, no hard stops, no anti-skip critical"
    producer: "classify_continuation_state() at autonomous_cycle.py:125-132"
    consumer: "Worker reads continuation-signal.json"
    hard_gate: false  # advisory signal
    next_action: "Worker proceeds to next sprint"
  YES_WITH_REWORK:
    condition: "auto_continue_value == 'true_with_rework', rework items exist, no overclaimed"
    producer: "classify_continuation_state() at autonomous_cycle.py:122-123"
    consumer: "Worker reads rework_items from signal"
    hard_gate: false  # advisory signal
    next_action: "Worker addresses rework items first, then new work"
  YES_WITH_LIMITATIONS:
    condition: "Low-severity anti-skip violations only"
    producer: "classify_continuation_state() at autonomous_cycle.py:127"
    consumer: "Worker reads limitations"
    hard_gate: false
    next_action: "Worker proceeds with caution"
  NO_UNSAFE_SOURCE_STATE:
    condition: "overclaimed list is non-empty"
    producer: "classify_continuation_state() at autonomous_cycle.py:85-86"
    consumer: "Worker MUST stop"
    hard_gate: true  # exit 3
    next_action: "Worker must fix overclaimed items"
  NO_MAX_ITERATIONS:
    condition: "iteration >= max_iterations"
    producer: "classify_continuation_state() at autonomous_cycle.py:96-97"
    consumer: "Worker MUST stop"
    hard_gate: true  # unless governed rollover
    next_action: "Worker presents summary to user"
  NO_BROKEN_BASELINE:
    condition: "non-iteration hard stops exist"
    producer: "classify_continuation_state() at autonomous_cycle.py:120"
    consumer: "Worker MUST stop"
    hard_gate: true
    next_action: "Worker addresses hard stops"
  NO_EXTERNAL_GATE:
    condition: "default — no positive continuation signal"
    producer: "classify_continuation_state() at autonomous_cycle.py:134"
    consumer: "Worker MUST stop"
    hard_gate: true
    next_action: "Worker reports termination reason"
  # ... additional states: NO_GENERIC_NEXT_PROMPT, NO_PROMPT_QUALITY_FAILURE, etc.
```

#### 3. `autonomous-supervision-enforcement-proof.md`

| Enforcement Point | Expected Behavior | Actual Behavior (with file:line) | Wired? | Gap ID |
|-------------------|-------------------|--------------------------------|--------|--------|
| Lane ownership | Worker can only modify lane-owned files | No code validates file paths against lane assignment | NOT WIRED | SUP-GAP-001 |
| File ownership | Worker blocked from writing outside allowed paths | product_source_executor.py:39-46 has _HARD_FORBIDDEN but pre-flight only; no post-execution validation | PARTIAL | SUP-GAP-013 |
| Dependency DAG | Lane N blocked until Lane N-1 dependencies complete | No DAG validation in autonomous_cycle.py; prerequisites in prompt text only | NOT WIRED | SUP-GAP-002 |
| Wave 3 gate | Product regeneration blocked until system healing passes | No wave concept in autonomous_cycle.py code | NOT WIRED | SUP-GAP-002 |
| Product regeneration block | Lanes 7-13 blocked before Lanes 1-6,14,15 | No wave/lane ordering enforcement exists | NOT WIRED | SUP-GAP-002 |
| Gate 11 approval block | Gate 11 cannot be claimed without Babar Raza | No Gate 11 validator exists in governance_validators.py | NOT WIRED | NEW |
| Evidence declaration schema | Invalid declarations rejected | validate_declaration() at autonomous_cycle.py:209 → EXIT 1 | WIRED | — |
| Anti-skip | Critical violations block continuation | anti_skip_checks at autonomous_cycle.py:502-505 → EXIT 3 | WIRED | — |
| Overclaim | Overclaimed items block continuation | classify_continuation_state at autonomous_cycle.py:85-86 → NO_UNSAFE_SOURCE_STATE | WIRED | — |
| Overclaim detector integration | 10 patterns run during grading | overclaim_detector.py exists with 10 patterns but is NOT called by autonomous_cycle or grade_declared_work | NOT WIRED | SUP-GAP-003 |
| Spec authority | Spec fact refs required for product items | validate_spec_fact_refs.py:266-430; called upstream as requirements authority validation | WIRED | — |
| Spec parity | QName validators run | No spec parity validators exist yet | NOT WIRED | — (Lane 5 scope) |
| Continuation signal | Signal controls next sprint start | continuation-signal.json written at autonomous_cycle.py:755-862; advisory only, no enforcement | ADVISORY ONLY | SUP-GAP-011 |
| Rework generation | Exit 3 produces machine-readable rework | rework_items in continuation-signal.json; advisory list, not machine-executable taskcards | PARTIAL | NEW |

#### 4. `autonomous-supervision-bypass-analysis.md`

| Bypass Scenario | Possible? | Evidence | Severity |
|----------------|-----------|---------|----------|
| Worker ignores supervisor entirely | YES — worker can skip autonomous_cycle call | No enforcement that autonomous_cycle MUST run | HIGH |
| Worker ignores continuation-signal.json | YES — signal is advisory, no read-enforcement | autonomous_cycle.py:755-862 writes only; no consumer enforcement | MEDIUM |
| Worker ignores lane assignment | YES — lane is prompt text, not code | generate_next_worker_prompt.py has no path restrictions | BLOCKER |
| Worker executes Wave 5 before Wave 3 | YES — no wave concept in code | No DAG/wave validation anywhere | BLOCKER |
| Worker changes product source before system healing | YES — no system-healing gate in code | autonomous_cycle.py has no wave/phase concept | BLOCKER |
| Worker claims Gate 11 readiness in text | YES — no Gate 11 validator exists | governance_validators.py has no gate-level check | HIGH |
| Worker declares evidence for missing files | NO — declaration validation checks file existence | autonomous_cycle.py:209 validate_declaration() | — |
| Stale continuation state triggers wrong work | POSSIBLE — no staleness check on signal age | continuation-signal.json has no timestamp validation | MEDIUM |
| Hardcoded task selection overrides capability queues | YES — _EXPANSION_GOALS at autonomous_task_generator.py:29-1372 is primary source | Gap-ledger merged but hardcoded goals dominate | HIGH |
| Manual/skill execution bypasses route enforcement | YES — documented gap in autonomy-default-routing-policy.md:77-80 | MEDIUM |

#### 5. `autonomous-supervision-rectification-backlog.yaml`

```yaml
items:
  - id: SUP-RECT-001
    failure_type: LANE_DRIFT_FAILURE
    severity: BLOCKER
    evidence: "autonomous_cycle.py has no lane enforcement code; grep 'lane' finds only advisory data structures"
    current_behavior: "Lane assignment exists only in prompt text"
    expected_behavior: "autonomous_cycle.py validates that declared changed_files are within lane-allowed paths"
    root_cause: "Lane ownership was designed as prompt guidance, never implemented as code validation"
    required_fix: "Add lane_allowed_paths to declaration schema; add validator in governance_validators.py that checks changed_files against allowed paths"
    target_files: ["tools/supervisor/governance_validators.py", ".supervisor/schemas/evidence-declaration.schema.json"]
    tests_required: ["test worker writing outside lane path triggers FAIL", "test worker writing inside lane path passes"]
    validators_required: ["lane_ownership_validator"]
    taskcard_id: "TC-SUP-LANE-001"
    blocks_product_regeneration: true

  - id: SUP-RECT-002
    failure_type: SUPERVISOR_CONTROL_FAILURE
    severity: BLOCKER
    evidence: "autonomous_cycle.py has no wave/DAG/prerequisite validation; grep 'wave|dependency|dag' finds only advisory structures"
    current_behavior: "DAG ordering exists only in prompt text"
    expected_behavior: "autonomous_cycle.py reads execution-dag.yaml and validates that lane prerequisites are met before accepting declarations"
    root_cause: "Wave/DAG ordering was designed as prompt guidance, never implemented as code validation"
    required_fix: "Add lane_id and required_prerequisites to declaration schema; add validator that checks prerequisites completed"
    target_files: ["tools/supervisor/governance_validators.py", ".supervisor/schemas/evidence-declaration.schema.json", "schemas/governance/execution-dag.schema.json"]
    tests_required: ["test Wave 5 declaration rejected when Wave 3 incomplete", "test Lane 9 declaration rejected when Lane 1 incomplete"]
    validators_required: ["dag_ordering_validator"]
    taskcard_id: "TC-SUP-DAG-001"
    blocks_product_regeneration: true

  - id: SUP-RECT-003
    failure_type: OVERCLAIM_GATE_FAILURE
    severity: HIGH
    evidence: "overclaim_detector.py has 10 patterns (including Pattern #5 at line 228-253) but is NOT imported by autonomous_cycle.py or grade_declared_work.py"
    current_behavior: "Overclaim detector exists but is never called in the grading pipeline"
    expected_behavior: "autonomous_cycle.py calls overclaim_detector.detect_all() after grading; findings with ERROR severity promote to REWORK"
    root_cause: "Overclaim detector was built as standalone tool, never integrated into autonomous cycle"
    required_fix: "Import overclaim_detector in autonomous_cycle.py; call detect_all() after grade_all(); promote ERROR findings to critical_rework_count"
    target_files: ["tools/supervisor/autonomous_cycle.py"]
    tests_required: ["test overclaim ERROR finding triggers exit 3", "test overclaim WARN finding does not block"]
    validators_required: []
    taskcard_id: "TC-SUP-OVERCLAIM-001"
    blocks_product_regeneration: false

  - id: SUP-RECT-004
    failure_type: AUTONOMOUS_CONTINUATION_FAILURE
    severity: HIGH
    evidence: "grade_declared_work.py:143-144 defaults to adequate=True with confidence=0.0 when no evidence found; line 223-225 overrides LLM inadequate if confidence<0.80"
    current_behavior: "Missing evidence defaults to adequate; low-confidence inadequacy overridden to adequate"
    expected_behavior: "Missing evidence should default to inadequate; LLM verdict should not be overridden below 0.80 threshold"
    root_cause: "Permissive defaults to avoid false negatives on evidence verification"
    required_fix: "Change fallback to adequate=False or adequate=None requiring explicit resolution; remove confidence<0.80 override"
    target_files: ["tools/supervisor/grade_declared_work.py"]
    tests_required: ["test missing evidence returns inadequate", "test low-confidence LLM inadequate is not overridden"]
    validators_required: []
    taskcard_id: "TC-SUP-GRADE-001"
    blocks_product_regeneration: false

  - id: SUP-RECT-005
    failure_type: TASK_SELECTION_FAILURE
    severity: HIGH
    evidence: "autonomous_task_generator.py:29-1372 has ~100+ hardcoded _EXPANSION_GOALS; no circuit breaker; no stall detection"
    current_behavior: "Task selection uses frozen hardcoded goals merged with gap-ledger; can produce zero tasks with no detection"
    expected_behavior: "Task selection driven by capability map + gap-ledger; circuit breaker after N zero-task cycles"
    root_cause: "_EXPANSION_GOALS was designed as bootstrap data, never replaced by dynamic generation"
    required_fix: "Add circuit breaker (max 3 zero-task cycles before escalation); deprecate _EXPANSION_GOALS in favor of capability-map-driven selection"
    target_files: ["tools/supervisor/autonomous_task_generator.py"]
    tests_required: ["test zero-task loop triggers escalation after 3 cycles", "test capability-map-driven selection produces tasks", "test hardcoded goals not used for product acquisition"]
    validators_required: ["zero_progress_circuit_breaker"]
    taskcard_id: "TC-SUP-TASK-001"
    blocks_product_regeneration: false

  - id: SUP-RECT-006
    failure_type: AUTONOMOUS_CONTINUATION_FAILURE
    severity: HIGH
    evidence: "grade_declared_work.py:166-168 reads only first 300 lines of test files; large files truncated"
    current_behavior: "Test files >300 lines are truncated; passing tests at end may be missed"
    expected_behavior: "All test results are verified, not just first 300 lines"
    root_cause: "Line cap to limit LLM context usage"
    required_fix: "Search for test results section (pass/fail counts) rather than reading linearly; or read tail of file for pytest summary"
    target_files: ["tools/supervisor/grade_declared_work.py"]
    tests_required: ["test large file (>300 lines) with passing tests at line 400 is verified correctly"]
    validators_required: []
    taskcard_id: "TC-SUP-GRADE-002"
    blocks_product_regeneration: false

  - id: SUP-RECT-007
    failure_type: STATE_STALENESS_FAILURE
    severity: MEDIUM
    evidence: "continuation-signal.json has no timestamp; no staleness check"
    current_behavior: "Signal from prior sprint may be read by new sprint without freshness check"
    expected_behavior: "continuation-signal.json includes timestamp; reader validates signal is from current cycle"
    root_cause: "Signal was designed for single-session use, not cross-session recovery"
    required_fix: "Add written_at timestamp to signal; add validator that rejects signals older than current declaration"
    target_files: ["tools/supervisor/autonomous_cycle.py"]
    tests_required: ["test stale signal (>1 hour old) triggers warning", "test current signal passes"]
    validators_required: []
    taskcard_id: "TC-SUP-STALE-001"
    blocks_product_regeneration: false
```

#### 6. `autonomous-supervision-integration-tests-plan.md`

Required tests (each must be a pytest test with concrete assertions):

| Test ID | Scenario | Expected Result | Target File |
|---------|----------|----------------|-------------|
| SUP-TEST-001 | Worker declares changed_files outside lane-allowed paths | governance_validator returns FAIL, blocks_sprint=True | tests/supervisor/test_lane_ownership_enforcement.py |
| SUP-TEST-002 | Wave 5 declaration submitted when Wave 3 gate incomplete | dag_ordering_validator returns FAIL, blocks_sprint=True | tests/supervisor/test_dag_ordering_enforcement.py |
| SUP-TEST-003 | Product regeneration declaration submitted before system-healing lanes pass | Validator returns FAIL | tests/supervisor/test_system_healing_gate.py |
| SUP-TEST-004 | Evidence declaration references non-existent file path | validate_declaration returns invalid, exit 1 | tests/supervisor/test_declaration_validation.py |
| SUP-TEST-005 | Overclaim detector reports ERROR severity finding | autonomous_cycle integrates finding, exit 3 | tests/supervisor/test_overclaim_integration.py |
| SUP-TEST-006 | Continuation signal is stale (from prior cycle) | Warning or rejection | tests/supervisor/test_continuation_staleness.py |
| SUP-TEST-007 | Zero-task loop repeats 3+ times | Circuit breaker triggers escalation | tests/supervisor/test_zero_progress_breaker.py |
| SUP-TEST-008 | Task generator with fake gap-ledger produces matching tasks | Tasks match gap priorities, not hardcoded goals | tests/supervisor/test_task_selection_from_gaps.py |
| SUP-TEST-009 | Gate 11 claim appears in declaration without Babar approval | Validator rejects | tests/supervisor/test_gate11_approval_required.py |
| SUP-TEST-010 | grade_declared_work with empty evidence_paths | Returns inadequate (not adequate fallback) | tests/supervisor/test_grading_no_fallback.py |

---

## 21B. AUTONOMOUS HEALING AND LEARNING FORENSIC DEEP DIVE AND RECTIFICATION PLAN

### Mission

Determine whether the system performs durable healing and learning, or only local rework. This must be proven through repo research, prior sprint evidence, prompt/skill wiring, state files, and failure records.

### Forensic Research Findings (From Codebase Audit)

The following findings are based on file:line evidence from `ai_learning_loop.py`, `generate_sprint_learning.py`, `rework_orchestrator.py`, `embedding_retrieval.py`, `anti_skip_checker.py` (17 detectors), `governance_validators.py` (10 validators), `stop_reason_adjudicator.py` (21 signal categories), `.supervisor/skill-registry.yaml` (25 skills), and 20+ supporting files.

#### Executive Finding: ZERO Durable Learning

The Format Factory system operates on a **DETERMINISTIC DECISION MODEL, not a LEARNING MODEL.** All decision logic uses static rules. No validator, skill, prompt template, schema, or decision rule evolves from execution evidence.

| Component | File | Learning Capacity | Evidence |
|-----------|------|------------------|---------|
| Skill registry | .supervisor/skill-registry.yaml | ZERO — 25 static skills, never auto-updated | No "healing", "learning", or "failure" in any skill definition |
| Anti-skip checker | tools/supervisor/anti_skip_checker.py | ZERO — 17 detectors with hardcoded patterns | Static marker strings (lines 43-58); no failure memory read |
| Governance validators | tools/supervisor/governance_validators.py | ZERO — 10 validators with frozenset constants | Lines 33-84: immutable sets; no auto-generation |
| Stop reason adjudicator | tools/supervisor/stop_reason_adjudicator.py | ZERO — 21 signal categories, pre-defined | Lines 29-49: class SignalCategory with static enum; lines 77-150: static dict |
| AI learning loop | tools/supervisor/ai_learning_loop.py | ADVISORY ONLY — outputs marked non_authoritative=True | Line 48-49: authority_state="ai_draft", non_authoritative=True |
| Sprint learning generator | tools/supervisor/generate_sprint_learning.py | PROSE ONLY — markdown for human reading | Outputs: agent-learning-notes.md, speed-bottlenecks.md — not machine-consumed |
| Rework orchestrator | tools/supervisor/rework_orchestrator.py | QUEUE STATE ONLY — marks items "done" | Lines 52-56: DefectClass enum has only 4 classes; no source mutations |
| Embedding retrieval | tools/supervisor/embedding_retrieval.py | ADVISORY ONLY — advisory-only retrieval | Line 49: _AUTHORITY_STATE="ai_advisory"; line 53: _MAX_INDEX_DOCS=50 |
| Auto-memory | MEMORY.md | PARTIALLY DURABLE — survives context close, 200-line limit | Currently 1359 lines (truncated); human-maintained; not machine-queryable |
| Project memory | .supervisor/project-memory.md | METADATA ONLY — sprint timestamps and verdicts | ~100 entries; no pattern refs, no defect taxonomy |

#### Verified Learning Channels and Durability

| Channel | Mechanism | Survives Context Close? | Machine-Readable? | Consumed by Future Sprint? | Auto-Updated? |
|---------|-----------|------------------------|-------------------|---------------------------|---------------|
| Auto-memory (MEMORY.md) | Write tool during conversation | YES | NO (prose) | YES (loaded into context) | YES (by agent) |
| Project memory | YAML append-only log | YES (git) | PARTIAL (metadata only) | NO (never read by code) | YES (by autonomous_cycle) |
| Prompt code changes | Edit to .py files | YES (git) | YES (code) | YES (executed) | NO (requires code PR) |
| Validator code changes | Edit to .py files | YES (git) | YES (code) | YES (always run) | NO (requires code PR) |
| Schema changes | Edit to .json files | YES (git) | YES (schema) | YES (loaded at validation) | NO (requires code PR) |
| Skill file updates | Edit to .md files | YES (git) | PARTIAL | CONDITIONAL (must be invoked) | NO (never auto-updated) |
| AI learning loop output | sprint-learnings.jsonl | YES (file) | YES (JSONL) | NO (non_authoritative, never read) | YES (by ai_learning_loop.py) |
| Sprint learning notes | Markdown files | YES (file) | NO (prose) | NO (human-readable only) | YES (by generate_sprint_learning.py) |
| Rework items | continuation-signal.json | SINGLE SPRINT | YES (JSON) | NEXT SPRINT ONLY | YES (by autonomous_cycle) |
| Grader system prompt | Constructed per LLM call | PER-CALL | N/A | NO (reconstructed each time) | N/A |

#### Concrete Failure Recurrence Examples

These are real failures from MEMORY.md that the system CANNOT prevent from recurring:

| Failure | First Occurrence | MEMORY.md Entry? | System-Level Prevention? | Would Recur Without Memory? |
|---------|-----------------|-------------------|-------------------------|---------------------------|
| `evidence_artifacts` requires `type` field | Sprint PAGD | YES (line ~170) | NO — no validator checks this before declaration | YES |
| `from csv import` collides with stdlib | Sprint Probe Coverage | YES (line ~40) | NO — no import collision validator | YES |
| LLM grader false positive (claims function missing) | Sprint PAGD, Sprint Probe | YES (line ~147) | NO — grader context not updated | YES |
| `next_recommended_work` must be list not string | Sprint Probe Coverage | YES (line ~162) | NO — schema validates but error message unclear | YES |
| `worker_self_grade: PASS` not `ACCEPTED` | Sprint Probe Coverage | YES (line ~163) | NO — no pre-submission validator | YES |
| `acceptance_criteria` must be string not list | Sprint OGHPR | YES (line ~195) | NO — YAML parse fails but root cause not prevented | YES |

**Critical insight:** MEMORY.md is the ONLY mechanism preventing failure recurrence, and it works only if: (a) the same Claude instance loads it, (b) the entry is within the 200-line limit, (c) the agent reads it before making the error. With 1359 lines and a 200-line load limit, most entries are already truncated.

### Required Deep Questions (With Answers from Audit)

| # | Question | Answer | Evidence |
|---|----------|--------|---------|
| 1 | When a failure occurs, where is it recorded? | Rework items in continuation-signal.json (single sprint); MEMORY.md (if agent writes); ai_learning_loop output (non_authoritative) | autonomous_cycle.py:755-862 |
| 2 | Who classifies the failure? | grade_declared_work.py (ACCEPTED/REWORK/OVERCLAIMED); stop_reason_adjudicator.py (21 signal types) | grade_declared_work.py:286-438; stop_reason_adjudicator.py:29-49 |
| 3 | Is there a failure taxonomy? | NO — only pre-defined signal categories (21) and defect classes (4) | stop_reason_adjudicator.py:29-49; rework_orchestrator.py:52-56 |
| 4 | Is there a repair taskcard generated? | NO — rework items are JSON entries in continuation-signal.json, not taskcards | autonomous_cycle.py:785-800 |
| 5 | Is the repair taskcard machine-executable? | N/A — no repair taskcards generated | — |
| 6 | Does the system decide whether durable healing is needed? | NO — all repairs are local to current sprint | No decision point for "this should become a permanent rule" |
| 7 | Where are durable lessons stored? | NOWHERE durably machine-readable. MEMORY.md (prose, truncated). ai_learning_loop (non_authoritative) | MEMORY.md:1359 lines truncated at 200 |
| 8 | Are lessons linked to skills or prompts? | NO | skill-registry.yaml has no lesson_refs field |
| 9 | Are prompts regenerated from lessons? | NO — generate_next_worker_prompt.py is static code | generate_next_worker_prompt.py: no lesson/failure imports |
| 10 | Are future worker prompts changed? | NO — prompt template is static | mega-train-template.md: no dynamic learning injection |
| 11 | Are validators updated on repeated failures? | NO — all validators use frozenset constants | governance_validators.py:33-84 |
| 12 | Are taskcard schemas updated on ambiguity? | NO — schema changes require manual code edit | .supervisor/schemas/*.json: no auto-evolution |
| 13 | Are evidence schemas updated on proof gaps? | NO | Same as above |
| 14 | Are skills updated when agents drift? | NO — skill registry is static YAML | skill-registry.yaml: no update mechanism |
| 15 | Is there a regression test for learned rules? | NO — no learned rules exist | — |
| 16 | Is there a replay test for old failures? | NO — no failure replay infrastructure | — |
| 17 | Does continuation state know healing occurred? | NO — continuation-signal has no healing_applied field | continuation-signal.json schema |
| 18 | Does next sprint prioritize durable healing? | NO — task selection uses hardcoded goals or gap-ledger | autonomous_task_generator.py:29-1372 |
| 19 | Is there a stale learning detector? | NO | No code found |
| 20 | Learning-to-skill propagation gate? | NO | No code found |
| 21 | Learning-to-validator propagation gate? | NO | No code found |
| 22 | Learning-to-taskcard propagation gate? | NO | No code found |
| 23 | Learning-to-prompt propagation gate? | NO | No code found |
| 24 | Can system repeat same failure undetected? | YES — no failure deduplication | No failure registry exists |
| 25 | Are learning artifacts machine-readable? | ai_learning_loop: JSONL (non_authoritative); sprint_learning: markdown (prose) | ai_learning_loop.py:48-49 |
| 26 | Does healing loop close with evidence? | NO — no healing loop exists; only local rework | — |

### Failure Taxonomy v2 (Required for Lane 15 Execution)

```yaml
taxonomy_version: "2.0"
categories:
  SPEC_AUTHORITY_FAILURE:
    description: "Spec facts missing, quarantined, or not verified against source"
    detection: "validate_spec_fact_refs.py"
    current_handling: "blocks if FAIL"
    durable_target: "auto-extend fact registry from spec pipeline"

  CAPABILITY_EXTRACTION_FAILURE:
    description: "Capability map incomplete, stale, or not consuming spec facts"
    detection: "capability_verifier.py (4-bucket sync)"
    current_handling: "advisory report"
    durable_target: "promote to blocking validator"

  CAPABILITY_TO_FEATURE_FAILURE:
    description: "Capability exists but no feature/taskcard generated"
    detection: "NONE — no compiler exists yet"
    current_handling: "manual gap identification"
    durable_target: "compiler Phase 5 taskcard generation"

  QNAME_MAPPING_FAILURE:
    description: "Spec QName not mapped to code namespace/class"
    detection: "NONE — no QName validators exist yet"
    current_handling: "manual naming"
    durable_target: "SpecParityQNameValidator (Lane 5)"

  TASKCARD_GENERATION_FAILURE:
    description: "Generated taskcard is ambiguous, missing fields, or not executable by weak agents"
    detection: "NONE — no taskcard quality validator"
    current_handling: "manual review"
    durable_target: "taskcard template validator from schema + prior failure patterns"

  SKILL_WIRING_FAILURE:
    description: "Skill exists but not registered, not invoked, or produces wrong output"
    detection: "NONE — SkillWiringValidator not yet implemented"
    current_handling: "manual skill invocation"
    durable_target: "SkillWiringValidator (Lane 5)"

  SUPERVISOR_CONTROL_FAILURE:
    description: "Supervisor allows unsafe work (lane drift, DAG violation, overclaim)"
    detection: "PARTIAL — overclaim hard gate; lane/DAG not enforced"
    current_handling: "prompt-only enforcement for lane/DAG"
    durable_target: "Lane ownership + DAG validators (Lane 14 rectification)"

  AUTONOMOUS_CONTINUATION_FAILURE:
    description: "Continuation state incorrect, stale, or not respected"
    detection: "classify_continuation_state() in autonomous_cycle.py"
    current_handling: "advisory signal; worker can ignore"
    durable_target: "mandatory signal validation"

  AUTONOMOUS_HEALING_FAILURE:
    description: "Repair applied but not propagated durably; same failure recurs"
    detection: "NONE — no failure deduplication"
    current_handling: "MEMORY.md (prose, truncated at 200 lines)"
    durable_target: "failure-memory.json + propagation gates"

  AUTONOMOUS_LEARNING_FAILURE:
    description: "Lesson identified but not converted to durable rule"
    detection: "NONE — ai_learning_loop outputs are non_authoritative"
    current_handling: "sprint-learnings.jsonl (never consumed)"
    durable_target: "learning-to-rule propagation pipeline"

  PRODUCT_ARCHITECTURE_FAILURE:
    description: "Product code doesn't follow spec hierarchy or has zero classes"
    detection: "NONE — no architecture validator"
    current_handling: "manual review"
    durable_target: "NamespaceTreeValidator + SkeletonProgressValidator (Lane 5)"

  IMPLEMENTATION_DEPTH_FAILURE:
    description: "Product claims depth but has shallow/skeleton implementation"
    detection: "NONE — no depth validator"
    current_handling: "LLM advisory grading"
    durable_target: "validator_implementation_depth_score (Lane 5)"

  TEST_VALIDATION_FAILURE:
    description: "Tests exist but are stubs (assert True, pass) or miss coverage"
    detection: "NONE — no stub test detector"
    current_handling: "LLM grading (300-line cap)"
    durable_target: "validator_no_stub_tests (Lane 5)"

  EVIDENCE_DECLARATION_FAILURE:
    description: "Declaration schema violated, missing fields, or incorrect types"
    detection: "validate_declaration() in autonomous_cycle.py → EXIT 1"
    current_handling: "hard gate (exit 1)"
    durable_target: "already enforced; extend schema for spec_qname fields"

  OVERCLAIM_FAILURE:
    description: "Work declared complete with insufficient evidence"
    detection: "grade_declared_work.py verdict; overclaim_detector.py (NOT INTEGRATED)"
    current_handling: "grading detects some; overclaim detector not called"
    durable_target: "integrate overclaim_detector into autonomous_cycle"

  GATE_CRITERIA_FAILURE:
    description: "Gate criteria not met but gate claimed"
    detection: "NONE — no gate criteria validator"
    current_handling: "manual review"
    durable_target: "SpecParityGateValidator (Lane 5)"

  CI_PACKAGE_FAILURE:
    description: "CI fails, package not buildable, wheel missing"
    detection: "CI pipeline (when run)"
    current_handling: "CI currently Python-only; no .NET CI"
    durable_target: ".NET CI + package validators (Lane 12)"

  AGENT_LANE_DRIFT:
    description: "Agent works on files outside assigned lane"
    detection: "NONE — no lane enforcement"
    current_handling: "prompt-only lane assignment"
    durable_target: "lane_ownership_validator (Lane 14 rectification)"

  STALE_STATE_FAILURE:
    description: "State file (continuation signal, current-run) is stale or contradictory"
    detection: "NONE — no timestamp validation on signals"
    current_handling: "manual inspection"
    durable_target: "timestamp + freshness validation"

  REPEATED_FAILURE_PATTERN:
    description: "Same failure occurs 3+ times without system-level fix"
    detection: "NONE — no failure deduplication"
    current_handling: "MEMORY.md (if within 200-line limit)"
    durable_target: "failure-memory.json with deduplication + escalation"

  PROMPT_ONLY_HEALING_FAILURE:
    description: "Fix applied in prompt text but not in durable machinery"
    detection: "NONE"
    current_handling: "prompt changes work for current session only"
    durable_target: "learning-to-code propagation gate"

  NON_DURABLE_REPAIR_FAILURE:
    description: "Repair fixes symptom but root cause not addressed in persistent store"
    detection: "NONE"
    current_handling: "local sprint fix only"
    durable_target: "repair-to-learning escalation gate"

  LEARNING_PROPAGATION_FAILURE:
    description: "Lesson exists but not propagated to skills/validators/schemas/prompts"
    detection: "NONE"
    current_handling: "MEMORY.md (prose)"
    durable_target: "4-channel propagation pipeline (skill, validator, schema, prompt)"
```

### Healing Loop Model (Verified Against Codebase)

```
STEP 1: FAILURE OCCURS during sprint execution
  ├── Detected by: test runner / validator / grading / anti-skip
  └── VERIFIED: Detection works for schema errors (exit 1), overclaim (exit 3), anti-skip critical (exit 3)
       BUT NOT for: architecture violations, depth failures, lane drift, DAG violations

STEP 2: FAILURE CLASSIFIED
  ├── By: grade_declared_work.py → ACCEPTED/REWORK/OVERCLAIMED (3 grades)
  │   [grade_declared_work.py:286-438]
  ├── By: governance_validators.py → PASS/WARN/FAIL per validator (3 levels)
  │   [governance_validators.py:162]
  ├── By: stop_reason_adjudicator.py → 8 decision types from 21 signal categories
  │   [stop_reason_adjudicator.py:56-70]
  └── GAP: Three separate classification systems with NO unified taxonomy.
       No failure_type field in any output. No severity-to-action mapping.

STEP 3: CORRECTION APPLIED
  ├── In current sprint: fix code, fix declaration, reorder evidence
  ├── In repair loop: rework_items consumed by next sprint (single use)
  │   [continuation-signal.json rework_items array]
  └── GAP: Correction is ALWAYS symptom-level. No mechanism asks
       "should this become a permanent rule?"

STEP 4: CORRECTION PROPAGATED — THE CRITICAL GAP
  ├── To auto-memory: SOMETIMES (agent must explicitly write; 200-line limit)
  ├── To prompt code: NEVER automatically (requires manual code edit)
  ├── To validator code: NEVER automatically (requires manual code edit)
  ├── To skill files: NEVER automatically (static YAML)
  ├── To schema files: NEVER automatically (requires manual edit)
  ├── To taskcard templates: NEVER automatically (no template system)
  └── CONCLUSION: 0% automatic propagation. 100% manual.

STEP 5: CORRECTION VERIFIED DURABLE — DOES NOT EXIST
  ├── No regression test generated for any correction
  ├── No replay of prior failure to verify fix works
  ├── No failure deduplication to detect recurrence
  └── CONCLUSION: Durability verification does not exist.
```

### Learning Propagation Proof Matrix

| Failure Type | First Fix Location | Survives Context Close? | Consumed by Future Sprint? | Propagated to Validator? | Propagated to Skill? | Propagated to Prompt? | Propagated to Schema? | Regression Test? |
|-------------|-------------------|------------------------|---------------------------|------------------------|---------------------|----------------------|---------------------|-----------------|
| Schema validation error | Fix YAML in sprint | NO | NO | NO | NO | NO | NO | NO |
| LLM grading false positive | Rework item (advisory) | NO | NEXT SPRINT ONLY | NO | NO | NO | NO | NO |
| Import path collision | sys.path fix in test | PARTIAL (MEMORY.md) | PARTIAL (if loaded) | NO | NO | NO | NO | NO |
| API signature mismatch | Fix call site | PARTIAL (MEMORY.md) | PARTIAL (if loaded) | NO | NO | NO | NO | NO |
| Governance false trigger | Reorder evidence | NO | NO | NO | NO | NO | NO | NO |
| Missing evidence type field | Add type to YAML | PARTIAL (MEMORY.md) | PARTIAL (if loaded) | NO | NO | NO | NO | NO |
| acceptance_criteria list→string | Fix YAML | PARTIAL (MEMORY.md) | PARTIAL (if loaded) | NO | NO | NO | NO | NO |

**Every cell should eventually be YES. Currently almost all are NO.**

### Healing/Learning Rectification Backlog

```yaml
items:
  - id: HEAL-RECT-001
    failure_type: AUTONOMOUS_HEALING_FAILURE
    severity: BLOCKER
    evidence: "No failure-memory.json or equivalent exists anywhere in repo; grep 'failure.memory|failure-memory' returns 0 results in tools/"
    current_behavior: "Failures recorded only in MEMORY.md (prose, 200-line limit) or rework_items (single sprint)"
    expected_behavior: "Machine-readable failure-memory.json with category, root_cause, correction, propagation_status"
    root_cause: "No failure persistence infrastructure was ever built"
    required_fix: "Create tools/supervisor/failure_memory.py with read/write/query functions; create .local/supervisor/failure-memory.json"
    target_files: ["tools/supervisor/failure_memory.py", ".local/supervisor/failure-memory.json"]
    tests_required: ["test failure recorded to memory", "test duplicate failure detected", "test failure count incremented", "test escalation at count>=3"]
    validators_required: ["failure_memory_validator"]
    taskcard_id: "TC-HEAL-MEMORY-001"
    blocks_product_regeneration: true

  - id: HEAL-RECT-002
    failure_type: LEARNING_PROPAGATION_FAILURE
    severity: BLOCKER
    evidence: "ai_learning_loop.py outputs non_authoritative=True (line 49); sprint-learnings.jsonl never consumed by any validator or decision maker"
    current_behavior: "Learnings are written but never read by the system"
    expected_behavior: "Learnings with 3+ occurrences auto-promote to durable rule proposals"
    root_cause: "Learning loop was designed as logging, not as a feedback mechanism"
    required_fix: "Add learning_consumer.py that reads sprint-learnings.jsonl, deduplicates, and proposes validator/skill/schema updates"
    target_files: ["tools/supervisor/learning_consumer.py"]
    tests_required: ["test repeated learning produces rule proposal", "test proposal includes target file and implementation sketch"]
    validators_required: []
    taskcard_id: "TC-HEAL-PROPAGATE-001"
    blocks_product_regeneration: true

  - id: HEAL-RECT-003
    failure_type: REPEATED_FAILURE_PATTERN
    severity: HIGH
    evidence: "MEMORY.md has 1359 lines but 200-line load limit; most failure entries truncated and never seen"
    current_behavior: "Auto-memory is the primary learning mechanism but is overloaded and truncated"
    expected_behavior: "Failure patterns extracted to machine-readable store; MEMORY.md kept under 200 lines as index"
    root_cause: "All sprint-specific context dumped into MEMORY.md without topic separation"
    required_fix: "Create topic-specific memory files (debugging.md, api-quirks.md, schema-patterns.md); restructure MEMORY.md as 200-line index"
    target_files: ["C:\\Users\\prora\\.claude\\projects\\c--Users-prora-OneDrive-Documents-GitHub-format-factory\\memory\\MEMORY.md"]
    tests_required: []
    validators_required: []
    taskcard_id: "TC-HEAL-MEMORY-002"
    blocks_product_regeneration: false

  - id: HEAL-RECT-004
    failure_type: AUTONOMOUS_LEARNING_FAILURE
    severity: HIGH
    evidence: "stop_reason_adjudicator.py:29-49 has 21 signal categories; governance_validators.py:33-84 has frozenset constants; anti_skip_checker.py:43-58 has static markers — all static, none evolve"
    current_behavior: "All decision rules are hardcoded; no rule evolves from observed failures"
    expected_behavior: "After 3+ occurrences of same failure pattern, system proposes new validator detector or governance rule"
    root_cause: "System was designed as deterministic execution engine, not adaptive system"
    required_fix: "Add failure_pattern_to_rule_proposer.py that queries failure-memory.json and produces machine-readable rule proposals"
    target_files: ["tools/supervisor/failure_pattern_to_rule_proposer.py"]
    tests_required: ["test 3 same-category failures produce rule proposal", "test proposal includes code sketch and target validator"]
    validators_required: []
    taskcard_id: "TC-HEAL-RULES-001"
    blocks_product_regeneration: false

  - id: HEAL-RECT-005
    failure_type: NON_DURABLE_REPAIR_FAILURE
    severity: HIGH
    evidence: "rework_items in continuation-signal.json are consumed once and lost; no persistence beyond single sprint"
    current_behavior: "Rework items exist for one sprint cycle only"
    expected_behavior: "Unresolved rework items persist across sprints; resolved rework items archived with resolution evidence"
    root_cause: "continuation-signal.json is overwritten each cycle"
    required_fix: "Add rework_archive.jsonl (append-only); archive resolved rework; carry forward unresolved"
    target_files: ["tools/supervisor/autonomous_cycle.py", ".local/supervisor/rework_archive.jsonl"]
    tests_required: ["test unresolved rework carried forward", "test resolved rework archived with evidence"]
    validators_required: []
    taskcard_id: "TC-HEAL-REWORK-001"
    blocks_product_regeneration: false

  - id: HEAL-RECT-006
    failure_type: PROMPT_ONLY_HEALING_FAILURE
    severity: HIGH
    evidence: "generate_next_worker_prompt.py has no lesson/failure imports; mega-train-template.md has no dynamic learning injection"
    current_behavior: "Worker prompts are static templates; no lessons injected from failure memory"
    expected_behavior: "generate_next_worker_prompt.py reads failure-memory.json and injects relevant warnings for current format/lane"
    root_cause: "Prompt generation was designed as template expansion, not adaptive generation"
    required_fix: "Add failure_memory_advisory_injection() function to generate_next_worker_prompt.py"
    target_files: ["tools/supervisor/generate_next_worker_prompt.py"]
    tests_required: ["test prompt includes failure advisory when relevant failures exist", "test prompt excludes irrelevant failures"]
    validators_required: []
    taskcard_id: "TC-HEAL-PROMPT-001"
    blocks_product_regeneration: false
```

### Healing/Learning Integration Tests Plan

| Test ID | Scenario | Expected Result | Target File |
|---------|----------|----------------|-------------|
| HEAL-TEST-001 | Failure occurs; check failure-memory.json updated | New entry with category, root_cause, timestamp | tests/supervisor/test_failure_memory.py |
| HEAL-TEST-002 | Same failure occurs 3rd time | failure_count >= 3; escalation flag set | tests/supervisor/test_failure_deduplication.py |
| HEAL-TEST-003 | Repeated failure triggers rule proposal | Proposal contains target_file, code_sketch, validation_command | tests/supervisor/test_rule_proposal.py |
| HEAL-TEST-004 | Worker prompt generated with relevant failure memory | Prompt includes failure advisory section | tests/supervisor/test_prompt_failure_injection.py |
| HEAL-TEST-005 | Unresolved rework item carries forward across cycles | rework_archive.jsonl contains unresolved item | tests/supervisor/test_rework_persistence.py |
| HEAL-TEST-006 | Resolved rework archived with evidence | rework_archive.jsonl entry has resolution_evidence | tests/supervisor/test_rework_archive.py |
| HEAL-TEST-007 | Learning loop: failure → classify → repair → propagate → verify | End-to-end pipeline produces validator proposal | tests/supervisor/test_learning_loop_e2e.py |
| HEAL-TEST-008 | Stale learning entry detected (>30 days, never re-verified) | Stale flag set; re-verification scheduled | tests/supervisor/test_stale_learning.py |
| HEAL-TEST-009 | Sprint-learnings.jsonl consumed by learning_consumer | Entries deduplicated; high-count patterns flagged | tests/supervisor/test_learning_consumer.py |
| HEAL-TEST-010 | No product work selected while blocker healing remains unresolved | Task generator skips product work if BLOCKER healing items exist | tests/supervisor/test_healing_priority.py |

---

## 22. PLAN GAP REVIEW

### Gap Analysis Table

| # | Area | Covered? | Problem | Evidence from Plan | Required Fix | Additive? |
|---|------|----------|---------|-------------------|-------------|-----------|
| 1 | System healing before product regen | YES | Wave ordering enforced by prompt only, not code | Section 11: "System healing lanes MUST pass" — no code enforcement | Add DAG validator (SUP-RECT-002) | YES |
| 2 | No information loss | PARTIAL | Prior plan had 31 artifacts, grew to 49, now 75+ — no tracking mechanism | Section headings enumerate artifacts but no diff tracking | Add plan-preservation-diff.md, dropped-content-ledger.yaml | YES |
| 3 | Spec-literal QName hierarchy | YES | Well-defined in Sections 7A, 9, 10 | QName rules, ontology, validators designed | No fix needed — execution pending | — |
| 4 | Skills and prompt wiring | YES | 5 new skills designed; 67+ wiring points identified | Section 9 skill definitions | No fix needed — execution pending | — |
| 5 | Taskcard schema extension | YES | spec_parity_fields designed | Section 9 schema extension | No fix needed — execution pending | — |
| 6 | Evidence schema extension | YES | spec_qname_refs etc. designed | Section 9 schema extension | No fix needed — execution pending | — |
| 7 | Validator and Gate 11 hardening | YES | 8 spec-parity + 5 depth validators designed; C1-C20, P1-P11 | Sections 10, 13 | No fix needed — execution pending | — |
| 8 | SAL pipeline healing | YES | 17 dead tools identified; master runner designed | Section 2, Lane 1 | No fix needed — execution pending | — |
| 9 | Capability layer healing | YES | Disconnection chain documented; reintegration planned | Section 3, Lane 2 | No fix needed — execution pending | — |
| 10 | Capability-to-feature compiler | YES | 9-phase compiler designed | Section 6, Lane 3 | No fix needed — execution pending | — |
| 11 | QName-to-code ontology | YES | 9 ontology artifacts designed | Section 7A, Lane 6 | No fix needed — execution pending | — |
| 12 | .NET canonical namespace regen | YES | Target structures defined; migration tables complete | Section 8A, Lane 7 | No fix needed — execution pending | — |
| 13 | Python reduced spec-literal migration | YES | Staged migration; parity matrix; compatibility wrappers | Section 8, Lane 8 | No fix needed — execution pending | — |
| 14 | ZST strategy | YES | Python-only FOSS; DEC-ZST-NET-TRACK | Section 11 Lane 11 | No fix needed | — |
| 15 | CI/package/evidence hardening | YES | .NET CI + wheel build + coverage audit | Lane 12 | No fix needed — execution pending | — |
| 16 | Post-regeneration recompute | YES | Full artifact regeneration | Lane 13 | No fix needed — execution pending | — |
| 17 | Autonomous supervision | SHALLOW→DEEP | Was 26 questions + tables; now has file:line evidence, call graph, state machine, enforcement proof, bypass analysis, rectification backlog | Sections 20, 20B | HEALED by Section 20B | YES |
| 18 | Autonomous healing/learning | SHALLOW→DEEP | Was 26 questions + conceptual tables; now has verified findings, failure taxonomy, healing loop model, learning propagation proof | Sections 21, 21B | HEALED by Section 21B | YES |
| 19 | Swarm readiness | PARTIAL | Swarm roles defined but no lane enforcement in code | FINAL PLAN HEALING SPRINT section | Swarm cannot enforce lanes without SUP-RECT-001/002 | YES |
| 20 | Weak-agent executability | PARTIAL | Taskcards not yet generated; acceptance criteria per-lane exist | Lane definitions | Rectification taskcards now defined in 20B/21B | YES |

### Specific Gaps Found and Fixed

| Gap | Status | Fix Applied |
|-----|--------|-------------|
| Lane 14/15 declarative not evidence-forcing | FIXED | Section 20B/21B add exact research method, required commands, file:line findings |
| Wave 1 may wire before autonomy audits | FIXED | Wave 1A (autonomy research) before Wave 1B (governance wiring) — see Part E below |
| System-healing gate accepts "implementable" | FIXED | New gate requires implemented_and_tested or patch_ready_with_exact_files — see Gap 3 fix below |
| Lane 7/8 skeleton contradiction | FIXED | Skeleton/stub reclassified as architecture_only — see Gap 1 fix below |
| "Validators pass against current codebase" ambiguity | FIXED | Separated: validator self-tests pass; validator runs; current product fails correctly — see Gap 2 fix below |
| Arbitrary fact counts | FIXED | Replaced with concept inventory completeness — see Gap 4 fix below |
| No raw audit logs / grep traces required | FIXED | Section 20B requires exact grep commands and raw output in evidence |
| No prior failure evidence required | FIXED | Section 21B failure recurrence table uses real MEMORY.md failures |
| No prompt before/after comparison | FIXED | HEAL-TEST-004 requires prompt comparison |
| No durable learning propagation proof | FIXED | Learning propagation proof matrix in Section 21B |
| No task selection test against queue | FIXED | SUP-TEST-008 seeds fake gap-ledger |
| No lane/file-lock violation tests | FIXED | SUP-TEST-001 tests lane violation |
| No product-regeneration block tests | FIXED | SUP-TEST-002, SUP-TEST-003 |
| No overclaim blocking tests | FIXED | SUP-TEST-005 |
| No repeated no-progress loop detection | FIXED | SUP-TEST-007 + SUP-RECT-005 circuit breaker |
| No replay tests from prior failures | FIXED | HEAL-TEST-007 e2e learning loop |

---

## 23. PLAN GAP FIXES

### Gap 1 Fix — Skeleton/Stub Contradiction

**Problem:** Plan says skeleton-only files don't count as progress, but Lanes 7-8 ask to generate skeletons and use build/import success as gate.

**Fix:** All skeleton/stub generation in Lanes 7-8 is reclassified:
- Skeleton files MUST be marked `architecture_only: true` in evidence declarations
- `dotnet build` success on skeletons counts as ARCHITECTURE GATE, not PRODUCT PROGRESS
- Product rebuild lanes (9, 10) must replace skeleton gates with BEHAVIOR GATES:
  - Class has at least 1 public method with implementation (not `throw NotImplementedException`)
  - Class has at least 3 tests exercising real behavior
  - Class has spec_qname mapping
- Anti-fake-progress rule 1 amended: "Skeleton-only source files do NOT count as product progress; they are architecture_only scaffolding."

### Gap 2 Fix — Validator Acceptance Ambiguity

**Problem:** "Validators pass against current codebase" incentivizes weak validators.

**Fix:** System-healing Lane 5 iteration gate amended to require:
1. **Validator self-tests pass** — validator code itself is tested with positive and negative cases
2. **Validator runs successfully** — no crashes, no unhandled exceptions
3. **Current product validation produces EXPECTED failures** — validators correctly identify known gaps
4. **Failures recorded as known gaps** in `validator-known-gaps.yaml`
5. **Gate 11 remains blocked** — validators finding failures does NOT mean Gate 11 passes

### Gap 3 Fix — Weak System-Healing Gate

**Problem:** System-healing gate says "validators implementable" — can pass with plans instead of actual wiring.

**Fix:** Each system-healing lane must achieve one of:
- `implemented_and_tested` — code exists, tests pass, validators run
- `patch_ready_with_exact_files_and_tests` — exact patch (diff), target files, and tests are specified; implementation deferred to execution phase with explicit taskcard
- `blocked_external_with_evidence` — blocked by external dependency with classification

Only `implemented_and_tested` unlocks product regeneration. `patch_ready` items must be individually classified as `blocks_product_regeneration: true/false` with evidence.

### Gap 4 Fix — Arbitrary Fact Counts

**Problem:** Plan mentions "FODS 50+ facts, FODT 40+ facts" as targets.

**Fix:** Lane 1 iteration gate amended:
- Replace "50+ facts" with "product-scope concept inventory complete"
- Top-level and second-level in-scope concepts covered
- Every excluded concept has explicit exclusion reason
- Fact count reported as METRIC, not ACCEPTANCE GATE
- Acceptance gate is: "no in-scope concept without a verified fact or explicit exclusion"

### Gap 5 Fix — Autonomous Task Selection Not Proven

**Fix:** Lane 2 iteration gate amended to require:
- Proof run: seed test gap-ledger with 5 fake gaps of varying priority
- Run autonomous_task_generator.py against test ledger
- Verify output taskcards match gap priorities (P0 before P1)
- Verify hardcoded _EXPANSION_GOALS are NOT used for product acquisition when gap-ledger is available
- Verify zero-task output triggers circuit breaker (SUP-RECT-005)

### Gap 6 Fix — No Durable "Agent Stays on Lane"

**Fix:** Added to Lane 14 rectification backlog as SUP-RECT-001 (BLOCKER). Lane enforcement tests added as SUP-TEST-001.

### Gap 7 Fix — No Plan Preservation Mechanism

**Fix:** New required artifacts:
- `plan-preservation-diff.md` — diff between prior plan version and current
- `section-to-requirement-map.csv` — every section → REQ-* IDs
- `requirement-to-taskcard-map.csv` — every REQ-* → TC-* IDs
- `dropped-or-merged-content-ledger.yaml` — any dropped content with reason and owner
- Hard fail: any source section with no mapped requirement/taskcard/deferred reason

### Gap 8 Fix — Product Acquisition Readiness Gate

**Fix:** New gate added. Before product acquisition for any NEW format (beyond FODS/FODT/ZST), the system must prove:
1. SAL pipeline can process a new format end-to-end
2. Capability compiler can generate concept/capability/feature/taskcards for a new format
3. QName mapper can generate namespace/class plan (if applicable to format family)
4. Autonomous supervisor can schedule lanes (once lane enforcement exists)
5. Healing/learning can record and propagate failures for the new format
6. No manual hardcoded format exceptions required in _EXPANSION_GOALS

### Gap 9 Fix — Artifact Count Normalization

Artifact count updated from 49 to 75 (see Section 24 below).

---

## 24. UPDATED ARTIFACT REGISTRY (75 Artifacts)

All under `.local/evidences/<run_id>/`:

### Original Diagnostic Artifacts (1-13)
1-13: (unchanged from Section 16)

### System Healing Artifacts (14-34)
14-34: (unchanged from Section 16)

### Autonomous Supervision Audit Artifacts (35-41)
35-41: (unchanged from Section 16)

### Autonomous Healing/Learning Audit Artifacts (42-49)
42-49: (unchanged from Section 16, with 49 = `healing-learning-validator-design.md`)

### Deep-Dive Addendum Artifacts (50-75) — NEW
50. `plan-gap-review.md`
51. `no-information-loss-audit-v2.md`
52. `plan-preservation-diff.md`
53. `section-to-requirement-map.csv`
54. `requirement-to-taskcard-map.csv`
55. `dropped-or-merged-content-ledger.yaml`
56. `autonomy-layer-deep-dive-addendum.md`
57. `autonomous-supervision-call-graph.md`
58. `autonomous-supervision-state-machine.yaml`
59. `autonomous-supervision-enforcement-proof.md`
60. `autonomous-supervision-bypass-analysis.md`
61. `autonomous-supervision-rectification-backlog.yaml`
62. `autonomous-supervision-integration-tests-plan.md`
63. `taskcards/lane-14-autonomous-supervision-hardening/*.yaml`
64. `autonomous-healing-learning-call-graph.md`
65. `failure-taxonomy-v2.yaml`
66. `healing-learning-state-machine.yaml`
67. `learning-propagation-proof-matrix.md`
68. `healing-learning-bypass-analysis.md`
69. `healing-learning-rectification-backlog.yaml`
70. `healing-learning-integration-tests-plan.md`
71. `taskcards/lane-15-autonomous-healing-learning-hardening/*.yaml`
72. `product-acquisition-readiness-gate.md`
73. `updated-execution-dag-v2.yaml`
74. `updated-swarm-lane-registry-v2.yaml`
75. `updated-ready-to-execute-swarm-prompt-v2.md`

---

## 25. UPDATED LANE STRUCTURE AND WAVE ORDERING

### Sublane Expansion

Lanes 0-13 unchanged. Lanes 14-15 expanded into sublanes:

```
Lane 14A — Autonomous Supervision Research Audit (file:line evidence, call graph, state machine)
Lane 14B — Autonomous Supervision Rectification Backlog (gap classification, severity, patches)
Lane 14C — Autonomous Supervision Integration Tests (10+ test scenarios)
Lane 14D — Autonomous Supervision Hardening Taskcards (per-rectification-item taskcards)

Lane 15A — Autonomous Healing/Learning Research Audit (file:line evidence, failure taxonomy)
Lane 15B — Failure Taxonomy and Learning State Machine (23+ failure categories, state transitions)
Lane 15C — Learning Propagation and Durable Rule Update Plan (4-channel propagation design)
Lane 15D — Autonomous Healing/Learning Integration Tests (10+ test scenarios)
Lane 15E — Healing/Learning Rectification Taskcards (per-rectification-item taskcards)
```

### Updated Wave Structure

```
Wave 0:   Intake, preservation, normalization (no source mutation)

Wave 1A:  Autonomy/Supervision/Healing RESEARCH (Lane 14A, Lane 15A)
          - Must complete BEFORE governance wiring uses autonomy findings
          - Outputs: call graphs, state machines, enforcement proofs, bypass analyses, failure taxonomy

Wave 1B:  Governance wiring WITH autonomy findings (Lanes 1, 4, 5, 14B-14D, 15B-15E)
          - Lane 4/5 consume Lane 14A/15A findings to wire correct enforcement
          - Lane 14B-14D produce rectification taskcards for supervision gaps
          - Lane 15B-15E produce rectification taskcards for healing/learning gaps

Wave 2:   Capability and compiler integration (Lanes 2, 3, 6; depends on Wave 1B contracts)

Wave 3:   System-healing gate check — HARDENED REQUIREMENTS:
          - Autonomy call graphs complete (Lane 14A)
          - Supervision enforcement proof complete (Lane 14A)
          - Healing/learning call graph complete (Lane 15A)
          - Learning propagation proof complete (Lane 15C)
          - Rectification backlogs exist (Lane 14B, 15B)
          - BLOCKER rectification items created as taskcards (Lane 14D, 15E)
          - No BLOCKER item remains without patch_ready_with_exact_files or implemented_and_tested
          - Each healing lane status is implemented_and_tested OR patch_ready OR blocked_external
          - Only implemented_and_tested lanes unlock product regeneration
          - Product acquisition readiness gate met (Gap 8 fix)

Wave 4:   Architecture/regeneration planning (Lanes 7, 8, 11)
          - Skeletons marked architecture_only (Gap 1 fix)
          - No product progress claims

Wave 5:   Product rebuild execution (Lanes 9, 10, 11; only after Wave 3 passes)
          - Behavior gates replace skeleton gates (Gap 1 fix)
          - Lane ownership enforced if SUP-RECT-001 implemented

Wave 6:   CI, package, evidence hardening (Lane 12)

Wave 7:   Post-regeneration recompute and closeout (Lane 13)
```

---

## 26. UPDATED NO-INFORMATION-LOSS REQUIREMENTS

The `no-information-loss-audit-v2.md` must prove:

1. No original plan section (1-19) was dropped
2. No system healing section (20, 21) was dropped
3. No deep-dive section (20B, 21B, 22-26) was dropped
4. No previous healing prompt requirement was dropped
5. No Lane (0-15) was removed
6. No sublane (14A-14D, 15A-15E) was removed
7. No artifact from the 75-artifact list was dropped
8. No Gate 11 criterion (C1-C20, P1-P11) was removed
9. No anti-fake-progress rule (1-10) was weakened
10. No constraint from Section 19 was removed
11. Any merged content is traceable via section-to-requirement-map.csv
12. Any deferred content has reason, owner, and taskcard reference
13. Any contradiction has a repair taskcard in rectification backlogs
14. Product regeneration remains blocked until Wave 3 gate passes
15. Gate 11 remains blocked; Babar Raza is the only approver
16. Rectification backlogs (SUP-RECT-*, HEAL-RECT-*) all have severity and taskcard IDs

---

## 27. PLAN COMPOSITION, COHERENCE, AND SPEC-LITERAL NORMALIZATION (Prompt 7 Healing)

### Purpose

This section resolves the **canonical naming contradiction** found throughout the plan: format-prefixed names (`FodsCell`, `FodtList`, `FodsTypedValue`) were used as primary implementation targets in Sections 7, 8, 9, 10, contradicting the spec-literal hierarchy rules defined in Sections 7A, 8A, 9, 10. This normalization sprint makes naming consistent everywhere.

### Canonical Naming Rule (BINDING — applies to all sections)

```
RULE: Spec QName → Canonical Class Name → Format-Prefixed Name is Facade ONLY

Examples:
  table:table-cell  → Canonical: Table.TableCell  → Facade: FodsCell (Compat/ only)
  text:list          → Canonical: Text.List         → Facade: FodtList (Compat/ only)
  office:value-type  → Canonical: Table.TypedValue  → Facade: FodsTypedValue (Compat/ only)
  style:style        → Canonical: Style.Style       → Facade: FodsStyle (Compat/ only)
  table:formula      → Canonical: Table.Formula     → Facade: FodsFormula (Compat/ only)
  text:span          → Canonical: Text.Span         → Facade: FodtTextSpan (Compat/ only)
  text:h             → Canonical: Text.Heading      → Facade: FodtHeading (Compat/ only)
  text:footnote      → Canonical: Text.Footnote     → Facade: FodtFootnote (Compat/ only)
  text:section       → Canonical: Text.Section      → Facade: FodtSection (Compat/ only)
  draw:frame         → Canonical: Draw.Frame        → Facade: FodtFrame (Compat/ only)

NEVER use format-prefixed names as the PRIMARY implementation target.
ALWAYS implement the canonical spec-literal class FIRST.
THEN create the facade wrapper in Compat/ that delegates to the canonical class.
```

### Terminology Normalization

| Term | Correct Usage | Incorrect Usage |
|------|--------------|-----------------|
| Canonical class | `Table.TableCell`, `Text.List` — spec-derived, lives in namespace folder | `FodsCell`, `FodtList` used as implementation target |
| Facade/Legacy wrapper | `FodsCell` in `Compat/` — delegates to canonical class | `FodsCell` as the primary class to implement |
| Spec QName | `table:table-cell` — the ODF qualified name | `table-cell` without prefix |
| Namespace folder | `Table/`, `Text/`, `Office/`, `Style/`, `Draw/` | Flat `Model/` folder for all classes |
| Implementation target | What agents MUST create first | Should never be a facade name |

### Canonical vs Legacy Name Audit Results

**Violations found and corrected in this healing sprint:**

| Section | Line(s) | Old (Violated) | Corrected To | Classification |
|---------|---------|----------------|-------------|---------------|
| S7 FODS Classes to ADD | 595 | `FodsTypedValue` as New Class | `Table.TypedValue` (canonical) + `FodsTypedValue` (facade) | CORRECTED |
| S7 FODS Classes to ADD | 596 | `FodsFormula` as New Class | `Table.Formula` (canonical) + `FodsFormula` (facade) | CORRECTED |
| S7 FODS Classes to ADD | 597 | `FodsStyle` as New Class | `Style.Style` (canonical) + `FodsStyle` (facade) | CORRECTED |
| S7 FODS Classes to ADD | 598 | `FodsColumnDefinition` as New Class | `Table.TableColumn` (canonical) + `FodsColumnDefinition` (facade) | CORRECTED |
| S7 FODS Classes to ADD | 599 | `FodsMergedCellRange` as New Class | `Table.CoveredTableCell` (canonical) + `FodsMergedCellRange` (facade) | CORRECTED |
| S7 FODS Classes to ADD | 600 | `FodsDataValidation` as New Class | `Validation.ContentValidation` (canonical) + `FodsDataValidation` (facade) | CORRECTED |
| S7 FODT Classes to ADD | 606-615 | All `Fodt*` as New Class | Canonical spec-literal names + facade aliases | CORRECTED |
| S8 Parity Matrix | 813-826 | `FodsWorkbook`, `FodsTypedValue`, `FodsFormula` as python_class | Canonical `Workbook`, `TypedValue`, `Formula` + facade aliases | CORRECTED |
| Lane 9 .NET expansion | 1311-1315 | `FodsTypedValue`, `FodsFormula`, `FodsStyle`, `FodsMergedCellRange` | Spec QName → canonical class targets | CORRECTED |
| Lane 9 Python migration | 1318-1319 | `FodsWorkbook/FodsSheet/FodsRow/FodsCell` | Spec QName → canonical class targets | CORRECTED |
| Lane 10 .NET expansion | 1332-1337 | `FodtList`, `FodtTable`, `FodtTextSpan`, `FodtHeading`, etc. | Spec QName → canonical class targets | CORRECTED |
| Lane 10 Python migration | 1340 | `FodtDocument/FodtParagraph/FodtList/FodtTable` | Spec QName → canonical class targets | CORRECTED |

**Section 7 current inventory table (lines 579-589):** NOT a violation — these document EXISTING classes, not new targets. Existing classes become facades during migration; documenting them accurately is correct.

**Section 8A (lines 831-890):** ALREADY CORRECT — uses canonical namespace structure with Compat/ folder. This is the model all other sections must follow.

### Contradiction Ledger

| ID | Contradiction | Sections | Resolution |
|----|-------------|----------|-----------|
| CONTRA-001 | S7 says "add FodsTypedValue" as new class; S7A/S8A say canonical is `Table.TypedValue` | S7 vs S7A/S8A | S7 rewritten: canonical is `Table.TypedValue`; `FodsTypedValue` is facade in Compat/ |
| CONTRA-002 | S7 puts new classes in `Model/Fods*.cs`; S8A puts them in `Table/*.cs`, `Style/*.cs` | S7 vs S8A | S7 rewritten: target files follow S8A canonical structure |
| CONTRA-003 | S8 parity matrix uses `FodsWorkbook` as python_class; S8 post-spec-literal structure uses `fods.office.document` | S8 vs S8 | Parity matrix rewritten: canonical python_class is `office.document.Document`; `FodsWorkbook` is compat alias |
| CONTRA-004 | Lane 9 says "P1: FodsTypedValue hierarchy + FodsCell refactor"; Lane 6 says QName map drives all naming | Lane 9 vs Lane 6 | Lane 9 rewritten with spec QName → canonical class targets |
| CONTRA-005 | Lane 10 says "P1: FodtList + FodtListItem"; Lane 6 says QName map drives all naming | Lane 10 vs Lane 6 | Lane 10 rewritten with spec QName → canonical class targets |

### Plan Coherence Summary

The plan accumulated across 7 prompts:
- **Prompt 1-3:** Diagnostic sections (S1-S8) written before spec-literal hierarchy was conceived → used format-prefixed names as targets
- **Prompt 4:** Added S7A, S8A, S9, S10 with correct spec-literal canonical naming
- **Prompt 5-6:** Added execution infrastructure (lanes, waves, artifacts, autonomy audits) — naming-neutral
- **Prompt 7 (this section):** Resolved contradictions between pre-spec-literal sections (S7, S8, Lanes 9-10) and post-spec-literal sections (S7A, S8A)

After this healing, ALL sections agree: **canonical classes are spec-literal; format-prefixed names are facades only.**

### Updated Artifact Registry (75 → 95)

Artifacts 76-95 (all under `.local/evidences/<run_id>/`):

76. `evidence-declaration.yaml` (composition sprint)
77. `current-plan-preservation-ledger.md`
78. `plan-composition-gap-review.md`
79. `terminology-and-naming-normalization-report.md`
80. `canonical-vs-legacy-name-audit.csv`
81. `contradiction-ledger.yaml`
82. `section-recomposition-map.csv`
83. `information-preservation-map.csv`
84. `dropped-merged-deferred-ledger.yaml`
85. `composed-executable-master-plan.md`
86. `human-readable-execution-flow.md`
87. `canonical-spec-literal-architecture-section.md`
88. `normalized-lane-registry.yaml`
89. `normalized-wave-plan.yaml`
90. `normalized-artifact-registry.yaml`
91. `normalized-taskcard-index.yaml`
92. `requirements-to-normalized-plan-traceability.csv`
93. `legacy-facade-migration-policy.md`
94. `plan-coherence-validator-design.md`
95. `updated-ready-to-execute-swarm-prompt-v3.md`

### Plan Coherence Validator Design

A validator that ensures plan internal consistency:

**Check 1: No format-prefixed canonical targets** — scan all "Classes to ADD", Lane expansion items, and parity matrix entries; FAIL if any format-prefixed name appears as the primary implementation target (not in Compat/ or facade column).

**Check 2: Section cross-references consistent** — every canonical class mentioned in Lanes 9-10 must appear in S7A QName-to-code map and S8A canonical structure.

**Check 3: Artifact count matches registry** — total artifact count in all sections matches the artifact registry.

**Check 4: Lane dependencies match wave structure** — every lane's prerequisites match its wave assignment.

**Check 5: No orphan contradictions** — every entry in the contradiction ledger has a resolution status.

**Check 6: Terminology consistent** — "canonical class" never refers to a format-prefixed name; "facade" never appears without a canonical class it delegates to.

### Legacy Facade Migration Policy

1. **Facades are NOT deprecated** — they remain as the public API for backward compatibility
2. **Facades MUST delegate** — every facade method calls the canonical class method; no independent logic
3. **Facades live in Compat/** — never in the canonical namespace folders
4. **New code uses canonical imports** — `using FormatFactory.Fods.Table;` not `using FormatFactory.Fods.Compat;`
5. **Tests reference canonical classes** — new tests import from canonical namespaces; existing tests may reference facades
6. **Documentation references canonical** — API docs, architecture docs, taskcards reference canonical names
7. **Evidence declarations reference canonical** — `spec_qname_refs` and `canonical_classes_added` use canonical names

---

# Section 28 — Stage 0: Capability Fact-to-Feature Truth Reconstruction

## Status: REQUIRED HARD DEPENDENCY before Capability Healing (Lanes 2-3, 6)

> Added: 2026-06-16 forensic audit `cap-fact-to-feature-forensics-20260616`.
> Full forensic report: `.local/evidences/cap-fact-to-feature-forensics-20260616/forensic-report.md`
> Surgical enhancement detail: `.local/evidences/cap-fact-to-feature-forensics-20260616/surgical-plan-enhancement.md`
> All prior sections (1-27) preserved unchanged. This section adds new findings and taskcards only.

---

## 28.1 — Stale Plan Assumption Corrections

### CORRECTED: Gap Ledger Not Consumed (was HIGH risk)
**Repository truth:** `autonomous_task_generator.py` lines 1564-1568 make gap-ledger the PRIMARY source; `_EXPANSION_GOALS` is fallback.
**Revised risk:** MEDIUM — gap-ledger IS consumed. However, compiled taskcards (output of `capability_queue_consumer.py`) are NOT fed to sprint selection. This is the actual remaining defect.

### CORRECTED: No capability_map_generator.py (was HIGH risk)
**Repository truth:** `tools/capability_layer/capability_map_generator.py` exists and is functional.
**Revised risk:** MEDIUM for SAL-derivation deficiency only.

### CORRECTED: No capability_compiler.py (was implied missing)
**Repository truth:** `tools/supervisor/capability_compiler.py` exists with SAL fact loading and feature IR compilation.
**Remaining gap:** Wiring between compiler output and autonomous loop — not compiler existence.

### CONFIRMED: Proof graph dormant (HIGH)
GraphStore + CoverageEvaluator + MainstreamGapQueueGenerator exist in `tools/requirements_authority/` but NO production JSONL files are populated. The 6 fixture packs are test-only. This is the largest structural gap remaining.

### CONFIRMED: Capability derivation is POC-driven, not SAL-driven (HIGH)
`capability_map_generator.py` derives capabilities from `poc-targets.yaml` field names. SAL facts are post-hoc enrichment metadata. No spec fact causes a new capability to be generated.

### NEW: Compiled taskcards not consumed (HIGH)
`capability_queue_consumer.py` → `capability_compiler.py` pipeline writes taskcard JSON to `.local/capability-consumer/taskcards/`. `autonomous_task_generator.py` does NOT read this path. The compiler pipeline is validated in isolation but drives no autonomous work.

### NEW: Capability closure loop absent (HIGH)
After implementation + verification, no component updates `gap-ledger.json`. Gaps remain `open` indefinitely and can be re-selected by task generation.

---

## 28.2 — Reclassified Findings

**Confirmed root causes:**
1. poc-targets.yaml used as capability derivation source (not SAL facts)
2. Compiled taskcard output path not registered as autonomous loop input
3. GraphStore not populated from production capability data
4. No closure event emitted after capability verification

**Contributing defects:**
1. SAL facts are hand-authored (external gate for live download)
2. Action queue (action-queue.json) has 1 entry and no consumers

**Downstream symptoms (not causes):**
1. Autonomous loop generates tasks from limited set
2. Sprint selection does not improve as features are implemented
3. Capability gap count (696) includes already-implemented entries

---

## 28.3 — Diagnostic Taskcards

### TC-CAP-DIAG-001: Wire Compiled Taskcards into Autonomous Task Selection

**Status:** OPEN | **Priority:** P0 | **Root cause:** compiled taskcards not consumed

Add `_load_compiled_taskcards()` to `autonomous_task_generator.py`. Reads `*.json` files from `.local/capability-consumer/taskcards/`. Compiled taskcards take priority over raw gap-ledger records.

**Acceptance criteria:**
1. Compiled taskcard for any FOSS gap appears in `product-task-candidates.json`
2. Focused-proof script (<80 lines) demonstrates end-to-end selection
3. No regression in existing tests

**Dependency:** TC-CAP-DIAG-002 must complete first (compiled taskcards need `source_fact_refs`).

---

### TC-CAP-DIAG-002: Add SAL-Derived Capability Generation Step

**Status:** OPEN | **Priority:** P1 | **Root cause:** poc-derived capabilities, not spec-derived

Add `_derive_from_sal_facts(sal_facts, format_id) -> list[dict]` to `capability_map_generator.py`. Map SAL qnames to capability categories using minimum taxonomy:

```python
SAL_TO_CAPABILITY_CATEGORY = {
    "ODF-FACT-NAMESPACE": ["parse", "validate"],
    "ODF-FACT-ROOT-ELEMENT": ["parse", "load"],
    "ODF-FACT-BODY": ["parse", "inspect"],
    "ODF-SHEET-FACT-TABLE": ["inspect", "edit", "save"],
    "ODF-SHEET-FACT-ROW": ["inspect", "edit"],
    "ODF-SHEET-FACT-CELL": ["inspect", "edit", "validate"],
    "FODS-FACT-003": ["validate", "roundtrip"],
    "ODF-FACT-STYLES": ["parse", "save"],
    "ODF-FACT-METADATA": ["inspect", "edit"],
}
```

New candidates flagged `derivation_source: "sal_fact"`. poc-targets.yaml status becomes VERIFICATION evidence, not derivation.

**Acceptance criteria:**
1. ≥3 new SAL-derived candidates for FODS with resolvable `source_fact_refs`
2. No existing capabilities removed
3. Before/after gap count comparison logged

---

### TC-CAP-DIAG-003: Populate GraphStore from Production Capability Map

**Status:** OPEN | **Priority:** P1 | **Root cause:** proof graph dormant

Create `tools/capability_layer/capability_map_to_graph.py`. Reads `unified-capability-map.json`, emits JSONL to `.local/proof-graph/nodes.jsonl` and `.local/proof-graph/edges.jsonl`. For each `implementation_verified` capability: 1 CapabilityClaim node + ImplementationArtifact nodes + TestArtifact nodes + edges.

**Acceptance criteria:**
1. ≥20 CapabilityClaim nodes for FODS in output JSONL
2. `mainstream_gap_queue.py` produces non-empty queue from populated graph
3. CoverageEvaluator verdicts differ from simple gap-ledger heuristics for ≥3 capabilities

---

### TC-CAP-DIAG-004: Implement Capability Closure Loop

**Status:** OPEN | **Priority:** P1 | **Root cause:** no closure mechanism

Add `emit_closure_event(gap_id, format_id, function_name)` to `capability_verifier.py`. Events written to `.local/capability-events/closures.jsonl`. `capability_map_generator.py` reads closures at startup and marks matching gaps `status: closed`. `autonomous_task_generator.py` skips closed gaps.

**Acceptance criteria:**
1. Verifier emits closure events for all-green format functions
2. Re-running generator marks those gaps closed
3. Re-running task generator excludes closed gaps from candidates
4. Dependency: TC-CAP-DIAG-001 must be wired before closure has observable effect

---

### TC-CAP-DIAG-005: Validate SAL → Capability Traceability (FODS Slice)

**Status:** OPEN | **Priority:** P2

Create `tools/capability_layer/trace_capability_to_sal.py`. For a given capability_id, resolves `source_fact_refs` → SAL qname → section → authority. Reports broken traces.

**Acceptance criteria:**
1. For 5 SAL-derived FODS capabilities: all traces resolve
2. For 5 poc-derived capabilities: `source_fact_refs: []` (explicit empty)
3. No capability has `source_fact_refs: null`

---

### TC-CAP-DIAG-006: Proof-Level Census for FODS Capabilities

**Status:** OPEN | **Priority:** P2

Extend `select_poc_gaps.py` `detect_target_writer_readiness()` to produce proof-level census. Report distribution: NO_PROOF / IMPLEMENTATION_ONLY / TESTED / DOGFOODED for FODS commercial capabilities.

**Acceptance criteria:**
1. Proof census output for ≥30 FODS commercial capabilities
2. ≥1 capability at TESTED level or higher
3. Discrepancy between poc-targets.yaml PASS count vs TESTED-level count logged

---

## 28.4 — Dependency Order

```
TC-CAP-DIAG-002 → TC-CAP-DIAG-003 → TC-CAP-DIAG-005
                                         ↓
TC-CAP-DIAG-001 → TC-CAP-DIAG-004 → TC-CAP-DIAG-006
```

TC-CAP-DIAG-001 must follow TC-CAP-DIAG-002 (compiled taskcards need `source_fact_refs`).
TC-CAP-DIAG-004 must follow TC-CAP-DIAG-001 (closure needs a working selection loop).

---

## 28.5 — Existing Taskcards Requiring Updates

| Taskcard | Contradicted Premise | Required Update |
|----------|---------------------|-----------------|
| CAP-SEL-001 | gap-ledger not consumed | Replace with TC-CAP-DIAG-001 (compiled taskcard wiring) |
| CAP-GEN-006 | FUL packs as proxy for proof graph | Replace with TC-CAP-DIAG-003 (populate GraphStore directly) |
| CAP-GEN-011 | machine-readable action queue | Deprecate action-queue.json; gap-ledger IS the queue |
| CAP-PROD-005 | poc-targets.yaml update as capability fix | Clarify: poc-targets.yaml is VERIFICATION evidence only after TC-CAP-DIAG-002 |

---

## 28.6 — Stage 0 Completion Gate

Complete when ALL of:
1. ≥3 SAL-derived FODS capabilities with resolvable `source_fact_refs` (TC-CAP-DIAG-002)
2. GraphStore populated with ≥20 FODS CapabilityClaim nodes (TC-CAP-DIAG-003)
3. `mainstream_gap_queue.py` produces non-empty queue (TC-CAP-DIAG-003)
4. ≥1 compiled taskcard appears in `autonomous_task_generator.py` output (TC-CAP-DIAG-001)
5. Closure events emitted and processed for ≥1 implemented format function (TC-CAP-DIAG-004)
6. Proof-level census shows ≥0 capabilities at TESTED level (TC-CAP-DIAG-006)
7. No new test regression

Does NOT require live spec downloads (DEFECT-005 is external gate).
Does NOT require Gate 11 approval.

---

## Section 29 — Source-Realization Forensic Audit Taskcards (TC-SRFA)

**Origin:** `source-realization-forensics-20260625-001` forensic dry run (glimmering-shimmying-hamming plan)
**Authority mode:** SURGICAL ENHANCEMENT — all findings route here as TC-SRFA-### taskcards
**Evidence root:** `.local/evidences/source-realization-forensics-20260625-001/source-realization/`

---

### TC-SRFA-014: Write Architecture Contract Document

**Status:** CLOSED | **Priority:** P2 | **Severity:** MEDIUM
**Finding source:** TC-FORENSIC-012 (architecture contract creation)
**Defect classification:** architecture

**Defect:** No formal architecture contract document exists. The consistent layering pattern
(spec/ → Compat/ → models.py → __init__.py) is observed in all 20 packages but is undocumented.
New format authors have no specification to follow.

**Resolution:** `docs/code-quality/architecture-contract.md` written (2026-06-25).
Also: `docs/python-foss/spec-to-source-chain-contract.md` documenting the spec → source authority chain.

**Acceptance criteria:**
1. `docs/code-quality/architecture-contract.md` exists and covers 10+ architectural conventions
2. `docs/python-foss/spec-to-source-chain-contract.md` maps chain integrity status for all 20 formats
3. New contributors can implement a new format by following these documents alone

**Evidence:** `docs/code-quality/architecture-contract.md`, `docs/python-foss/spec-to-source-chain-contract.md`
**Blocking gate:** None (documentation debt)

---

### TC-SRFA-015: FeatureFactory — Add spec_qname Registry Check Before Insertion

**Status:** OPEN | **Priority:** P2 | **Severity:** MEDIUM
**Finding source:** TC-FORENSIC-002 (source-producing system dry run)
**Defect classification:** architecture

**Defect:** FeatureFactory (`tools/supervisor/product_feature_factory.py`) inserts Python functions
into source files without verifying that the target class has a `spec_qname` entry in
`shared/qname-registry/{format}.yaml`. A function can be inserted for a format not yet in the registry,
breaking the spec-to-source authority chain.

**Root cause:** FeatureFactory Pattern A-F insertion logic has no pre-validation step that checks
registry existence before writing to disk.

**Resolution:**
1. Add `_validate_format_in_registry(format_name)` function to FeatureFactory
2. Before any file write: check `shared/qname-registry/{format}.yaml` exists
3. If missing: raise `FeatureFactoryError(f"Format '{format}' not in qname-registry — add registry entry first")`
4. Add regression test in `tests/supervisor/test_feature_factory_authority.py`

**Acceptance criteria:**
1. FeatureFactory raises FeatureFactoryError for unknown format (no registry entry)
2. FeatureFactory proceeds normally for registered formats
3. Test: 2 negative controls (missing registry), 2 positive controls (registered format)

**Blocking gate:** Lane 5 (capability-to-feature compiler) — compiler must validate authority

---

### TC-SRFA-016: .NET Model Classes Lack spec_qname Runtime Attribute

**Status:** OPEN | **Priority:** P2 | **Severity:** MEDIUM
**Finding source:** TC-FORENSIC-003, TC-FORENSIC-004, TC-FORENSIC-008
**Defect classification:** spec_fidelity

**Defect:** Python format classes have `spec_qname: ClassVar[str]` runtime metadata on every
model class (FodsDocument, FodsSheet, FodsCell, etc.), enabling V53 compliance checking.
.NET model classes (FodsDocument.cs, FodsSheet.cs, FodtParagraph.cs, NetpbmDocument.cs) have
NO equivalent runtime metadata — spec traceability is comment-only (XML documentation comments).

**Root cause:** V53 validator is Python-only. No .NET governance validator enforces runtime metadata.
The .NET classes were authored before the spec_qname convention was established.

**Resolution:**
1. Add `public const string SpecQName = "table:table"` to each .NET model class
2. Add equivalent constants to FODT, Netpbm, ZST model classes
3. Create `tests/net/governance/SpecQNameTests.cs` verifying all model classes have SpecQName constant
4. Update `shared/qname-registry/*.yaml` to reference .NET const path alongside `python_file`

**Acceptance criteria:**
1. All 10 .NET model classes have `SpecQName` constant matching qname-registry entry
2. `SpecQNameTests.cs` verifies SpecQName is non-null and matches format registry
3. Validator (if .NET governance is extended) can check at build time

**Blocking gate:** C15 (.NET spec_qname compliance criterion)

---

### TC-SRFA-017: HTML/TXT/Markdown .NET Projects Are Empty Stubs

**Status:** OPEN | **Priority:** LOW | **Severity:** LOW
**Finding source:** TC-FORENSIC-010 (consolidated audit)
**Defect classification:** packaging

**Defect:** The .NET projects `src/net/html/`, `src/net/txt/`, `src/net/markdown/` exist as
empty placeholder directories. They are referenced in solution files but produce no output.
This inflates the apparent .NET format count.

**Resolution:** Either implement stubs or remove from solution and document as future roadmap.
Recommended: mark as `architecture_only` stubs in `registry/format-registry.yaml` to avoid
misleading the gate readiness calculation.

**Acceptance criteria:**
1. Either: minimal stub with `HtmlDocument.cs` class (not packageable) explicitly marked as architecture_only
2. Or: removed from `format-registry.yaml` with `status: roadmap_only`

**Blocking gate:** None (low priority cleanup)

---

### TC-SRFA-018: Test Templates Produce Placeholder Assertions

**Status:** OPEN | **Priority:** LOW | **Severity:** LOW
**Finding source:** TC-FORENSIC-002 (source-producing system dry run)
**Defect classification:** test_quality

**Defect:** 4 of 5 test driver templates in `tools/supervisor/drivers/python/*.py.tmpl` produce
trivial assertions (`isinstance(result, ...)`, `result is not None`). These pass immediately
without verifying any behavioral correctness. The `summary_test.tmpl` and similar templates
require manual replacement of PLACEHOLDER assertion blocks.

**Root cause:** Templates are designed as starting points but callers do not replace assertions
before committing tests. V36 (`validate_no_stub_tests`) flags these as weak but does not block.

**Resolution:**
1. Upgrade V36 to FAIL (not WARN) when >60% of assertions in a test file are trivial
2. Add `# TODO: REPLACE_THIS_ASSERTION` marker in templates and add it to V36 detection
3. Or: make templates generate realistic assertions using fixture values from the registry

**Acceptance criteria:**
1. V36 FAIL (not WARN) for new test files with >60% trivial assertions
2. All 5 templates have `# TODO: REPLACE_THIS_ASSERTION` markers
3. CI blocks merge if TODO markers remain in test files older than 48 hours

**Blocking gate:** None (quality improvement)

---

### TC-SRFA-019: generate_canonical_stubs.py Not Called by Any Automated System

**Status:** OPEN | **Priority:** P2 | **Severity:** MEDIUM
**Finding source:** TC-FORENSIC-002 (source-producing system dry run)
**Defect classification:** architecture

**Defect:** `tools/spec/generate_canonical_stubs.py` is the only tool that creates spec/
skeleton classes from `shared/qname-registry/*.yaml`. However, it is never called by:
- `autonomous_cycle.py` (sprint loop)
- CI/CD pipeline
- Any monitoring script for registry changes

New registry entries do NOT automatically produce skeleton classes. Engineers must manually
invoke the tool and commit the results.

**Resolution:**
1. Add Step 0a-stubs in `autonomous_cycle.py`: check if any registry entry lacks a matching
   `spec/{concept}/{class}.py` file; if so, run `generate_canonical_stubs.py {format}`
2. Or: add CI job `check-stubs-in-sync.yml` that fails if registry diverges from generated stubs
3. Add regression test verifying all "seeded" registry entries have corresponding spec/ files

**Acceptance criteria:**
1. `autonomous_cycle.py` detects missing stubs and generates them before sprint execution
2. Or: CI check flags registry/stubs divergence in PRs
3. Test: add registry entry for synthetic format → verify stub is generated without manual invocation

**Blocking gate:** Lane 2 (canonical stub generation wiring)

---

### TC-SRFA-020: Netpbm Parser Allocation Bomb Guard Unverified

**Status:** OPEN | **Priority:** HIGH | **Severity:** HIGH
**Finding source:** TC-FORENSIC-005 (pilot 3 — .NET binary codec)
**Defect classification:** security

**Defect:** NetpbmDocument.cs (1914 LOC) loads PBM/PGM/PPM images with `width × height` pixel
arrays. If an attacker supplies a crafted header with `width=65535, height=65535`, this allocates
4 GB of memory before any I/O error is detected. The guard exists but was NOT directly verified
during the forensic review (file read was blocked by tooling limits).

**Root cause:** NetpbmParser.cs was not directly readable in the forensic session due to file
size. The allocation guard existence cannot be confirmed from the model class alone.

**Resolution:**
1. Read `src/net/netpbm/NetpbmParser.cs` to verify width×height overflow guard exists
2. If missing: add `if ((long)width * height > MaxPixelCount) throw new NetpbmSizeException(...)`
3. Add test in `tests/net/netpbm/NetpbmSecurityTests.cs`:
   - Crafted PBM header with `width=65535 height=65535` → expects `NetpbmSizeException`
   - Not a real image — just header bytes sufficient to trigger the guard
4. Verify `MaxPixelCount` constant is ≤ 100,000,000 (100M pixels = 400 MB max at 32-bit RGBA)

**Acceptance criteria:**
1. `NetpbmParser.cs` contains explicit `width * height > MaxPixelCount` guard before array allocation
2. `NetpbmSecurityTests.cs` has at least 1 test with oversized dimensions → `NetpbmSizeException`
3. Test runs in CI and passes

**Blocking gate:** C18 (.NET security — input validation)

---

### TC-SRFA-021: FODS Python QName Coverage at 12/50+ (24%)

**Status:** OPEN | **Priority:** P2 | **Severity:** MEDIUM
**Finding source:** TC-FORENSIC-006 (pilot 4 — Python FODS)
**Defect classification:** spec_fidelity

**Defect:** The FODS format has 50+ distinct ODF QNames for spreadsheet concepts. Only 12 are
mapped in `shared/qname-registry/fods.yaml` (24% coverage). V53 compliance requires facades for
all registered QNames, but the registry itself is incomplete — unmapped QNames have no spec/
class or Compat/ facade.

**Root cause:** Registry was seeded with the most visible QNames (table:table, table:table-cell,
etc.) but not the full ODF spreadsheet vocabulary (table:covered-table-cell, table:table-header-rows,
office:annotation, table:table-column, etc.).

**Resolution:**
1. Enumerate all ODF 1.3 FODS QNames from SAL (`sal-facts-fods.json` 4988 facts)
2. Add the top 25 missing QNames to `shared/qname-registry/fods.yaml`
3. Run `generate_canonical_stubs.py fods` to produce spec/ skeletons
4. Implement Compat/ facades for the new entries

**Acceptance criteria:**
1. `shared/qname-registry/fods.yaml` has ≥ 25 entries (current: 12)
2. V53 passes for all new entries (spec_qname present, ClassVar pattern)
3. No regression in existing FODS tests

**Blocking gate:** P5 (Python spec QName coverage ≥ 80% for Gate 11)

---

### TC-SRFA-024: Python FODS Lacks Mutation API

**Status:** OPEN | **Priority:** HIGH | **Severity:** HIGH
**Finding source:** TC-FORENSIC-008 (pilot 6 — cross-language parity)
**Defect classification:** consumer_readiness

**Defect:** Python FodsDocument is READ-ONLY. Consumers cannot mutate cells, insert rows,
delete rows, or manage sheets. The .NET equivalent has 23+ mutation methods (SetCellValue,
InsertRow, DeleteRows, MergeCells, AddSheet, RemoveSheet, RenameSheet, CopySheet, ClearSheet,
SetCellFormula, SortRows, etc.).

This is the MOST CRITICAL cross-language parity gap for FODS.

**Root cause:** Python FOSS tier was implemented as read-only analytics/inspection platform.
Mutation API was never added to `models.py:FodsDocument`.

**Resolution:**
1. Add mutation methods to `src/python/fods/models.py:FodsDocument`:
   - `set_cell_value(sheet_name, row, col, value)` — minimum viable mutation
   - `insert_row(sheet_name, row_index, values)` — row insertion
   - `delete_rows(sheet_name, start_row, count)` — row deletion
2. Update `write_fods()` to persist mutations
3. Add round-trip mutation test:
   - Load fixture → set_cell_value → write → reload → verify value preserved
4. Add skill-attributed work item with gap_ledger_ref pointing to GAP-FODS-MUTATION-001

**Acceptance criteria:**
1. `FodsDocument.set_cell_value(sheet, row, col, value)` works
2. Mutation round-trip test passes: load → mutate → save → reload → verify
3. `FodsDocument.insert_row(sheet, row_index, values)` works
4. TC-GUARD-001 compliant: gap_ledger_ref present in evidence

**Blocking gate:** P6 (Python FOSS mutation API)

---

### TC-SRFA-025: Python FODS Missing HTML/JSON/Markdown Export

**Status:** OPEN | **Priority:** P2 | **Severity:** MEDIUM
**Finding source:** TC-FORENSIC-008 (pilot 6 — cross-language parity)
**Defect classification:** consumer_readiness

**Defect:** Python FODS has CSV export only (1 format). .NET FODS has 6 export formats
(HTML, JSON, Markdown, CSV, TSV, XML). Python consumers requiring HTML table output, JSON
serialization, or Markdown tables from FODS spreadsheets have no API.

**Resolution:**
1. Add `export_fods_to_html(workbook, sheet=0)` → str
2. Add `export_fods_to_json(workbook, sheet=0)` → str (JSON array of row objects)
3. Add `export_fods_to_markdown(workbook, sheet=0)` → str
4. Route through `src/python/fods/fods_analytics.py` or new `fods_exporters.py`
5. Add tests covering empty sheet, single row, multiple sheets

**Acceptance criteria:**
1. 3 new export functions available via `from fods import export_fods_to_html, ...`
2. HTML output is valid HTML table structure
3. JSON output is parseable `json.loads()` result
4. Markdown output renders in standard Markdown renderers
5. TC-GUARD-001 compliant (gap_ledger_ref)

**Blocking gate:** P7 (Python FOSS export parity)

---

### TC-SRFA-026: parity-matrix.yaml FODS Overclaims COMPLETE

**Status:** OPEN | **Priority:** P2 | **Severity:** MEDIUM
**Finding source:** TC-FORENSIC-008 (pilot 6 — cross-language parity)
**Defect classification:** architecture

**Defect:** `registry/parity-matrix.yaml` states `spec_parity_status: COMPLETE` for FODS.
This claim is accurate for QName registry/facade coverage (12/12 entries, 45/45 V53 tests)
but is INACCURATE for behavioral API parity: Python has NO mutation API vs. .NET's 23 methods;
Python has 1 export format vs. .NET's 6.

**Root cause:** `spec_parity_status` conflates two orthogonal dimensions:
(a) QName registry coverage, and (b) behavioral API parity. These must be tracked separately.

**Resolution:**
Update `registry/parity-matrix.yaml` FODS entry to:
```yaml
fods:
  spec_parity_status: PARTIAL
  spec_qname_registry_coverage: COMPLETE  # 12/12 entries, 45/45 V53 tests
  behavioral_parity: PARTIAL              # .NET full CRUD; Python read+CSV-export only
  parity_notes: ".NET has 23 mutation methods; Python is read-only. .NET has 6 exporters; Python has 1."
  missing_python: [set_cell_value, insert_row, delete_rows, export_to_html, export_to_json, export_to_markdown]
```

**Acceptance criteria:**
1. `parity-matrix.yaml` FODS entry has `spec_qname_registry_coverage` and `behavioral_parity` as separate fields
2. `spec_parity_status: PARTIAL` (not COMPLETE) for FODS
3. Missing Python APIs are enumerated in `missing_python` list

**Blocking gate:** None (accuracy cleanup; blocks overclaim reporting)

---

### TC-SRFA-027: generate_canonical_stubs.py python_file Path Not Validated

**Status:** OPEN | **Priority:** LOW | **Severity:** LOW
**Finding source:** TC-FORENSIC-009 (pilot 7 — negative generation)
**Defect classification:** architecture

**Defect:** When `generate_canonical_stubs.py` processes a valid registry YAML, it creates files
at the `python_file` path specified in the YAML without validating that the path is within the
expected package directory. A malformed or adversarial `python_file: ../../sensitive/path.py`
would create a file outside `src/python/`.

**Root cause:** Entry validation happens at format level (registry YAML must exist) but not at
individual entry level (python_file path within valid scope).

**Resolution:**
1. Add path validation in `generate_canonical_stubs.py` entry processing
2. Assert: `resolved_python_file.is_relative_to(repo_root / 'src' / 'python')`
3. If assertion fails: raise `StubGenerationError(f"python_file path escapes src/python: {python_file}")`

**Acceptance criteria:**
1. Malformed python_file with `../../` path raises `StubGenerationError`
2. Valid python_file within src/python/ proceeds normally
3. Test: 1 negative (escape path), 1 positive (valid path)

**Blocking gate:** None (security hardening)

---

### TC-SRFA-028: V53 Cannot Detect spec_qname as Instance Field vs ClassVar

**Status:** OPEN | **Priority:** P2 | **Severity:** MEDIUM
**Finding source:** TC-FORENSIC-009 (pilot 7 — negative generation)
**Defect classification:** governance

**Defect:** V53 validator (`governance_validators.py`) checks for `spec_qname` presence using
AST parsing. However, it cannot distinguish:
- `spec_qname: ClassVar[str] = "ns:elem"` (correct: class-level attribute, accessible as `Class.spec_qname`)
- `spec_qname: str = "ns:elem"` (incorrect: instance field, NOT accessible as `Class.spec_qname`)

Both produce similar AST nodes. The runtime workaround (`type(NdjsonRecord.__dict__["spec_qname"]) is str`)
works but is only present in specific tests, not in the validator itself.

**Root cause:** AST analysis of `AnnAssign` nodes does not inspect the annotation type for `ClassVar`.

**Resolution:**
1. In V53 `_check_spec_qname_attribute()`, add inspection of `AnnAssign` nodes
2. If annotation is `Name("str")` (not `Subscript(ClassVar, str)`): warn "spec_qname is instance field, use ClassVar[str]"
3. New warning code: `CLASSVAR_PATTERN_MISSING`
4. Add test: class with `spec_qname: str = "x"` → CLASSVAR_PATTERN_MISSING warning

**Acceptance criteria:**
1. V53 emits CLASSVAR_PATTERN_MISSING for `spec_qname: str = "..."` pattern
2. V53 passes for `spec_qname: ClassVar[str] = "..."` pattern
3. Existing 45/45 V53 FODS tests still pass

**Blocking gate:** Governance accuracy (non-blocking but enables better enforcement)

---

### TC-SRFA-029: FeatureFactory Anchor Loss Silent EOF Fallback

**Status:** OPEN | **Priority:** LOW | **Severity:** LOW
**Finding source:** TC-FORENSIC-009 (pilot 7 — negative generation)
**Defect classification:** architecture

**Defect:** `FeatureFactory._find_insertion_point(content, insert_before="target_fn")` silently
returns `len(content)` (end of file) when the anchor function is not found. This causes generated
functions to be appended at EOF with no error, violating the expected insertion order. The
`FeatureFactoryError` class exists but is never raised for this case.

**Root cause:** The fallback to EOF was intentional for "append at end" semantics, but when
a specific `insert_before` anchor is specified, silent EOF fallback produces confusing output.

**Resolution:**
1. In `_find_insertion_point()`, when `insert_before` is specified but anchor is not found:
   raise `FeatureFactoryError(f"Anchor function '{insert_before}' not found in {source_path}")`
2. When `insert_before=None` (no anchor specified): EOF fallback is correct, keep it
3. Add test: invoke FeatureFactory with non-existent anchor → FeatureFactoryError

**Acceptance criteria:**
1. `FeatureFactory` raises `FeatureFactoryError` when specified anchor not found
2. `FeatureFactory` silently appends to EOF when `insert_before=None`
3. Test: negative control (missing anchor) → FeatureFactoryError

**Blocking gate:** None (robustness improvement)

---

## Section 29.1 — TC-SRFA Taskcard Status Summary

| Taskcard | Severity | Status | Blocking Gate |
|----------|----------|--------|---------------|
| TC-SRFA-014 | MEDIUM | **CLOSED** | None |
| TC-SRFA-015 | MEDIUM | OPEN | Lane 5 |
| TC-SRFA-016 | MEDIUM | OPEN | C15 |
| TC-SRFA-017 | LOW | OPEN | None |
| TC-SRFA-018 | LOW | OPEN | None |
| TC-SRFA-019 | MEDIUM | OPEN | Lane 2 |
| TC-SRFA-020 | HIGH | OPEN | C18 |
| TC-SRFA-021 | MEDIUM | OPEN | P5 |
| TC-SRFA-024 | HIGH | OPEN | P6 |
| TC-SRFA-025 | MEDIUM | OPEN | P7 |
| TC-SRFA-026 | MEDIUM | OPEN | None |
| TC-SRFA-027 | LOW | OPEN | None |
| TC-SRFA-028 | MEDIUM | OPEN | None |
| TC-SRFA-029 | LOW | OPEN | None |

**Note on TC-SRFA-001 through TC-SRFA-013:** The forensic audit initially identified that
13/20 Python packages lacked `models.py`. Direct verification at HEAD confirmed this finding
was STALE — all 20 Python packages have `models.py` as of the forensic run date (2026-06-25).
These taskcards are NOT added to this plan. The work was completed in the prior session
(2026-06-24 domain model sprint, GAP-PROD-INV-MODEL-001 CLOSED).

**Note on TC-SRFA-022 and TC-SRFA-023:** These were LOW-severity findings that are resolved by
the existing `models.py` implementations. Not added as separate taskcards.
