# Taskcard: GATE11-COMMERCIAL-REBASELINE

**Status:** completed
**Created:** 2026-05-13
**Sprint:** COMMERCIAL-REQUIREMENTS-DOC-SYNC-20260513

## Purpose

Rebaseline Gate 11 expectations so that approval requires load-edit-save-convert capability (C7+), not just Tier 0 parser success. Update all authority files to reflect the rebaselined requirements.

## Scope

- Update `plans/master-plan.md` Rule 12 and next-required-action
- Update `registry/format-registry.yaml` Gate 11 entries for FODS and FODT
- Update `AGENTS.md` with commercial readiness rules (AF9-AF11)
- Update `GOVERNANCE.md` with commercial governance (26.8-26.9)
- Ensure Gate 11 human review packets reference capability model
- Ensure no authority file overstates current commercial readiness

## Non-Goals

- Approving or rejecting Gate 11
- Creating commercial implementation code
- Changing Gate 1-10 statuses

## Acceptance Criteria

- [x] master-plan Rule 12 references capability model
- [x] master-plan next-required-action states Gate 11 is deferred/rebaselined
- [x] Registry FODS gate_11 includes commercial_capability_level: C2, commercial_product_ready: false
- [x] Registry FODT gate_11 includes same fields
- [x] AGENTS.md AF9-AF11 added
- [x] GOVERNANCE.md 26.8-26.9 added
- [x] No contradictory "commercial ready" claims remain in authority files

## Evidence Requirements

- Diff of all updated authority files
- Contradiction search report (no false positives)

## Files Allowed

- plans/master-plan.md (edit)
- registry/format-registry.yaml (edit)
- AGENTS.md (edit)
- GOVERNANCE.md (edit)

## Prohibited Actions

- No gate approval
- No gate status change to "passed"
- No code creation

## Tests Required

- Cross-reference: registry commercial_capability_level matches capability model
- No "commercial ready" or "product ready" claims for C2 source

## Next Dependency

- FODS-COMMERCIAL-LOAD-SAVE-MODEL (implementation planning)
- FODT-COMMERCIAL-LOAD-SAVE-MODEL (implementation planning)
- NEXT-COMMERCIAL-IMPLEMENTATION-SWARM (execution)
