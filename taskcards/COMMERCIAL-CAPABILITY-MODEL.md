# Taskcard: COMMERCIAL-CAPABILITY-MODEL

**Status:** completed
**Created:** 2026-05-13
**Sprint:** COMMERCIAL-REQUIREMENTS-DOC-SYNC-20260513

## Purpose

Document the commercial product capability model (C0-C10) so all agents and gate reviews use a shared definition of what "commercial product readiness" means for the .NET product track.

## Scope

- Create `docs/product-factory/commercial-product-capability-model.md`
- Define capability levels C0 through C10
- Establish that Tier 0 parser success (C0-C2) is NOT commercial readiness
- Define load-edit-save-convert as the commercial requirement (C7+)
- Document object model, same-format save, edit-and-save, and export requirements

## Non-Goals

- Implementing any commercial code
- Changing gate pass/fail status
- Modifying tier-map definitions (those remain in docs/product-factory/product-tracks.md)

## Acceptance Criteria

- [x] `docs/product-factory/commercial-product-capability-model.md` exists with C0-C10 levels
- [x] Load-edit-save-convert requirement explicitly stated
- [x] Object model requirement explicitly stated
- [x] Same-format save requirement explicitly stated
- [x] Edit-and-save requirement explicitly stated
- [x] Export/conversion requirement explicitly stated
- [x] Current FODS/FODT .NET classified as C2
- [x] Gate 11 linked to C7+ requirement

## Evidence Requirements

- File exists and is internally consistent
- Referenced by master-plan and AGENTS.md

## Files Allowed

- docs/product-factory/commercial-product-capability-model.md (create)

## Prohibited Actions

- No code creation
- No gate status changes

## Tests Required

- File existence check
- Cross-reference consistency with master-plan Rule 12

## Next Dependency

- COMMERCIAL-DOTNET-ARCHITECTURE (parallel)
- GATE11-COMMERCIAL-REBASELINE (depends on this)
