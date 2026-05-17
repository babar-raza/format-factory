# Python FOSS Examples Index

**Date:** 2026-05-17
**Status:** ALPHA FOSS PREVIEW

## Overview

All examples are local scripts that demonstrate codec usage with sample files from `samples/by-format/`.
No network access required. No installation required (use `PYTHONPATH=src/python`).

## Examples

### ZST (Zstandard)

**Script:** [examples/python/zst/compress_decompress_file.py](../../examples/python/zst/compress_decompress_file.py)
**Run:** `PYTHONPATH=src/python python examples/python/zst/compress_decompress_file.py`
**Demonstrates:** compress_bytes, decompress_bytes, probe_frame, validate_file
**Requirement:** `pip install zstandard` for compress/decompress (probe works without it)

### FODP (Flat OpenDocument Presentation)

**Script:** [examples/python/fodp/extract_presentation_text.py](../../examples/python/fodp/extract_presentation_text.py)
**Run:** `PYTHONPATH=src/python python examples/python/fodp/extract_presentation_text.py`
**Demonstrates:** load, get_page_count, extract_text, get_page_metadata
**Samples:** samples/by-format/fodp/ (3 samples)

### FODG (Flat OpenDocument Graphics)

**Script:** [examples/python/fodg/inspect_drawing_shapes.py](../../examples/python/fodg/inspect_drawing_shapes.py)
**Run:** `PYTHONPATH=src/python python examples/python/fodg/inspect_drawing_shapes.py`
**Demonstrates:** load, get_page_count, get_shape_count, extract_text, get_page_metadata
**Samples:** samples/by-format/fodg/ (3 samples)

### Gnumeric

**Script:** [examples/python/gnumeric/extract_cells.py](../../examples/python/gnumeric/extract_cells.py)
**Run:** `PYTHONPATH=src/python python examples/python/gnumeric/extract_cells.py`
**Demonstrates:** load, get_sheet_count, get_cell_count, extract_values, get_sheet_metadata
**Samples:** samples/by-format/gnumeric/ (3 samples)

### ABW (AbiWord)

**Script:** [examples/python/abw/extract_text.py](../../examples/python/abw/extract_text.py)
**Run:** `PYTHONPATH=src/python python examples/python/abw/extract_text.py`
**Demonstrates:** load, get_section_count, get_paragraph_count, extract_text
**Samples:** samples/by-format/abw/ (3 samples)

## Smoke Tests

All examples are covered by smoke tests:
**Test:** tests/examples/test_python_examples_smoke.py
**Result:** 18 passed

## Alpha Label

All examples display:
```
<Format> FOSS Example — alpha-foss-preview
```
and end with:
```
NOTE: This is alpha-foss-preview. Do not use in production or commercial products.
```
