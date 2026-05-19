# memory/47 — R27 Gate 4 Prototypes, G11 C7/C8, Publication Blocker Reduction

**Sprint:** FORMAT-FACTORY-R27-GATE4-PROTOTYPES-G11-C7-C8-HARDENING-PUBLICATION-PACKET-AND-METADATA-SYNC-001
**Date:** 2026-05-19
**Verdict:** R27_COMPLETE

## Summary

R27 is the first "substantial work" sprint — three Gate 4 prototypes implemented, C7/C8 round-trip tests added for FODS/FODT .NET, publication blockers reduced for 5 Python FOSS packages, and two new format candidates (XCF, ZPAQ) acquired through Gates 1-3.

## Lanes and Outcomes

| Lane | Description | Outcome |
|------|-------------|---------|
| 0 | Coordinator/state | Preflight PASS, dirty AI files classified OUT_OF_SCOPE |
| A | R26 metadata sync | R26_METADATA_STALE_BUNDLE_COPY (known pattern, no repair) |
| B | Gate 4 authorization | ODS/ODT/QOI all GATE4_PROTOTYPE_AUTHORIZED (G-NORM-004 waiver) |
| C | ODS Gate 4 prototype | PASS — 9/9 tests, ZIP+XML parser, cell types, repeated col/row |
| D | ODT Gate 4 prototype | PASS — 10/10 tests, ZIP+XML parser, paragraphs/headings/lists |
| E | QOI Gate 4 prototype | PASS — 10/10 tests, full 6-op binary decoder |
| F | Cross-format harness | PASS — 15/15 tests (metadata, pack.yaml, safety guards, parse) |
| G | FODS C7/C8 | PASS — 16 new tests (10 C7 + 6 C8), FODS 136/136 |
| H | FODT C7/C8 | PASS — 16 new tests (9 C7 + 7 C8), FODT 124/124 |
| I | Python FOSS publication | README + LICENSE for 5 packages, 68/68 packaging PASS |
| J | New candidates | XCF Gates 1-3 PASS (7.8/10), ZPAQ Gates 1-2 PASS/G3 BLOCKED (6.2/10) |
| K | Memory/registry | Registry updated (6 formats), memory/47 created |
| L | Validation/IV/evidence | Full test suite, safety, adversarial review |

## Key Artifacts Created

### Source Code (Gate 4 Prototypes)
- `src/python/ods/` — ODS parser (ZIP container + content.xml, cell types, repeated cols/rows)
- `src/python/odt/` — ODT parser (ZIP container + content.xml, paragraphs, headings, lists)
- `src/python/qoi/` — QOI decoder (14-byte header, 6 chunk types, full pixel decode)

### .NET Tests (C7/C8 Round-Trip)
- `tests/net/fods/FodsC7C8RoundtripPreservationTests.cs` + fixture
- `tests/net/fodt/FodtC7C8RoundtripPreservationTests.cs` + fixture

### Publication Packet
- `src/python/{zst,fodp,fodg,gnumeric,abw}/README.md` — per-package READMEs
- `src/python/{zst,fodp,fodg,gnumeric,abw}/LICENSE` — Apache-2.0 license files

### New Format Candidates
- `acquisition-packs/xcf/pack.yaml` — XCF (GIMP) Gates 1-3 PASS
- `acquisition-packs/zpaq/pack.yaml` — ZPAQ Gates 1-2 PASS, Gate 3 BLOCKED
- `samples/by-format/xcf/` — 3 valid + 1 invalid XCF samples

## Test Baselines (R27)

| Suite | Count | Result |
|-------|-------|--------|
| Python full (--ignore=tests/net --ignore=tests/ai) | TBD | TBD |
| .NET FODS | 136 | 136/136 PASS |
| .NET FODT | 124 | 124/124 PASS |
| ODS prototype | 9 | 9/9 PASS |
| ODT prototype | 10 | 10/10 PASS |
| QOI prototype | 10 | 10/10 PASS |
| Cross-format harness | 15 | 15/15 PASS |
| Packaging | 68 | 68/68 PASS |

## Governance

- commercial_product_ready: false (all formats)
- G11-G: NOT_STARTED (requires Babar Raza)
- No AI files modified by this sprint (AI agent work classified OUT_OF_SCOPE)
- No push/PR/publication
- Gate 4 overclaim guard: production_source_authorized=true, commercial_product_ready=false
- ZPAQ in Review band (6.2/10) — human decision recommended
