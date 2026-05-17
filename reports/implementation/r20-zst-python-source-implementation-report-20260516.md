# R20 ZST Python Source Implementation Report
Sprint: FORMAT-FACTORY-R20-PRODUCTIZATION-TRAIN-ZST-FODP-FODG-GNUMERIC-ABW-SOURCE-AND-GATE11-ARCHITECTURE-SWARM-001
Date: 2026-05-16

## Authorization

- ZST Gates 1-7: all PASSED (G5 waived — G-NORM-004 codec/no-DOM)
- R20 sprint prompt explicitly authorizes Python FOSS source for ZST
- implementation_authorized: true (python_foss_only) — set in registry

## Source Created

### src/python/zst/

- `__init__.py` — package init, exports public API, declares __commercial_ready__ = False
- `zst_codec.py` — full codec implementation

### API Surface

| Function | Signature | Description |
|----------|-----------|-------------|
| `compress_bytes` | `(data: bytes, level: int = 3) -> bytes` | Compress to Zstandard frame |
| `decompress_bytes` | `(data: bytes, max_output_size: int = 256MiB) -> bytes` | Decompress with size guard |
| `probe_frame` | `(data: bytes) -> dict` | Non-raising frame probe |
| `validate_file` | `(path) -> dict` | File-level validation |

### Exception Hierarchy

- `ZstError` — base
- `ZstInvalidFrameError` — invalid magic / frame header
- `ZstDecompressionError` — decompression failure
- `ZstOutputLimitExceeded` — output size guard triggered

### Key Safety Features

1. Magic bytes check before decompression (ZSTD_MAGIC = b"\x28\xb5\x2f\xfd")
2. Output size guard (default 256 MiB) via streaming decompression
3. Window size guard (max 2 GiB) via ZstdDecompressor(max_window_size=...)
4. Truncated frame detection: uses `dctx.decompress()` first (raises on truncation),
   falls back to streaming only for frames without declared content_size
5. `probe_frame` never raises — always returns dict with error field

### Dependency Strategy

- Requires python-zstandard (`zstandard` package, BSD-3-Clause, v0.25.0 verified)
- No vendored dependencies
- Clear error if zstandard not installed
- No commercial library usage

## Tests Created

### tests/python/zst/test_zst_codec.py

25 tests:
- compress_bytes: 5 tests (magic, size, levels, input type, level validation)
- decompress_bytes round-trip: 3 tests (basic, empty, binary)
- decompress_bytes invalid: 4 tests (wrong magic, truncated magic, type, truncated frame)
- output guard: 3 tests (triggers, within limit, disabled)
- probe_frame: 5 tests (valid, wrong magic, too short, non-bytes, never-raises)
- validate_file: 5 tests (valid, not found, wrong magic, corpus valid, corpus invalid)

**Test Result:** 25 passed, 0 failed

## Corpus Test Coverage

- Valid corpus: samples/by-format/zst/valid/ (all PASS)
- Invalid corpus: samples/by-format/zst/invalid/generated/ (all correctly FAIL)
  - claimed-large-truncated.zst: ZstDecompressionError (did not decompress full frame)
  - corrupted-block-data.zst: ZstDecompressionError (Data corruption detected)
  - magic-only-no-fhd.zst: ZstDecompressionError (error determining content size)
  - truncated-header-2b.zst: ZstInvalidFrameError (too short)
  - wrong-magic.zst: ZstInvalidFrameError (invalid magic)

## Governance Compliance

- FOSS track only: YES
- No src/net mutation: YES
- commercial_product_ready: false — YES
- No package publishing: YES
- No commercial branding: YES

ZST_PYTHON_SOURCE_IMPLEMENTATION: COMPLETE
