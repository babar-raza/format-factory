# aspose-format-factory-zst

Python FOSS codec for the Zstandard (ZST) compression format.

**Package:** `aspose-format-factory-zst`
**Version:** 0.1.0.dev0
**Track:** python-foss
**Capability Level:** alpha-foss-preview
**License:** Apache-2.0
**Spec:** RFC 8878 (Zstandard Compression)
**Gate history:** Gates 1-7 PASSED (format-factory project)

---

## Quick Start

```python
from zst import compress_bytes, decompress_bytes, probe_frame, validate_file

# Compress data
compressed = compress_bytes(b"Hello, Zstandard!")

# Decompress data
original = decompress_bytes(compressed)

# Probe a .zst frame header
info = probe_frame("path/to/file.zst")
print(info)

# Validate a .zst file
result = validate_file("path/to/file.zst")
```

## Security Notes

- Decompression output capped at 256 MiB by default.
- Window size guard at 2 GiB (Zstandard bomb protection).
- No external dependencies beyond `zstandard` (python-zstandard).

## Dependencies

- `zstandard>=0.21.0`

## Package Structure

```
src/python/zst/
    __init__.py          Public API exports
    zst_codec.py         Core ZST compress/decompress/probe API
    LICENSE              Apache-2.0 license
    README.md            This file
```
