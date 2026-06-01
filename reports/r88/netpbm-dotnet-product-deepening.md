# R88 Train J: Netpbm .NET Product Deepening

## Train: J (Group 3 — Commercial .NET)
## Sprint: FORMAT-FACTORY-R88-DECLARATION-DRIVEN-AUTONOMOUS-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001

## Work Done

### FlipVertical Transform
Added `NetpbmImage.FlipVertical()` to `src/net/netpbm/Model/NetpbmImage.cs`:
- Swaps pixel rows top-to-bottom
- Handles PBM/PGM (Pixels array) and PPM (R/G/B channels separately)
- In-place operation, no allocation

### Invert Transform
Added `NetpbmImage.Invert()` to `src/net/netpbm/Model/NetpbmImage.cs`:
- PBM: toggles 0/1
- PGM: v -> MaxValue - v
- PPM: each channel inverted against MaxValue

### Tests Added
File: `tests/net/netpbm/NetpbmR88TransformTests.cs` (8 tests)
- FlipVertical_PGM_SwapsTopAndBottom
- FlipVertical_PBM_SwapsRows
- FlipVertical_PPM_SwapsColorRows
- FlipVertical_Twice_RestoresOriginal
- Invert_PBM_Toggles01
- Invert_PGM_SubtractsFromMax
- Invert_PPM_InvertsAllChannels
- Invert_Twice_RestoresOriginal

## Test Result
Netpbm .NET: 71 passed, 0 failed (was 63 baseline, +8 new)

## Status: COMPLETE
