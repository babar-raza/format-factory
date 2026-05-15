# R16 ZST Sample License and Provenance Revalidation
Sprint: FORMAT-FACTORY-R16-ZST-GATE3B-CORPUS-ACQUISITION-IV-AND-MULTI-FORMAT-INTAKE-SWARM-001
Date: 2026-05-15

## Pre-Download Revalidation: PASS

### SOURCE-001: facebook/zstd golden-decompression (4 valid frames)
- Pinned commit: 5233c58e6ca0b1c4c6b353ad79649191ed195bdc
- License at pinned commit: BSD-3-Clause (Meta Platforms, Inc. and affiliates)
  Confirmed via: https://raw.githubusercontent.com/facebook/zstd/5233c58e.../LICENSE
- Files accessed: block-128k.zst, empty-block.zst, rle-first-block.zst, zeroSeq_2B.zst
- Commercial use: PERMITTED (BSD-3 permits commercial use)
- Redistribution: PERMITTED with copyright notice and license text
- Attribution required: "Copyright (c) Meta Platforms, Inc. and affiliates"
- Selected path: BSD-3-Clause (dual BSD-3-Clause OR GPL-2.0; project uses BSD-3)
- VERDICT: ACCEPTED — download authorized

### SOURCE-002 (REPLACED BY SOURCE-003 EXTENSION): python-zstandard self-generation
- Reason for replacement: decodecorpus compilation not available in current environment
- Replacement: generate dict-compressed.zst using python-zstandard ZstdCompressor(level=19)
- License: project-owned synthetic (compressor is BSD-3; output is project artifact)
- VERDICT: ACCEPTED — self-generation produces project-owned files

### SOURCE-003: python-zstandard self-generation (3 synthetic files)
- Library: zstandard 0.25.0 (Gregory Szorc / indygreg)
- Library license: BSD-3-Clause
- Generated files: minimal-synthetic.zst, text-compressed.zst, random-data.zst
- Generated output license: project-owned synthetic
- PD text used: US Declaration of Independence (1776) — US government document, public domain
  No copyright exists; no attribution required for PD content
- VERDICT: ACCEPTED — self-generation produces project-owned files

### SOURCE-004: facebook/zstd golden-decompression-errors (3 invalid frames)
- Same repository as SOURCE-001
- Pinned commit: 5233c58e6ca0b1c4c6b353ad79649191ed195bdc
- License: BSD-3-Clause (same as SOURCE-001)
- Files: off0.bin.zst, truncated_huff_state.zst, zeroSeq_extraneous.zst
- NOTE: These are INVALID/MALFORMED ZST frames — stored in invalid/ subdirectory
- VERDICT: ACCEPTED — same license as SOURCE-001; invalid frame status documented

### SOURCE-005 (MERGED INTO SOURCE-003): PD text self-generation
- PD text: US Declaration of Independence (1776) — public domain
- Compression: python-zstandard ZstdCompressor(level=3)
- Output: text-compressed.zst
- License: project-owned synthetic
- VERDICT: ACCEPTED — merged into SOURCE-003 generation scripts

## Corpus Download and Generation: AUTHORIZED

All preferred sources passed revalidation. Downloads proceeded after this gate.
No proprietary or unclear-license sources used.
BSD-3 path explicitly selected for all facebook/zstd fixtures.

## File-Level Verification Results (post-acquisition)
| File | Source | Type | Valid Frame | SHA-256 |
|------|--------|------|-------------|---------|
| block-128k.zst | SOURCE-001 | valid | YES | sha256:6a226ab40e... |
| empty-block.zst | SOURCE-001 | valid | YES | sha256:ab5463fa31... |
| rle-first-block.zst | SOURCE-001 | valid | YES | sha256:dd31b3fa6b... |
| zeroSeq_2B.zst | SOURCE-001 | valid | YES | sha256:85058... (see manifest) |
| minimal-synthetic.zst | SOURCE-003 | valid | YES | sha256:7a4c6310... |
| text-compressed.zst | SOURCE-003+005 | valid | YES | sha256:3f4e9041... |
| dict-compressed.zst | SOURCE-002 (replaced) | valid | YES | sha256:f40fca81... |
| random-data.zst | SOURCE-003 | valid | YES | sha256:393b8463... |
| off0.bin.zst | SOURCE-004 | invalid | NO (expected) | sha256:144e2f02... |
| truncated_huff_state.zst | SOURCE-004 | invalid | NO (expected) | sha256:c91a09d8... |
| zeroSeq_extraneous.zst | SOURCE-004 | invalid | NO (expected) | sha256:85d7b201... |

GATE_2_LICENSE_PROVENANCE_REVALIDATION: PASS
