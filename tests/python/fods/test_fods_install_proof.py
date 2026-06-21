"""TC-EXEC-005 (FODS part): FODS source-tree install proof.

Verifies module importability and core API functionality from the source tree.
Note: This is D6.5 proof (source-tree import), not D7 (wheel-install).
D7 proof is covered by TC-ZST-D7-001 methodology applied to FODS.
"""
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_FODS_SAMPLE = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"


class TestFodsInstallProof:
    def test_fods_module_importable(self):
        """src.python.fods is importable and has core attributes."""
        import src.python.fods as fods_mod
        assert fods_mod is not None
        assert hasattr(fods_mod, "parse_fods_strict")
        assert hasattr(fods_mod, "write_fods")
        assert hasattr(fods_mod, "workbook_to_csv")

    def test_fods_version_set(self):
        """__version__ is set and not a zero placeholder."""
        from src.python.fods import __version__
        assert __version__ is not None
        assert __version__ != "0.0.0"
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_parse_fods_strict_on_real_sample(self):
        """parse_fods_strict on a real .fods file returns a workbook dict."""
        if not _FODS_SAMPLE.exists():
            pytest.skip(f"Sample not found: {_FODS_SAMPLE}")
        from src.python.fods import parse_fods_strict
        wb = parse_fods_strict(str(_FODS_SAMPLE))
        assert isinstance(wb, dict)
        assert "sheet_count" in wb
        assert wb["sheet_count"] >= 1

    def test_write_fods_produces_file(self):
        """write_fods produces a non-empty file."""
        from src.python.fods import write_fods
        wb = {"sheets": [{"name": "Test", "rows": [{"cells": [{"value": "x", "value_type": "string"}]}]}]}
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "out.fods"
            write_fods(wb, out)
            assert out.exists()
            assert out.stat().st_size > 100

    def test_workbook_to_csv_returns_string(self):
        """workbook_to_csv on a parsed workbook returns a CSV string."""
        if not _FODS_SAMPLE.exists():
            pytest.skip(f"Sample not found: {_FODS_SAMPLE}")
        from src.python.fods import parse_fods_strict, workbook_to_csv
        wb = parse_fods_strict(str(_FODS_SAMPLE))
        csv_str = workbook_to_csv(wb)
        assert isinstance(csv_str, str)
        assert len(csv_str) > 0
