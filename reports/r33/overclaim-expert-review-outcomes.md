# R33 Overclaim Expert Review Outcomes

**Sprint:** R33 Lanes B+C
**Date:** 2026-05-19
**Method:** Delegated expert review (source inspection, test analysis, gate criteria comparison)

---

## Review Summary

| Format | Claimed Gate | Evidence-Backed Gate | Verdict | Action |
|--------|-------------|---------------------|---------|--------|
| FODP | G10 | G4 | GATE_CORRECTION_REQUIRED | Annotate as probe_only, cap at G4 |
| FODG | G10 | G4 | GATE_CORRECTION_REQUIRED | Annotate as probe_only, cap at G4 |
| Gnumeric | G10 | G4 | GATE_CORRECTION_REQUIRED | Annotate as probe_only, cap at G4 |
| ABW | G10 | G4 | GATE_CORRECTION_REQUIRED | Annotate as probe_only, cap at G4 |
| XCF | G8 | G5-G6 | DEEPENING_REQUIRED (MINOR) | Accept G8 security pass for header scope; needs 8+ tests to reach 50 |
| PPM | G8 | G7 | READ_ONLY_SCOPE_APPROVED | G8 security valid for P3; P6 needed before G10 |
| PGM | G7 | G7 | CURRENT_GATE_SUPPORTED | No correction needed |
| PBM | G7 | G7 | CURRENT_GATE_SUPPORTED | No correction needed |

---

## Detailed Findings

### FODP — GATE_CORRECTION_REQUIRED

**Source:** 192 LOC page counter. Plain dict output, no neutral model, no write/export.
**Tests:** 16 — prove slide/page counting only.
**Why G10 is overclaimed:** Gate 10 per docs/gate-quality-criteria.md requires "write/export capability implemented and tested, OR round-trip capability verified, OR explicit read-only release scope approved." FODP has none of these.
**Correction:** evidence_backed_gate remains G4. Maturity class: probe_only. DRIFT taskcard updated with review outcome.

### FODG — GATE_CORRECTION_REQUIRED

**Source:** 217 LOC shape counter. Plain dict output, no neutral model, no write/export.
**Tests:** 19 — prove shape counting only.
**Same gap as FODP.** 217 LOC shape counter cannot be a "local release candidate."
**Correction:** Same as FODP.

### Gnumeric — GATE_CORRECTION_REQUIRED

**Source:** 170 LOC (smallest spreadsheet parser). Plain dict, no cell type detection, no write.
**Tests:** 16 — prove cell counting only.
**Gap:** G10 requires write/export. 170-line cell counter with no type detection has no path to release candidate without significant deepening.
**Correction:** Same as FODP.

### ABW — GATE_CORRECTION_REQUIRED

**Source:** 141 LOC (smallest parser in project). Plain dict, paragraph text extraction only.
**Tests:** 17 — prove text extraction works.
**Gap:** Same as FODP. 141 lines with no model, no write, no export.
**Correction:** Same as FODP.

### XCF — DEEPENING_REQUIRED (MINOR)

**Source:** 271 LOC header+layer inspector. Has dataclass model (XcfImage). Explicitly declares pixel_decode/tile_decode as unsupported.
**Tests:** 42 — prove header, property list, layer offset parsing. Quality is adequate for what it does.
**Security:** G8 security review is valid for the scope of parsing (header/property/layer metadata).
**Gap:** Parser is a probe/inspector, not an image library. However, XCF pixel decoding is extremely complex (RLE tiles, layer compositing). Deepening to pixel decode may not be cost-effective.
**Decision:** Accept G8 as valid for header-inspector scope. Add scope annotation to matrix. Need 8 more tests to reach 50-test floor for library-quality consideration.
**No gate correction needed** — G8 is earned for the parsing it performs. Maturity class stays probe_only with annotation.

### PPM — READ_ONLY_SCOPE_APPROVED

**Source:** 228 LOC, P3 ASCII full pixel decode. Has dataclass model (PpmImage).
**Tests:** 40 — prove complete P3 decode with dimension guards, malformed input handling.
**Security:** G8 is valid for P3 parsing.
**Gap:** P6 binary is the dominant real-world format. Without P6, library has limited practical value.
**Decision:** G8 is accurate for P3 scope. P6 must be added before G10. No gate correction, but scope limitation annotated.

### PGM — CURRENT_GATE_SUPPORTED

**Source:** 224 LOC, P2 ASCII decode. Dataclass model.
**Tests:** 40. Gate G7 is appropriate.
**Decision:** No correction needed. Binary P5 needed before advancing past G7.

### PBM — CURRENT_GATE_SUPPORTED

**Source:** 215 LOC, P1 ASCII decode. Dataclass model.
**Tests:** 40. Gate G7 is appropriate.
**Decision:** No correction needed. Binary P4 needed before advancing past G7.

---

## Aggregate Impact

- **4 formats with GATE_CORRECTION_REQUIRED** (FODP, FODG, Gnumeric, ABW): All at claimed G10 but evidence only supports G4. These are the clearest overclaim cases in the project.
- **1 format with DEEPENING_REQUIRED** (XCF): Minor — needs more tests but gate is valid for scope.
- **1 format with scope annotation** (PPM): G8 is valid but P6 gap must be disclosed.
- **2 formats with no correction** (PGM, PBM): Gate claims are honest.

## Gate Correction Policy Applied

Per docs/gate-quality-criteria.md and docs/prototype-quarantine-policy.md:
- Overclaimed gates are NOT rolled back in pack.yaml (preserve history)
- format-completion-matrix.yaml `evidence_backed_gate` records the true gate
- DRIFT taskcards record the review outcome and remediation path
- Formats remain in src/python/ but are classified as probe_only in the matrix
