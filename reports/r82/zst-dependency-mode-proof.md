# R82 Train K — ZST Dependency Mode Proof

**Sprint:** FORMAT-FACTORY-R82
**Date:** 2026-05-31

## Objective

Clarify ZST's role: is it a standalone format parser or a compression dependency for other formats? Prove compression/decompression functions work from the installed wheel.

## ZST Classification

**Classification:** ZST_DEPENDENCY_MODE — the `zst` package is a compression library dependency
- It provides `compress_bytes` / `decompress_bytes` / `probe` APIs
- It is NOT a format parser producing human-readable output
- Other packages (e.g., future archive formats) may depend on it for ZStandard compression
- The `probe()` function validates ZStandard frame headers (magic: 0xFD2FB528)

## Test Environment

- **Venv:** `.local/venv-zst-proof/` — isolated
- **Package:** `aspose_format_factory_zst-0.1.0.dev0-py3-none-any.whl` (9780 bytes)
- **Import:** `import zst` (canonical namespace)

## Proof Steps

| Step | Operation | Result |
|------|-----------|--------|
| 1 | `import zst` | PASS |
| 2 | `zst.__version__ == "0.1.0.dev0"` | PASS |
| 3 | `zst.__track__ == "python-foss"` | PASS |
| 4 | `zst.probe(b"not-zst-data")` | PASS — returns probe dict with valid=False |
| 5 | `probe["magic_ok"] == False` | PASS — correct for non-ZST data |
| 6 | `zst.compress_bytes(b"hello world")` | PASS — returns bytes |
| 7 | `zst.decompress_bytes(compressed)` → b"hello world" | PASS |
| 8 | Roundtrip verified | PASS |

## Raw Output

```
ZST_NAMESPACE: zst
ZST_VERSION: 0.1.0.dev0
ZST_TRACK: python-foss
PROBE_RESULT: {'valid': False, 'magic_ok': False, 'decompressed_size': None, 'decompression_error': 'Not a ZST frame'}
PROBE_MODE: PASS
COMPRESS_DECOMPRESS: PASS
ZST_DEPENDENCY_ROUNDTRIP: PASS
```

## ZST Dependency Classification

The `zst` package serves as a **compression dependency layer**:
- Gates 1-10 PASSED (R78)
- `commercial_product_ready: false`
- No human-readable output — byte-level compression only
- Suitable as a dependency for archive format parsers

The ZST classification is **NOT a format parser** in the FODS/FODT sense. It is a compression utility that enables:
1. Standalone ZStandard compression/decompression
2. Building blocks for future archive-format integration (e.g., Zstandard-compressed archives)

## ZST_DEPENDENCY_MODE_CLASSIFICATION: CONFIRMED
## ZST_INSTALLED_WHEEL_PROOF: PASS
