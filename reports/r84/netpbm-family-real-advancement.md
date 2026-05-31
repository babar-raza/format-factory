# R84 Train M: Netpbm Family Real Advancement

**Sprint:** FORMAT-FACTORY-R84
**Train:** M
**Date:** 2026-05-31
**Status:** COMPLETE

## PBM: write_pbm

Added `write_pbm(pixels, width, height, file_path, *, comment="")` to pbm_parser.py.

- Writes P1 (ASCII portable bitmap) format
- Validates dimensions against MAX_DIMENSION (65536)
- Validates pixel list length equals width*height
- Optional comment line in header
- Round-trip verified: write then parse produces identical pixels

Source: `src/python/pbm/pbm_parser.py`
Exported: `src/python/pbm/__init__.py`

## PGM: write_pgm

Added `write_pgm(pixels, width, height, maxval, file_path, *, comment="")` to pgm_parser.py.

- Writes P2 (ASCII portable graymap) format
- maxval must be 1-65535
- Validates dimensions and pixel list length
- Optional comment line in header

Source: `src/python/pgm/pgm_parser.py`
Exported: `src/python/pgm/__init__.py`

## PPM: Basic Parser

Added `src/python/ppm/` package with Gate 4 prototype support.

- Parses P3 (ASCII portable pixmap) format
- parse_ppm(file_path) -> dict (never raises)
- parse_ppm_strict(file_path) -> PpmImage (raises PpmError)
- probe_ppm(file_path) -> header metadata dict
- P6 (binary) format: not yet supported
- PpmImage: width, height, maxval, pixels (flat list of [R,G,B] tuples)

Source: `src/python/ppm/ppm_parser.py`, `src/python/ppm/__init__.py`

## Tests

- `tests/python/pbm/test_r84_pbm_roundtrip.py` — write+parse roundtrip
- `tests/python/pgm/test_r84_pgm_write.py` — write_pgm basic tests
- `tests/python/ppm/test_r84_ppm_parser.py` — P3 parse tests

## Result

PASS — PBM write, PGM write, and PPM parser implemented and tested.
