---
artifact_id: zst-gate6-oracle-plan-v1
format_id: zst
gate: 6
sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
date: "2026-05-16"
status: active
---

# ZST Gate 6 Oracle Plan

## Oracle Strategy

ZST is a pure compression codec. Gate 6 oracle strategy: deterministic SHA-256 round-trip.

## Oracle Models (in priority order)

### Oracle 1: python-zstandard Round-Trip (PRIMARY)
- Library: zstandard 0.25.0 (BSD-3-Clause, pypi)
- Method: compress → decompress → SHA-256 equality check
- Availability: CONFIRMED (verified R19)
- Deterministic: YES (same input → same decompressed output)
- Test type: mathematical oracle (hash equality)

### Oracle 2: Corpus Validity Oracle
- Method: valid corpus must decompress without error
- Method: invalid corpus must fail with ZstdError
- Availability: CONFIRMED (existing corpus in samples/by-format/zst/)
- Test type: binary pass/fail oracle

### Oracle 3: CLI zstd Oracle (FALLBACK)
- Availability: NOT AVAILABLE on this platform (Windows; no zstd CLI)
- Status: SKIPPED — skip decorator applied in tests

### Oracle 4: Prototype Wrapper Oracle
- Method: use frame_header.py to parse magic bytes / frame structure
- Method: validate frame header fields match decompressed content_size
- Availability: CONFIRMED (prototypes/by-format/zst/frame_header.py)
- Test type: structural oracle

## Oracle Test Requirements

1. Valid corpus: all 8 valid samples must decompress successfully with SHA-256 match
2. Invalid corpus: all 3 invalid samples must fail decompression with ZstdError
3. Synthetic round-trip: compress/decompress/compare for 4 payload types:
   - text payload (ASCII repeated)
   - binary payload (structured bytes)
   - empty payload (0 bytes)
   - high-entropy payload (pseudo-random)
4. Dictionary sample: dict-compressed.zst behavior documented (content_size in header)
5. Max-window / bomb-risk guard: documented max window size per RFC 8878

## Decompression Bomb Controls

Per RFC 8878 Section 3.1.1:
- Maximum window size: 2^31 bytes (2 GB) — Window_Descriptor field
- python-zstandard enforces max_window_size parameter
- Oracle tests must pass max_window_size=2**31 (2 GB limit)
- Streaming strategy: use ZstdDecompressor.stream_reader() for large files

## Dictionary Sample Behavior

dict-compressed.zst uses dictionary compression:
- Header reports content_size from the frame header (64 bytes in test observation)
- Actual decompressed size may differ if dictionary context extends frame
- Oracle must handle dictionary-compressed files gracefully
- Status: decompression requires matching dictionary ID or falls back to no-dict attempt

## .tar.zst Archive/Container Risks

- .tar.zst = tar archive compressed with zstandard
- Container risk: tar path traversal, symlink attacks, zip-slip equivalents
- Mitigation: decompress only, do not untar in oracle tests
- Oracle tests treat .tar.zst as opaque byte streams for compression oracle purposes

## Gate 6 Pass Criteria

- All valid corpus round-trips PASS (SHA-256 match)
- All invalid corpus files rejected (ZstdError or header parse failure)
- Synthetic payloads round-trip correctly
- Bomb guard documented and tested
- No production code created
- Tests: tests/skills/test_zst_gate6_oracle.py

GATE6_ORACLE_PLAN: ACTIVE
