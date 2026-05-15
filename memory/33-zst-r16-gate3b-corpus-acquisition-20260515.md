# Memory 33: ZST R16 — Gate 3B Corpus Acquisition

**Sprint:** FORMAT-FACTORY-R16-ZST-GATE3B-CORPUS-ACQUISITION-IV-AND-MULTI-FORMAT-INTAKE-SWARM-001
**Date:** 2026-05-15
**Gate:** ZST Gate 3 PASSED (delegated)

## Status

ZST Gate 3 PASSED under delegated authority (R16 execution prompt, Babar Raza instruction).

## Corpus Acquired

Location: `samples/by-format/zst/`

| File | Source | License | Size |
|------|--------|---------|------|
| valid/block-128k.zst | facebook/zstd (SOURCE-001) | BSD-3-Clause | 131081 bytes |
| valid/empty-block.zst | facebook/zstd (SOURCE-001) | BSD-3-Clause | 11 bytes |
| valid/rle-first-block.zst | facebook/zstd (SOURCE-001) | BSD-3-Clause | 45 bytes |
| valid/zeroSeq_2B.zst | facebook/zstd (SOURCE-001) | BSD-3-Clause | 25 bytes |
| valid/minimal-synthetic.zst | python-zstandard (SOURCE-003) | project-owned | 10 bytes |
| valid/text-compressed.zst | python-zstandard + PD text | project-owned | 272 bytes |
| valid/dict-compressed.zst | python-zstandard level=19 | project-owned | 74 bytes |
| valid/random-data.zst | python-zstandard (SOURCE-003) | project-owned | 276 bytes |
| invalid/off0.bin.zst | facebook/zstd (SOURCE-004) | BSD-3-Clause | 17 bytes |
| invalid/truncated_huff_state.zst | facebook/zstd (SOURCE-004) | BSD-3-Clause | 19 bytes |
| invalid/zeroSeq_extraneous.zst | facebook/zstd (SOURCE-004) | BSD-3-Clause | 27 bytes |

Pinned commit: `5233c58e6ca0b1c4c6b353ad79649191ed195bdc` (facebook/zstd)

## Key Technical Notes

- SOURCE-002 (decodecorpus) replaced: C compilation unavailable in Windows env.
  Replacement: python-zstandard `level=19` high-compression structural variant (dict-compressed.zst)
- 3 upstream fixtures lack `Content_Size` in frame header — use `ZstdDecompressor.stream_reader()`
- `zstandard` 0.25.0: `decompress()` requires `Content_Size`; `stream_reader()` works without it

## Test Suite

`tests/skills/test_zst_gate3b_sample_corpus.py` — 57 tests
- Directory structure (3), valid files (8), invalid files (3), SHA-256 (11), valid decompression (8),
  invalid error detection (3), manifest structure (6), provenance (2), Gate 3A preserved (5),
  no src/ mutations (2), no generated-requirements (1), generation script (2)

## Artifacts Created

- `samples/by-format/zst/_corpus-manifest.yaml`
- `samples/by-format/zst/_provenance.yaml`
- `samples/by-format/zst/source-materials/generation-scripts/generate_synthetic_zst.py`
- `tests/skills/test_zst_gate3b_sample_corpus.py`
- `reports/testing/r16-zst-sample-corpus-validation-report-20260515.md`
- `reports/legal/r16-zst-sample-license-provenance-revalidation-20260515.md`
- `reports/verification/r16-r15a-closure-verification-and-repair-20260515.md`
- `reports/verification/r16-zst-gate3-independent-verification-20260515.md`
- `reports/governance/r16-zst-gate3-delegated-approval-report-20260515.md`
- `reports/governance/r16-zst-pack-registry-gate3b-update-report-20260515.md`
- `reports/planning/r16-multi-format-intake-and-next-candidates-20260515.md`
- `reports/planning/r16-opendocument-status-and-next-actions-20260515.md`
- `acquisition-packs/_candidate-shortlists/r16-multi-format-intake-and-next-candidates-20260515.md`
- `taskcards/ZST-R17-GATE4-PARSER-PROTOTYPE-PLANNING.md`
- `taskcards/R17-MULTI-FORMAT-GATE1-INTAKE.md`

## Registry State After R16

- `registry/format-registry.yaml` ZST: `gate_3.status: passed`; `approved_by: delegated (R16 prompt)`
- `acquisition-packs/zst/pack.yaml`: `sample_sources.status: passed`

## Next Sprint

ZST Gate 4: FORMAT-FACTORY-R17-ZST-GATE4-PARSER-PROTOTYPE-PLANNING-SWARM-001
Taskcard: `taskcards/ZST-R17-GATE4-PARSER-PROTOTYPE-PLANNING.md`
Deliverable: `acquisition-packs/zst/parser-notes.md`
