# ZST Candidate Source Discovery Report
Sprint: FORMAT-FACTORY-R15A-ZST-GATE3A-SAMPLE-SOURCE-IDENTIFICATION-SWARM-001
Date: 2026-05-15
Gate: 3A (Source Identification)

## Summary

8 candidate sources identified. 5 preferred candidates selected.
Internet access used for research only — no files downloaded.

## Discovery Method

- Web research via WebFetch/WebSearch (internet-authorized for this sprint)
- Repository browsing: facebook/zstd, indygreg/python-zstandard
- Self-generation options assessed (zstd CLI and Python library)
- No files downloaded; URLs and license info recorded only

---

## Candidate Sources

### SOURCE-001: facebook/zstd golden-decompression test fixtures
- URL: https://github.com/facebook/zstd/tree/dev/tests/golden-decompression
- Files: block-128k.zst, empty-block.zst, rle-first-block.zst, zeroSeq_2B.zst (4 files)
- License: BSD-3-Clause OR GPL-2.0 (dual license); project uses BSD-3 path
- Copyright: Meta Platforms Inc.
- Status: PREFERRED
- Rationale: Authoritative test fixtures from the zstd reference implementation. All 4 files are
  valid ZST frames used by the official test suite to verify decompressor correctness. BSD-3 path
  permits redistribution with attribution. Covers key structural categories: 128k compressed block
  (core data), empty block (trivial/empty case), RLE-encoded first block (structural variant),
  zero-sequence frame (edge case). Canonical provenance (upstream project artifacts).

### SOURCE-002: facebook/zstd decodecorpus self-generation tool
- URL: https://github.com/facebook/zstd/blob/dev/tests/decodecorpus.c
- License: BSD-3-Clause OR GPL-2.0 (dual license); BSD-3 path applies
- Copyright: Meta Platforms Inc.
- Status: PREFERRED
- Rationale: decodecorpus is the official zstd tool for generating valid ZST frames for verifying
  decoder implementations. Running it during Gate 3B will produce project-owned synthetic samples
  with full control over frame structure. Generated output files are project-owned synthetic
  artifacts with no third-party IP encumbrances. Covers: random frame structures, various block
  types, checksum variants, dictionary-compressed frames.

### SOURCE-003: python-zstandard library self-generation
- URL: https://github.com/indygreg/python-zstandard
- PyPI: https://pypi.org/project/zstandard/
- License: BSD-3-Clause (Gregory Szorc / indygreg)
- Status: PREFERRED
- Rationale: The python-zstandard library (already listed as the Python library for ZST in
  acquisition-packs/zst/pack.yaml) can generate .zst files via Python script. Using
  `zstandard.ZstdCompressor().compress(data)` produces project-owned synthetic artifacts.
  Enables fine-grained control over compression parameters, content type, and frame options.
  Generated files are project-owned synthetic artifacts — no license encumbrances.

### SOURCE-004: facebook/zstd golden-decompression-errors test fixtures
- URL: https://github.com/facebook/zstd/tree/dev/tests/golden-decompression-errors
- Files: off0.bin.zst, truncated_huff_state.zst, zeroSeq_extraneous.zst (3 files)
- License: BSD-3-Clause OR GPL-2.0 (dual license); BSD-3 path applies
- Copyright: Meta Platforms Inc.
- Status: PREFERRED (for negative/error testing)
- Rationale: These are intentionally malformed/invalid ZST frames used to test error handling
  in decompressors. Valuable for Gate 7 (malformed/fuzz testing). BSD-3 path permits
  redistribution with attribution. NOTE: these test INVALID frames — they should be classified
  as negative test fixtures, not valid corpus samples. Separately tracked from valid corpus.

### SOURCE-005: Public domain text self-generation via zstd CLI
- URL: https://www.gutenberg.org/ (for source text; PD)
- License: Generated .zst files are project-owned; source text is public domain
- Status: PREFERRED
- Rationale: Compress Project Gutenberg public domain text (e.g., plain UTF-8 .txt) using
  the `zstd` CLI tool. This produces project-owned synthetic samples backed by public domain
  source material. The compression itself adds no copyright. Useful for "real-world data"
  category: text data compression, varying compression ratios, multi-block frames from larger
  inputs. Gutenberg text has confirmed PD status under US law.

### SOURCE-006: facebook/zstd golden-compression input data files
- URL: https://github.com/facebook/zstd/tree/dev/tests/golden-compression
- Files: PR-3517-block-splitter-corruption-test, http, huffman-compressed-larger,
  large-literal-and-match-lengths (4 files — NOT .zst; raw input data)
- License: BSD-3-Clause OR GPL-2.0 (dual license); BSD-3 path applies
- Status: CANDIDATE (input data, not .zst files themselves)
- Rationale: These raw data files can be used as input when self-generating ZST samples via
  SOURCE-002 or SOURCE-003, providing a variety of input data types. They are not .zst files
  themselves but serve as useful generation seeds. Lower priority than direct .zst sources.

### SOURCE-007: python-zstandard test suite fixture generation
- URL: https://github.com/indygreg/python-zstandard/tree/main/tests
- License: BSD-3-Clause (Gregory Szorc)
- Status: REJECTED
- Rationale: Inspected tests/ directory — no .zst fixture files found. All tests generate data
  inline using Python code. No pre-existing .zst binary fixtures available in this repository.
  Python-zstandard is still valuable as a self-generation tool (SOURCE-003) but does not
  contribute pre-built fixture files.

### SOURCE-008: Arch Linux .pkg.tar.zst packages
- URL: https://archlinux.org/packages/ (general)
- License: Per-package (varies: GPL, MIT, BSD, etc.)
- Status: CANDIDATE (conditional, high-overhead)
- Rationale: Arch Linux packages use .zst compression. Each .pkg.tar.zst is a valid ZST frame
  wrapping a tar archive. However, license is per-package and requires individual audit for each
  file used. Copyright is per-package maintainer. High provenance overhead. Conditionally useful
  if a specific small BSD/MIT-licensed package is identified for edge-case testing only.
  NOT recommended as primary source due to per-package audit burden.

---

## Preferred Candidates Summary

| ID | Source | License | Files | Category |
|----|--------|---------|-------|----------|
| SOURCE-001 | facebook/zstd golden-decompression | BSD-3 | 4 .zst | Valid frames (canonical) |
| SOURCE-002 | decodecorpus self-generation | Project-owned synthetic | Generated | Structural variants |
| SOURCE-003 | python-zstandard self-generation | Project-owned synthetic | Generated | Configurable |
| SOURCE-004 | facebook/zstd golden-decompression-errors | BSD-3 | 3 .zst | Error/malformed frames |
| SOURCE-005 | PD text + zstd CLI | Project-owned synthetic | Generated | Real-world data |

Preferred count: 5 (meets minimum of 5)
Total candidates identified: 8 (meets minimum of 8)

---

## Gate 3B Acquisition Plan (Preview)

For Gate 3B (future sprint R16), preferred acquisition strategy:
1. Copy SOURCE-001 files from facebook/zstd (BSD-3, redistribution permitted)
2. Run decodecorpus (SOURCE-002) to generate structural variants
3. Use python-zstandard (SOURCE-003) to generate configurable test frames
4. Copy SOURCE-004 error fixtures for negative testing (BSD-3)
5. Generate SOURCE-005 PD-text samples for real-world coverage

Expected corpus: minimum 12 .zst files covering all Gate 3 categories.
