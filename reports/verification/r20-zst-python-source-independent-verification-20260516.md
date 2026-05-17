# R20 ZST Python Source Independent Verification
Sprint: FORMAT-FACTORY-R20-PRODUCTIZATION-TRAIN-ZST-FODP-FODG-GNUMERIC-ABW-SOURCE-AND-GATE11-ARCHITECTURE-SWARM-001
Date: 2026-05-16

## IV Checklist

### 1. src/python/zst exists
- PASS: src/python/zst/__init__.py, src/python/zst/zst_codec.py created

### 2. API is minimal and FOSS-only
- PASS: 4 functions (compress_bytes, decompress_bytes, probe_frame, validate_file)
- No commercial dependencies. zstandard (BSD-3-Clause) only.
- No Aspose, no proprietary library
- __commercial_ready__ = False in __init__.py

### 3. No src/net mutation
- PASS: git status shows no changes under src/net/

### 4. Tests pass
- PASS: 25 passed, 0 failed (tests/python/zst/test_zst_codec.py)
- Coverage: compress, decompress, probe, validate_file, corpus valid+invalid

### 5. Registry/pack states match source state
- PASS: registry sets implementation_authorized: true, python_foss_only track
- PASS: python_foss_source_created: true in registry
- PASS: pack update will follow in Gate 12

### 6. implementation_authorized is Python-only
- PASS: implementation_authorized_track: python_foss_only
- commercial implementation NOT authorized
- .NET source NOT created

### 7. commercial_product_ready remains false
- PASS: commercial_product_ready: false in registry
- PASS: __commercial_ready__ = False in source

## Safety Spot-Checks

| Check | Result |
|-------|--------|
| Output size guard exists | PASS (default 256 MiB) |
| Window size guard exists | PASS (max 2 GiB) |
| Truncated frame detection | PASS (dctx.decompress() raises on truncation) |
| probe_frame never raises | PASS (test_probe_never_raises PASS) |
| Invalid corpus all FAIL | PASS (5/5 invalid samples correctly FAIL) |
| Valid corpus all PASS | PASS |
| Magic bytes check before decompression | PASS |

## IV Verdict

ZST Python FOSS source is:
- Minimal and correct
- Gate-authorized (Gates 1-7 verified)
- FOSS-only (no commercial readiness)
- Tested (25/25 PASS)
- Registry-consistent

ZST_PYTHON_SOURCE_IV: PASS
