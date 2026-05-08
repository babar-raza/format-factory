---
artifact_id: TC-0048-fodt-gate9-product-mapping
artifact_type: taskcard
path: taskcards/TC-0048-fodt-gate9-product-mapping.md
format_id: fodt
product_family: words
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
notes: "FODT Gate 9 product mapping taskcard. not_started. Created run048 (2026-05-08). Requires explicit Gate 9 prompt."
---

# TC-0048: FODT Gate 9 — Product Mapping

**Taskcard ID:** TC-0048
**Status:** COMPLETED — Gate 9 PASSED (run050, 2026-05-08)
**Gate:** Gate 9
**Created:** 2026-05-08 (run048)
**Prerequisite:** Gate 8 PASSED (Babar Raza, 2026-05-08, run048)

---

## STOP — Authorization Required

Must not execute until human issues explicit Gate 9 execution prompt naming
"FODT Gate 9 product mapping."

Gate 9 requires: FODT tier map creation (analogous to FODS tier-map.yaml v1.0).
Tiers 0-4 for FODT (words/text format, similar feature structure to FODS but for text docs).

---

## Objective

Define the product tier map for FODT:
1. Map FODT features to tiers (Tier 0-4, analogous to FODS)
2. Identify first OSS release tiers (expected: Tiers 0-2)
3. Identify deferred commercial tiers (expected: Tiers 3-4+)
4. Create tier-map.yaml for FODT
5. Create Gate 9 human-review packet
6. DEC-034 verification (separate session or inline per prompt)

---

## Expected Tier Structure (preliminary)

| Tier | Description | Examples |
|---|---|---|
| 0 | File Identity | Format detection, MIME, version, doc stats |
| 1 | Structural Extraction | Para count, heading list, word count |
| 2 | Typed Content | Para text, heading levels, list items |
| 3 | Tables + Rich Content | Tables, embedded images (deferred) |
| 4 | Advanced | Tracked changes, comments, sections (deferred) |

---

## Deliverables

| Artifact | Path |
|---|---|
| FODT tier map | acquisition-packs/fodt/tier-map.yaml |
| OSS release scope | acquisition-packs/fodt/gate9-oss-scope.md |
| Gate 9 review packet | acquisition-packs/fodt/gate9-human-review-packet.md |

---

## Reuse from FODS

FODT Gate 9 can reuse the FODS tier-map.yaml v1.0 template (docs/odf-flat-family-reuse-strategy.md).
Adapt tier names for text/words domain vs spreadsheet/cells domain.

---

## Forbidden

- No product source creation (src/python/fodt/ forbidden until Gate 10)
- No src/net/ creation
