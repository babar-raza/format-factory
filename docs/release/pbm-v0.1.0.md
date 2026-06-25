# PBM Release Notes — v0.1.0

**Package:** `aspose-format-factory-pbm`
**Version:** 0.1.0
**Release Date:** 2026-06-25
**Track:** Python FOSS
**Format:** Portable Bitmap — Netpbm P1 (ASCII) and P4 (binary)

---

## Summary

First pre-release of the Format Factory PBM Python package.
Provides parse, inspect, transform, and convert capabilities for `.pbm` files.

This is a `v0.1.0` developer release. Not yet published to PyPI.
Commercial .NET Netpbm product is separately tracked under `aspose-format-factory-netpbm` NuGet.

---

## Features

### Parse
- `parse_pbm_strict(path)` — Returns a `PbmImage` dataclass with `magic`, `width`, `height`, `pixels`
- `parse_pbm(path)` — Dict-based parse for interoperability
- `probe_pbm(path)` — Header-only probe (no pixel decode)
- P1 (ASCII) and P4 (binary) format support
- Comment stripping per Netpbm specification

### Write
- `write_pbm(pixels, width, height, dest_path)` — Write P4 (binary, default) or P1 (ASCII) output

### Transform
- `flip_horizontal(src, dest)` — Mirror image left-to-right
- `invert(src, dest)` — Swap black and white pixels
- `rotate_90(src, dest)` — 90-degree clockwise rotation
- `crop(src, dest, x, y, w, h)` — Rectangular crop
- `scale_nearest(src, dest, factor)` — Nearest-neighbor upscale

### Analytics (30+ functions)
- Pixel counts: `count_black`, `count_white`, `pixel_count`
- Ratios: `pbm_black_pixel_ratio`, `pbm_white_pixel_ratio`
- Density: `pbm_black_density`, `pbm_white_density`
- Row/column analysis: `pbm_row_black_counts`, `pbm_column_black_counts`
- Geometry: `get_dimensions`, `aspect_ratio`, `pbm_perimeter`, `pbm_megapixels`
- Predicates: `pbm_all_black`, `pbm_all_white`, `pbm_is_uniform`, `pbm_is_square`

### Conversion
- `convert_pbm_to_pgm(src, dest)` — Convert to grayscale PGM
- `convert_pbm_to_ppm(src, dest)` — Convert to color PPM

---

## Security

- File size guard: raises `PbmSizeError` for oversized inputs
- Strict magic-byte validation (P1/P4 only)
- No external resource loading; pure stdlib implementation

---

## Exceptions

- `PbmError` — base class
- `PbmInvalidMagicError` — unrecognized magic bytes
- `PbmInvalidHeaderError` — missing or malformed width/height
- `PbmSizeError` — file too large or dimensions out of range
- `PbmDecodeError` — pixel data parse failure

---

## Compatibility

- Python 3.10+
- No third-party dependencies (stdlib only)
- Tested on: Windows 11, Ubuntu 22.04

---

## Known Limitations

- P1/P4 only; P-format autodetect not implemented
- No color profile or DPI metadata support (outside Netpbm spec scope)
- Alpha channel not applicable (1-bit format)

---

## Gate History

Gates 1-7 PASSED. See `registry/format-registry.yaml` for gate criteria.
Gate 11 (G11-G) commercial approval: requires Babar Raza sign-off.
