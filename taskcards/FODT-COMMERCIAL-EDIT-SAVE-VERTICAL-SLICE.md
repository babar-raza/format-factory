# Taskcard: FODT-COMMERCIAL-EDIT-SAVE-VERTICAL-SLICE

**Status:** not_started
**Created:** 2026-05-13
**Sprint:** (awaiting explicit human-authorized implementation sprint)
**Depends on:** FODT-COMMERCIAL-LOAD-SAVE-MODEL

## Purpose

Implement and validate a complete edit-and-save vertical slice for FODT: load a document, programmatically edit paragraphs/styles, save back to FODT, and verify the edit is present in the output.

## Scope

- Implement typed paragraph text setters
- Implement basic style modification (bold, italic, font size, paragraph alignment)
- Implement paragraph/heading insertion and deletion
- Implement list and table modification
- End-to-end test: load -> edit -> save -> reload -> verify

## Non-Goals

- Complex formatting (tracked changes, embedded objects, footnotes)
- Export to non-FODT formats
- Performance optimization

## Acceptance Criteria

- [ ] Text edit: modify paragraph text, save, verify
- [ ] Style edit: modify bold/italic, save, verify
- [ ] Structural edit: add paragraph, add heading, save, verify
- [ ] Round-trip: edits survive load-save-reload cycle
- [ ] No data loss on unsupported features (opaque preservation)
- [ ] Capability level C7 confirmed per capability model

## Evidence Requirements

- Test results for all edit operations
- Round-trip fidelity report
- Capability level C7 evidence

## Files Allowed

- src/net/fodt/ (modify)
- tests/net/fodt/ (modify/create)

## Prohibited Actions

- No Gate 11 approval claims
- No publish/package

## Tests Required

- Edit-and-save tests per entity type
- Round-trip regression tests
- Opaque preservation tests

## Next Dependency

- FODT-COMMERCIAL-EXPORT-HTML-PDF-PNG
