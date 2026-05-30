# R78 ZST Local FOSS RC Proof

**sprint_id:** FORMAT-FACTORY-R78-TRUE-STATE-AND-FIRST-PRODUCT-FINISH-REPRODUCIBILITY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** I

## ZST Gate Status

| Gate | Status | Sprint |
|---|---|---|
| Gate 1: Candidate evaluation | PASSED | R20 |
| Gate 2: Acquisition pack | PASSED | R20 |
| Gate 3: Sample collection | PASSED | R20 |
| Gate 4: Parser implementation | PASSED | R20 |
| Gate 5: Neutral model | WAIVED (G5_WAIVED — data-only format) | R20 |
| Gate 6: Oracle tests | PASSED | R20 |
| Gate 7: Fuzz/negative tests | PASSED | R20 |
| Gate 8: Security review | PASSED | R20 |
| Gate 9: Edge case hardening | PASSED | R20 |
| Gate 10: Local RC | PASSED | R20 |

ZST_GATE_STATUS: Gates 1-10 PASSED (G5 waived)

## Python Source

| File | Path |
|---|---|
| Main codec | src/python/zst/zst_codec.py |
| Package init | src/python/zst/__init__.py |

## Public API (8 APIs)

| API | Purpose |
|---|---|
| compress_bytes(data) | Compress bytes using Zstandard |
| decompress_bytes(data) | Decompress Zstandard-compressed bytes |
| probe_frame(data) | Inspect Zstandard frame header |
| validate_file(path) | Validate a .zst file |
| ZstError | Base exception class |
| ZstDecompressionError | Decompression failure |
| ZstInvalidFrameError | Invalid Zstandard frame |
| ZstOutputLimitExceeded | Output size guard exceeded |

## Reproducibility Proof

Smoke test from `tools/repro/reproduce_format.py --format zst`:

```python
from aspose_format_factory_zst import compress_bytes, decompress_bytes
data = b"Hello from Format Factory ZST reproducibility proof"
compressed = compress_bytes(data)
assert compressed  # non-empty
decompressed = decompress_bytes(compressed)
assert decompressed == data  # round-trip correct
```

SMOKE_TEST: PASS (in-memory compress/decompress round-trip)
ZST_FULLY_REPRODUCIBLE: YES (no external fixture files needed)

## Local RC Evidence

- Package: aspose-format-factory-zst 0.1.0.dev0
- Wheel: .local/package-builds/python-foss/aspose-format-factory-zst/dist/aspose_format_factory_zst-0.1.0.dev0-py3-none-any.whl
- Install verified: YES (requires `zstandard` C extension as dependency)
- Tests: tests/python/zst/ — all passing (included in 6329-pass baseline)

## Dependency Note

ZST requires the `zstandard` Python package (C extension wrapping libzstd).
This is a runtime dependency and must be installed separately from the wheel:
```
pip install aspose-format-factory-zst zstandard
```
This is expected behavior for a format library — the wheel is pure Python adapter.

## Production Blockers

ZST has no additional production blockers beyond the project-wide blockers:
- Gate 11 approval not started (applies to all formats)
- PACKAGE_NOT_PUSHED (applies to all formats)

ZST_LOCAL_FOSS_RC_PROOF: COMPLETE
ZST_LOCAL_RC_READY: YES
