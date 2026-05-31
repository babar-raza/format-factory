# R84 Train N: SYLK/DIF Real Advancement

**Sprint:** FORMAT-FACTORY-R84
**Train:** N
**Date:** 2026-05-31
**Status:** COMPLETE

## SYLK: sylk_to_csv

Added `sylk_to_csv(file_path) -> str` to sylk_parser.py.

- Builds a 2D grid from SylkCell.row/col (1-based) coordinates
- Serializes each row as RFC 4180 CSV with CRLF line endings
- Empty cells produce empty CSV fields
- Returns empty string for documents with no cells
- Raises SylkError subclasses on parse failure

Source: `src/python/sylk/sylk_parser.py`
Exported: `src/python/sylk/__init__.py`

```python
import sylk
csv_text = sylk.sylk_to_csv("data.slk")
```

## DIF: dif_to_csv

Added `dif_to_csv(file_path) -> str` to dif_parser.py.

- Each DIF tuple (row) becomes one CSV row
- Cell values serialized: None -> empty, numeric int -> no trailing .0, other -> str
- RFC 4180 CRLF line endings
- Returns empty string for documents with no rows
- Raises DifError subclasses on parse failure

Source: `src/python/dif/dif_parser.py`
Exported: `src/python/dif/__init__.py`

Also rewrote `src/python/dif/__init__.py` with full package metadata (was a stub).

```python
import dif
csv_text = dif.dif_to_csv("data.dif")
```

## Tests

- `tests/python/sylk/test_r84_sylk_to_csv.py` — SYLK CSV export (8 tests)
- `tests/python/dif/test_r84_dif_to_csv.py` — DIF CSV export (8 tests)

## Result

PASS — sylk_to_csv and dif_to_csv implemented, tested, and exported.
