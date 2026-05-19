# Format Completion Matrix — Human-Readable Summary

**Created:** R32 (2026-05-19)
**Source of truth:** `registry/format-completion-matrix.yaml`

---

## Summary

| Class | Count | Formats |
|-------|-------|---------|
| production_track_real | 3 | FODS, FODT, ZST |
| read_only_library_foundation | 2 | ODS, QOI |
| read_only_prototype | 4 | ODT, DIF, PPM, SYLK |
| probe_only | 5 | FODP, FODG, Gnumeric, ABW, XCF |
| acquisition_only | 4 | CSV, TSV, XPM, PAM |
| blocked | 1 | ZPAQ |
| stale_or_contaminated | 1 | ORA |
| **Total** | **20** | |

---

## Overclaim Risk

| Risk | Formats | Issue |
|------|---------|-------|
| **HIGH** | FODP, FODG, Gnumeric, ABW | Claimed G10, evidence supports G4 |
| **Moderate** | XCF | G8 passed but parser is header-only probe |
| **Low** | PPM | G8 passed but only ASCII P3 variant supported |
| **Low** | PGM, PBM | G7 reasonable for ASCII variant |
| None | All others | Claimed gates match evidence |

---

## Production Track (3 formats)

### FODS — Flat OpenDocument Spreadsheet
- **Tracks:** Python FOSS + .NET Commercial
- **Python:** 715 LOC, streaming XML, 6-entity neutral model, 70 tests
- **.NET:** 1286 LOC, Load/Save/Edit, 3 exporters (CSV/HTML/JSON), 160 tests, round-trip verified
- **Gate:** G11 in progress (G11-E complete, G11-G not started)
- **Weakest area:** Python has no write/export

### FODT — Flat OpenDocument Text
- **Tracks:** Python FOSS + .NET Commercial
- **Python:** 761 LOC, streaming XML, depth-tracking, 7-entity neutral model, 101 tests
- **.NET:** 1222 LOC, Load/Save/Edit, 3 exporters (HTML/TXT/Markdown), 142 tests, round-trip verified
- **Gate:** G11 in progress (G11-E complete, G11-G not started)
- **Weakest area:** Python has no write/export

### ZST — Zstandard Compressed File
- **Track:** Python FOSS only
- **Python:** 303 LOC, full codec (compress+decompress), bomb guards, 25 tests
- **Gate:** G10 verified
- **Strength:** Only Python format with write + round-trip

---

## Promising But Incomplete (6 formats)

| Format | LOC | Tests | Key Strength | Key Gap | Maturity |
|--------|-----|-------|-------------|---------|----------|
| ODS | 303 | 61 | ZIP container, typed cells, dataclass model | No write/export | read_only_library_foundation |
| QOI | 307 | 62 | Complete pixel decode (all 6 chunk types) | No encoder/export | read_only_library_foundation |
| ODT | 250 | 66 | ZIP container, paragraph/heading model | Shallow content extraction | read_only_prototype |
| DIF | 303 | 39 | Typed cell parsing, triplet structure | No write, 10 unsupported features | read_only_prototype |
| PPM | 228 | 40 | P3 ASCII full decode | P6 binary not supported | read_only_prototype |
| SYLK | 241 | 40 | Record-based parsing, cell coordinates | F/B/P records unsupported | read_only_prototype |

---

## Probe-Only (5 formats) — Overclaimed

| Format | LOC | Tests | What It Does | Claimed Gate | Evidence Gate |
|--------|-----|-------|-------------|-------------|---------------|
| FODP | 192 | 16 | Counts slides, extracts page names | G10 | G4 |
| FODG | 217 | 19 | Counts shapes by tag | G10 | G4 |
| Gnumeric | 170 | 16 | Counts cells from gzip+XML | G10 | G4 |
| ABW | 141 | 17 | Extracts paragraph text | G10 | G4 |
| XCF | 271 | 42 | Parses header+layer offsets (no pixels) | G8 | G5-G6 |

---

## Partial Support (3 formats)

| Format | LOC | Tests | Limitation | Gate |
|--------|-----|-------|-----------|------|
| PGM | 224 | 40 | P2 ASCII only, no P5 binary | G7 |
| PBM | 215 | 40 | P1 ASCII only, no P4 binary | G7 |
| PPM | 228 | 40 | P3 ASCII only, no P6 binary | G8 |

---

## Acquisition Only (4 formats)

CSV, TSV, XPM, PAM — packs and samples exist, no source code. Gate 3. No overclaims.

---

## Blocked / Stale

- **ZPAQ:** G3 blocked, ZPAQL VM complexity, requires zpaq CLI
- **ORA:** Deferred, 6.8/10 below 7.0 threshold
