# Taskcard: FODT-COMMERCIAL-LOAD-SAVE-MODEL

**Status:** not_started
**Created:** 2026-05-13
**Sprint:** (awaiting explicit human-authorized implementation sprint)

## Purpose

Design and implement the FODT document object model and same-format save capability, advancing from C2 (streaming parser) to C7 (load + object model + edit + same-format save).

## Scope

- Design `FodtDocument` class with full entity graph (paragraphs, lists, tables, styles, metadata)
- Implement DOM-building parser (replace or extend streaming `FodtParser`)
- Implement `OpaqueNode` preservation for unsupported elements
- Implement `FodtDocument.Save()` serializer (same-format round-trip)
- Implement edit API for paragraph text and basic styles
- All code under `src/net/fodt/`

## Non-Goals

- Export/conversion to other formats (separate taskcard)
- Tier 5-6 advanced features (tracked changes, embedded objects, etc.)
- NuGet packaging or publishing

## Acceptance Criteria

- [ ] `FodtDocument.Load(path)` builds typed object model
- [ ] Object model includes: Paragraphs, Lists, Tables, Styles, Metadata, Sections
- [ ] `FodtDocument.Save(path)` writes valid FODT XML
- [ ] Round-trip test: load reference file, save, structural comparison passes
- [ ] Edit test: load, modify paragraph text, save, verify modification
- [ ] Opaque nodes preserved on round-trip
- [ ] Security guards maintained (DTD prohibition, size limits)
- [ ] Capability level reaches C7 per docs/commercial-product-capability-model.md

## Evidence Requirements

- Test results (unit, round-trip, edit)
- Capability level assessment against C-level definitions
- DEC-034 independent verification

## Files Allowed

- src/net/fodt/ (modify/create)
- tests/net/fodt/ (modify/create)

## Prohibited Actions

- No Gate 11 approval claims
- No NuGet publish
- No code outside src/net/fodt/ and tests/net/fodt/

## Tests Required

- Unit tests for each entity class
- Round-trip fidelity tests against reference FODT files
- Edit-and-save tests
- Regression tests for existing Tier 0 functionality

## Next Dependency

- FODT-COMMERCIAL-EDIT-SAVE-VERTICAL-SLICE (refinement)
- FODT-COMMERCIAL-EXPORT-HTML-PDF-PNG (export pipeline)
