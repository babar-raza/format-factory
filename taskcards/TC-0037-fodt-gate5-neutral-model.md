---
artifact_id: TC-0037-fodt-gate5-neutral-model
artifact_type: taskcard
path: taskcards/TC-0037-fodt-gate5-neutral-model.md
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
notes: "FODT Gate 5 neutral model planning taskcard. Created run045 (2026-05-08) after Gate 4 PASSED. Planning only — execution requires explicit Gate 5 execution prompt. DEC-034 independent verification required before human approval."
---

# TC-0037: FODT Gate 5 — Neutral Model

**Taskcard ID:** TC-0037
**Phase:** 3 (Gate 5 — neutral model)
**Gate:** Gate 5
**Status:** not_started — awaiting explicit Gate 5 execution prompt
**Created:** 2026-05-08 (run045)
**Created by:** claude-sonnet-4-6 (run045)
**Prerequisite:** Gate 4 PASSED ✓ (Babar Raza, 2026-05-08, run045)
**Blocking:** Gate 5 DEC-034 verification + human approval

---

## STOP — Authorization Required

**This taskcard must not be executed until a human issues an explicit Gate 5 execution prompt.**

Per AGENTS.md: Gate 5 neutral model execution requires an explicit human prompt. This planning
document is created in run045, but execution is blocked until the next session with explicit
authorization naming Gate 5 and the FODT format.

---

## Objective

Define the language-neutral intermediate representation (neutral model) for parsed FODT text
document content. Create all Gate 5 schema artifacts at `schemas/neutral-model/fodt/`. Validate
the model against all 4 Gate 3 FODT samples. Produce a DEC-034 verification sprint.

---

## Scope

### In scope

1. **Neutral model schema** — `schemas/neutral-model/fodt/model.yaml`:
   - Document entity (root container: mime_type, version, word_count)
   - Block entity (paragraphs and headings: element, text, outline_level)
   - List entity (container: list_style ["bullet"|"numbered"], items)
   - Table entity (container: row_count, column_count, rows)
   - TableRow entity (cells)
   - TableCell entity (text content, span information)

2. **JSON Schema** — `schemas/neutral-model/fodt/model.schema.json`:
   - Validates parser output `dict` structure
   - Enforces required fields and value constraints

3. **Field map** — `schemas/neutral-model/fodt/field-map.yaml`:
   - Maps each neutral model field to its FODT XML source (ODF 1.3 element and attribute)
   - Documents reuse from FODS neutral model where applicable

4. **Coverage matrix** — `schemas/neutral-model/fodt/coverage-matrix.yaml`:
   - FODT elements covered, partially covered, deferred, out-of-scope
   - FR-001 through FR-007 coverage verification

5. **Validation rules** — `schemas/neutral-model/fodt/validation-rules.yaml`:
   - Cross-entity constraints (e.g., outline_level 1-10 for headings)
   - Type constraints and cardinality rules

6. **README** — `schemas/neutral-model/fodt/README.md`:
   - Entity summary, field counts, sample validation results

7. **Model validator** — `tools/model/validate_fodt_neutral_model.py`:
   - Validates all 4 FODT samples against the neutral model
   - Must achieve 4/4 PASS

8. **DEC-034 verification sprint** (separate session):
   - Create TC-0038 (if not already used for FODS Gate 8) or next available TC number
   - Run in separate session from execution

### Out of scope — FORBIDDEN

| Item | Reason | Gate |
|---|---|---|
| Product source code | Gate 10+ | `src/python/fodt/`, `src/net/fodt/` |
| Gate 5 self-approval | Human-only | — |
| FODS neutral model modifications | Gate 5 complete; FODT model is separate | — |
| FODT Gate 6 oracle work | Requires Gate 5 approval + explicit prompt | — |
| reports/security/fodt.md | Gate 8 scope | — |
| CI workflows | Gate 10+ | — |

---

## Execution Plan

### Step 1: Read parser output
- Read `prototypes/by-format/fodt/fodt_parser.py` — understand output structure
- Run `validate_against_samples.py` to see actual parser output for each sample
- Note all field names and value types from parser dict

### Step 2: Design neutral model entities
Following FODS model pattern (6 entities), design FODT entities:
- **Document** — root (format_id, spec_version, mime_type, version_attr, word_count,
  block_count, list_count, table_count)
- **Block** — paragraph or heading (element: "paragraph"|"heading", text, outline_level)
- **List** — (list_style: "bullet"|"numbered"|"unknown", item_count, items)
- **ListItem** — (text, nested_list: optional)
- **Table** — (row_count, column_count, rows)
- **TableRow** — (cells)
- **TableCell** — (text)

### Step 3: Create schema artifacts (7 files)
Create all 7 artifacts under `schemas/neutral-model/fodt/`.

### Step 4: Validate against 4 samples
Run `tools/model/validate_fodt_neutral_model.py` against:
- `samples/by-format/fodt/minimal-document.fodt`
- `samples/by-format/fodt/headings-and-paragraphs.fodt`
- `samples/by-format/fodt/list-basic.fodt`
- `samples/by-format/fodt/table-basic.fodt`
Must achieve 4/4 PASS.

### Step 5: DEC-034 verification
Create DEC-034 taskcard (TC-0038 or TC-0039 depending on Gate 8 usage).
Run in separate session from execution.

### Step 6: Human approval
Present `acquisition-packs/fodt/gate5-human-review-packet.md` for human approval.

---

## Related Files

- `acquisition-packs/fodt/gate5-neutral-model-plan.md` — detailed planning notes (run045)
- `prototypes/by-format/fodt/fodt_parser.py` — Gate 4 parser output structure
- `schemas/neutral-model/fods/` — FODS neutral model (structural reference)
- `samples/by-format/fodt/` — 4 Gate 3 samples (validation targets)
- `tools/model/validate_neutral_model.py` — FODS validator (reference implementation)

---

## FODS Neutral Model Reuse Notes

The FODT neutral model reuses the FODS structural pattern (model.yaml → field-map.yaml →
coverage-matrix.yaml → validation-rules.yaml → model.schema.json → README.md) but defines
entirely different entities. FODT is a text document (paragraphs, headings, lists, tables);
FODS is a spreadsheet (workbook, sheets, rows, cells, formulas).

Shared concepts:
- Document-level metadata fields (format_id, spec_version, mime_type, version_attr)
- word_count concept
- Table structure (table → row → cell)

New concepts specific to FODT:
- Block elements (text:p vs text:h distinction + outline_level)
- List structure (bullet vs numbered style detection from office:automatic-styles)
- Heading hierarchy (outline_level 1-10)

---

## DEC-034 Requirement

Per DEC-034 and AGENTS.md Section V: after Gate 5 execution, a separate independent
verification sprint must run before Gate 5 is submitted for human approval. The DEC-034
taskcard will be created during Gate 5 execution and run in a separate session.

---

## Expected Deliverables

| Artifact | Path |
|---|---|
| Neutral model | `schemas/neutral-model/fodt/model.yaml` |
| JSON Schema | `schemas/neutral-model/fodt/model.schema.json` |
| Field map | `schemas/neutral-model/fodt/field-map.yaml` |
| Coverage matrix | `schemas/neutral-model/fodt/coverage-matrix.yaml` |
| Validation rules | `schemas/neutral-model/fodt/validation-rules.yaml` |
| README | `schemas/neutral-model/fodt/README.md` |
| Validator | `tools/model/validate_fodt_neutral_model.py` |
| Human review packet | `acquisition-packs/fodt/gate5-human-review-packet.md` |
| DEC-034 taskcard | `taskcards/TC-0038 or TC-0039` |
| Registry update | `registry/format-registry.yaml` gate_5 | After human approval |
| Pack update | `acquisition-packs/fodt/pack.yaml` gate_5 | After human approval |
