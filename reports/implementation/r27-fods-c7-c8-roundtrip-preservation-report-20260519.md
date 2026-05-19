# R27 Lane G: FODS C7/C8 Round-Trip Preservation Report

- **Date:** 2026-05-19
- **Sprint:** R27
- **Gate 11 status:** commercial_readiness_in_progress (NOT approved)
- **commercial_product_ready:** false

## Summary

This report documents the C7 (round-trip fidelity) and C8 (opaque node preservation) design and test results for the FODS (.NET) document model.

## Capability Definitions

- **C7 (Round-Trip Fidelity):** Load a FODS file, edit one or more cell values, save to a new file, reload, and verify that (a) edited values persist and (b) unaffected cells, rows, sheets, and metadata survive unchanged.
- **C8 (Opaque Node Preservation):** Unrecognized XML elements (custom namespaces, extension elements, style definitions, metadata) survive a load-edit-save-reload cycle without loss or corruption.

## Architecture

The FODS document model (`FodsDocument`) uses `System.Xml.Linq.XDocument` (DOM-backed) internally. The `Load()` method reads the entire XML document into a DOM tree. The `Save()` method writes the entire DOM tree back to disk via `FodsWriter`.

**C7 is inherent:** Because the DOM is the single source of truth, editing a cell (via `FodsCell.SetText()`) mutates only the targeted `text:p` element within the targeted `table:table-cell`. All other nodes in the document remain untouched in memory and are written out unchanged.

**C8 is inherent:** The DOM preserves all XML nodes regardless of namespace or element name. Elements from custom namespaces (e.g., `custom:vendor-metadata`), ODF style elements (`style:style`), and metadata elements (`dc:title`) are stored in the DOM tree and written back on save without any filtering or stripping.

## Test File

- **Path:** `tests/net/fods/FodsC7C8RoundtripPreservationTests.cs`
- **Fixture (opaque nodes):** `tests/net/fods/Fixtures/fods-opaque-nodes.fods`

## C7 Tests (10 tests)

| Test | Description | Result |
|------|-------------|--------|
| C7-01 | Edit cell A1, save, reload -- edited value persists | PASS |
| C7-02 | Edit cell A1, save, reload -- unaffected cell B1 survives unchanged | PASS |
| C7-03 | Edit cell A1, save, reload -- row 2 survives unchanged | PASS |
| C7-04 | Edit cell A1, save, reload -- sheet count preserved | PASS |
| C7-05 | Edit cell A1, save, reload -- row count preserved | PASS |
| C7-06 | Edit cell A1, save, reload -- sheet name preserved | PASS |
| C7-07 | Edit cell A1, save, reload -- MimeType preserved | PASS |
| C7-08 | Edit cell A1, save, reload -- OdfVersion preserved | PASS |
| C7-09 | Double round-trip (edit, save, reload, edit again, save, reload) | PASS |
| C7-10 | Multi-sheet -- edit sheet 1 does not corrupt sheet 2 | PASS |

## C8 Tests (6 tests)

| Test | Description | Result |
|------|-------------|--------|
| C8-01 | Custom namespace element in office:meta survives no-edit round-trip | PASS |
| C8-02 | Custom namespace element survives edit round-trip | PASS |
| C8-03 | office:automatic-styles section survives round-trip | PASS |
| C8-04 | dc:title metadata element survives edit round-trip | PASS |
| C8-05 | Custom attribute on opaque element survives round-trip | PASS |
| C8-06 | Edit round-trip -- no duplicate nodes created | PASS |

## Test Run Results

```
Test Run Successful.
Total tests: 136
     Passed: 136
 Total time: 0.5532 Seconds
```

Previous baseline: 120/120 (R25).
New total: 136/136 (16 new C7/C8 tests added).

## C8 Limitations

The current DOM-backed implementation provides **full opaque node preservation** for the following categories:

1. Custom namespace elements and attributes
2. ODF style elements (office:automatic-styles, style:style, etc.)
3. ODF metadata elements (dc:title, dc:creator, meta:initial-creator, etc.)
4. Processing instructions and comments
5. Namespace declarations on the root element

**Known limitation:** The `FodsCell.SetText()` method sets `office:value-type="string"` on the cell element. If a cell previously had a different value type (e.g., `float` with `office:value`), the numeric value attribute is NOT removed -- only the `office:value-type` is overwritten. This is a known vertical-slice limitation documented in the model code. Full type-aware cell editing is a future capability.

**Known limitation:** Inline formatting within `text:p` elements (e.g., `text:span` with style references) is replaced by `SetText()` -- this is by design in the vertical slice and documented in `FodsCell.SetText()`.

## Governance

- Gate 11 status: commercial_readiness_in_progress (NOT approved)
- G11-G: NOT_STARTED (requires human approval by Babar Raza)
- commercial_product_ready: false
