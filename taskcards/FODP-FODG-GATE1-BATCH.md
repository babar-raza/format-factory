---
taskcard_id: FODP-FODG-GATE1-BATCH
title: "FODP + FODG Gate 1 Batch Approval (R19)"
type: gate_sprint
sprint: FORMAT-FACTORY-R18-QUARTER-MILE-ZST-GATE4-GATE5-AND-MULTI-FORMAT-GATE1-SWARM-001
created_by_sprint: FORMAT-FACTORY-R17-R16-CLOSURE-VERIFY-ZST-GATE4-PLANNING-AND-MULTI-FORMAT-GATE1-SWARM-001
created_at: "2026-05-16"
status: completed
visibility: internal
publish_allowed: false
authority: plans/master-plan.md
gate: 1
---

# Taskcard: FODP-FODG-GATE1-BATCH

## Identity Summary

| Format | Extension | MIME | Spec | Legal |
|--------|-----------|------|------|-------|
| FODP | .fodp | application/vnd.oasis.opendocument.presentation-flat-xml | OASIS ODF 1.3 | Cat 1 (OASIS RF) |
| FODG | .fodg | application/vnd.oasis.opendocument.graphics-flat-xml | OASIS ODF 1.3 | Cat 1 (OASIS RF) |

## Scope

Gate 1 batch approval for FODP and FODG.

### Deliverables

1. **Scoring sheets** for FODP and FODG (using _scoring-model.md)
2. **Aspose support audit** for:
   - Aspose.Slides + .fodp
   - Aspose.Diagram or Aspose.Imaging + .fodg
3. **DEC-034 IV** of Gate 1 scoring for both formats
4. **Registry entries** for fodp and fodg (if Gate 1 approved)
5. **Acquisition packs** under acquisition-packs/fodp/ and acquisition-packs/fodg/
6. **Gate 1 reports**

### Fast-Path

FODP and FODG use same OASIS ODF 1.3 spec as FODS/FODT.
Gate 2 fast-path eligible once Gate 1 is approved.

### Hard Invariants
- No Gate 2+ proceeding without Gate 1 approval
- No spec download without authorization
- No samples without Gate 3 authorization
- DEC-034 IV required before Gate 1 approval

## Pre-conditions for Sprint Launch

1. Conway R9 stable (FODS/FODT proof foundation solid)
2. Aspose audit authorized for Slides + Diagram
3. Execution prompt from Babar Raza naming both formats
4. WIP check: ≤2 formats in Gates 4-6 simultaneously

## Suggested Sprint ID

FORMAT-FACTORY-R19-FODP-FODG-GATE1-BATCH-SWARM-001

## Notes

FODP and FODG share identical spec, legal basis, and pipeline infrastructure with FODS/FODT.
Batch approach is strongly recommended — process both in same sprint to minimize overhead.
Estimated Gate 1 scores: FODP ~8.5-8.8, FODG ~8.2-8.5.
