---
taskcard_id: R17-MULTI-FORMAT-GATE1-INTAKE
title: "R17 Multi-Format Gate 1 Intake — Gnumeric, ABW, FODP, FODG"
type: planning
sprint: FORMAT-FACTORY-R17-R16-CLOSURE-VERIFY-ZST-GATE4-PLANNING-AND-MULTI-FORMAT-GATE1-SWARM-001
created_by_sprint: FORMAT-FACTORY-R16-ZST-GATE3B-CORPUS-ACQUISITION-IV-AND-MULTI-FORMAT-INTAKE-SWARM-001
created_at: "2026-05-15"
completed_at: "2026-05-16"
status: completed
visibility: internal
publish_allowed: false
authority: plans/master-plan.md
---

# Taskcard: R17-MULTI-FORMAT-GATE1-INTAKE

## Current State: PENDING_AUTHORIZATION

Multi-format intake survey completed in R16. Format identities documented.
Gate 1 NOT approved for any new format. Awaiting Conway R9 proof and human authorization.

## Scope

Gate 1 intake candidates for the next batch sprint:

| Format | Score | Priority | Blocker |
|--------|-------|----------|---------|
| Gnumeric | 8.75 (R11) | HIGH | Conway R9; DEC-034 IV |
| ABW | 8.75 (R11) | HIGH | Conway R9; DEC-034 IV |
| FODP | Accept | Medium | Conway R9; ODF batch |
| FODG | Borderline | Lower | Conway R9; ODF batch |

## Pre-conditions

1. Conway R9 proof complete (FODS/FODT automation proven)
2. ZST R17 Gate 4 (parser planning) either in-flight or complete
3. WIP check: ≤2 formats in Gates 4-6 simultaneously
4. DEC-034 IV of Gate 1 scoring for each new format (separate session)
5. Explicit R17 prompt from Babar Raza naming each authorized format

## What Is NOT Authorized

- No Gate 1 approval for any format listed here
- No acquisition pack creation
- No registry entry for any new format
- No spec download or corpus work

## Source Documents

- Identity survey: acquisition-packs/_candidate-shortlists/r16-multi-format-intake-and-next-candidates-20260515.md
- Gnumeric/ABW scores: R11 planning bundle (tools/skills/acquisition_planning_runtime.py)
- ODF family: registry/candidates/odf-flat-family-shortlist.yaml
