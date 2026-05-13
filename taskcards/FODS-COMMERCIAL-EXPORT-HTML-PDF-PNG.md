# Taskcard: FODS-COMMERCIAL-EXPORT-HTML-PDF-PNG

**Status:** not_started
**Created:** 2026-05-13
**Sprint:** (awaiting explicit human-authorized implementation sprint)
**Depends on:** FODS-COMMERCIAL-LOAD-SAVE-MODEL

## Purpose

Implement export/conversion from FODS document object model to PDF, HTML, PNG, and related formats (ODS).

## Scope

- Implement `FodsDocument.ExportToHtml()` — structural HTML conversion
- Implement `FodsDocument.ExportToPdf()` — PDF rendering pipeline
- Implement `FodsDocument.ExportToPng()` — sheet/page image rendering
- Implement `FodsDocument.SaveAs(path, format)` — family format conversion (e.g., ODS)
- Document supported feature subsets per export format
- All code under `src/net/fods/`

## Non-Goals

- Full formatting fidelity in all export targets (initial release may have feature subset)
- Interactive/viewer features
- Web application integration

## Acceptance Criteria

- [ ] HTML export: valid HTML output with table structure preserved
- [ ] PDF export: readable PDF with cell values and basic formatting
- [ ] PNG export: image output of sheet content
- [ ] ODS export: valid ODS file (ZIP-based) with data preserved
- [ ] Export fidelity documented per format
- [ ] Capability level C9 per capability model

## Evidence Requirements

- Export test results
- Sample outputs for visual inspection
- Capability level assessment

## Files Allowed

- src/net/fods/ (modify/create)
- tests/net/fods/ (modify/create)

## Prohibited Actions

- No Gate 11 approval claims
- No publish/package

## Tests Required

- Export output validation per format
- Content verification (exported values match source)
- Rendering regression tests

## Next Dependency

- Gate 11 human review (after C9+ achieved)
