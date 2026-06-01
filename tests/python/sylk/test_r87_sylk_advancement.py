"""
test_r87_sylk_advancement.py — SYLK FOSS advancement tests.

Sprint: FORMAT-FACTORY-R87-CLEAN-SUPERVISOR-CLOSEOUT-REVIEW-PACKAGE-POC-PRODUCT-FACTORY-DEEPENING-MEGA-TRAIN-001
Train M: SYLK reduced/FOSS advancement
"""

import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from sylk.sylk_parser import parse_sylk


class TestSylkParserEdgeCases:
    """Train M: SYLK parser edge-case hardening."""

    def test_parse_minimal_sylk(self):
        """Parse a minimal valid SYLK file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "minimal.sylk"
            path.write_text("ID;P\nC;X1;Y1;K\"Hello\"\nE\n", encoding="utf-8")
            result = parse_sylk(str(path))
            assert result["ok"] is True

    def test_parse_empty_sylk_has_id_record(self):
        """Minimal SYLK with only ID and E records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "empty.sylk"
            path.write_text("ID;P\nE\n", encoding="utf-8")
            result = parse_sylk(str(path))
            assert result["ok"] is True
            assert result["id_line"] == "ID;P"

    def test_parse_numeric_value(self):
        """SYLK with a numeric cell value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "numeric.sylk"
            path.write_text("ID;P\nC;X1;Y1;K42\nE\n", encoding="utf-8")
            result = parse_sylk(str(path))
            assert result["ok"] is True
            assert result["cell_count"] == 1

    def test_parse_multiple_cells(self):
        """SYLK with multiple cells."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "multi.sylk"
            path.write_text("ID;P\nC;X1;Y1;K\"A\"\nC;X2;Y1;K\"B\"\nE\n", encoding="utf-8")
            result = parse_sylk(str(path))
            assert result["ok"] is True
            assert result["cell_count"] == 2

    def test_sylk_to_csv_exists(self):
        """Verify sylk_to_csv function exists and is importable."""
        from sylk.sylk_parser import sylk_to_csv
        assert callable(sylk_to_csv)

    def test_sylk_to_csv_produces_output(self):
        """Convert a SYLK file to CSV and verify output is returned."""
        from sylk.sylk_parser import sylk_to_csv
        with tempfile.TemporaryDirectory() as tmpdir:
            sylk_path = Path(tmpdir) / "test.sylk"
            sylk_path.write_text("ID;P\nC;X1;Y1;K\"Hello\"\nE\n", encoding="utf-8")
            result = sylk_to_csv(str(sylk_path))
            # Should return string or dict with CSV content
            assert result is not None
