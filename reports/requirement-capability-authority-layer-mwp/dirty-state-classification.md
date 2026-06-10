# Dirty State Classification

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-MWP-001

## Classification

**ALLOWED_MWP_DIRTY_STATE** (pre-existing from R93/R92) + **PRE_EXISTING_SUPERVISOR_WIP** (tri-lane untracked files)

## Pre-Existing Dirty Entries (356 total)

All pre-existing from prior sprints. Categories:
- `.claude/commands/` — M (modified command files from R93)
- `.supervisor/` — M (supervisor context, policies, schemas)
- `plans/master-plan.md` — M
- `product-capability-matrix/poc-targets.yaml` — M (dashboard updates from R93)
- `reports/supervisor/**` — M (supervisor outputs from R93)
- `reports/r90/**` — M (ledger from R90)
- `src/net/fods/`, `src/net/fodt/`, `src/net/netpbm/` — M (product source from R93)
- `src/python/sylk/` — M (product source from R93)
- `tools/supervisor/**` — M and ?? (supervisor tools)
- Various `tests/net/**`, `tests/python/**` — ?? (untracked test files from R93)
- Various `examples/**` — ?? (untracked examples from R93)

**Action:** None. Pre-existing state is not touched by this sprint.

## Tri-Lane Files (PRE_EXISTING_SUPERVISOR_WIP)

Untracked (`??`) files — another sprint's output, not modified:
- `tests/supervisor/test_supervisor_tri_lane_reconciliation.py`
- `tests/supervisor/test_tri_lane_integration_fabric.py`
- `tests/supervisor/test_tri_lane_integration_refresh_readiness.py`
- `tools/supervisor/tri_lane_integration.py`
- `tools/supervisor/validate_tri_lane_contract.py`

**Action:** These are not touched. This sprint does not write to `tools/supervisor/tri_lane_integration.py` or `validate_tri_lane_contract.py`.

## This Sprint's New Files

All new files will be under:
- `requirements-authority/`
- `tools/requirements_authority/`
- `tests/supervisor/test_requirement_capability_*.py`
- `reports/requirement-capability-authority-layer-mwp/`
- `.local/evidences/requirement-capability-authority-layer-mwp/`
- `.local/supervisor/reviews/requirement-capability-authority-layer-mwp/`
