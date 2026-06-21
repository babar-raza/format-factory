# FODT Release Notes — v0.1.0

**Package:** `aspose-format-factory-fodt`
**Version:** 0.1.0
**Release Date:** 2026-06-21
**Track:** Python FOSS
**Format:** Flat OpenDocument Text (OASIS ODF 1.3)

---

## Summary

First pre-release of the Format Factory FODT Python package.
Provides parse, inspect, edit, and export capabilities for `.fodt` (Flat OpenDocument Text) files.

This is a `v0.1.0` developer release. Not yet published to PyPI.
Commercial .NET product is separately tracked under `aspose-format-factory-fodt` NuGet.

---

## Features

### Parse
- `parse_fodt(path)` — Load a FODT file into a document dict
- `parse_fodt_strict(path)` — Strict mode with structural validation
- ODF 1.3 compliant XML parsing with security hardening
- File size guard: configurable via `MAX_FILE_BYTES` (default 100 MB)

### Write
- `write_fodt(document, path)` — Serialize document dict to `.fodt` XML
- `document_to_xml(document)` — In-memory XML serialization

### Text Access and Editing
- `document_get_paragraph_text(doc, index)` — Read paragraph by index
- `document_set_paragraph_text(doc, index, text)` — Write paragraph text
- `document_append_paragraph(doc, text)` — Add new paragraph at end
- `document_remove_paragraph(doc, index)` — Remove paragraph
- `document_remove_all_paragraphs(doc)` — Clear all content

### Heading Operations
- `document_heading_outline(doc)` — Structured heading list with levels
- `document_get_heading_texts(doc)` — All heading strings in order
- `document_heading_level_distribution(doc)` — Heading count by level
- `insert_heading(doc, text, level)`, `remove_heading(doc, index)`

### Export
- `document_to_text(doc)` — Plain text export

### Statistics (141 total public functions)
- `document_stats`, `document_word_count`, `document_get_char_count`, `document_reading_level`
- `document_table_summary`, `document_list_stats`, `document_hyperlink_count`
- `document_footnote_count`, `document_image_frame_list`, `document_section_summary`
- Full list: see `docs/api/fodt.md`

---

## Test Evidence

| Suite | Count | Status |
|-------|-------|--------|
| .NET commercial (567 tests) | 567/567 | PASS |
| Install proof (Sprint R129) | Wheel + import + API smoke | PASS |

---

## Known Limitations

1. **Dict-based API** — Document model is a plain Python dict, not a class-based object model.
   Class-based migration is planned for a future release.

2. **No PDF/PNG export** — Python track does not include PDF or PNG rendering.
   PDF rendering is available in the .NET commercial product only.

3. **No FODT-to-ODT conversion** — Family-format conversion (FODT ↔ ODT) is not yet implemented.

4. **Table support is read-only** — Table parsing is supported; table editing via Python API is not.

5. **Formula cells not supported** — No formula evaluation engine is included.

---

## Breaking Changes

None (first release).

---

## Installation

```bash
pip install aspose-format-factory-fodt
```

Or from source:

```bash
cd src/python/fodt
python -m build --wheel
pip install dist/aspose_format_factory_fodt-0.1.0-py3-none-any.whl
```

---

## License

Apache-2.0
