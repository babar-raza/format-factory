# PPM Release Notes — v0.1.0

**Package:** `aspose-format-factory-ppm`
**Version:** 0.1.0
**Release Date:** 2026-06-25
**Track:** Python FOSS
**Format:** Portable Pixmap — Netpbm P3 (ASCII) and P6 (binary)

---

## Summary

First pre-release of the Format Factory PPM Python package.
Provides parse, inspect, transform, and color analytics capabilities for `.ppm` files.

This is a `v0.1.0` developer release. Not yet published to PyPI.
Commercial .NET Netpbm product is separately tracked under `aspose-format-factory-netpbm` NuGet.

---

## Features

### Parse
- `parse_ppm_strict(path)` — Returns a `PpmImage` dataclass with `magic`, `width`, `height`, `maxval`, `pixels`
- `parse_ppm(path)` — Dict-based parse for interoperability
- `probe_ppm(path)` — Header-only probe (no pixel decode)
- P3 (ASCII) and P6 (binary) format support
- 24-bit RGB pixel data (R, G, B tuples)
- Comment stripping per Netpbm specification

### Write
- `write_ppm(pixels, width, height, maxval, dest_path)` — Write P6 (binary, default) or P3 (ASCII) output

### Transform
- `flip_horizontal(src, dest)` — Mirror image left-to-right
- `flip_vertical(src, dest)` — Mirror image top-to-bottom
- `rotate_90(src, dest)` — 90-degree clockwise rotation
- `invert(src, dest)` — Invert all RGB channels
- `crop(src, dest, x, y, w, h)` — Rectangular crop
- `brightness(src, dest, factor)` — Scale brightness (float factor)
- `to_grayscale(src, dest)` — Convert to PGM grayscale file

### Analytics (40+ functions)
- Per-channel: `ppm_red_channel_average`, `ppm_green_channel_average`, `ppm_blue_channel_average`
- Color composition: `ppm_dominant_channel`, `ppm_unique_color_count`, `average_color`
- Luminance: `ppm_luminance_average`, `ppm_brightness_variance`
- Predicates: `ppm_is_grayscale`, `ppm_is_binary`, `ppm_is_dark`, `ppm_has_pure_black`, `ppm_has_pure_white`
- Geometry: `get_dimensions`, `ppm_aspect_ratio`, `ppm_megapixels`, `ppm_perimeter`

### Conversion
- `convert_ppm_to_pgm(src, dest)` — Convert to grayscale PGM

---

## Security

- File size guard: raises `PpmSizeError` for oversized inputs
- Strict magic-byte validation (P3/P6 only)
- No external resource loading; pure stdlib implementation

---

## Exceptions

- `PpmError` — base class
- `PpmInvalidMagicError` — unrecognized magic bytes
- `PpmInvalidHeaderError` — missing or malformed width/height/maxval
- `PpmSizeError` — file too large or dimensions out of range
- `PpmDecodeError` — pixel data parse failure

---

## Compatibility

- Python 3.10+
- No third-party dependencies (stdlib only)
- Tested on: Windows 11, Ubuntu 22.04

---

## Known Limitations

- 8-bit `maxval` (255) only; 16-bit PPM not yet supported
- No ICC color profile support (outside Netpbm spec scope)

---

## Gate History

Gates 1-7 PASSED. See `registry/format-registry.yaml` for gate criteria.
Gate 11 (G11-G) commercial approval: requires Babar Raza sign-off.
