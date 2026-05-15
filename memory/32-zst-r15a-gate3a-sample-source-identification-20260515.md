# Memory Note 32: ZST R15A Gate 3A Sample Source Identification
Sprint: FORMAT-FACTORY-R15A-ZST-GATE3A-SAMPLE-SOURCE-IDENTIFICATION-SWARM-001
Date: 2026-05-15

## Gate 3A Status

ZST Gate 3A source identification COMPLETE (R15A, 2026-05-15).
Gate 3 NOT passed — corpus acquisition (Gate 3B) requires separate R16 execution prompt.

## Candidate Sources Identified (8 total, 5 preferred)

| ID | Source | License | Files | Status |
|----|--------|---------|-------|--------|
| SOURCE-001 | facebook/zstd golden-decompression | BSD-3-Clause | 4 .zst | PREFERRED |
| SOURCE-002 | facebook/zstd decodecorpus | Project-owned synthetic | Generated | PREFERRED |
| SOURCE-003 | python-zstandard self-generation | Project-owned synthetic | Generated | PREFERRED |
| SOURCE-004 | facebook/zstd golden-decompression-errors | BSD-3-Clause | 3 .zst (INVALID) | PREFERRED (neg. fixtures) |
| SOURCE-005 | PD text + zstd CLI | Project-owned synthetic | Generated | PREFERRED |
| SOURCE-006 | facebook/zstd golden-compression inputs | BSD-3-Clause | 4 raw data | CANDIDATE (seeds) |
| SOURCE-007 | python-zstandard test suite | BSD-3-Clause | — | REJECTED (no .zst files) |
| SOURCE-008 | Arch Linux .pkg.tar.zst | Per-package | — | CONDITIONAL |

## Key URLs

- facebook/zstd golden-decompression: https://github.com/facebook/zstd/tree/dev/tests/golden-decompression
- facebook/zstd golden-decompression-errors: https://github.com/facebook/zstd/tree/dev/tests/golden-decompression-errors
- decodecorpus: https://github.com/facebook/zstd/blob/dev/tests/decodecorpus.c
- python-zstandard: https://github.com/indygreg/python-zstandard

## Files Created (R15A)

- acquisition-packs/zst/sample-sources.md (Gate 3A output)
- reports/samples/zst-candidate-source-discovery-report-20260515.md
- reports/legal/zst-sample-source-license-provenance-audit-20260515.md
- reports/samples/zst-corpus-design-plan-20260515.md
- reports/governance/r15a-preflight-and-lane-ownership-20260515.md
- reports/governance/r15a-gate3-semantics-and-boundary-report-20260515.md
- reports/governance/r15a-registry-and-pack-state-update-report-20260515.md
- taskcards/ZST-R16-GATE3B-SAMPLE-CORPUS-ACQUISITION.md (pending R16)
- taskcards/ZST-GATE3-IV.md (pending Gate 3B completion)

## Registry State After R15A

- registry gate_3.status: source_identification_complete (NOT passed)
- pack.yaml sample_sources.status: source_identification_complete
- samples/by-format/zst/: DOES NOT EXIST
- implementation_authorized: false (unchanged)
- commercial_product_ready: false (unchanged)

## Planned Gate 3B Corpus

8 valid frames + 3 error fixtures = 11 files in samples/by-format/zst/
See: reports/samples/zst-corpus-design-plan-20260515.md

## Next Sprint

R16: FORMAT-FACTORY-R16-ZST-GATE3B-SAMPLE-CORPUS-ACQUISITION-SWARM-001
Requires: execution prompt from Babar Raza
Pre-conditions: R15A complete (YES), sample-sources.md (YES), ZST-R16 taskcard (YES)
