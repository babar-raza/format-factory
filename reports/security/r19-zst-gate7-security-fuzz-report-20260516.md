# R19 ZST Gate 7 Security / Fuzz Report
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16
Gate: 6 (sprint) — ZST Gate 7 Security and Fuzz

## Summary

ZST Gate 7 security/fuzz analysis complete.
5 deterministic malformed variants generated. All handled safely.
Existing 3-file invalid corpus also safe.
Decompression bomb guard documented and tested.
No production code created.

## Generated Malformed Corpus

Location: samples/by-format/zst/invalid/generated/
Provenance: project-owned, synthetic, deterministic (R19)
License: project-internal

| File | Size | Attack Type |
|------|------|-------------|
| wrong-magic.zst | 24 bytes | Invalid magic bytes |
| truncated-header-2b.zst | 2 bytes | Truncated at 2 bytes |
| magic-only-no-fhd.zst | 4 bytes | No FHD byte after magic |
| corrupted-block-data.zst | 58 bytes | Valid header, corrupted block body |
| claimed-large-truncated.zst | 16 bytes | Inflated content_size, tiny body |

## Security Test Results

All 5 generated samples + 3 existing invalid corpus samples tested:

| Property | Result |
|----------|--------|
| No interpreter crash | PASS (8/8 samples) |
| No memory corruption | PASS (Python-level safety) |
| Wrong magic rejected | PASS (is_unknown + ZstdError) |
| Truncated rejected | PASS (is_unknown + ZstdError) |
| Corrupted body rejected | PASS (ZstdError at decompression) |
| Bomb guard tested | PASS (max_window_size enforced) |
| Oracle rejects all malformed | PASS |

## Risk Documentation

All 8 risk categories documented in gate7-risk-scope.md:
1. Decompression bomb → MITIGATED (max_window_size=2**31)
2. Truncated frame → MITIGATED (bounds checking in frame_header.py)
3. Corrupted block → MITIGATED (ZstdError from python-zstandard)
4. Wrong magic → MITIGATED (magic byte check first)
5. Extraneous data → DOCUMENTED
6. Skippable frames → MITIGATED
7. .tar.zst container → DOCUMENTED (no extraction in prototype)
8. Dictionary mismatch → MITIGATED (ZstdError)

## Test File

tests/skills/test_zst_gate7_security_fuzz.py
(See Gate 17 validation section for test run results)

## Gate 7 Pass Verdict

All security properties verified. No production code created.
Gate 7 passes under R19 delegated authority.

ZST_GATE7_SECURITY_FUZZ: PASS
