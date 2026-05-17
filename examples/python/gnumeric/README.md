# Gnumeric Examples — Gnumeric Spreadsheet

**Status:** ALPHA FOSS PREVIEW — NOT FOR COMMERCIAL USE
**Package:** aspose-format-factory-gnumeric
**capability_level:** alpha-foss-preview
**commercial_product_ready:** false

## What This Does

Demonstrates the `gnumeric` Python FOSS codec: load a .gnumeric file
(gzip-compressed XML), count sheets and cells, and extract cell values.

## Requirements

- Python 3.9+
- No external dependencies (stdlib: gzip + xml.etree.ElementTree)
- No network access required

## Sample Files

Uses `samples/by-format/gnumeric/` from the repository root.

## Run

```bash
cd <repo-root>
PYTHONPATH=src/python python examples/python/gnumeric/extract_cells.py
```

## Expected Output

```
Gnumeric FOSS Example — alpha-foss-preview
File: minimal-spreadsheet.gnumeric
  Sheets: 1
  Cells: N
  Values: [...]
```

## What Is NOT Supported

- No formula evaluation
- No chart/image extraction
- No write/modify operations
- Not for commercial use
