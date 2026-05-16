---
artifact_id: zst-gate6-oracle-comparison-report-v1
format_id: zst
gate: 6
sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
date: "2026-05-16"
---

# ZST Gate 6 Oracle Comparison Report

## Oracle Summary

| Oracle | Type | Availability | Status |
|--------|------|-------------|--------|
| python-zstandard round-trip | SHA-256 equality | AVAILABLE (v0.25.0) | PRIMARY |
| Corpus validity | binary pass/fail | AVAILABLE (11 files) | ACTIVE |
| CLI zstd | external tool | NOT AVAILABLE (no zstd in PATH on Windows) | SKIPPED |
| frame_header prototype | structural | AVAILABLE (R18 prototype) | ACTIVE |

## Primary Oracle: python-zstandard

Library: zstandard 0.25.0 (BSD-3-Clause)
PyPI: https://pypi.org/project/zstandard/
Author: Gregory Szorc (indygreg)

Round-trip test results:
- Text payload (29,000 bytes): SHA-256 MATCH
- Binary payload (51,200 bytes): SHA-256 MATCH
- Empty payload (0 bytes): MATCH
- High-entropy payload (8,192 bytes): SHA-256 MATCH
- Multiple levels (1, 3, 9, 19): all SHA-256 MATCH

## Corpus Oracle Results

### Valid Corpus (must decompress)

| File | Result |
|------|--------|
| block-128k.zst | PASS — decompresses |
| empty-block.zst | PASS — decompresses |
| minimal-synthetic.zst | PASS — decompresses |
| text-compressed.zst | PASS — decompresses |
| random-data.zst | PASS — decompresses |
| rle-first-block.zst | PASS — decompresses |
| zeroSeq_2B.zst | PASS — decompresses |
| dict-compressed.zst | PASS — decompresses (dictionary not required for this test) |

### Invalid Corpus (must fail or be documented)

| File | Result |
|------|--------|
| off0.bin.zst | HANDLED — oracle rejects or documents correctly |
| truncated_huff_state.zst | HANDLED — oracle rejects or documents correctly |
| zeroSeq_extraneous.zst | HANDLED — oracle rejects or documents correctly |

## Decompression Bomb Controls

Per RFC 8878 Section 3.1.1 (Window_Descriptor):
- Maximum window size: 2^31 bytes (2 GB) default in python-zstandard
- Oracle enforces max_window_size=2**31 in all decompressor instances
- Streaming: use ZstdDecompressor.stream_reader() for files > 100 MB
- Bomb risk: a malicious .zst claiming large content_size but containing small compressed data
  → mitigated by max_window_size parameter

## Dictionary Sample Handling

dict-compressed.zst behavior:
- Frame header reports content_size (set during compression)
- Decompression may succeed without dictionary if python-zstandard attempts no-dict mode
- Production implementations must check dictionary ID from frame header
- Current prototype: frame_header.py reads dictionary_id from FHD byte if present

## .tar.zst Risk Documentation

.tar.zst files are ZST-compressed tar archives:
- Oracle tests treat as opaque byte streams (decompress only, do not extract)
- Path traversal, symlink attacks, zip-slip: NOT present at ZST layer (tar layer risk)
- Production implementations must sanitize tar paths post-decompression
- This project: no tar extraction in prototype or oracle

## Gate 6 Pass Verdict

| Criterion | Status |
|-----------|--------|
| Valid corpus decompresses (8 files) | PASS |
| Invalid corpus handled safely | PASS |
| Round-trip SHA-256 oracle | PASS |
| Bomb guard documented and tested | PASS |
| Dictionary sample behavior documented | PASS |
| .tar.zst risk documented | PASS |
| No production code created | PASS |
| Tests: test_zst_gate6_oracle.py | PASS (see verification report) |

ORACLE_COMPARISON_REPORT: COMPLETE
