# R28 XCF Gate 4 Prototype — Implementation Report
Sprint: R28 Lane G
Date: 2026-05-19
Format: XCF (GIMP Native Image Format)

## Summary

Minimal Gate 4 controlled prototype for XCF format. Parses header, property list,
and layer offset table. Does NOT decode pixel/tile data.

## Files Created

| File | Purpose |
|------|---------|
| `src/python/xcf/__init__.py` | Package metadata (v0.1.0.dev0, python-foss track) |
| `src/python/xcf/xcf_parser.py` | Parser: parse_xcf, parse_xcf_strict, probe_xcf |
| `tests/python/xcf/test_xcf_parser.py` | 17 tests covering valid/invalid/probe/validation |

## Public API

- `parse_xcf(file_path) -> dict` — never raises, returns `{"ok": True/False, ...}`
- `parse_xcf_strict(file_path) -> XcfImage` — raises `XcfError` on failure
- `probe_xcf(file_path) -> dict` — header metadata without full parse

## XcfImage Dataclass Fields

`width`, `height`, `image_type`, `version`, `num_layers`, `path`

## Security Guards

- Max file size: 64 MiB
- Magic validation: `gimp xcf ` (9 bytes)
- Dimension limit: 262144 x 262144
- Image type validation: 0 (RGB), 1 (Grayscale), 2 (Indexed)
- Property payload bounds check
- No pixel/tile data decoding (attack surface minimized)

## Parse Scope

1. Header: magic, version, NUL, width, height, image_type (26 bytes)
2. Property list: TLV scan until PROP_END (type=0), count properties
3. Layer offset table: read uint32 offsets until 0 sentinel, count layers

## Test Results

17 passed, 0 failed.

## Dependencies

Python stdlib only: `struct`, `pathlib`, `os`, `dataclasses`.

## Status

- commercial_product_ready: false
- production_source_authorized: true (prototype scope)
- Gate 4: prototype_complete
