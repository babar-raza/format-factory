# Taskcard: COMMERCIAL-DOTNET-ARCHITECTURE

**Status:** completed
**Created:** 2026-05-13
**Sprint:** COMMERCIAL-REQUIREMENTS-DOC-SYNC-20260513

## Purpose

Document the expected .NET commercial architecture (API shape, object model, save pipeline, conversion pipeline, test strategy) so future implementation sprints have clear technical requirements.

## Scope

- Create `docs/product-factory/commercial-dotnet-architecture.md`
- Define expected API shape (Load/Edit/Save/Export)
- Define expected object model for FODS and FODT
- Define expected save pipeline (collect, validate, merge, serialize, verify)
- Define expected conversion/export pipeline
- Define expected preservation model (full, structural, opaque)
- Define expected test strategy
- Define expected format-first layout under `src/net/{format}/`

## Non-Goals

- Implementing any code
- Prescribing specific third-party libraries
- Defining pricing or licensing

## Acceptance Criteria

- [x] `docs/product-factory/commercial-dotnet-architecture.md` exists
- [x] API shape documented with code examples
- [x] FODS and FODT object models defined
- [x] Save pipeline documented
- [x] Conversion/export pipeline documented
- [x] Preservation model documented (full/structural/opaque)
- [x] Test strategy documented
- [x] Format-first layout documented

## Evidence Requirements

- File exists and is internally consistent
- Referenced by capability model

## Files Allowed

- docs/product-factory/commercial-dotnet-architecture.md (create)

## Prohibited Actions

- No code creation
- No gate status changes

## Tests Required

- File existence check
- Consistency with capability model C-levels

## Next Dependency

- FODS-COMMERCIAL-LOAD-SAVE-MODEL (implementation)
- FODT-COMMERCIAL-LOAD-SAVE-MODEL (implementation)
