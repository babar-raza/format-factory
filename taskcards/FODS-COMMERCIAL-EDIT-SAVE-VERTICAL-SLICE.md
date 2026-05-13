# Taskcard: FODS-COMMERCIAL-EDIT-SAVE-VERTICAL-SLICE

**Status:** not_started
**Created:** 2026-05-13
**Sprint:** (awaiting explicit human-authorized implementation sprint)
**Depends on:** FODS-COMMERCIAL-LOAD-SAVE-MODEL

## Purpose

Implement and validate a complete edit-and-save vertical slice for FODS: load a document, programmatically edit cell values/styles, save back to FODS, and verify the edit is present in the output.

## Scope

- Implement typed cell value setters (string, number, date, boolean, formula)
- Implement basic style modification (bold, italic, font size, cell background)
- Implement row/column insertion and deletion
- Implement sheet add/remove/rename
- End-to-end test: load -> edit -> save -> reload -> verify

## Non-Goals

- Complex formatting (conditional formatting, charts, pivot tables)
- Export to non-FODS formats
- Performance optimization

## Acceptance Criteria

- [ ] Cell value edit: modify string/number/date cell, save, verify
- [ ] Style edit: modify bold/italic, save, verify
- [ ] Structural edit: add row, add sheet, save, verify
- [ ] Round-trip: edits survive load-save-reload cycle
- [ ] No data loss on unsupported features (opaque preservation)
- [ ] Capability level C7 confirmed per capability model

## Evidence Requirements

- Test results for all edit operations
- Round-trip fidelity report
- Capability level C7 evidence

## Files Allowed

- src/net/fods/ (modify)
- tests/net/fods/ (modify/create)

## Prohibited Actions

- No Gate 11 approval claims
- No publish/package

## Tests Required

- Edit-and-save tests per entity type
- Round-trip regression tests
- Opaque preservation tests

## Next Dependency

- FODS-COMMERCIAL-EXPORT-HTML-PDF-PNG
