# ZST Sample Sources
Format: Zstandard Compressed File (.zst)
Sprint: FORMAT-FACTORY-R15A-ZST-GATE3A-SAMPLE-SOURCE-IDENTIFICATION-SWARM-001
Date: 2026-05-15
Gate: 3A (Source Identification Complete)

## Purpose

This document records candidate sources for ZST (.zst) sample files to be acquired during
Gate 3B (sprint R16). It is produced by Gate 3A source identification (this sprint).

Gate 3 is NOT yet passed. No files have been downloaded or created in samples/by-format/zst/.
Gate 3 pass requires actual corpus files + confirmed provenance + human approval (Gate 3B).

## Sample Requirements (from docs/gates.md)

Gate 3 corpus must cover:
- Minimal valid ZST frame
- Empty/trivial content
- Core data (typical compression)
- Edge cases (structural variants)
- Each sample must have _provenance.yaml with provenance_status: confirmed
- Acceptable licenses: project-owned synthetic, BSD-3-Clause, MIT, Apache-2.0, CC0, CC-BY, PD

## Preferred Candidate Sources

### SOURCE-001: facebook/zstd golden-decompression
- URL: https://github.com/facebook/zstd/tree/dev/tests/golden-decompression
- Files: block-128k.zst, empty-block.zst, rle-first-block.zst, zeroSeq_2B.zst
- License: BSD-3-Clause (dual BSD-3-Clause OR GPL-2.0; BSD-3 path selected)
- Copyright: Meta Platforms Inc.
- Commercial use: permitted
- Redistribution: permitted with attribution
- Acquisition action (Gate 3B): copy files; record SHA-256; create _provenance.yaml per file

### SOURCE-002: facebook/zstd decodecorpus self-generation
- URL: https://github.com/facebook/zstd/blob/dev/tests/decodecorpus.c
- Output: project-owned synthetic .zst files
- License: project-owned synthetic (tool is BSD-3; output belongs to project)
- Acquisition action (Gate 3B): build/run decodecorpus; record output SHA-256

### SOURCE-003: python-zstandard library self-generation
- URL: https://github.com/indygreg/python-zstandard
- PyPI: https://pypi.org/project/zstandard/
- Output: project-owned synthetic .zst files
- License: project-owned synthetic (library is BSD-3; output belongs to project)
- Acquisition action (Gate 3B): run Python script using zstandard library; record SHA-256

### SOURCE-004: facebook/zstd golden-decompression-errors (negative fixtures)
- URL: https://github.com/facebook/zstd/tree/dev/tests/golden-decompression-errors
- Files: off0.bin.zst, truncated_huff_state.zst, zeroSeq_extraneous.zst
- License: BSD-3-Clause (same repository as SOURCE-001)
- Copyright: Meta Platforms Inc.
- NOTE: These are INVALID/MALFORMED ZST frames. Stored in _error-fixtures/ subdirectory.
- Acquisition action (Gate 3B): copy files; label as invalid in _provenance.yaml

### SOURCE-005: Public domain text + zstd CLI self-generation
- Source text: confirmed public domain UTF-8 text (e.g., US government work or pre-1928 text)
- Output: project-owned synthetic .zst files
- License: project-owned synthetic (PD source + project compression = project artifact)
- Acquisition action (Gate 3B): identify specific PD text; compress with zstd; record SHA-256

## Additional Candidates (Not Preferred)

### SOURCE-006: facebook/zstd golden-compression input data
- URL: https://github.com/facebook/zstd/tree/dev/tests/golden-compression
- License: BSD-3-Clause
- Status: input data seeds only; not .zst files themselves
- Use: compress these files during Gate 3B to create additional structured samples

### SOURCE-008: Arch Linux .pkg.tar.zst packages
- Status: conditional; high per-file audit burden
- Use: only if specific edge case cannot be covered by preferred sources

## Rejected Sources

### SOURCE-007: python-zstandard test suite
- URL: https://github.com/indygreg/python-zstandard/tree/main/tests
- Reason: no .zst fixture files found in repository

## Planned Corpus (Gate 3B Output)

Minimum 8 valid .zst files + 3 error fixtures = 11 files total.
See: reports/samples/zst-corpus-design-plan-20260515.md for detailed plan.

## Gate 3 Status

- Source identification: COMPLETE (Gate 3A, R15A, 2026-05-15)
- Corpus acquisition: NOT STARTED (requires Gate 3B authorization prompt)
- Gate 3 status: source_identification_complete (NOT passed)
- Next action: R16 execution prompt for Gate 3B corpus acquisition

## Sign-off

Gate 3A source identification complete.
Gate 3 NOT passed — requires actual corpus files in samples/by-format/zst/ + confirmed provenance + human approval.
Next sprint: FORMAT-FACTORY-R16-ZST-GATE3B-SAMPLE-CORPUS-ACQUISITION-SWARM-001
