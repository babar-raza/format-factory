# Spec-to-Feature Radical Correction Plan — Agent Quick Reference

**Full plan:** `plans/strategic/spec-to-feature-radical-correction-plan.md` (27 sections, ~3200 lines)
**Run ID:** `spec-to-feature-radical-correction-plan-20260612-8e45224`
**Gate 11:** NOT APPROVED. Babar Raza is the only approver.

---

## Executive Summary

The current system has **6 systemic failures** that prevent commercial-grade products:

1. **Specification Authority Layer is ghost infrastructure** — 3 of 20 tools active; 17 are dead code. Facts extracted once (run030), never regenerated.
2. **Capability Layer generates output nobody consumes** — 800+ capability records and 398-gap ledger exist but gap-ledger.json is NEVER read by task generation; action-queue has `advisory_only: true` on ALL items.
3. **No capability-to-feature compiler exists** — Pipeline from spec to capability ENDS at capability map generation with no downstream consumer.
4. **Spec-literal parity not enforced** — 67+ wiring points across 35+ files need spec-literal rules. Without system healing, agents follow naming instructions once then forget.
5. **Autonomous Supervision may be partially wired** — Lane ownership, DAG ordering, file ownership enforcement exist only as prompt text, not code. Overclaim detector (10 patterns) is NEVER CALLED.
6. **Autonomous Healing/Learning is prompt-only** — ZERO durable learning. All decision rules static. No failure memory, no skill auto-evolution, no validator auto-extension.

---

## 16-Lane Remediation Structure

### System Healing Lanes (MUST complete before product work)

| Lane | Purpose | Key Deliverables |
|------|---------|-----------------|
| 0 | Coordinator + supervision | DAG, file locks, lane scheduling |
| 1 | SAL Pipeline Wiring | Master runner chaining 17 dormant tools; concept inventories for FODS/FODT/ZST |
| 2 | Capability Reintegration | Replace hardcoded `_EXPANSION_GOALS` with gap-ledger-driven task selection |
| 3 | Capability-to-Feature Compiler | 9-phase compiler (concept graph → capability graph → feature graph → QName ontology → architecture → taskcards → test obligations → evidence obligations → gate readiness) |
| 4 | Skills + Prompt Wiring | 67+ wiring points; 5 new skills; base prompt updates |
| 5 | Validators + Gate Hardening | 8 spec-parity validators + 5 depth validators + overclaim pattern #5; Gate 11 criteria C1-C20, P1-P11 |
| 6 | QName-to-Code Ontology | 9 ontology artifacts per format (qname-to-code-map, namespace-tree, containment-graph, etc.) |
| 14 | Autonomous Supervision Audit | 26 investigation questions; 14 verified gaps (SUP-GAP-001..014); 7 rectification items |
| 15 | Autonomous Healing/Learning Audit | 26 investigation questions; 23 failure categories; 6 rectification items |

### Product Regeneration Lanes (only after system healing gate)

| Lane | Purpose |
|------|---------|
| 7 | .NET Architecture Blueprint + Spec-Literal Regeneration |
| 8 | Python Blueprint + Spec-Literal Migration |
| 9 | FODS Product Rebuild (target: 20/25 .NET, 18.5/25 Python) |
| 10 | FODT Product Rebuild (target: 20/25 .NET, 18.5/25 Python) |
| 11 | ZST Product Hardening (target: 20/25 Python) |
| 12 | CI, Package, Evidence Hardening |
| 13 | Post-Regeneration Recompute |

---

## Wave Execution Order

```
Wave 0:  Intake, preservation, normalization (no source mutation)
Wave 1A: Autonomy/supervision/healing RESEARCH (Lanes 14A, 15A)
Wave 1B: Governance wiring WITH autonomy findings (Lanes 1, 4, 5, 14B-D, 15B-E)
Wave 2:  Capability + compiler integration (Lanes 2, 3, 6)
Wave 3:  System-healing gate check (BLOCKER for product work)
Wave 4:  Architecture/regeneration planning (Lanes 7, 8, 11)
Wave 5:  Product rebuild execution (Lanes 9, 10, 11)
Wave 6:  CI, package, evidence hardening (Lane 12)
Wave 7:  Post-regeneration recompute + closeout (Lane 13)
```

---

## Canonical Naming Rule (BINDING)

```
Spec QName -> Canonical Class -> Facade (Compat/ only)

Examples:
  table:table-cell  -> Table.TableCell  -> FodsCell (facade)
  text:list          -> Text.List        -> FodtList (facade)
  office:value-type  -> Table.TypedValue -> FodsTypedValue (facade)

NEVER use format-prefixed names as PRIMARY implementation targets.
ALWAYS implement canonical spec-literal class FIRST, then facade wrapper.
```

---

## Key Supervision Gaps (from Lane 14 Audit)

| Gap ID | Description | Severity |
|--------|-------------|----------|
| SUP-GAP-001 | Lane ownership not enforced by code | BLOCKER |
| SUP-GAP-002 | DAG ordering not enforced by code | BLOCKER |
| SUP-GAP-003 | Overclaim detector (10 patterns) NEVER CALLED | HIGH |
| SUP-GAP-004 | grade_declared_work defaults to adequate=True with confidence=0.0 | HIGH |
| SUP-GAP-005 | LLM "inadequate" verdict overridden if confidence < 0.80 | HIGH |
| SUP-GAP-007 | No circuit breaker for zero-task loops | HIGH |
| SUP-GAP-008 | `_EXPANSION_GOALS` is frozen hardcoded list (~100+ entries) | HIGH |

---

## Key Healing/Learning Gaps (from Lane 15 Audit)

- **ZERO durable learning** — all decision logic uses static rules
- **No failure-memory.json** — failures recorded only in MEMORY.md (prose, 200-line limit) or rework_items (single sprint)
- **0% automatic propagation** — corrections never auto-propagate to skills, validators, schemas, prompts, or taskcard templates
- **ai_learning_loop outputs are `non_authoritative=True`** — never consumed by any validator or decision maker

---

## Anti-Fake-Progress Rules

1. Skeleton-only source files do NOT count as product progress
2. Architecture-only files MUST be labeled `architecture_only`
3. Generated taskcards do NOT count as implemented features
4. Capability maps do NOT count as source progress
5. No model class without `spec_qname` mapping
6. No product-progress claim without spec parity evidence
7. No time estimates as acceptance logic — iteration gates only
8. Every product-progress claim MUST include source + tests + spec_qname refs + evidence

---

## Gate 11 Criteria Summary

### .NET Commercial (C1-C20)
- C1: implementation_depth_score >= 4/5
- C2: capability_coverage >= 80%
- C3: Every public method has >= 1 spec_fact_ref
- C4: class_count >= 15 for complex formats
- C5: .NET CI passes (build + test)
- C6: >= 3 roundtrip tests with XML verification
- C11-C20: Spec-parity (QName map, namespace tree, containment graph, facade mapping, etc.)

### Python FOSS (P1-P11)
- P1: Class-based model exists
- P2: Parity matrix exists and up to date
- P3: capability_coverage >= 60%
- P6-P11: Spec-parity (prefix hierarchy, reduced parity matrix, wrapper delegation, etc.)

---

## 5 New Skills (Lane 4)

1. **`spec-literal-qname-to-code-mapping`** — Convert spec QNames to canonical namespace/class mappings
2. **`spec-shaped-product-architecture-blueprint`** — Generate architecture from QName-to-code ontology
3. **`spec-parity-source-regeneration-and-migration`** — Regenerate/rename source per canonical hierarchy
4. **`python-reduced-spec-parity-model`** — Ensure Python follows canonical concept graph with explicit reduced scope
5. **`spec-parity-verification`** — Validate namespace tree, class inventory, attribute map, containment graph

---

## 8 Spec-Parity Validators (Lane 5)

1. SpecParityQNameValidator
2. NamespaceTreeValidator
3. AttributePropertyMapValidator
4. ContainmentGraphValidator
5. AliasCompatibilityValidator
6. SkeletonProgressValidator
7. SpecParityGateValidator (Gate 11 extension)
8. SkillWiringValidator

---

## Constraints (always active)

- System healing BEFORE product regeneration
- No ad hoc manual renaming — all renames from QName-to-code map
- No skeleton-only files counted as progress
- No Gate 11 approval — Babar Raza only
- Iteration gates, NOT time estimates
- DO NOT start product regeneration with unresolved supervision/healing findings
- DO NOT treat autonomous supervision or healing/learning as working without file:line evidence
