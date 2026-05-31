# Playbook: Simple Binary/Text Image Format

**Applies to:** PBM, PGM, PPM, QOI, and similar simple image formats
**Added:** R85 Train H

---

## Acquisition Inputs
- Format spec (Netpbm man pages, QOI spec)
- Public domain test images or generated synthetic samples

## Expected Spec Artifacts
- acquisition-packs/{format}/ — gate evidence, sample images
- schemas/neutral-model/{format}/ — 3-6 entities (image header, pixels, metadata)

## Object Model Skeleton (Python)
```
image = {
  "width": int,
  "height": int,
  "max_value": int,          # for PGM/PPM: max pixel value (1 for PBM)
  "format": "P1"|"P2"|"P3"|"P4"|"P5"|"P6",
  "pixels": [[pixel, ...], ...],   # 2D list; pixel is int or (r,g,b)
  "comments": [str, ...]
}
```

## Parser Strategy
1. Header: ASCII lines until first data
2. Pixels: ASCII (P1-P3) or binary (P4-P6)
3. Guard: width*height size check before pixel allocation
4. No third-party deps (pure Python)

## Writer Strategy
1. Write ASCII variants (P1-P3) for simplicity in first slice
2. Binary variants (P4-P6) as optimization
3. Roundtrip test: parse → write → parse → compare

## Edit Model Strategy
1. Direct pixel mutation: image["pixels"][row][col] = new_value
2. Image statistics: pixel_stats() for mean/min/max/histogram
3. Channel manipulation: convert between family members

## Export/Dogfood Strategy (family-based)
- PBM (1-bit) → PGM (grayscale): expand bits to 0/255 range using FF pgm write_pgm
- PGM (gray) → PPM (color): replicate channel using FF ppm write_ppm (when available)
- PBM/PGM/PPM → other: define when additional export targets exist
- Always use Format Factory's own library for family-to-family conversion

## Tests
- Gate 4: prototype parser (10-15 tests)
- Gate 5: neutral model (10-20 tests)
- Gate 6: oracle pixel comparison (10-15 tests)
- Gate 7: fuzz/malformed header guard (10-15 tests)
- Gate 8: security review (oversized image, integer overflow guard)
- Gate 9-10: full API + write + roundtrip (20+ tests)

## Package Artifacts
- pyproject.toml from packaging/python/pyproject.template.toml
- __version__ = "0.1.0.dev0", __track__ = "python-foss", __commercial_ready__ = False
- No external runtime dependencies (stdlib only)

## Examples/Docs
- examples/python/{format}/parse_and_edit_{format}.py
- examples/python/{format}/export_{format}_to_{other}.py

## .NET Commercial Strategy
- Load: BinaryReader/StreamReader for header; array for pixels
- Edit: 2D pixel array mutation
- Save: StreamWriter with proper Netpbm header
- Export: Convert PBM→PGM by mapping 1-bit to 8-bit using FF-produced PGM writer (C# port)
- Tests: 20+ tests per member (parse + edit + save + export)
