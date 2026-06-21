---
artifact_id: TC-0002
artifact_type: taskcard
path: taskcards/TC-0002-schema-language.md
format_id: null
product_family: null
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: 2026-05-03
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: Infrastructure taskcard. Resolves DEC-008 (schema language decision).
---

# TC-0002: Neutral Model Schema Language Selection

**Phase:** 1
**Status:** completed
**Owner:** Autonomous agent (TC-0002 sprint 2026-06-18)
**Created:** 2026-05-03
**Last updated:** 2026-06-18
**Blocking:** Phase 3 Gate 5 (neutral model design requires language to be selected)
**Blocked by:** TC-0001 (FODS must be confirmed pilot before schema work begins)
**Format:** none (infrastructure)
**Gate:** none (supports Gate 5)

---

## Objective

Decide and document the schema language to be used for neutral-model schemas in `schemas/neutral-model/`. The decision must be recorded as a formal update to Decision DEC-008 in `plans/master-plan.md`. The output is a confirmed decision with documented rationale and a concrete schema language specification written into `schemas/_readme.md`.

---

## Context

Decision DEC-008 (schema language for neutral model) was marked "Tentative" in Phase 0. The architecture (`docs/architecture.md`) says "YAML or JSON Schema" but does not commit. This needs to be resolved before Gate 5 (neutral model design) begins, so the schema work is done in a consistent format from the first format.

Factors to consider: tooling support in Python and .NET, human readability, validation library availability, round-trip fidelity for complex data structures.

---

## Scope

### In scope

- Research: what schema language options are available that work well in both Python and .NET
- Decision: select one primary schema language
- Documentation: update `schemas/_readme.md` with the decision and rationale
- Decision register: update DEC-008 status from "Tentative" to "Decided" in `plans/master-plan.md`

### Out of scope

- Designing the actual neutral model schema for any format (that is Gate 5 work)
- Implementing schema validation tools (that is Phase 3+ work)
- Selecting a different schema language later — this decision should be stable

---

## Acceptance Criteria

- [ ] At least two schema language options evaluated with pros/cons documented
- [ ] One primary schema language selected with documented rationale
- [ ] `schemas/_readme.md` updated to specify the chosen schema language and validation approach
- [ ] DEC-008 updated in `plans/master-plan.md` from "Tentative" to "Decided"
- [ ] Self-challenge completed (AGENTS.md Section I)
- [ ] `plans/master-plan.md` updated with taskcard completion

---

## Artifacts Produced

| Artifact | Path | Visibility | Notes |
|---|---|---|---|
| Schema readme update | `schemas/_readme.md` | internal | Updated with language decision |

---

## Artifacts Consumed (Inputs)

| Artifact | Path | Required? |
|---|---|---|
| Architecture doc | `docs/architecture.md` | Required |
| Schemas readme | `schemas/_readme.md` | Required |
| Master plan decisions | `plans/master-plan.md` (Decision DEC-008) | Required |

---

## Steps

1. Review `docs/architecture.md` and `docs/product-tracks.md` for constraints on schema language.
2. Evaluate options: YAML with custom schema, JSON Schema, LinkML, Avro IDL, Protocol Buffers, plain Python dataclasses.
3. For each option, note: Python library availability, .NET library availability, human readability, tooling maturity.
4. Select the primary language. Document rationale.
5. Update `schemas/_readme.md` with the chosen language, validation approach, and tooling recommendations.
6. Update DEC-008 in `plans/master-plan.md` to "Decided" with rationale.
7. Complete self-challenge.
8. Update `plans/master-plan.md` taskcard completion record.

---

## Completion Record

**Completed by:** (to be filled)
**Completion date:** (to be filled)
**Artifacts produced:** (to be filled)
**Gaps discovered:** (to be filled)
**Notes:** (to be filled)
