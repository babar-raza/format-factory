---
document_type: sprint_report
sprint: FORMAT-FACTORY-R28-LANE-L-NEW-CANDIDATE-EXPANSION-001
title: "R28 Lane L — New Candidate Expansion: PPM and DIF"
date: "2026-05-19"
visibility: internal
publish_allowed: false
authority: plans/master-plan.md
---

# R28 Lane L — New Candidate Expansion Report

**Sprint:** FORMAT-FACTORY-R28-LANE-L-NEW-CANDIDATE-EXPANSION-001
**Date:** 2026-05-19
**Lane:** L (New Candidate Expansion)

---

## 1. Candidate Selection

Two new format candidates were selected from the format expansion roadmap based on these criteria:
- Public domain / fully public specification (legal category 1)
- NOT supported by Aspose (high differentiation value)
- Trivially simple structure (deterministic sample generation with Python stdlib)
- No overlap with existing formats (FODS, FODT, ZST, FODP, FODG, Gnumeric, ABW, ODS, ODT, QOI, XCF, ZPAQ)
- No AI needed for any gate work

### Selected Candidates

| Format | Family | Spec Status | Aspose | Score | Band |
|--------|--------|-------------|--------|-------|------|
| **PPM** (Portable Pixmap / Netpbm) | imaging | Public domain (1988) | NOT_SUPPORTED | 9.1/10 | Accept |
| **DIF** (Data Interchange Format) | cells | Public domain (1981) | NOT_SUPPORTED | 8.7/10 | Accept |

### Why These Two

**PPM** is the simplest possible raster image format. P3 (ASCII) variant is human-readable text. No compression, no container, no metadata complexity. It is the color member of the Netpbm family (PBM/PGM/PPM), widely used in scientific imaging and Unix toolchains. Not supported by Aspose. Gateway to the entire Netpbm family.

**DIF** is a text-based spreadsheet interchange format created by the makers of VisiCalc in 1981. Line-oriented, trivially parseable, still supported by Excel and LibreOffice for import. Not supported by Aspose. Complements FODS/ODS in the cells track with an entirely different format structure.

### Candidates Considered but Not Selected

| Format | Reason |
|--------|--------|
| SVG | XML-based, large spec (W3C), higher implementation complexity than needed for this sprint |
| ICO | Binary format with moderate complexity (multiple image sizes, BMP/PNG embedded) |
| SYLK | Text-based cells format, but less well-documented than DIF and more obscure |
| PBM/PGM | Same Netpbm family as PPM; PPM is the superset (color), so it covers the family |

---

## 2. Gate Results Summary

### PPM — Gates 1-3

| Gate | Status | Method |
|------|--------|--------|
| Gate 1 (Scoring) | PASS (9.1/10, Accept) | delegated_agent_decision_r28 |
| Gate 2 (Spec Evidence) | PASS | delegated_agent_decision_r28 |
| Gate 3 (Sample Corpus) | PASS (3 valid + 1 invalid) | delegated_agent_decision_r28 |

**Gate 1 Scoring Detail (PPM):**
- Legal safety: 3/3 (30 pts) — public domain
- Spec availability: 3/3 (20 pts) — single-page spec, complete
- Parseable structure: 3/3 (15 pts) — trivially parseable text
- Community demand: 2/3 (10 pts) — toolchain standard, not consumer
- Strategic track value: 2/3 (7 pts) — not supported by Aspose, imaging gap
- Implementation complexity: 3/3 (6 pts) — ~50 lines of Python
- Family overlap: 2/3 (3 pts) — new Netpbm family
- **Total: 91/100 = 9.1/10**

**Gate 3 Corpus (PPM):**
- `valid/1x1-red.ppm` — 19 bytes, 1x1 red pixel
- `valid/2x2-rgbw.ppm` — 47 bytes, 2x2 RGBW test image
- `valid/3x1-gradient.ppm` — 41 bytes, 3x1 greyscale gradient
- `invalid/wrong-magic.ppm` — 19 bytes, P9 instead of P3/P6

### DIF — Gates 1-3

| Gate | Status | Method |
|------|--------|--------|
| Gate 1 (Scoring) | PASS (8.7/10, Accept) | delegated_agent_decision_r28 |
| Gate 2 (Spec Evidence) | PASS | delegated_agent_decision_r28 |
| Gate 3 (Sample Corpus) | PASS (3 valid + 1 invalid) | delegated_agent_decision_r28 |

**Gate 1 Scoring Detail (DIF):**
- Legal safety: 3/3 (30 pts) — public domain
- Spec availability: 3/3 (20 pts) — multiple public sources
- Parseable structure: 3/3 (15 pts) — line-oriented text
- Community demand: 1/3 (5 pts) — legacy format, low modern demand
- Strategic track value: 2/3 (7 pts) — not supported by Aspose, cells gap
- Implementation complexity: 3/3 (6 pts) — ~80 lines of Python
- Family overlap: 2/3 (4 pts) — same cells family but different structure
- **Total: 87/100 = 8.7/10**

**Gate 3 Corpus (DIF):**
- `valid/minimal-2x2.dif` — 187 bytes, 2x2 mixed string/numeric
- `valid/single-cell.dif` — 108 bytes, single numeric cell
- `valid/numeric-row.dif` — 123 bytes, 3-column numeric row
- `invalid/missing-table-header.dif` — 47 bytes, NOTABLE instead of TABLE

---

## 3. Artifacts Created

### Acquisition Packs
- `acquisition-packs/ppm/pack.yaml` — Gates 1-3 complete
- `acquisition-packs/dif/pack.yaml` — Gates 1-3 complete

### Sample Corpus
- `samples/by-format/ppm/valid/` — 3 valid PPM P3 samples
- `samples/by-format/ppm/invalid/` — 1 invalid sample
- `samples/by-format/ppm/_corpus-manifest.yaml`
- `samples/by-format/ppm/_provenance.yaml`
- `samples/by-format/dif/valid/` — 3 valid DIF samples
- `samples/by-format/dif/invalid/` — 1 invalid sample
- `samples/by-format/dif/_corpus-manifest.yaml`
- `samples/by-format/dif/_provenance.yaml`

### Report
- `reports/planning/r28-new-candidate-expansion-report-20260519.md` (this file)

---

## 4. Human IV Status

All gates are `awaiting_human_iv: true` per DEC-034. No gate has been self-approved.

---

## 5. Next Steps

1. Human IV of Gates 1-3 for both PPM and DIF
2. Gate 4 parser planning (after IV approval)
3. Consider PBM/PGM as fast-path additions once PPM parser is proven (same Netpbm family)

---

## 6. Format Pipeline Status (Updated)

| Format | Gates Passed | Status |
|--------|-------------|--------|
| FODS | 1-10 | Gate 11 in progress |
| FODT | 1-10 | Gate 11 in progress |
| ZST | 1-10 | Release candidate ready |
| FODP | 1-10 | Verified |
| FODG | 1-10 | Verified |
| Gnumeric | 1-10 | Verified |
| ABW | 1-10 | Verified |
| ODS | 1-4 | Gate 4 prototype complete |
| ODT | 1-3 | IV verified |
| QOI | 1-3 | IV verified |
| XCF | 1-3 | Active |
| ZPAQ | 1-3 | Active |
| **PPM** | **1-3** | **NEW — awaiting human IV** |
| **DIF** | **1-3** | **NEW — awaiting human IV** |
