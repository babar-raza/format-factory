# FODP Examples — Flat OpenDocument Presentation

**Status:** ALPHA FOSS PREVIEW — NOT FOR COMMERCIAL USE
**Package:** aspose-format-factory-fodp
**capability_level:** alpha-foss-preview
**commercial_product_ready:** false

## What This Does

Demonstrates the `fodp` Python FOSS codec: load a .fodp file,
count slides, and extract text content.

## Requirements

- Python 3.9+
- No external dependencies (stdlib only)
- No network access required

## Sample Files

Uses `samples/by-format/fodp/` from the repository root.

## Run

```bash
cd <repo-root>
PYTHONPATH=src/python python examples/python/fodp/extract_presentation_text.py
```

## Expected Output

```
FODP FOSS Example — alpha-foss-preview
File: minimal-presentation.fodp
  Pages: 1
  Text: ['Welcome']
```

## What Is NOT Supported

- No slide rendering or image export
- No embedded media extraction
- No write/modify operations
- No ODP (compressed) format support (use LibreOffice to convert first)
- Not for commercial use
