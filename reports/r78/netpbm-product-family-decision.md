# R78 Netpbm Product Family Decision

**sprint_id:** FORMAT-FACTORY-R78-TRUE-STATE-AND-FIRST-PRODUCT-FINISH-REPRODUCIBILITY-MEGA-TRAIN-001
**date:** 2026-05-30
**train:** K

## Formats Under Decision

| Format | Description | Current Gate |
|---|---|---|
| PGM | Portable Graymap (P2 ASCII grayscale) | Gates 1-7 |
| PBM | Portable Bitmap (P1 ASCII bitmap) | Gates 1-7 |
| PPM | Portable Pixmap (P3 ASCII) | Gates 1-7 |

PPM is included for completeness as part of the Netpbm family.

## Decision Criteria

1. Public spec availability: YES (Netpbm is public domain, well-documented)
2. Implementation complexity: LOW (ASCII text format, simple parsing)
3. Python source exists: YES (src/python/pgm, src/python/pbm, src/python/ppm)
4. Package built: YES (wheel + sdist for pgm + pbm)
5. Market/use case: NICHE (legacy format; used in computer vision toolchains)
6. Gate 8 security: LOW RISK (read-only ASCII raster; no embedded code)

## Decision

NETPBM_FAMILY_DECISION: CONTINUE_TO_GATE_8_AND_BEYOND

Rationale:
- All three formats (PGM, PBM, PPM) have complete Gates 1-7 technical evidence
- Implementation is already done — no additional cost to advance
- The Netpbm family decision logically includes all three formats together
- Gate 8 security review is straightforward (ASCII read-only format)
- These formats serve as good examples of "simple image format" support
- Advancing them adds breadth to the format portfolio

## Format-Specific Notes

### PGM (Portable Graymap)
- Acquisition score: 8.9/10 (Accept band)
- Source: src/python/pgm/pgm_parser.py
- Tests: tests/python/pgm/
- Package: .local/package-builds/python-foss/aspose-format-factory-pgm/

### PBM (Portable Bitmap)
- Acquisition score: 8.7/10 (Accept band)
- Source: src/python/pbm/pbm_parser.py
- Tests: tests/python/pbm/
- Package: .local/package-builds/python-foss/aspose-format-factory-pbm/

### PPM (Portable Pixmap)
- Acquisition score: ~8.5/10 (Accept band — inferred from similar metrics)
- Source: src/python/ppm/ppm_parser.py
- Tests: tests/python/ppm/

## Next Steps Required

1. Submit Gate 8 security review packet for PGM/PBM/PPM (human approval required)
2. After Gate 8 approval: advance to Gate 9 (edge case hardening)
3. After Gate 9: advance to Gate 10 (local RC)
4. Gate 11 follows FODS/FODT trajectory (requires commercial approval)

NETPBM_DECISION: CONTINUE
FORMATS_IN_FAMILY: PGM, PBM, PPM
GATE_8_REQUIRED: YES (human approval)
