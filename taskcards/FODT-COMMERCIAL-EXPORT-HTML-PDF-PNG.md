# Taskcard: FODT-COMMERCIAL-EXPORT-HTML-PDF-PNG

**Status:** not_started
**Created:** 2026-05-13
**Sprint:** (awaiting explicit human-authorized implementation sprint)
**Depends on:** FODT-COMMERCIAL-LOAD-SAVE-MODEL

## Purpose

Implement export/conversion from FODT document object model to PDF, HTML, PNG, and related formats (ODT).

## Scope

- Implement `FodtDocument.ExportToHtml()` — structural HTML conversion
- Implement `FodtDocument.ExportToPdf()` — PDF rendering pipeline
- Implement `FodtDocument.ExportToPng()` — page image rendering
- Implement `FodtDocument.SaveAs(path, format)` — family format conversion (e.g., ODT)
- Document supported feature subsets per export format
- All code under `src/net/fodt/`

## Non-Goals

- Full formatting fidelity in all export targets (initial release may have feature subset)
- Interactive/viewer features
- Web application integration

## Acceptance Criteria

- [ ] HTML export: valid HTML output with paragraph/list/table structure preserved
- [ ] PDF export: readable PDF with text and basic formatting
- [ ] PNG export: image output of document pages
- [ ] ODT export: valid ODT file (ZIP-based) with content preserved
- [ ] Export fidelity documented per format
- [ ] Capability level C9 per capability model

## Evidence Requirements

- Export test results
- Sample outputs for visual inspection
- Capability level assessment

## Files Allowed

- src/net/fodt/ (modify/create)
- tests/net/fodt/ (modify/create)

## Prohibited Actions

- No Gate 11 approval claims
- No publish/package

## Tests Required

- Export output validation per format
- Content verification (exported values match source)
- Rendering regression tests

## Next Dependency

- Gate 11 human review (after C9+ achieved)
