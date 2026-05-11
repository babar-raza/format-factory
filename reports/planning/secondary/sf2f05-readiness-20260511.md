# S-F2F-05 Readiness Plan
**Date:** 2026-05-11
**Sprint:** FODT-GATE10-APPROVAL-AND-SWARM-NEXT-LANES-001 (Lane C)

---

## 1. S-F2F-04 Closure Status

S-F2F-04 is **CLOSED_VERIFIED**:
- Golden dry-run tests: 140 PASS, 1 skip, 0 fail
- 7 golden fixtures (FODS + FODT format-agnostic)
- Bundle validated: 497 entries, 1,278,016 bytes, BUNDLE_VALIDATION: PASS
- Proof repair: CLOSED_VERIFIED (520 entries, 1,315,330 bytes)

## 2. S-F2F-05 Objective

Create the ODF-flat family playbook — an acquisition-playbook.yaml for the ODF flat format family (FODS, FODT, FODP, FODB) that captures:
- Shared spec (ODF 1.3), shared legal basis, shared oracle tooling
- Per-format differences (neutral model, tier map, parser strategy)
- Reuse patterns for future ODF flat acquisitions

## 3. File Ownership Proposal

S-F2F-05 would create/modify:
- schemas/playbook/odf-flat-family-playbook.yaml (NEW)
- schemas/playbook/ (existing schema — read-only reference)
- tests/playbook/ (new tests for ODF family playbook)
- docs/playbook-layer.md (minor update if needed)

**Does NOT touch:**
- src/python/fods/ or src/python/fodt/ (product source)
- registry/format-registry.yaml (gate fields)
- plans/master-plan.md (except status note via coordinator)
- tools/evidence/ (evidence contracts)

## 4. Conflicts with Main Lane

**None identified.** S-F2F-05 file scope is entirely within schemas/playbook/, tests/playbook/, and docs/playbook-layer.md. These are structurally isolated from:
- Product source (src/python/)
- Gate state (registry/)
- Master plan authority sections
- Evidence tooling (tools/evidence/)

## 5. Can S-F2F-05 Run in Parallel?

**YES** — after this sprint commits, S-F2F-05 can run as Lane B in a subsequent swarm or as a standalone sprint. Conditions:
- Same worktree: only one writer at a time (per acceleration plan)
- S-F2F-05 must not modify shared files without coordinator
- Master plan status update via coordinator only
- No apply-mode (dry-run only per S-F2F governance)

## 6. Expected Evidence Contract Shape

- required_repo_files: odf-flat-family-playbook.yaml, test files, docs update
- required_metadata_files: ~30 (baseline, execution, validation, drift, proof)
- semantic_checks: playbook created, no product source change, no apply mode
- min_metadata_count: 30

## 7. No Apply-Mode Boundary

S-F2F-05 must use dry-run mode only (per AGENTS.md Section AA). The playbook YAML is documentation/planning, not execution. The playbook does not modify product source, registry, or gate state.

## 8. Stop Conditions

- Product source modified: STOP
- Registry gate fields modified: STOP
- Apply mode used: STOP
- Shared file conflict with active main-lane sprint: STOP
