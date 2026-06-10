# R106 Product Capability Delta

## New .NET APIs (Wave 2)

| Format | API | Behavior | Tests |
|--------|-----|----------|-------|
| FODS | `ClearSheet(string)` | Remove all rows from named sheet | 8 |
| FODS | `GetColumnValues(string, int)` | Extract column values as string list | 8 |
| FODT | `RemoveAllParagraphs()` | Remove all paragraph elements | 8 |
| FODT | `GetTextBetweenParagraphs(int, int)` | Extract text range between paragraph indices | 8 |
| Netpbm | `FlipDiagonal()` | Transpose image (swap rows/columns) | 8 |
| Netpbm | `Overlay(NetpbmImage, int, int)` | Composite overlay image at offset | 10 |

## FOSS Python Tests (Wave 3)

| Format | Test File | Tests | Coverage |
|--------|-----------|-------|----------|
| ZST | test_r106_zst_streaming_proof.py | 9 | Chunk roundtrip, magic bytes, validation |
| PBM | test_r106_pbm_write_roundtrip.py | 10 | 1x1, checkerboard, wide, tall, large |
| PGM | test_r106_pgm_strict_errors.py | 9 | Empty, invalid magic, safe mode, comments |
| PPM | test_r106_ppm_write_maxval.py | 9 | Maxval variants, single pixel, gradient |
| SYLK | test_r106_sylk_write_roundtrip.py | 9 | Numeric, string, grid, mixed, sparse |

## Dogfood Tests (Wave 4)

| Format | Test File | Tests | Pipeline |
|--------|-----------|-------|----------|
| FODS | FodsR106DogfoodSaveRoundtripTests.cs | 6 | ClearSheet+InsertRow+Save roundtrip |
| FODT | FodtR106DogfoodSaveRoundtripTests.cs | 6 | RemoveAll+Append+Save roundtrip |
| Netpbm | NetpbmR106DogfoodCropOverlayTests.cs | 6 | Crop+Overlay+FlipDiagonal pipeline |

## Cumulative Test Counts

| Track | Before R106 | After R106 | Delta |
|-------|-------------|------------|-------|
| Python | 2857 | 2903 | +46 |
| FODS .NET | 353 | 375 | +22 |
| FODT .NET | 363 | 363 | +22 → 363 |
| Netpbm .NET | 267 | 291 | +24 |
| **Grand Total** | **3818** | **3932** | **+114** |
