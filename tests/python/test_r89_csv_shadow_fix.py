"""R89 Train E: CSV shadow fix regression tests.

Verifies that stdlib csv.writer/csv.reader remain available when the full
test suite is collected, including tests/python/csv/ (Format Factory CSV tests).

Root cause: tests/python/csv/__init__.py made that directory a Python package
which shadowed stdlib csv when pytest added tests/python/ to sys.path.
Fix: removed tests/python/csv/__init__.py + pinned stdlib csv in conftest.py.

Sprint: FORMAT-FACTORY-R89-AUTHORITATIVE-TEST-BASELINE-DECLARATION-CLOSEOUT-POC-PRODUCT-DEEPENING-MEGA-TRAIN-001
"""
from __future__ import annotations

import csv
import sys


class TestStdlibCsvAvailable:
    """Stdlib csv must always be the resolved module, not the FF csv package."""

    def test_csv_has_writer(self):
        assert hasattr(csv, "writer"), "stdlib csv.writer missing — shadow active"

    def test_csv_has_reader(self):
        assert hasattr(csv, "reader"), "stdlib csv.reader missing — shadow active"

    def test_csv_has_dictwriter(self):
        assert hasattr(csv, "DictWriter"), "stdlib csv.DictWriter missing — shadow active"

    def test_csv_module_is_stdlib(self):
        # stdlib csv lives in Python's Lib/ directory, not in src/python/csv/
        assert "src" not in (csv.__file__ or ""), (
            f"csv module resolves to {csv.__file__} — should be stdlib"
        )
        assert "format-factory" not in (csv.__file__ or "").replace("\\", "/"), (
            f"csv module resolves to {csv.__file__} — should be stdlib"
        )


class TestCsvShadowConftest:
    """Verify conftest.py pinning mechanism works."""

    def test_sys_modules_csv_is_stdlib(self):
        mod = sys.modules.get("csv")
        assert mod is not None, "csv not in sys.modules"
        assert hasattr(mod, "writer"), "sys.modules['csv'] lacks writer — shadow active"

    def test_no_init_py_in_tests_csv(self):
        """tests/python/csv/__init__.py must not exist (root cause of shadow)."""
        from pathlib import Path
        init_path = Path(__file__).parent / "csv" / "__init__.py"
        assert not init_path.exists(), (
            f"{init_path} exists — this causes stdlib csv shadow in full-suite runs"
        )


class TestCsvExportFunctionality:
    """Verify that FODS/SYLK/DIF csv-export functions work correctly."""

    def test_fods_workbook_to_csv(self):
        from fods.neutral_model import workbook_to_csv
        wb = {"sheets": [{"name": "Sheet1", "rows": [
            {"cells": [{"value": "hello"}]}
        ]}]}
        result = workbook_to_csv(wb)
        assert "hello" in result

    def test_sylk_to_csv_available(self):
        from sylk.sylk_parser import sylk_to_csv
        assert callable(sylk_to_csv)

    def test_dif_to_csv_available(self):
        from dif.dif_parser import dif_to_csv
        assert callable(dif_to_csv)
