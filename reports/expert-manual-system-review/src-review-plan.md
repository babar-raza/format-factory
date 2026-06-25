# Source Code Review Plan
# Format Factory — Expert Manual System Review
# Phase 2 output — Generated: 2026-06-25

## Purpose

This plan defines the methodology for reviewing the `src/` directory — the actual product output.
The review approach is: **read source first, form independent judgment, then compare to authority claims**.

## Review Dimensions Per Product

Each product is reviewed on 8 dimensions (0–5 scale):
1. **API Design** — clean namespaces, professional naming, stable public surface
2. **Architecture Separation** — parser / model / writer / exporter boundaries
3. **Object Model Depth** — properties accessible, mutable where appropriate
4. **Error Handling** — meaningful exceptions, null safety, culture-invariant
5. **Roundtrip Correctness** — load → edit → save → reload verified
6. **Export/Dogfood** — exports to other FF libraries, physical output tested
7. **Test Meaningfulness** — behavior tests, edge cases, malformed input
8. **Commercial Polish** — XML docs, examples, streaming, culture settings

## .NET Review Order

Review order follows commercial priority (Gate 11 first, thin parsers last):

1. **FODS** — Gate 11 G11-G approved. Expected: HIGH score. Key check: ODS exporter "PROTOTYPE STATUS" vs. PASS in poc-targets.
2. **FODT** — Gate 11 G11-G approved. Expected: HIGH score. Key check: no table traversal in public model despite Spec/Table/*.cs stubs.
3. **NetPBM** — In progress. Expected: MEDIUM-HIGH. Key check: no dogfood export path; no NET format conversion.
4. **CSV** — Thin. Expected: LOW-MEDIUM. Key check: no edit API (AddRow/SetCell missing).
5. **TSV** — Thin. Expected: LOW-MEDIUM. Key check: minimal test surface despite CSV exporter.
6. **NDJSON** — Thin. Expected: LOW-MEDIUM. Key check: minimal test surface despite CSV exporter.
7. **ZST** — CRITICAL GAP. Expected: VERY LOW. Key check: probe-only with no decompression.
8. **HTML/Markdown/TXT** — Not format products. Expected: N/A (target writers only).

## Python Review Order

Review order by richness and commercial interest:

1. **FODS** — Most complete Python product. 12 Compat facades. Expected: HIGH.
2. **FODT** — Most complete Python product. 10 Compat facades. Expected: HIGH.
3. **GNUMERIC** — Full parser with dict model. Expected: MEDIUM.
4. **SYLK** — 741 LOC parser. File-based API. Expected: MEDIUM.
5. **TOML** — 728 LOC codec. Expected: MEDIUM.
6. **NDJSON** — 570+ LOC with analytics. Expected: MEDIUM.
7. **ZST** — 1,549 LOC codec (heavy analytics). Expected: MEDIUM (core is thin).
8. **XCF** — 1,272 LOC, parser-only. Expected: LOW-MEDIUM.
9. **PBM/PGM/PPM** — Image formats with cross-format exports. Expected: MEDIUM.
10. **QOI** — Has encoder. Expected: LOW-MEDIUM.
11. **ABW** — Parser + writer. Expected: MEDIUM.
12. **ODS** — Has ods_writer.py. Expected: MEDIUM.
13. **ODT** — Has odt_writer.py (added 2026-06-24). Expected: MEDIUM.
14. **CSV/TSV/DIF** — Thin parsers. Expected: LOW-MEDIUM.
15. **FODG** — Large codec. Expected: MEDIUM.
16. **FODP** — Read-only (no write_fodp). Expected: LOW (significant limitation).

## Review Verification Checks

For each product, verify against:
- `product-capability-matrix/poc-targets.yaml` — PASS claims must be traced to source
- `registry/parity-matrix.yaml` — spec parity claims must be traced to SAL or source
- `shared/qname-registry/{format}.yaml` — every `spec_qname` in source must match registry
- `.local/spec-cache/sal-facts-{format}.json` — if available, cross-check spec-parity claims

## Known Discrepancies to Investigate

| Claim | Location | Status | Investigation |
|-------|---------|--------|--------------|
| FodsOdsExporter PASS | poc-targets.yaml | Unverified | Source says "PROTOTYPE STATUS" |
| FODT table_support PASS | poc-targets.yaml | Unverified | Spec/Table/*.cs not in public API |
| ZST decompression | (absent) | VERIFIED MISSING | ZstParser.cs is probe-only |
| PDF Unicode support | (absent) | VERIFIED MISSING | FodsPdfExporter Latin-1 only |
| PPM/PBM/PGM writers | poc-targets.yaml | Now corrected | write_pbm/pgm/ppm confirmed in source |
| ODS Python write | poc-targets.yaml | Now corrected | ods_writer.py confirmed in source |

## Output Files

This review plan produces:
- `src-review-checklist.md` — per-product checklist with status
- `dotnet-commercial-review-matrix.json` — scored matrix (already exists)
- `python-foss-review-matrix.json` — scored matrix (already exists)
- `phase-a-investigation/confirmed-problems.json` — confirmed problem matrix
