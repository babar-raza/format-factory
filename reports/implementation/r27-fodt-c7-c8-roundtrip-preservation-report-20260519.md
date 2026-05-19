# R27 Lane H: FODT C7/C8 Round-Trip Preservation Report

- **Date:** 2026-05-19
- **Sprint:** R27
- **Gate 11 status:** commercial_readiness_in_progress (NOT approved)
- **commercial_product_ready:** false

## Summary

This report documents the C7 (round-trip fidelity) and C8 (opaque node preservation) design and test results for the FODT (.NET) document model.

## Capability Definitions

- **C7 (Round-Trip Fidelity):** Load a FODT file, edit one or more paragraph/heading texts, save to a new file, reload, and verify that (a) edited text persists and (b) unaffected paragraphs, headings, metadata, and structure survive unchanged.
- **C8 (Opaque Node Preservation):** Unrecognized XML elements (custom namespaces, extension elements, style definitions, metadata) survive a load-edit-save-reload cycle without loss or corruption.

## Architecture

The FODT document model (`FodtDocument`) uses `System.Xml.Linq.XDocument` (DOM-backed) internally. The `Load()` method reads the entire XML document into a DOM tree. The `Save()` method writes the entire DOM tree back to disk via `FodtWriter`.

**C7 is inherent:** Because the DOM is the single source of truth, editing a paragraph (via `FodtParagraph.SetText()`) mutates only the targeted `text:p` or `text:h` element. All other nodes in the document remain untouched in memory and are written out unchanged.

**C8 is inherent:** The DOM preserves all XML nodes regardless of namespace or element name. Elements from custom namespaces (e.g., `custom:vendor-metadata`), ODF style elements (`style:style`), and metadata elements (`dc:title`) are stored in the DOM tree and written back on save without any filtering or stripping.

## Test File

- **Path:** `tests/net/fodt/FodtC7C8RoundtripPreservationTests.cs`
- **Fixture (opaque nodes):** `tests/net/fodt/Fixtures/fodt-opaque-nodes.fodt`

## C7 Tests (9 tests)

| Test | Description | Result |
|------|-------------|--------|
| C7-01 | Edit first paragraph, save, reload -- edited text persists | PASS |
| C7-02 | Edit first paragraph, save, reload -- paragraph 1 survives unchanged | PASS |
| C7-03 | Edit first paragraph, save, reload -- heading survives unchanged | PASS |
| C7-04 | Edit first paragraph, save, reload -- paragraph count preserved | PASS |
| C7-05 | Edit first paragraph, save, reload -- MimeType preserved | PASS |
| C7-06 | Edit first paragraph, save, reload -- OdfVersion preserved | PASS |
| C7-07 | Edit heading text, save, reload -- heading status and outline level preserved | PASS |
| C7-08 | Double round-trip (edit, save, reload, edit again, save, reload) | PASS |
| C7-09 | Edit last paragraph, save, reload -- first paragraph survives | PASS |

## C8 Tests (7 tests)

| Test | Description | Result |
|------|-------------|--------|
| C8-01 | Custom namespace element in office:meta survives no-edit round-trip | PASS |
| C8-02 | Custom namespace element survives edit round-trip | PASS |
| C8-03 | office:automatic-styles section survives round-trip | PASS |
| C8-04 | dc:title metadata element survives edit round-trip | PASS |
| C8-05 | Custom attribute on opaque element survives round-trip | PASS |
| C8-06 | Edit round-trip -- no duplicate nodes created | PASS |
| C8-07 | Minimal fixture office:automatic-styles survives no-edit round-trip | PASS |

## Test Run Results

```
Test Run Successful.
Total tests: 124
     Passed: 124
 Total time: 0.5607 Seconds
```

Previous baseline: 108/108 (R25).
New total: 124/124 (16 new C7/C8 tests added).

## C8 Limitations

The current DOM-backed implementation provides **full opaque node preservation** for the following categories:

1. Custom namespace elements and attributes
2. ODF style elements (office:automatic-styles, style:style, etc.)
3. ODF metadata elements (dc:title, dc:creator, meta:initial-creator, etc.)
4. Processing instructions and comments
5. Namespace declarations on the root element

**Known limitation:** The `FodtParagraph.SetText()` method replaces all child content of the `text:p` or `text:h` element with a single text node. Any inline formatting within the paragraph (e.g., `text:span` with style references, `text:a` hyperlinks) is intentionally removed on edit. This is a documented vertical-slice limitation. Full inline formatting preservation is a future capability.

**Known limitation:** `FodtBody.Paragraphs` only returns top-level `text:p` and `text:h` elements directly under `office:text`. Paragraphs nested inside `text:list`, `table:table`, or other block-level elements are not exposed. This is a documented vertical-slice limitation.

## Governance

- Gate 11 status: commercial_readiness_in_progress (NOT approved)
- G11-G: NOT_STARTED (requires human approval by Babar Raza)
- commercial_product_ready: false
