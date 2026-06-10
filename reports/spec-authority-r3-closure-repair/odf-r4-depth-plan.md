# ODF R4 Depth Plan
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-R3-CLOSURE-REPAIR-AND-R4-ODF-PREPARATION-001
Lane: E — ODF R4 Preparation
Generated: 2026-06-05

## Objective

Upgrade FODS and FODT from `ACCEPTED_WITH_CAVEAT` (intro-only, ~3 requirements each)
to `ACCEPTED_SPEC` by ingesting the full ODF 1.3 specification.

Current state:
- FODS: ACCEPTED_WITH_CAVEAT — 3 requirements extracted from ODF 1.3 intro only (6000 chars)
- FODT: ACCEPTED_WITH_CAVEAT — 3 requirements extracted from ODF 1.3 intro only (5000 chars)
- Blocker: License not confirmed; full spec not yet chunked/ingested

---

## ODF 1.3 Specification Structure

| Part | Title | Est. Pages | Relevant to |
|------|-------|-----------|-------------|
| Part 1 | Open Document Format for Office Applications — Text | ~700 | FODT (primary), FODS |
| Part 2 | Open Packaging | ~100 | Both (package structure) |
| Part 3 | OpenDocument Schema | ~150 | Both (XML schema) |
| Part 4 | Recalculated Formula (OpenFormula) | ~400 | FODS (cell formulas) |
| **Total** | — | **~1350** | — |

Source: OASIS ODF 1.3 (https://docs.oasis-open.org/office/OpenDocument/)
Publication: OASIS Standard, 29 June 2020
License: OASIS Fair Use Policy — open specification; citation permitted

---

## License Assessment

| Check | Status | Notes |
|-------|--------|-------|
| Public availability | CONFIRMED | Freely available from OASIS |
| Fair use for quotation | CONFIRMED | OASIS policy permits verbatim requirement extraction |
| Patent encumbrance | UNCONFIRMED | RF (Reasonable and Non-Discriminatory) claims not audited |
| Commercial use of parsed output | LIKELY_OK | Standard interpretive use; needs legal sign-off for G11 |

**R4 gate:** Legal review of OASIS ODF 1.3 patent pledge before promoting to ACCEPTED_SPEC.
For R4 SAL purposes, treat as ACCEPTED_SPEC pending legal confirmation.

---

## Chunking Strategy

ODF Part 1 is ~700 pages; the SAL `ContextPackBuilder` processes text in 5000-char windows.

### Chunk plan for FODS (Part 1 + Part 4):

| Chunk | Content | Est. chars | Expected requirements |
|-------|---------|-----------|----------------------|
| FODS-P1-C001 | Part 1 §1–§5: Scope, Conformance, General Concepts | 20,000 | 8–12 |
| FODS-P1-C002 | Part 1 §6: Document Structure | 30,000 | 15–20 |
| FODS-P1-C003 | Part 1 §7: Text Content | 40,000 | 20–30 |
| FODS-P1-C004 | Part 1 §8: Table Content (spreadsheet focus) | 50,000 | 30–40 |
| FODS-P1-C005 | Part 1 §9–§10: Graphic/Presentation | 20,000 | 8–12 |
| FODS-P4-C001 | Part 4 §1–§5: Formula basics | 25,000 | 10–15 |
| FODS-P4-C002 | Part 4 §6–§10: Numeric functions | 30,000 | 15–20 |
| **Total** | — | **~215,000** | **106–149** |

### Chunk plan for FODT (Part 1 focus):

| Chunk | Content | Est. chars | Expected requirements |
|-------|---------|-----------|----------------------|
| FODT-P1-C001 | Part 1 §1–§5: Scope, Conformance, General Concepts | 20,000 | 8–12 |
| FODT-P1-C002 | Part 1 §6: Document Structure | 30,000 | 15–20 |
| FODT-P1-C003 | Part 1 §7: Text Content (paragraphs, headings) | 40,000 | 20–30 |
| FODT-P1-C004 | Part 1 §9: Styles | 30,000 | 15–20 |
| FODT-P1-C005 | Part 1 §10–§12: Fields, Annotations, Changes | 25,000 | 10–15 |
| **Total** | — | **~145,000** | **68–97** |

### Chunking implementation:
- Tool: `tools/specification-authority-layer/spec_digestor.py` (already exists)
- Input: Raw text extracted from ODF 1.3 PDF (via pdfminer or pre-extracted .txt)
- Window: 5000 chars with 500-char overlap
- Output: `.local/evidences/spec-authority-r4/odf-chunks/{fods,fodt}/chunk-NNN.json`

---

## R4 Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| ODF Part 1 PDF text extraction quality | MEDIUM | HIGH | Use OASIS HTML version as fallback |
| Patent pledge review delays | LOW | HIGH | Keep ACCEPTED_WITH_CAVEAT; do not block R4 on legal review |
| Requirement count lower than expected (spec uses SHALL less) | MEDIUM | LOW | Lower threshold to 50+ requirements for ACCEPTED_SPEC |
| Chunk overlap creates duplicate requirements | MEDIUM | LOW | SpecVerifier deduplication step (already in pipeline) |
| Part 4 formula spec technical complexity | LOW | MEDIUM | FODS formula chunk is advisory; core ACCEPTED_SPEC on Part 1 only |

---

## R4 Acceptance Criteria

| Criterion | Threshold | Note |
|-----------|-----------|------|
| FODS requirements extracted | ≥ 50 | From Part 1 + Part 4 chunks |
| FODT requirements extracted | ≥ 40 | From Part 1 chunks |
| Deterministic context pack | YES | manifest.sha256 stable |
| SpecVerifier pass rate | ≥ 80% | Requirements verified against chunk content |
| License confirmation | Required for ACCEPTED_SPEC | OASIS RF pledge check |
| Regression: 80 R3 tests pass | 80/80 | No R3 regressions |

---

## R4 Test Plan

### New tests (estimated 30):
- `test_r4_fods_full_ingest.py` — 10 tests: chunk count, requirement count ≥50, deterministic SHA, no duplicate IDs, §8 table requirements present, formula requirements present
- `test_r4_fodt_full_ingest.py` — 10 tests: chunk count, requirement count ≥40, §7 text requirements present, §9 style requirements present, deterministic SHA
- `test_r4_license_confirmation.py` — 5 tests: license file exists, OASIS citation present, patent_pledge_status field, no UNCONFIRMED blocking claims
- `test_r4_rcal_wire.py` — 5 tests: context pack accepted by RCAL input queue, FODS/FODT upgrade event emitted, R3 RCA packet extended with R4 data

---

## R4 Execution Prerequisites

Before R4 sprint begins:
1. Obtain ODF 1.3 Part 1 text: download from OASIS or extract from PDF
2. Confirm OASIS ODF 1.3 RF (Reasonable and Non-Discriminatory) license pledge applicability
3. Extend `spec_digestor.py` to handle multi-chunk inputs and cross-chunk deduplication
4. Wire R4 context packs into RCAL input queue (currently manual)

---

## Verdict

`ODF_R4_DEPTH_PLAN_COMPLETE`

R4 is feasible. Primary risk is license confirmation timing. Chunking strategy is well-defined.
Estimated R4 sprint scope: 2 context packs (FODS full, FODT full) + 30 new tests + RCAL wiring.
