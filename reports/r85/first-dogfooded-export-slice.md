# R85 Train P — First Dogfooded Export Slice

Sprint: FORMAT-FACTORY-R85-POC-DIRECTION-LOCAL-SUPERVISOR-AUTONOMOUS-PRODUCT-FACTORY-MEGA-TRAIN-001
Date: 2026-05-31

## Summary

R85 delivers 2 new dogfooded export implementations across Python and .NET tracks.
Both use Format Factory's own produced libraries as write backends.

## New Dogfooded Exports (R85)

### 1. Python: PBM → PGM

**File:** src/python/pbm/pbm_to_pgm.py

| Property | Value |
|----------|-------|
| Source library | format-factory-pbm (parse_pbm_strict) |
| Write backend | format-factory-pgm (write_pgm) |
| dogfood_status | IMPLEMENTED |
| External libs | NONE (verified by test) |
| Tests | 17 in tests/python/netpbm/test_r85_pbm_to_pgm_dogfood.py |
| Test result | ALL PASS |

**Pixel mapping:** PBM 1 (black) → PGM 0; PBM 0 (white) → PGM maxval

**Exported from package:** pbm.__init__ exports convert_pbm_to_pgm + pbm_pixels_to_pgm_pixels

### 2. .NET: PBM → PGM (and PBM → PPM)

**File:** src/net/netpbm/NetpbmExporter.cs

| Property | Value |
|----------|-------|
| Source model | FormatFactory.Netpbm.NetpbmImage |
| Write backend | FormatFactory.Netpbm.NetpbmWriter (FF) |
| dogfood_status | IMPLEMENTED |
| External libs | NONE (pure .NET, no NuGet image packages) |
| Tests | NetpbmExporterTests.cs (in 43-test suite) |
| Test result | ALL PASS |

**Methods:**
- `NetpbmExporter.PbmToPgm(NetpbmImage pbm, int maxValue=255)` → NetpbmImage (P2)
- `NetpbmExporter.PbmToPpm(NetpbmImage pbm, int maxValue=255)` → NetpbmImage (P3)
- `NetpbmExporter.PbmToPgmFile(NetpbmImage, string, int)` — file convenience
- `NetpbmExporter.PbmToPpmFile(NetpbmImage, string, int)` — file convenience

## Pre-existing Dogfooded Exports (R84 and earlier)

| Format | Track | Export | Status | Sprint |
|--------|-------|--------|--------|--------|
| SYLK | Python | CSV | IMPLEMENTED | R84 |
| FODT | Python | TXT | IMPLEMENTED | R79 |

## Dogfood Gap Status

Three .NET FODT exporters remain as GAP_DOGFOOD_EXTERNAL (TXT/HTML/MD).
All gaps documented in reports/r85/dogfood-export-map.md.
Gap remediation requires building .NET text/HTML/Markdown FF libraries (future sprint).

## Test Evidence

```
tests/python/netpbm/test_r85_pbm_to_pgm_dogfood.py
  TestPbmPixelsToPgmPixels: 9 tests — pixel mapping unit tests
  TestConvertPbmToPgmFile: 6 tests — file I/O integration
  TestDogfoodLibraryUsage: 2 tests — no external libs + uses FF write_pgm

tests/net/netpbm/NetpbmExporterTests.cs (included in 43-test total)
  PbmToPgm_ConvertsBlackToZero, PbmToPgm_ConvertsWhiteToMaxValue
  PbmToPgm_PreservesWidthHeight, PbmToPgm_RoundtripVerifiable
  PbmToPgm_DogfoodStatusComment, PbmToPpm_ConvertsToThreeChannel
```

## TRAIN_P_STATUS: COMPLETE
