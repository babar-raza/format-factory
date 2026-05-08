---
artifact_id: fods-gate9-product-mapping-plan
artifact_type: acquisition-pack
path: acquisition-packs/fods/gate9-product-mapping-plan.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODS Gate 9 product mapping planning document. Created run046 (2026-05-08). Planning only — execution requires explicit Gate 9 prompt. TC-0040 not_started."
---

# FODS Gate 9 — Product Mapping Plan

**Gate:** 9 — Tier Map and Delivery Plan Complete
**Format:** FODS
**Run:** run046 planning (2026-05-08)
**Status:** planning_ready — execution blocked until explicit Gate 9 prompt

---

## Prerequisites (all met)

| Prerequisite | Status |
|---|---|
| Gate 8 PASSED | PASS — Babar Raza, 2026-05-08, run046 |
| Security report complete | YES — reports/security/fods.md |
| TC-0038 DEC-034 | PASS 20/20 |
| Neutral model (Gate 5) | PASSED — schemas/neutral-model/fods/ |
| Parser prototype (Gate 4) | PASSED — prototypes/by-format/fods/fods_parser.py |

---

## Gate 9 Deliverables

Gate 9 requires two artifacts:
1. **Tier map** — `acquisition-packs/fods/tier-map.yaml` (what features belong to which tier)
2. **Delivery plan** — defines first OSS release tiers and deferred commercial tiers

A draft tier map has been created at `acquisition-packs/fods/tier-map-draft.yaml`.
The executing agent must review and finalize it.

---

## Tier Model Reference

From `docs/product-tracks.md`, Tier 0–4 for Python FOSS:

| Tier | Scope |
|---|---|
| 0 | File identity (parse root element, confirm MIME type, return version) |
| 1 | Tier 0 + structural extraction (sheet names, row/cell counts, basic values) |
| 2 | Tier 1 + typed values (float, string, boolean, date, time) |
| 3 | Tier 2 + formulas (raw formula string, cached value, OpenFormula prefix) |
| 4 | Tier 3 + styles, conditional formatting, merged cells, full fidelity |

---

## Proposed Tier Assignments (preliminary)

| Feature | Proposed Tier | Rationale |
|---|---|---|
| Root element identification | 0 | File identity baseline |
| MIME type validation | 0 | File identity baseline |
| Version extraction | 0 | File identity baseline |
| Sheet name extraction | 1 | Structural metadata |
| Row/cell count | 1 | Structural metadata |
| String cell values | 1 | Core data access |
| Float/numeric values | 2 | Typed value extraction |
| Boolean values | 2 | Typed value extraction |
| Date/time values | 2 | Typed value extraction |
| Empty cell handling | 2 | Typed value extraction |
| Formula raw string | 3 | Formula access |
| Formula cached value | 3 | Formula access |
| column-repeat expansion | 3 | Layout fidelity |
| Styles (basic) | 4 | Full fidelity |
| Merged cells | 4 | Full fidelity |
| Conditional formatting | 4 | Full fidelity |

---

## Execution Authorization

Gate 9 execution is blocked until:
1. A human issues an explicit Gate 9 execution prompt naming "FODS Gate 9 product mapping"
2. The executing agent reviews docs/product-tracks.md and docs/gates.md Section Gate 9
3. The executing agent finalizes tier-map.yaml from the draft
4. A human approves the tier map

---

## References

- `docs/product-tracks.md` — Tier 0–6 definitions
- `docs/gates.md` — Gate 9 pass criteria
- `acquisition-packs/fods/tier-map-draft.yaml` — Draft tier map
- `taskcards/TC-0040-fods-gate9-product-mapping.md` — Execution taskcard
