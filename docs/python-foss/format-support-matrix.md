# Python FOSS Format Support Matrix

**Status:** ALPHA FOSS PREVIEW â€” NOT PUBLISHED
**Date:** 2026-05-17 (updated R23)
**commercial_product_ready:** false
**publication_authorized:** false

## Supported Formats

| Format | Extension | Package | Gates | Status |
|--------|-----------|---------|-------|--------|
| Zstandard | .zst | aspose-format-factory-zst | 1-7 passed, 8-10 ready | alpha-foss-preview |
| Flat OpenDocument Presentation | .fodp | aspose-format-factory-fodp | 1-7 passed, 8-10 ready | alpha-foss-preview |
| Flat OpenDocument Graphics | .fodg | aspose-format-factory-fodg | 1-7 passed, 8-10 ready | alpha-foss-preview |
| Gnumeric Spreadsheet | .gnumeric | aspose-format-factory-gnumeric | 1-7 passed, 8-10 ready | alpha-foss-preview |
| AbiWord Document | .abw | aspose-format-factory-abw | 1-7 passed, 8-10 ready | alpha-foss-preview |

## Deferred / Rejected Formats

| Format | Extension | Status | Reason |
|--------|-----------|--------|--------|
| OpenRaster | .ora | DEFERRED_BORDERLINE | Gate 1 score 6.8/10 < 7.0 |
| Apple Numbers | .numbers | FORMAL_REJECT | Category 5 closed vendor |

## Capability Summary by Format

### ZST (Zstandard)
- **Works:** compress_bytes, decompress_bytes, probe_frame, validate_file
- **Doesn't work:** streaming, multi-frame, dictionary compression, .tar.zst
- **Dependency:** zstandard>=0.21.0 (pure FOSS)
- **Size limit:** 256 MiB decompressed output

### FODP (Flat OpenDocument Presentation)
- **Works:** load, get_page_count, extract_text, get_page_metadata
- **Doesn't work:** slide rendering, embedded media, write/modify, ODP (zipped)
- **Dependency:** none (stdlib only)
- **Size limit:** 64 MiB file

### FODG (Flat OpenDocument Graphics)
- **Works:** load, get_page_count, get_shape_count, extract_text, get_page_metadata
- **Doesn't work:** SVG/PNG export, embedded image extraction, write/modify, ODG (zipped)
- **Dependency:** none (stdlib only)
- **Size limit:** 64 MiB file

### Gnumeric
- **Works:** load, get_sheet_count, get_cell_count, extract_values, get_sheet_metadata
- **Doesn't work:** formula evaluation, charts, write/modify
- **Dependency:** none (stdlib: gzip + xml.etree)
- **Size limit:** 64 MiB compressed file

### ABW (AbiWord)
- **Works:** load, get_section_count, get_paragraph_count, extract_text
- **Doesn't work:** DOCX/PDF conversion, tables, footnotes, write/modify
- **Dependency:** none (stdlib: xml.etree)
- **Security:** DOCTYPE stripped before parsing
- **Size limit:** 64 MiB file

## Relationship to Aspose Commercial Products

These Python FOSS packages are an **independent FOSS track**, separate from the Aspose .NET commercial products.

- Aspose.Slides, Aspose.Cells, Aspose.Words: Full-featured commercial .NET products
- These Python packages: Minimal read-only FOSS implementations, alpha quality
- No Aspose .NET libraries are used in these Python packages
- No commercial licensing applies to the Python packages (Apache-2.0)

## Publication Status

**Not published.** No PyPI packages. No GitHub releases.
`publication_authorized: false` for all packages.


## R23 Validation Results (Publication Dry-Run)

All 5 Python FOSS packages validated in R23 sprint:

| Format   | Wheel Build | Isolated Install | API Consistency | Version    |
|----------|-------------|-----------------|-----------------|------------|
| zst      | PASS        | PASS            | PASS (43/43)    | 0.1.0.dev0 |
| fodp     | PASS        | PASS            | PASS (43/43)    | 0.1.0.dev0 |
| fodg     | PASS        | PASS            | PASS (43/43)    | 0.1.0.dev0 |
| gnumeric | PASS        | PASS            | PASS (43/43)    | 0.1.0.dev0 |
| abw      | PASS        | PASS            | PASS (43/43)    | 0.1.0.dev0 |

Tested by: tests/packaging/test_python_installed_wheels.py (25/25) and tests/python/test_cross_format_api_consistency.py (43/43).

**PUBLICATION BLOCKED** — . See release-manifests/python-foss/publication-packet/.

## Commercial Readiness

`commercial_product_ready: false` for all formats and both tracks (Python FOSS and .NET).
