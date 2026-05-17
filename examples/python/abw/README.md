# ABW Examples — AbiWord Document

**Status:** ALPHA FOSS PREVIEW — NOT FOR COMMERCIAL USE
**Package:** aspose-format-factory-abw
**capability_level:** alpha-foss-preview
**commercial_product_ready:** false

## What This Does

Demonstrates the `abw` Python FOSS codec: load a .abw file
(plain XML AWML 1.0), count sections and paragraphs, and extract text.

## Requirements

- Python 3.9+
- No external dependencies (stdlib: xml.etree.ElementTree)
- No network access required

## Sample Files

Uses `samples/by-format/abw/` from the repository root.

## Run

```bash
cd <repo-root>
PYTHONPATH=src/python python examples/python/abw/extract_text.py
```

## Expected Output

```
ABW FOSS Example — alpha-foss-preview
File: minimal-document.abw
  Sections: 1
  Paragraphs: N
  Text: [...]
```

## What Is NOT Supported

- No DOCX/PDF conversion
- No write/modify operations
- No embedded image extraction
- Not for commercial use
