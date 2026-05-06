---
artifact_id: TC-0022-evidence-bundle-contract-system
artifact_type: taskcard
path: taskcards/TC-0022-evidence-bundle-contract-system.md
format_id: null
product_family: null
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
notes: "Evidence Bundle Contract System taskcard. Created run031 (2026-05-06). Makes evidence bundle generation deterministic and contract-validated."
---

# TC-0022: Evidence Bundle Contract System

**Taskcard ID:** TC-0022
**Phase:** 3 (cross-cutting infrastructure)
**Gate:** N/A — cross-cutting tooling
**Status:** completed_verified
**Created:** run031 (2026-05-06)
**Format:** N/A (applies to all formats)
**Blocked by:** None

---

## Purpose

Make evidence bundle generation deterministic and contract-validated. Replace manual zip packaging with a contract-driven builder and validator that enforces completeness, forbidden-path exclusion, and correct top-level folder layout.

---

## Deliverables (run031)

| Artifact | Path | Status |
|---|---|---|
| Evidence builder | `tools/evidence/build_evidence_bundle.py` | Created run031 |
| Evidence validator | `tools/evidence/validate_evidence_bundle.py` | Created run031 |
| Git state collector | `tools/evidence/collect_git_state.py` | Created run031 |
| File inventory collector | `tools/evidence/collect_file_inventory.py` | Created run031 |
| Base contract | `tools/evidence/contracts/base-run.yaml` | Created run031 |
| run031 contract | `tools/evidence/contracts/run031-gate4-and-workbench-quality.yaml` | Created run031 |
| Readme | `tools/evidence/_readme.md` | Created run031 |

---

## Acceptance Criteria

- [x] run031 evidence bundle created by builder
- [x] run031 evidence bundle validated by validator
- [x] Missing metadata fails validation (tested: base contract dry-run with 0 metadata files = FAIL)
- [x] Forbidden files excluded from bundle
- [x] Top-level folders are exactly `repo/` and `bundle-metadata/`
- [x] Final response includes `BUNDLE_VALIDATION: PASS`
- [ ] Independent verification in future run (DEC-034)

---

## Scope

In scope:
- Bundle contracts (YAML)
- Builder (Python stdlib)
- Validator (Python stdlib)
- Git state and file inventory collection
- Forbidden path enforcement
- Evidence completeness gates

Out of scope:
- CI workflows
- GitHub Actions
- Push automation
- External storage
- Previous bundle migration

---

## Status

**Current status:** completed_verified

Created in run031, independently verified in run032. Evidence system smoke tests pass: dry-run correctly rejects missing metadata; run031 bundle validates PASS. Future runs must use this system (AGENTS.md Section Y, GOVERNANCE.md Section 18).

---

## Revision History

| Run | Change |
| run032 | Independent verification PASS; status → completed_verified |
|---|---|
| run031 | Taskcard created; all 7 artifacts delivered; run031 bundle built and validated |
