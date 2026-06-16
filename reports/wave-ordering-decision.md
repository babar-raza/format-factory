# Wave Ordering Decision (TC-H6-001)
Generated: 2026-06-16
Status: FORMAL_DEFERRAL

## Context

The spec-to-feature radical correction plan (`plans/spec-to-feature-radical-correction-plan.md`)
requires **system healing Lanes 1-6, 14, 15 to complete before product regeneration Lanes 7-13**.

Swarm sprints 1-31+ have been executing product gap-closure work while Lanes 2, 3, and 6 remain
at zero progress. This document records the formal decision on whether to block product work or
defer the outstanding lanes.

## Lanes Under Review

| Lane | Name | Status | Progress |
|------|------|--------|----------|
| 2 | Capability Reintegration — replace hardcoded `_EXPANSION_GOALS` with gap-ledger-driven task selection | ZERO | 0% |
| 3 | Capability-to-Feature Compiler — 9-phase compiler (concept graph → gate readiness) | ZERO | 0% |
| 6 | QName-to-Code Ontology — 9 artifacts per format (qname-to-code-map, namespace-tree, containment-graph, etc.) | ZERO | 0% |

## Assessment: Are These Lanes Still Required?

### Lane 2 (Capability Reintegration)
The `_EXPANSION_GOALS` frozen list in the supervisor drives task selection. The gap-ledger
(reports/capability-layer/gap-ledger.json) is being consumed directly by agents via skill
`select-poc-gap` and governed implementation taskcards. The immediate gap-closure work is
proceeding without Lane 2's formal reintegration wiring.

**Decision: DEFERRED** with the following rationale and scope limit:
- Gap-closure continues via direct ledger reads by agents (functional substitute)
- Lane 2 is required before any autonomous sprint loop is allowed to self-generate task queues
  from the gap-ledger programmatically. That capability does not exist yet and is not blocking
  current manual/agent-driven gap work.
- Reactivation trigger: When autonomous sprint loop iteration reaches MODE 5 (self-generating
  task queues), Lane 2 must be completed first.

### Lane 3 (Capability-to-Feature Compiler)
This 9-phase compiler was designed to translate ODF spec QNames → feature graph → taskcards →
test obligations → gate readiness automatically. Currently, taskcards are written by agents
manually and test obligations are derived from gap-ledger entries.

**Decision: DEFERRED** with the following rationale and scope limit:
- Current product work (Python FOSS analytics functions, dogfood tests) does not require
  spec-to-feature compilation. The gap-ledger entries describe capabilities in human-readable
  form that agents can act on directly.
- Lane 3 is required before Gate 11 EXECUTION (commercial release) because Gate 11 criteria
  C3/C11-C20 require spec-parity evidence that a compiler would generate automatically.
- Reactivation trigger: Gate 11 preparation for FODS/FODT. The gate readiness packet requires
  QName-to-code mapping which is Lane 3's output.

### Lane 6 (QName-to-Code Ontology)
9 artifacts per format: qname-to-code-map, namespace-tree, containment-graph, facade-mapping,
attribute-property-map, alias-compatibility-map, concept-inventory, parity-matrix,
skeleton-progress-map.

**Decision: DEFERRED** with the following rationale and scope limit:
- Python FOSS gap-closure tests do not require QName ontology because the functions being
  tested are analytics/utility functions (e.g., `abw_word_count`, `fods_sheet_count`) that
  do not correspond to ODF spec QNames directly.
- The spec-parity validators (Lane 5, V_SPEC_QNAME, V_NAMESPACE_TREE, etc.) that require
  Lane 6 artifacts currently emit WARN (not FAIL) for most declarations because PRODUCT_SOURCE
  items for Python FOSS do not carry `spec_qname_refs`.
- Reactivation trigger: Any PRODUCT_SOURCE item that targets ODF spec-parity classes (e.g.,
  `table:table-cell` → `Table.TableCell`) must complete Lane 6 for its format before
  implementation begins.

## Scope Limits on Current Product Work

While Lanes 2, 3, 6 are deferred, the following restrictions apply to all active product work:

1. **Python FOSS analytics tests** (r231/r232, dogfood): Permitted without Lane 6, because
   analytics functions are utility-layer (not spec-literal class implementations).

2. **New spec-literal classes** (e.g., `Table.TableCell`, `Text.List`): BLOCKED until Lane 6
   QName-to-code ontology exists for that format. Any PR adding canonical spec-literal classes
   without a qname-to-code-map MUST be marked `architecture_only` and counted as zero product
   progress.

3. **Autonomous sprint loop task generation** (MODE 5): BLOCKED until Lane 2 is complete.

4. **Gate 11 preparation packets** (FODS/FODT): BLOCKED on Lane 3 and Lane 6 completion for
   those formats before gate readiness packets can claim C11-C20 compliance.

## Formal Deferral Record

| Lane | Deferred Until | Reactivation Condition |
|------|---------------|----------------------|
| 2 | MODE 5 autonomous loop activation | Self-generating task queue required |
| 3 | Gate 11 preparation (FODS/FODT) | spec-parity C3/C11-C20 compliance required |
| 6 | First spec-literal class implementation per format | qname-to-code-map required for format |

## Decision Authority

This deferral is **ADVISORY** from the supervisor agent. Format Factory authority
(AGENTS.md, registry/format-registry.yaml) is final. Gate 11 approval requires Babar Raza
regardless of Lane 2/3/6 status.

## Anti-Ambiguity Statement

There is **no ambiguity** about whether Lanes 2/3/6 are active or deferred:
- **Active product work** (analytics, dogfood, gap-closure): CONTINUES under scope limits above
- **Spec-literal class implementation**: BLOCKED until Lane 6 complete for that format
- **Gate 11 gate packet submission**: BLOCKED until Lane 3 and 6 complete for FODS/FODT
- **Autonomous self-generating loops**: BLOCKED until Lane 2 complete
