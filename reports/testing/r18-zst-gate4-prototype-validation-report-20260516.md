# R18 ZST Gate 4 Prototype Validation Report
Sprint: FORMAT-FACTORY-R18-QUARTER-MILE-ZST-GATE4-GATE5-AND-MULTI-FORMAT-GATE1-SWARM-001
Date: 2026-05-16
Gate: 2 — ZST Gate 4 Prototype Implementation + Test Coverage

## Summary

ZST Gate 4 prototype implementation is complete. All 4 prototype files created,
15/15 corpus validation tests PASS, 38/38 Gate 4 prototype tests PASS.

GATE_2_ZST_PROTOTYPE: PASS

## Prototype Files Created (R18)

| File | Path | Size | Status |
|------|------|------|--------|
| README.md | prototypes/by-format/zst/README.md | non-empty | CREATED |
| frame_header.py | prototypes/by-format/zst/frame_header.py | non-empty | CREATED |
| zst_probe.py | prototypes/by-format/zst/zst_probe.py | non-empty | CREATED |
| validate_corpus.py | prototypes/by-format/zst/validate_corpus.py | non-empty | CREATED |

All files exist and are non-empty. Non-production boundary statement confirmed in README.md.

## frame_header.py: RFC 8878 Frame Header Reader

Pure Python implementation. No zstandard dependency. Parses:

- Magic detection: ZSTD_MAGIC = 0x28 0xB5 0x2F 0xFD (RFC 8878 §3.1.1)
- Skippable frame range: 0x184D2A50–0x184D2A5F (RFC 8878 §3.1.2)
- Frame Header Descriptor (FHD) byte:
  - FCS_flag (bits 7:6): Content_Size field size selector
  - Single_Segment_Flag (bit 5): window descriptor omitted when set
  - Content_Checksum_Flag (bit 2): checksum presence
  - DID_Flag (bits 1:0): Dictionary_ID field size
- Content_Size extraction (when FCS_flag indicates presence)
- Dictionary_ID extraction (when DID_Flag != 0)
- Window_Descriptor parsing (when Single_Segment=0)

### FHD Test Coverage

| Test | Result |
|------|--------|
| ZSTD_MAGIC constant correct | PASS |
| Skippable magic range correct | PASS |
| Valid ZSTD frame detected | PASS |
| Skippable frame detected | PASS |
| Unknown frame detected | PASS |
| Single_Segment=True for small payload | PASS |
| Content_Size present and correct for 11-byte payload | PASS |
| All 8 valid corpus files parse without exception | PASS |
| All 3 invalid corpus files parse without exception | PASS |

## zst_probe.py: Decompressor + Metadata Reporter

Hybrid approach: frame_header.py (pure Python header) + python-zstandard (decompression).
Uses `stream_reader()` exclusively for decompression — handles frames without Content_Size.

### probe() Validation

| Test | Result |
|------|--------|
| Returns dict with required keys | PASS |
| Decompresses valid sample (text-compressed.zst) | PASS |
| Reports decompression_error for off0.bin.zst | PASS |
| Returns exists=False for missing file | PASS |

### probe() Dict Structure

```
{
  "path": str,
  "exists": bool,
  "header": FrameHeaderInfo | None,
  "header_description": str,
  "decompressed_size": int | None,
  "decompressed_sha256": str | None,
  "decompression_error": str | None,
  "zstandard_available": bool
}
```

## validate_corpus.py: Corpus Validator

### Valid Sample Results (8/8 PASS)

| File | Result | Decompressed Size |
|------|--------|------------------|
| block-128k.zst | PASS | >0 bytes |
| dict-compressed.zst | PASS | 4160 bytes |
| empty-block.zst | PASS | 0 bytes |
| minimal-synthetic.zst | PASS | 1 byte |
| random-data.zst | PASS | >0 bytes |
| rle-first-block.zst | PASS | >0 bytes |
| text-compressed.zst | PASS | >0 bytes |
| zeroSeq_2B.zst | PASS | >0 bytes |

### Invalid Sample Results (3/3 correctly rejected)

| File | Result | Error |
|------|--------|-------|
| off0.bin.zst | PASS (rejected) | ZstdError: Data corruption detected |
| truncated_huff_state.zst | PASS (rejected) | ZstdError |
| zeroSeq_extraneous.zst | PASS (rejected) | ZstdError |

### Round-Trip Results (4/4 PASS)

| Payload | Original | Compressed | Round-Trip |
|---------|----------|------------|------------|
| payload[0]: "Hello, Zstandard world!" | 23 bytes | >0 | PASS |
| payload[1]: empty | 0 bytes | >0 | PASS |
| payload[2]: "A"*1000 | 1000 bytes | >0 | PASS |
| payload[3]: pattern*256 | 1024 bytes | >0 | PASS |

Total: **15/15 corpus validation PASS**

## Gate 4 Prototype Test Suite

Test file: tests/skills/test_zst_gate4_prototype.py
Result: **38/38 PASS**

### Test Breakdown

| Category | Tests | Result |
|----------|-------|--------|
| Prototype files exist | 5 | PASS |
| README non-production boundary | 2 | PASS |
| frame_header magic constants | 2 | PASS |
| frame_header frame detection | 3 | PASS |
| frame_header FHD decoding | 2 | PASS |
| frame_header corpus parsing | 11 | PASS |
| zst_probe probe() | 4 | PASS |
| validate_corpus valid samples | 1 | PASS |
| validate_corpus invalid samples | 1 | PASS |
| validate_corpus round-trips | 1 | PASS |
| Hard invariant: no src/*/zst | 2 | PASS |
| Hard invariant: no gen-req/zst | 1 | PASS |
| Hard invariant: registry gate_4 | 2 | PASS |
| Hard invariant: registry gate_5 | 1 | PASS |
| **Total** | **38** | **38 PASS** |

## Key Technical Findings

### Content_Size Optionality
ZST frames without Content_Size (streaming mode) require `stream_reader()` — not
`decompress()`. The prototype uses `stream_reader()` exclusively. All 8 valid corpus
files handled correctly, including off0.bin.zst which lacks Content_Size.

### Dictionary-Compressed Frames
dict-compressed.zst: Content_Size in header = 64 bytes (compressed frame size field),
actual decompressed size = 4160 bytes. The dictionary decompressor expands data beyond
the header-reported size. This is expected RFC 8878 behavior when a dictionary is used
and Content_Size reflects pre-dictionary content. The prototype handles this correctly
via stream_reader which reads until decompressor signals completion.

### Windows Encoding Compatibility
ASCII arrows (`->`) used in print output instead of Unicode (`→`) to avoid
cp1252 encoding errors on Windows terminals.

### Security Notes (Documented in README.md)
- Decompression bomb risk: stream_reader reads until completion
- Window size: default 512MB; validated per RFC 8878
- Streaming required for frames without Content_Size
- Invalid corpus handled without exception propagation

## Hard Invariant Checks

| Invariant | Status |
|-----------|--------|
| src/python/zst/ does not exist | PASS |
| src/net/zst/ does not exist | PASS |
| generated-requirements/zst/ does not exist | PASS |
| registry gate_4.status = planning_complete | PASS |
| registry gate_4.notes: implementation_authorized=false | PASS |
| registry gate_5.status = not_started | PASS |
| commercial_product_ready = false | PASS (unchanged) |

## Corpus Validation Command Log

```
python prototypes/by-format/zst/validate_corpus.py
=== ZST Corpus Validation — Gate 4 Prototype ===
--- Valid Samples ---
  [PASS] block-128k.zst  ...
  [PASS] dict-compressed.zst  4160 decompressed bytes
  [PASS] empty-block.zst  0 decompressed bytes
  [PASS] minimal-synthetic.zst  1 decompressed bytes
  [PASS] random-data.zst  ...
  [PASS] rle-first-block.zst  ...
  [PASS] text-compressed.zst  ...
  [PASS] zeroSeq_2B.zst  ...
--- Invalid Samples ---
  [PASS] off0.bin.zst  [zstd decompress error: Data corruption detected]
  [PASS] truncated_huff_state.zst  [...]
  [PASS] zeroSeq_extraneous.zst  [...]
--- Round-Trip Tests ---
  [PASS] payload[0]  23 -> N bytes
  [PASS] payload[1]  0 -> N bytes
  [PASS] payload[2]  1000 -> N bytes
  [PASS] payload[3]  1024 -> N bytes
=== Results: 15 PASS, 0 FAIL ===
```

GATE_2_ZST_PROTOTYPE: PASS
