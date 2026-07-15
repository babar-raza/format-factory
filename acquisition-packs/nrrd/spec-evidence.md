# Spec Evidence: Nearly Raw Raster Data

## Primary Specification
- **Title:** NRRD format specification
- **Version:** NRRD0005
- **URL:** https://teem.sourceforge.net/nrrd/format.html
- **Body:** Teem Project
- **Accessed:** 2026-07-14
- **License:** Apache 2.0/BSD/MIT

## Spec Availability Assessment
- Freely accessible: Yes
- Machine-readable schema: No
- Actively maintained: Yes

## Key Structural Facts
- The file begins with a magic line `NRRD0005` (or earlier version numbers), followed by key-value header lines separated by `: `
- Required header fields include `type` (data type), `dimension` (number of axes), and `sizes` (extent along each axis)
- Data encoding is specified by the `encoding` field: `raw`, `ascii`, `hex`, `gzip`, `bzip2`, or `zlib`
- Detached headers use `.nhdr` extension with a `data file` field pointing to the separate raw data file
