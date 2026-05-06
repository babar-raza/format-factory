---
artifact_id: fods-oracle-risk-register
artifact_type: gate-planning
path: acquisition-packs/fods/oracle-risk-register.md
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
notes: "Gate 6 oracle comparison risk register for FODS. Created run034 (2026-05-06). Planning only."
---

# FODS Gate 6 — Oracle Risk Register

**Format:** FODS
**Gate:** 6 — Oracle Comparison
**Status:** planning_only
**Created:** run034 (2026-05-06)

---

## Risks

| ID | Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|---|
| OR-001 | LibreOffice not installed or version incompatible | Medium | Low | Check installation before execution; document version. Alternative: Apache OpenOffice or odfpy. |
| OR-002 | LibreOffice CSV export loses cell type information | Medium | Medium | Use LibreOffice macro to export structured data (cell type + value) instead of plain CSV. Or use multiple export modes. |
| OR-003 | Float precision differences between parser and oracle | Low | High | Round to reasonable precision (e.g., 6 decimal places) before comparison. Document threshold. |
| OR-004 | Boolean value representation mismatch | Low | Medium | Normalize: Python True/False vs LibreOffice "TRUE"/"FALSE". Document normalization rules. |
| OR-005 | Formula evaluation differences obscure real bugs | Medium | Low | Compare cached values (parser) separately from evaluated values (oracle). Cached value should match oracle result if document hasn't been modified since last save. |
| OR-006 | Oracle exports empty cells differently than parser | Low | Medium | Define empty cell normalization: both outputs should treat missing/empty cells consistently. |
| OR-007 | Sheet ordering changes in oracle export | Low | Low | LibreOffice preserves document sheet order. If not, use sheet name matching instead of position. |
| OR-008 | Prototype bug found during comparison | Medium | Medium | Fix bug in prototype parser, re-run Gate 4/5 validation to confirm no regression. Document fix in oracle report. |
| OR-009 | Oracle reveals neutral model gaps | Medium | Low | Do NOT modify neutral model during Gate 6. Create separate TC for model update if needed. Gate 6 documents gaps only. |
| OR-010 | LibreOffice headless mode fails on Windows | Low | Low | Test headless command before batch processing. Fallback: use GUI mode with macro automation. |
