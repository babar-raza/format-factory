---
artifact_id: TC-0023-fods-gate5-neutral-model-execution
artifact_type: taskcard
path: taskcards/TC-0023-fods-gate5-neutral-model-execution.md
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
notes: "FODS Gate 5 neutral model execution taskcard. Created run031 (2026-05-06). EXECUTED run033 (2026-05-06): neutral model v1 created, 6 entities, 4/4 samples PASS. Status: neutral_model_created_pending_independent_verification."
---

# TC-0023: FODS Gate 5 Neutral Model Execution

**Taskcard ID:** TC-0023
**Phase:** 3+ (after Gate 4 approved)
**Gate:** 5
**Status:** neutral_model_created_pending_independent_verification
**Executed:** 2026-05-06 (run033)
**Executed by:** claude-opus-4-6 (run033)
**Created:** run031 (2026-05-06)
**Format:** fods
**Blocked by:** Gate 4 human approval (Babar Raza) + explicit Gate 5 execution prompt

---

## Purpose

Execute Gate 5 (Neutral Model Defined) for FODS after Gate 4 is human-approved and an explicit Gate 5 execution prompt is issued. This taskcard governs the actual schema creation and neutral model definition work.

---

## Preconditions

1. Gate 4 approved by Babar Raza (not yet approved as of run031)
2. TC-0019 (Gate 5 planning) completed or superseded
3. Explicit Gate 5 execution prompt from human
4. Spec Workbench v1 quality review passed (TC-0021 PASS as of run031)

---

## Deliverables (future)

1. Neutral model schema at `schemas/neutral-model/cells-v1.yaml` (or equivalent)
2. FODS-to-neutral-model mapping document
3. Gate 5 evidence for human review

---

## Out of Scope

- No work until Gate 4 approved and explicit prompt issued
- No product source (`src/python/fods/`, `src/net/fods/`)
- No Gate 6+ work
- No release manifests

---

## Status

**Current status:** neutral_model_created_pending_independent_verification

Gate 4 PASSED (Babar Raza, 2026-05-06, run033 prompt). Gate 5 execution completed run033:
- Neutral model v1 at `schemas/neutral-model/fods/` (7 files)
- 6 entities: Workbook, Sheet, Row, Cell, Formula, Warning
- 19 field mappings (14 direct, 1 rename, 1 expand, 3 derived)
- 30 coverage features (13 covered, 2 partial, 10 deferred, 5 out-of-scope)
- 21 validation rules (18 error, 3 warning)
- Validation: 4/4 samples PASS (87 total checks, 0 errors)
- TC-0024 (DEC-034 verification) created and ready for execution

---

## Revision History

| Run | Change |
|---|---|
| run031 | Taskcard created (not_started); blocked by Gate 4 approval |
| run033 | EXECUTED: Gate 4 approved; neutral model v1 created (6 entities, 7 files); 4/4 PASS; TC-0024 created |
