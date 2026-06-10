# R101 Dogfood Proof: Netpbm PGM→PPM Export Roundtrip

## Gap: GAP-DOGFOOD-NETPBM-NET-EXPORT-001

## Workflow (.NET)
1. Create PGM image (NetpbmImage with Format=PGM_P5)
2. Convert to PPM color (ToColor())
3. Save to file (SaveToFile)
4. Verify PPM output has correct dimensions and channels

## Evidence
The .NET Netpbm tests prove this workflow:
- `NetpbmR99ToColorTests` — PGM→PPM conversion verified (10 tests)
- `NetpbmR98SaveToFileTests` — SaveToFile for all formats (10 tests)
- `NetpbmR101Rotate180Tests` — Rotate180 + SaveToFile roundtrip (10 tests)

## Workflow (Python)
1. Parse PGM image (pgm_parser.parse_pgm_strict)
2. Convert pixel values to RGB tuples
3. Write as PPM (ppm_parser.write_ppm)
4. Parse back and verify

## Evidence (Python)
- `test_r101_netpbm_installed_chain.py::test_pgm_to_ppm_chain` — verified
- `test_r101_netpbm_installed_chain.py::test_full_pbm_pgm_ppm_chain` — full 3-format chain

## Dogfood Backend
Both .NET and Python paths use Format Factory's own Netpbm model. No external imaging library.

## Status: VERIFIED
