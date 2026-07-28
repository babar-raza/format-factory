"""Shared loader for format-factory's src/python/ff_csv package in tests.

`csv` collides with the Python stdlib module of the same name, so a plain
`import csv` (or `from csv.xxx import yyy`) inside a pytest session that has
already touched the real stdlib `csv` module anywhere resolves to the cached
stdlib module, not this repo's package -- `sys.modules` is checked before
`sys.path`. This loader instead loads `src/python/ff_csv/__init__.py` under a
private alias name with proper `submodule_search_locations`, so its internal
relative imports (`from .exceptions import ...`) resolve correctly while never
triggering the literal name "csv" through the normal import machinery.

Usage: `from tests.python.csv._ff_csv_loader import ff_csv` (or import
ff_csv directly now that the package is named ff_csv and no longer collides
with stdlib csv), then access `ff_csv.parse_csv`, `ff_csv.CsvError`, etc.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_CSV_PKG_DIR = _REPO / "src" / "python" / "ff_csv"
_ALIAS = "_ff_csv_pkg"

if _ALIAS in sys.modules:
    ff_csv = sys.modules[_ALIAS]
else:
    _spec = importlib.util.spec_from_file_location(
        _ALIAS,
        str(_CSV_PKG_DIR / "__init__.py"),
        submodule_search_locations=[str(_CSV_PKG_DIR)],
    )
    ff_csv = importlib.util.module_from_spec(_spec)
    sys.modules[_ALIAS] = ff_csv
    _spec.loader.exec_module(ff_csv)
