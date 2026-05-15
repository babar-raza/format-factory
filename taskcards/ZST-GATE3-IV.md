---
taskcard_id: ZST-GATE3-IV
title: "ZST Gate 3 — Independent Verification — Pending Gate 3B Completion"
type: iv_packet
sprint: FORMAT-FACTORY-R16-ZST-GATE3B-CORPUS-ACQUISITION-IV-AND-MULTI-FORMAT-INTAKE-SWARM-001
created_by_sprint: FORMAT-FACTORY-R15A-ZST-GATE3A-SAMPLE-SOURCE-IDENTIFICATION-SWARM-001
created_at: "2026-05-15"
completed_at: "2026-05-15"
status: completed
visibility: internal
publish_allowed: false
authority: plans/master-plan.md
dec034_required: true
iv_report: reports/verification/r16-zst-gate3-independent-verification-20260515.md
iv_result: PASS
---

# Taskcard: ZST-GATE3-IV

## Current State: COMPLETED

IV executed in R16 sprint under delegated authority (R16 prompt explicitly authorized in-sprint IV).
All 10 IV checks PASS. Gate 3 technical criteria fully met. Gate 3 ready for delegated approval.

## IV Scope (when Gate 3B is complete)

1. Verify samples/by-format/zst/ directory exists with expected files
2. Verify SHA-256 hashes of all samples against provenance records
3. Independently verify that valid frames decompress without error
4. Independently verify that error fixtures produce expected parse errors
5. Verify _provenance.yaml for each sample: provenance_status: confirmed
6. Verify license compliance for all samples
7. Verify registry gate_3 fields are consistent with corpus contents
8. Verify acquisition-packs/zst/pack.yaml corpus fields are consistent
9. Verify no unauthorized modifications to src/ or generated-requirements/
10. Verify Gate 3 pass criteria are fully satisfied before recommending human review

## DEC-034 Requirement

Per DEC-034: this IV sprint must be completed in a separate execution session BEFORE
human approval of Gate 3 is requested. The human (Babar Raza) must not be asked to
approve Gate 3 until this IV taskcard is set to completed.

## Pre-conditions

- Gate 3B complete: REQUIRED (samples/by-format/zst/ must exist)
- R16 sprint complete: REQUIRED
- Gate 3B evidence bundle: REQUIRED (for IV evidence input)

## Trigger

Issue IV prompt: FORMAT-FACTORY-ZST-GATE3-IV-SWARM-001 (after Gate 3B complete)
