# ZST Examples — Zstandard Compression

**Status:** ALPHA FOSS PREVIEW — NOT FOR COMMERCIAL USE
**Package:** aspose-format-factory-zst
**capability_level:** alpha-foss-preview
**commercial_product_ready:** false

## What This Does

Demonstrates the `zst` Python FOSS codec: compress bytes, decompress bytes,
probe a ZST frame header, and validate a ZST file.

## Requirements

- Python 3.9+
- `zstandard` package: `pip install zstandard`
- No network access required

## Sample Files

Uses `samples/by-format/zst/` from the repository root.

## Run

```bash
cd <repo-root>
PYTHONPATH=src/python python examples/python/zst/compress_decompress_file.py
```

## Expected Output

```
ZST FOSS Example — alpha-foss-preview
compress_bytes: 100 bytes → N bytes compressed
decompress_bytes: N bytes → 100 bytes (round-trip OK)
probe_frame: {'magic': '28b52ffd', 'is_valid': True, ...}
validate_file: VALID (or SKIPPED if no sample file)
```

## What Is NOT Supported

- No streaming compression for large files
- No multi-frame concatenation handling
- No dictionary compression
- No .tar.zst handling
- Not for commercial use
