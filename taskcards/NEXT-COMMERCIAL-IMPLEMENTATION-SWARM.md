# Taskcard: NEXT-COMMERCIAL-IMPLEMENTATION-SWARM

**Status:** not_started
**Created:** 2026-05-13
**Sprint:** (awaiting explicit human-authorized swarm prompt)

## Purpose

Coordinate the next implementation swarm for commercial .NET products, ensuring all vertical slices are executed in correct dependency order and product direction is preserved throughout.

## Scope

- Execute FODS-COMMERCIAL-LOAD-SAVE-MODEL (C2 -> C7)
- Execute FODS-COMMERCIAL-EDIT-SAVE-VERTICAL-SLICE (C7 validation)
- Execute FODS-COMMERCIAL-EXPORT-HTML-PDF-PNG (C7 -> C9)
- Execute FODT-COMMERCIAL-LOAD-SAVE-MODEL (C2 -> C7)
- Execute FODT-COMMERCIAL-EDIT-SAVE-VERTICAL-SLICE (C7 validation)
- Execute FODT-COMMERCIAL-EXPORT-HTML-PDF-PNG (C7 -> C9)
- Coordinate dependency order and evidence collection
- Controlled swarm execution with product direction checks at each stage

## Non-Goals

- Gate 11 approval (separate human decision after C9+ achieved)
- NuGet packaging or publishing
- Pricing or licensing decisions

## Acceptance Criteria

- [ ] FODS reaches C7+ per capability model
- [ ] FODT reaches C7+ per capability model
- [ ] All vertical slices have passing tests
- [ ] Round-trip fidelity verified for both formats
- [ ] Export pipelines functional for PDF, HTML, PNG
- [ ] DEC-034 independent verification for each stage
- [ ] No "commercial ready" claims until human reviews capability evidence

## Evidence Requirements

- Per-stage test results
- Per-stage capability level assessment (C-level)
- Final swarm report with achieved capability levels
- DEC-034 IV for each completed stage

## Files Allowed

- src/net/fods/ (modify/create)
- src/net/fodt/ (modify/create)
- tests/net/fods/ (modify/create)
- tests/net/fodt/ (modify/create)

## Prohibited Actions

- No Gate 11 approval claims
- No publishing or packaging
- No skipping dependency order
- No equating parser success with commercial readiness

## Tests Required

- All tests from dependent taskcards
- Cross-format consistency checks
- Security regression tests

## Next Dependency

- Gate 11 human review (after swarm completion and DEC-034 IV)

## Execution Order

1. FODS-COMMERCIAL-LOAD-SAVE-MODEL (parallel with FODT if resources allow)
2. FODT-COMMERCIAL-LOAD-SAVE-MODEL
3. FODS-COMMERCIAL-EDIT-SAVE-VERTICAL-SLICE
4. FODT-COMMERCIAL-EDIT-SAVE-VERTICAL-SLICE
5. FODS-COMMERCIAL-EXPORT-HTML-PDF-PNG (parallel with FODT)
6. FODT-COMMERCIAL-EXPORT-HTML-PDF-PNG
7. Final capability assessment and Gate 11 readiness report

## Product Direction Guard

At each stage transition, verify:
- Current capability level matches expected C-level
- No premature "commercial ready" claims
- Architecture matches docs/commercial-dotnet-architecture.md
- Product direction preserved per docs/commercial-product-capability-model.md
