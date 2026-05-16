---
taskcard_id: ORA-GNUMERIC-ABW-GATE1-SCORING-IV
title: "ORA + Gnumeric + ABW Gate 1 Scoring and IV (R19/R20)"
type: gate_sprint
sprint: null
created_by_sprint: FORMAT-FACTORY-R17-R16-CLOSURE-VERIFY-ZST-GATE4-PLANNING-AND-MULTI-FORMAT-GATE1-SWARM-001
created_at: "2026-05-16"
status: pending_execution_prompt
visibility: internal
publish_allowed: false
authority: plans/master-plan.md
gate: 1
---

# Taskcard: ORA-GNUMERIC-ABW-GATE1-SCORING-IV

## Identity Summary

| Format | Extension | Legal Cat | R11 Score | Estimated Score |
|--------|-----------|-----------|-----------|-----------------|
| Gnumeric | .gnumeric, .gnm | 2 (OSS) | 8.75 | 8.0-8.5 |
| ABW | .abw, .abw.gz | 2 (OSS) | 8.75 | 7.5-8.0 |
| ORA | .ora | 2 (community) | — | 6.5-7.0 |

## Scope

Gate 1 scoring verification and IV for ORA, Gnumeric, and ABW.

### Deliverables

1. **Gate 1 scoring sheets** for all three formats
2. **Aspose support audits** for:
   - Aspose.Cells + .gnumeric
   - Aspose.Words + .abw
   - Aspose.Imaging + .ora
3. **DEC-034 IV** of Gate 1 scoring for all three (separate session)
4. **Spec research** for ORA (confirm spec completeness at freedesktop.org)
5. **Registry entries** and acquisition packs (if Gate 1 approved)
6. **Rejection note** for any format that fails scoring

### Notes on Individual Formats

**Gnumeric:** R11 score 8.75. Gzip + XML structure. Re-score against current model.
**ABW:** R11 score 8.75. Outdated AWML DTD may reduce spec availability score.
**ORA:** New candidate. ZIP + PNG + XML. Lower community demand. Aspose audit critical.

### Hard Invariants
- No Gate 2+ without Gate 1 approval
- DEC-034 IV required before Gate 1 approval
- No spec download or sample creation without authorization

## Pre-conditions for Sprint Launch

1. R17 scoring packets complete (DONE in this sprint)
2. Aspose audit authorized for each format
3. Execution prompt from Babar Raza
4. WIP check: ≤2 formats in Gates 4-6 simultaneously

## Suggested Sprint ID

FORMAT-FACTORY-R20-ORA-GNUMERIC-ABW-GATE1-SCORING-IV-SWARM-001

## Priority

- Gnumeric: HIGH (ACQUISITION_READY band; strong pipeline fit)
- ABW: HIGH (ACQUISITION_READY band; spec risk needs re-assessment)
- ORA: MEDIUM (lower priority; Aspose audit is gating prerequisite)
