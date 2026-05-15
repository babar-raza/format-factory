# R16 ZST Sample Corpus Validation Report
Sprint: FORMAT-FACTORY-R16-ZST-GATE3B-CORPUS-ACQUISITION-IV-AND-MULTI-FORMAT-INTAKE-SWARM-001
Date: 2026-05-15
Gate: 4 — Corpus validation tooling and tests

## Test Suite: test_zst_gate3b_sample_corpus.py

File: `tests/skills/test_zst_gate3b_sample_corpus.py`
Tests collected: 57
Tests passed: 57
Tests failed: 0
Run command: `python -m pytest tests/skills/test_zst_gate3b_sample_corpus.py -v`

**RESULT: 57/57 PASS**

## Test Coverage

### 1. Directory Structure (3 tests)
- `test_samples_zst_directory_exists` — PASS
- `test_valid_subdirectory_exists` — PASS
- `test_invalid_subdirectory_exists` — PASS

### 2. Valid Files Present (8 parametrized tests)
All 8 expected valid .zst files present and non-empty:
- `block-128k.zst` — PASS
- `empty-block.zst` — PASS
- `rle-first-block.zst` — PASS
- `zeroSeq_2B.zst` — PASS
- `minimal-synthetic.zst` — PASS
- `text-compressed.zst` — PASS
- `dict-compressed.zst` — PASS
- `random-data.zst` — PASS

### 3. Invalid Files Present (3 parametrized tests)
All 3 expected invalid .zst files present and non-empty:
- `off0.bin.zst` — PASS
- `truncated_huff_state.zst` — PASS
- `zeroSeq_extraneous.zst` — PASS

### 4. SHA-256 Integrity (11 parametrized tests)
All 11 files match expected SHA-256 hashes from manifest — PASS

### 5. Valid Sample Decompression (8 parametrized tests)
All 8 valid frames decompressed via `zstandard.ZstdDecompressor.stream_reader()`:
- Note: `block-128k.zst`, `empty-block.zst`, `zeroSeq_2B.zst` are upstream golden-decompression
  fixtures that omit `Content_Size` in the frame header; `stream_reader()` handles these correctly.
- All 8 files decompress to bytes without ZstdError — PASS

### 6. Invalid Sample Error Frames (3 parametrized tests)
All 3 invalid frames raise `zstd.ZstdError` as expected:
- `off0.bin.zst` (invalid offset zero) — raises ZstdError ✓
- `truncated_huff_state.zst` (truncated huffman state) — raises ZstdError ✓
- `zeroSeq_extraneous.zst` (extraneous zero sequence) — raises ZstdError ✓

### 7. Corpus Manifest Structure (6 tests)
- `_corpus-manifest.yaml` exists — PASS
- `summary.valid_count == 8` — PASS
- `summary.invalid_count == 3` — PASS
- `summary.total_count == 11` — PASS
- `summary.gate_3_categories_met == true` — PASS
- All valid samples: `decompression_test: PASS` — PASS
- All invalid samples: `expected_error: true` — PASS

### 8. Provenance Completeness (2 tests)
- All 11 entries have `provenance_status: confirmed` — PASS
- All 11 entries have `sha256:` prefix hash — PASS

### 9. Gate 3A Artifacts Intact (5 tests)
- `acquisition-packs/zst/sample-sources.md` present — PASS
- ZST registry entry exists — PASS
- `implementation_authorized: false` — PASS
- `commercial_product_ready: false` — PASS
- Taskcards ZST-R16-GATE3B and ZST-GATE3-IV present — PASS

### 10. No src/ Mutations (2 tests)
- `src/python/zst/` absent — PASS
- `src/net/zst/` absent — PASS

### 11. No generated-requirements/zst (1 test)
- `generated-requirements/zst/` absent — PASS

### 12. Generation Script (2 tests)
- `generate_synthetic_zst.py` exists and is non-empty — PASS

## Technical Notes

### zstandard API Compatibility
- Library version: `zstandard 0.25.0`
- `ZstdDecompressor.decompress()` requires `Content_Size` in frame header
- 3 upstream fixtures (`block-128k.zst`, `empty-block.zst`, `zeroSeq_2B.zst`) compressed without `Content_Size`
- Resolution: use `ZstdDecompressor.stream_reader()` which handles both modes
- This is correct behavior per RFC — `Content_Size` is optional in the ZST frame format

### Provenance YAML Structure
- `_provenance.yaml` uses a mixed header-mapping + sequence format
- Entries extracted by finding first `- sample_id:` line and parsing the sequence independently
- All 11 entries confirmed with `provenance_status: confirmed`

## Summary

| Check | Result |
|-------|--------|
| Corpus directory structure | PASS |
| Valid file count (8) | PASS |
| Invalid file count (3) | PASS |
| SHA-256 integrity (11/11) | PASS |
| Valid frame decompression (8/8) | PASS |
| Invalid frame error detection (3/3) | PASS |
| Manifest structure | PASS |
| Provenance completeness | PASS |
| Gate 3A artifacts preserved | PASS |
| No src/ mutations | PASS |
| No scope drift | PASS |

GATE_4_CORPUS_VALIDATION: PASS
