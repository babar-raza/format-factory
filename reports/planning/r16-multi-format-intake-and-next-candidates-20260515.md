# R16 Multi-Format Intake and Next Candidates — Planning Report
Sprint: FORMAT-FACTORY-R16-ZST-GATE3B-CORPUS-ACQUISITION-IV-AND-MULTI-FORMAT-INTAKE-SWARM-001
Date: 2026-05-15
Gate: 8 — Multi-format intake planning

## Purpose

Identify and document candidate format identities as scoped in the R16 sprint prompt.
No Gate 1 approvals are granted. This is a planning and identity survey only.

## Formats Surveyed

### ODF Flat Family (FODP, FODG, FODB)

All three are single-file XML variants of ZIP-based ODF formats. They share:
- **Spec:** OASIS ODF 1.3 (same as FODS and FODT)
- **Legal:** OASIS Royalty-Free on Limited Terms (Category 1) — same basis already approved for FODS/FODT
- **Pipeline reuse:** HIGH — existing spec cache, oracle provider, and legal analysis reusable

| Format | Family | Priority | Notes |
|--------|--------|----------|-------|
| FODP (.fodp) | Slides | HIGH | Flat XML presentation; OASIS ODF 1.3; best candidate for ODF batch |
| FODG (.fodg) | Drawing/Diagram | Medium | Flat XML drawing; same spec; narrower use case |
| FODB (.fodb) | Database | DEFER | Database schema less standard; Aspose support unclear |

**Recommended approach:** Process FODP and FODG as a batch after FODS/FODT Conway R9 proof stable.
FODB deferred until Aspose support is confirmed.

### R11 Planning Bundle Candidates (Gnumeric, ABW)

| Format | Score | Band | Extension | Description |
|--------|-------|------|-----------|-------------|
| Gnumeric | 8.75 | ACQUISITION_READY | .gnumeric | Gzip XML spreadsheet; public spec; GNOME project |
| ABW | 8.75 | ACQUISITION_READY | .abw | XML word processor; public spec; AbiWord |

Both are ACQUISITION_READY by R11 scoring. Both require:
- Independent DEC-034 Gate 1 scoring verification
- Aspose support audit (neither confirmed yet)
- Conway R9 stable + FODS/FODT proof as prerequisite

### ORA (OpenRaster)

- `.ora`, image/openraster, freedesktop.org spec
- ZIP container with PNG tiles + XML stack
- Mentioned as "Gate 5 fallback ORA" in R13 context
- Aspose.Imaging support needs audit
- Medium priority; niche use case

### dnumber — IDENTITY UNRESOLVED

The identifier "dnumber" does not match any known standard format.
**Action required:** Human must clarify what format "dnumber" refers to before it can
be added to the acquisition pipeline.

## Current Pipeline State

| Format | Gate Status | Next Action |
|--------|-------------|-------------|
| FODS | Gates 1-10 PASSED; Gate 11 in_progress | Conway R9 + Gate 11 |
| FODT | Gates 1-10 PASSED; Gate 11 in_progress | Conway R9 + Gate 11 |
| ZST | **Gate 3 PASSED (R16)** | R17 Gate 4 planning |
| FODP | Candidate only | ODF batch after Conway R9 |
| FODG | Candidate only | ODF batch after Conway R9 |
| FODB | Candidate (DEFER) | Aspose audit first |
| Gnumeric | Candidate (8.75) | DEC-034 IV then Gate 1 |
| ABW | Candidate (8.75) | DEC-034 IV then Gate 1 |
| ORA | Candidate | Aspose audit + Gate 1 |
| dnumber | BLOCKED | Identity clarification needed |

## Candidate Shortlist Artifact

Full candidate survey: `acquisition-packs/_candidate-shortlists/r16-multi-format-intake-and-next-candidates-20260515.md`

## Constraints

- WIP limit: max 2 formats in Gates 4-6 simultaneously (per master-plan Section 38)
- No Gate 1 approved in this sprint for any new format
- Conway R9 must be proven before ODF batch begins
- DEC-034 IV required for any new Gate 1 scoring

GATE_8_MULTI_FORMAT_INTAKE: COMPLETE
