# Legal Notes: Nearly Raw Raster Data

## Classification
- **Legal Category:** 2
- **Category Name:** Permissive OSS
- **Patent Status:** No known patent barriers
- **License:** LGPL 2.1 (Teem library); format specification itself is unencumbered

## Implementation Freedom
- Read: Unrestricted
- Write: Unrestricted
- Distribution: Unrestricted under Apache 2.0

## Notes
NRRD is a scientific data format created by the Teem project. The format specification is publicly documented and unencumbered. While the reference Teem library is LGPL 2.1, the format itself can be freely implemented without any license obligations. Independent implementations exist in Python (pynrrd, MIT license), ITK, and 3D Slicer. The format is simple (text header + raw data) with no proprietary extensions. Safe for clean-room parser implementation.
