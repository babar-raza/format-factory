# R89 Trains H-J: .NET Product Deepening

## Sprint
FORMAT-FACTORY-R89-AUTHORITATIVE-TEST-BASELINE-DECLARATION-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

## Train H: Netpbm .NET (3 new APIs, 13 tests)

### New APIs
- `GetChannelStats()` — per-channel (R,G,B) statistics for PPM: Mean, Min, Max
- `Rotate90Cw()` — 90° clockwise rotation, returns new image (dimensions swap)
- `Crop(top, left, height, width)` — extract rectangular sub-region, returns new image

### Tests Added (NetpbmR89ProductDeepeningTests.cs)
- GetChannelStats: per-channel stats, throws on PGM, single pixel (3 tests)
- Rotate90Cw: dimension swap, pixel mapping, 4x restoration, PPM channels, comments (5 tests)
- Crop: subregion extraction, full-image copy, PPM channels, invalid bounds, zero dim (5 tests)

### Results
- Netpbm .NET: 84 passed (was 71, +13)

## Train I: FODS .NET (1 new API, 6 tests)

### New API
- `ExportSheetToCsvString(sheet)` — in-memory CSV export (no file I/O), LF line endings

### Tests Added (FodsR89InMemoryCsvTests.cs)
- Returns non-empty, contains cell data, LF endings, null guard, row count, escape (6 tests)

### Results
- FODS .NET: 191 passed (was 185, +6)

## Train J: FODT .NET (2 new APIs, 9 tests)

### New APIs
- `CharCount` — character count across all paragraphs (excludes joining newlines)
- `SearchText(query, comparison)` — find all occurrences, returns (paragraphIndex, position) tuples

### Tests Added (FodtR89TextSearchTests.cs)
- CharCount: non-negative, matches plaintext, non-zero for content (3 tests)
- SearchText: finds known word, empty for missing, case-insensitive, empty throws, paragraph index, multiple (6 tests)

### Results
- FODT .NET: 176 passed (was 167, +9)

## .NET Delta Summary
| Project | R88 | R89 | Delta |
|---------|-----|-----|-------|
| Netpbm  | 71  | 84  | +13   |
| FODS    | 185 | 191 | +6    |
| FODT    | 167 | 176 | +9    |
| **Total** | **423** | **451** | **+28** |

## Status: COMPLETE
