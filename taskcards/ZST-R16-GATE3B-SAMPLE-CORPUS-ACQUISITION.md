---
taskcard_id: ZST-R16-GATE3B-SAMPLE-CORPUS-ACQUISITION
title: "ZST Gate 3B — Sample Corpus Acquisition — Pending R16 Authorization"
type: gate_packet
sprint: null
created_by_sprint: FORMAT-FACTORY-R15A-ZST-GATE3A-SAMPLE-SOURCE-IDENTIFICATION-SWARM-001
created_at: "2026-05-15"
status: pending_authorization
visibility: internal
publish_allowed: false
authority: plans/master-plan.md
---

# Taskcard: ZST-R16-GATE3B-SAMPLE-CORPUS-ACQUISITION

## Current State: PENDING_AUTHORIZATION

Gate 3A source identification complete (R15A, 2026-05-15).
Gate 3B corpus acquisition NOT yet authorized.
A separate R16 execution prompt is required to begin corpus acquisition.

## Gate 3B Work (NOT YET STARTED)

Gate 3B must produce ALL of the following:
1. Create samples/by-format/zst/ directory with actual .zst files
2. Acquire or generate files from preferred sources (SOURCE-001 through SOURCE-005)
3. Create _provenance.yaml for each sample with provenance_status: confirmed
4. Create samples/by-format/zst/_error-fixtures/ with negative test fixtures
5. Record SHA-256 hash for each sample
6. Verify all samples using zstandard Python library (valid frames) or confirm expected parse errors (error fixtures)
7. Write corpus validation report
8. Update registry/format-registry.yaml gate_3.status (do NOT set to passed — that requires human approval)
9. Submit for DEC-034 IV (ZST-GATE3-IV.md) before requesting human review

## Planned Corpus (from Gate 3A design)

Valid frames (8):
- block-128k.zst (SOURCE-001, facebook/zstd, BSD-3)
- empty-block.zst (SOURCE-001, facebook/zstd, BSD-3)
- rle-first-block.zst (SOURCE-001, facebook/zstd, BSD-3)
- zeroSeq_2B.zst (SOURCE-001, facebook/zstd, BSD-3)
- minimal-synthetic.zst (SOURCE-003, python-zstandard, project-owned)
- text-compressed.zst (SOURCE-005, PD text + zstd CLI, project-owned)
- dict-compressed.zst (SOURCE-002, decodecorpus, project-owned)
- random-data.zst (SOURCE-002, decodecorpus, project-owned)

Error fixtures (3):
- off0.bin.zst (SOURCE-004, facebook/zstd, BSD-3)
- truncated_huff_state.zst (SOURCE-004, facebook/zstd, BSD-3)
- zeroSeq_extraneous.zst (SOURCE-004, facebook/zstd, BSD-3)

## Pre-conditions for R16

- Gate 3A complete: YES (R15A, 2026-05-15)
- sample-sources.md: YES (acquisition-packs/zst/sample-sources.md)
- Corpus design plan: YES (reports/samples/zst-corpus-design-plan-20260515.md)
- R16 execution prompt from Babar Raza: REQUIRED

## DEC-034 IV Requirement

Per DEC-034: independent IV sprint (ZST-GATE3-IV.md) required before requesting human review.
Gate 3 cannot be presented for human approval until ZST-GATE3-IV.md is completed.

## Trigger

Issue R16 prompt: FORMAT-FACTORY-R16-ZST-GATE3B-SAMPLE-CORPUS-ACQUISITION-SWARM-001
