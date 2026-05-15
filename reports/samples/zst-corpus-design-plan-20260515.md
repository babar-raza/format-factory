# ZST Corpus Design Plan
Sprint: FORMAT-FACTORY-R15A-ZST-GATE3A-SAMPLE-SOURCE-IDENTIFICATION-SWARM-001
Date: 2026-05-15
Gate: 3A (Source Identification — Corpus Design Plan for Gate 3B)

## Purpose

This report defines the planned structure and composition of the ZST sample corpus to be
created in Gate 3B (sprint R16). No files are created by this report. This is a design plan only.

## Gate 3 Corpus Requirements (from docs/gates.md)

The Gate 3 corpus must cover:
1. Minimal valid frame — smallest compliant ZST file
2. Empty/trivial content — empty input compressed to a ZST frame
3. Core data — typical compressed data representative of real use
4. Edge cases — structural variants, boundary conditions

## Planned Corpus Structure

Target directory (Gate 3B): samples/by-format/zst/

### Planned Files

| Filename | Source | Category | Description |
|----------|--------|----------|-------------|
| block-128k.zst | SOURCE-001 (facebook/zstd) | core-data | 128k compressed block; typical workload |
| rle-first-block.zst | SOURCE-001 (facebook/zstd) | structural-variant | RLE-encoded first block |
| zeroSeq_2B.zst | SOURCE-001 (facebook/zstd) | edge-case | Zero-sequence frame with 2-byte input |
| empty-block.zst | SOURCE-001 (facebook/zstd) | empty-trivial | Empty/trivial compressed frame |
| minimal-synthetic.zst | SOURCE-003 (python-zstandard) | minimal-valid | Minimal single-block ZST frame |
| text-compressed.zst | SOURCE-005 (PD text + zstd CLI) | real-world-data | PD text compressed, multi-block |
| dict-compressed.zst | SOURCE-002 (decodecorpus) | dictionary | Dictionary-compressed frame |
| random-data.zst | SOURCE-002 (decodecorpus) | structural-variant | Random frame structure from decodecorpus |

### Planned Error Fixtures (negative test corpus)

Target directory (Gate 3B): samples/by-format/zst/_error-fixtures/

| Filename | Source | Description |
|----------|--------|-------------|
| off0.bin.zst | SOURCE-004 (facebook/zstd) | Invalid offset=0 sequence |
| truncated_huff_state.zst | SOURCE-004 (facebook/zstd) | Truncated Huffman state |
| zeroSeq_extraneous.zst | SOURCE-004 (facebook/zstd) | Zero-sequence with extraneous data |

## Minimum Corpus Count

- Valid frames: 8 (covers all 4 required categories)
- Error frames: 3 (covers negative/malformed testing)
- Total planned: 11 files

## Provenance Requirements (Gate 3B)

Each file in samples/by-format/zst/ must have a _provenance.yaml with:
```yaml
sample_id: <filename>
source: <SOURCE-001 | SOURCE-002 | SOURCE-003 | SOURCE-004 | SOURCE-005>
source_url: <URL or "self-generated">
license: <BSD-3-Clause | project-owned-synthetic>
copyright: <holder>
provenance_status: confirmed
acquisition_date: <date>
sha256: <hash>
valid_zst_frame: <true | false>
```

## Gate 3B Prerequisites

Before Gate 3B can begin:
- R15A complete: YES (this sprint)
- ZST-R16-GATE3B-SAMPLE-CORPUS-ACQUISITION.md taskcard: created (this sprint)
- Gate 3B execution prompt from Babar Raza: REQUIRED

## DEC-034 IV Requirement

Per DEC-034: an independent IV sprint is required before human review of Gate 3.
Gate 3B will include a separate ZST-GATE3-IV.md taskcard (created in this sprint).
Human approval of Gate 3 requires both Gate 3B execution AND ZST-GATE3-IV completion.

## Coverage Assessment

The planned corpus covers all 4 required Gate 3 categories:
- Minimal valid: minimal-synthetic.zst (SOURCE-003)
- Empty/trivial: empty-block.zst (SOURCE-001)
- Core data: block-128k.zst + text-compressed.zst (SOURCE-001, SOURCE-005)
- Edge cases: rle-first-block.zst + zeroSeq_2B.zst + dict-compressed.zst + random-data.zst

CORPUS DESIGN: ADEQUATE for Gate 3 requirements
