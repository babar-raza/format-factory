# R37 Probe-Format Recovery Decision Packets

**Sprint:** R37
**Date:** 2026-05-20
**Context:** R33 overclaim review found FODP/FODG/Gnumeric/ABW at Gate 10 with probe-only maturity. R35/R36 applied gate corrections (G10->G4) and maturity_class=probe_only. This document provides recovery decision packets for each format.

## Recovery Options (applies to all 4 formats)

| Option | Description | Effort | Risk |
|--------|------------|--------|------|
| A: Deepen to Library | Add neutral model, write/export, round-trip. Restore to G5+ | High (per format) | Low |
| B: Quarantine as Probe | Keep in src/python/ but mark as probe-only. No further gate advancement | None | Medium (misleading) |
| C: Demote to Prototype | Move back to prototypes/by-format/. Remove from src/python/ | Low | Low |
| D: Deprecate | Remove from active pipeline. Keep acquisition pack only | Low | None |

## Format-Specific Decisions

### FODP (Flat ODP -- Presentation)
- **Current:** 192 LOC, page/slide counter, plain dict model, no write
- **Gate correction:** G10 -> G4 (probe_only)
- **Recovery value:** Low. Flat ODP is niche. LibreOffice Impress is the primary consumer.
- **Decision: QUARANTINE (Option B)**
  - Rationale: Not worth deepening investment. Keep as probe for format understanding. No gate advancement until explicit deepening sprint.
  - Required action: None -- already corrected in R35/R36.

### FODG (Flat ODG -- Graphics)
- **Current:** 217 LOC, shape counter, plain dict model, no write
- **Gate correction:** G10 -> G4 (probe_only)
- **Recovery value:** Low. Flat ODG is even more niche than FODP.
- **Decision: QUARANTINE (Option B)**
  - Rationale: Same as FODP. Keep as format probe. No gate advancement.
  - Required action: None -- already corrected.

### Gnumeric (Gnumeric Spreadsheet)
- **Current:** 170 LOC, gzip+XML cell counter, plain dict model, no write
- **Gate correction:** G10 -> G4 (probe_only)
- **Recovery value:** Medium. Gnumeric is a viable spreadsheet format with active community.
- **Decision: QUARANTINE (Option B) with DEEPENING_CANDIDATE flag**
  - Rationale: Worth deepening after ODS/ODT reach production quality. Gnumeric parsing benefits from ODS infrastructure (XML+ZIP patterns). Mark as deepening candidate for future sprint.
  - Required action: Add `deepening_candidate: true` to pack.yaml gate_correction.

### ABW (AbiWord)
- **Current:** 141 LOC, paragraph text extractor, plain dict model, no write
- **Gate correction:** G10 -> G4 (probe_only)
- **Recovery value:** Low. AbiWord project is dormant. Format has minimal adoption.
- **Decision: QUARANTINE (Option B)**
  - Rationale: Low investment value. Keep as probe. No gate advancement.
  - Required action: None -- already corrected.

## Summary Table

| Format | LOC | Decision | Deepening Priority | Next Gate Action |
|--------|-----|----------|-------------------|-----------------|
| FODP | 192 | Quarantine | None | No advancement |
| FODG | 217 | Quarantine | None | No advancement |
| Gnumeric | 170 | Quarantine + Candidate | After ODS/ODT | No advancement |
| ABW | 141 | Quarantine | None | No advancement |

## Production Deepening Priority Queue

These formats should be deepened BEFORE any probe-format recovery:

1. **ODS** (303 LOC, G8) -- Add write/export, formalize neutral model
2. **QOI** (307 LOC, G8) -- Add encoder/write capability
3. **ODT** (250 LOC, G8) -- Add write/export
4. **DIF** (303 LOC, G8) -- Add write capability
5. **SYLK** (241 LOC, G7) -- Deepen record support
6. Gnumeric (170 LOC, G4) -- Only after items 1-5

## Governance Note

All 4 formats have:
- `publication_authorized: false`
- `commercial_product_ready: false`
- `gate_correction.maturity_class: probe_only`
- Consistent corrections in pack.yaml, format-registry.yaml, and format-completion-matrix.yaml
