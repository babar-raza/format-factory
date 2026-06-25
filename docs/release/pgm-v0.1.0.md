# PGM Release Notes — v0.1.0

**Package:** `aspose-format-factory-pgm`
**Version:** 0.1.0
**Release Date:** 2026-06-25
**Track:** Python FOSS
**Format:** Portable Graymap — Netpbm P2 (ASCII) and P5 (binary)

---

## Summary

First pre-release of the Format Factory PGM Python package.
Provides parse, inspect, transform, histogram, and convert capabilities for `.pgm` files.

This is a `v0.1.0` developer release. Not yet published to PyPI.
Commercial .NET Netpbm product is separately tracked under `aspose-format-factory-netpbm` NuGet.

---

## Features

### Parse
- `parse_pgm_strict(path)` — Returns a `PgmImage` dataclass with `magic`, `width`, `height`, `maxval`, `pixels`
- `parse_pgm(path)` — Dict-based parse for interoperability
- `probe_pgm(path)` — Header-only probe (no pixel decode)
- P2 (ASCII) and P5 (binary) format support
- `maxval` support up to 255 (8-bit grayscale)
- Comment stripping per Netpbm specification

### Write
- `write_pgm(pixels, width, height, maxval, dest_path)` — Write P5 (binary, default) or P2 (ASCII) output

### Transform
- `flip_horizontal(src, dest)` — Mirror image left-to-right
- `rotate_90(src, dest)` — 90-degree clockwise rotation
- `normalize(src, dest, new_maxval=255)` — Normalize pixel range to 0–`new_maxval`
- `threshold(src, dest, value, *, invert=False)` — Binarize at threshold value

### Analytics (40+ functions)
- Brightness: `average_gray`, `pgm_average_brightness`, `pgm_median_pixel_value`
- Range: `min_max_gray`, `pgm_contrast_range`, `pgm_dynamic_range`
- Distribution: `histogram`, `pgm_brightness_quartiles`, `pgm_standard_deviation`, `grayscale_variance`
- Threshold: `count_above_threshold`, `pgm_dark_pixel_count`, `pgm_saturated_pixel_count`
- Unique values: `pgm_unique_value_count`
- Geometry: `get_dimensions`, `pgm_aspect_ratio`, `pgm_megapixels`, `pgm_perimeter`
- Predicates: `pgm_is_uniform`, `pgm_is_all_dark`, `pgm_is_all_bright`, `pgm_is_square`

### Conversion
- `convert_pgm_to_ppm(src, dest)` — Convert to color PPM

---

## Security

- File size guard: raises `PgmSizeError` for oversized inputs
- Strict magic-byte validation (P2/P5 only)
- No external resource loading; pure stdlib implementation

---

## Exceptions

- `PgmError` — base class
- `PgmInvalidMagicError` — unrecognized magic bytes
- `PgmInvalidHeaderError` — missing or malformed width/height/maxval
- `PgmSizeError` — file too large or dimensions out of range
- `PgmDecodeError` — pixel data parse failure

---

## Compatibility

- Python 3.10+
- No third-party dependencies (stdlib only)
- Tested on: Windows 11, Ubuntu 22.04

---

## Known Limitations

- 8-bit `maxval` (255) only; 16-bit PGM not yet supported
- No color profile or DPI metadata support (outside Netpbm spec scope)

---

## Gate History

Gates 1-7 PASSED. See `registry/format-registry.yaml` for gate criteria.
Gate 11 (G11-G) commercial approval: requires Babar Raza sign-off.
