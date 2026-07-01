# Taskcard: FODS-COMMERCIAL-LOAD-SAVE-MODEL

**Status:** completed
**Created:** 2026-05-13
**Completed:** 2026-05-13
**Sprint:** COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001

## Purpose

Design and implement the FODS document object model and same-format save capability, advancing from C2 (streaming parser) to C7 (load + object model + edit + same-format save).

## Scope

- Design `FodsDocument` class with full entity graph (sheets, rows, cells, styles, metadata)
- Implement DOM-building parser (replace or extend streaming `FodsParser`)
- Implement `OpaqueNode` preservation for unsupported elements
- Implement `FodsDocument.Save()` serializer (same-format round-trip)
- Implement edit API for cell values and basic styles
- All code under `src/net/fods/`

## Non-Goals

- Export/conversion to other formats (separate taskcard)
- Tier 5-6 advanced features (chart objects, macros, etc.)
- NuGet packaging or publishing

## Acceptance Criteria

- [ ] `FodsDocument.Load(path)` builds typed object model
- [ ] Object model includes: Sheets, Rows, Cells (typed values), Styles, Metadata
- [ ] `FodsDocument.Save(path)` writes valid FODS XML
- [ ] Round-trip test: load reference file, save, structural comparison passes
- [ ] Edit test: load, modify cell value, save, verify modification
- [ ] Opaque nodes preserved on round-trip
- [ ] Security guards maintained (DTD prohibition, size limits)
- [ ] Capability level reaches C7 per docs/product-factory/commercial-product-capability-model.md

## Evidence Requirements

- Test results (unit, round-trip, edit)
- Capability level assessment against C-level definitions
- DEC-034 independent verification

## Files Allowed

- src/net/fods/ (modify/create)
- tests/net/fods/ (modify/create)

## Prohibited Actions

- No Gate 11 approval claims
- No NuGet publish
- No code outside src/net/fods/ and tests/net/fods/

## Tests Required

- Unit tests for each entity class
- Round-trip fidelity tests against reference FODS files
- Edit-and-save tests
- Regression tests for existing Tier 0 functionality

## Next Dependency

- FODS-COMMERCIAL-EDIT-SAVE-VERTICAL-SLICE (refinement)
- FODS-COMMERCIAL-EXPORT-HTML-PDF-PNG (export pipeline)
