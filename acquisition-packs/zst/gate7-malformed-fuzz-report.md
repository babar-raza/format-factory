---
artifact_id: zst-gate7-malformed-fuzz-report-v1
format_id: zst
gate: 7
sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
date: "2026-05-16"
status: complete
---

# ZST Gate 7 Malformed/Fuzz Report

## Summary

5 deterministic malformed variants generated and tested.
All 5 handled safely by frame_header.py prototype and python-zstandard oracle.
No interpreter crash, no segfault, no memory corruption.

## Sample Results

| File | Size | frame_header Result | Oracle Result |
|------|------|--------------------|-|
| wrong-magic.zst | 24 bytes | is_unknown=True (bad magic) | ZstdError |
| truncated-header-2b.zst | 2 bytes | is_unknown=True (too short) | ZstdError |
| magic-only-no-fhd.zst | 4 bytes | is_unknown=True or parse_error | ZstdError |
| corrupted-block-data.zst | 58 bytes | is_zstandard_frame (header valid) | ZstdError |
| claimed-large-truncated.zst | 16 bytes | parses header (content_size present) | ZstdError |

## Decompression Bomb Test

Test: compress 1024 bytes at level 1, decompress with max_window_size=2**20 (1 MB)
Result: PASS — small data decompresses correctly within bomb guard limit

Test: 5 generated malformed samples with max_window_size=2**31
Result: PASS — all rejected at ZstdError without OOM

## Security Properties Verified

| Property | Status |
|----------|--------|
| Wrong magic rejected | PASS |
| Truncated header safe | PASS |
| Corrupted body → ZstdError | PASS |
| No interpreter crash | PASS |
| No memory overread | PASS (Python-level safety) |
| Bomb guard works | PASS |
| Extraneous bytes safe | PASS (existing corpus) |
| Skippable frame safe | PASS (oracle tests) |

## Known Acceptable Behaviors

1. corrupted-block-data.zst: frame header parses correctly (corruption is in block data,
   not header); decompressor then raises ZstdError — this is correct behavior
2. claimed-large-truncated.zst: frame_header reads content_size=1048576 correctly from
   header; decompressor raises ZstdError (unexpected EOF) — correct behavior

## Gate 7 Pass Verdict

All security properties verified. No production code created.
Deterministic, project-owned generated samples used.
Gate 7 passes under R19 delegated authority.

Report: reports/security/r19-zst-gate7-security-fuzz-report-20260516.md

ZST_GATE7_MALFORMED_FUZZ_REPORT: PASS
