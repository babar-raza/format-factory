---
artifact_id: fods-gate5-planning-checklist
artifact_type: gate-planning-checklist
path: acquisition-packs/fods/gate5-planning-checklist.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-06"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 5 planning checklist for FODS. Created run032 (2026-05-06). Prep only — no execution until Gate 4 approved."
---

# FODS Gate 5 Planning Checklist

**Format:** FODS (Flat OpenDocument Spreadsheet)
**Gate:** 5 — Neutral Model Defined
**Status:** prep_only (Gate 4 not yet approved)
**Created:** run032 (2026-05-06)

---

## Prerequisites (must be true before Gate 5 begins)

- [ ] Gate 4 approved by Babar Raza
- [ ] Explicit Gate 5 planning prompt issued
- [ ] TC-0019 status changed to `in_progress`

---

## Inputs Available for Gate 5 Planning

| Input | Path | Status |
|---|---|---|
| Parser prototype | `prototypes/by-format/fods/fods_parser.py` | 4/4 PASS, verified run030+run031+run032 |
| Parser requirements | `acquisition-packs/fods/parser-requirements.md` | 10 requirements, PR-001..PR-010 |
| Parser scope | `acquisition-packs/fods/parser-scope.md` | Tier 0-1 subset defined |
| Parser test plan | `acquisition-packs/fods/parser-test-plan.md` | PT-001..PT-004 |
| Prototype notes | `prototypes/by-format/fods/prototype-notes.md` | Design decisions documented |
| Spec workbench (local) | `.local/spec-cache/fods/1.3/workbench/` | 205/205 validation PASS |
| Verified facts (local) | `.local/spec-cache/fods/1.3/workbench/verified-facts.yaml` | 10 facts |
| Model reqs draft (local) | `.local/spec-cache/fods/1.3/workbench/requirement-packs/model-requirements-draft.yaml` | 3 draft MR-001..MR-003-DRAFT |

---

## Gate 5 Deliverables (from docs/gates.md)

1. Neutral model schema at `schemas/neutral-model/cells-v1.yaml` (or format-specific)
2. FODS-to-neutral-model mapping document
3. Value type mapping (float, string, boolean, date, formula)
4. Sheet/row/cell hierarchy definition
5. Limitations relative to full ODF 1.3 coverage
6. Gate 5 evidence for human review

---

## Design Questions to Resolve During Gate 5

1. Should the neutral model be FODS-specific or Cells-family generic?
2. What schema language: JSON Schema, YAML schema, or TypeScript interface?
3. How to represent formula cells (raw string + cached value vs. evaluated)?
4. How to handle merged cells, styles, conditional formatting (future tiers)?
5. What roundtrip guarantees are required at Tier 0-1?

---

## What Gate 5 Must NOT Do

- Create product source (`src/python/fods/`, `src/net/fods/`)
- Create CI workflows
- Self-approve Gate 5
- Create Gate 6+ artifacts
- Execute without explicit human prompt
