"""
test_r73_sylk_advancement.py — R73 Train G: SYLK parser advancement tests.

Deepens SYLK coverage: probe API, dict API fields, cell value_type discrimination,
empty file rejection, and corpus round-trip structure.

Sprint: FORMAT-FACTORY-R73-DELIVERY-PACKAGE-TRUTH-PRODUCT-ADVANCEMENT-GATE-READINESS-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.sylk.sylk_parser import (
    parse_sylk,
    parse_sylk_strict,
    probe_sylk,
    get_capabilities,
    SylkError,
    SylkInvalidFormatError,
)

VALID = PROJECT_ROOT / "samples" / "by-format" / "sylk" / "valid"
INVALID = PROJECT_ROOT / "samples" / "by-format" / "sylk" / "invalid"


class TestSylkProbeApi:
    """R73-SYLK-001: probe_sylk returns required fields."""

    def test_probe_valid_file_returns_exists_true(self):
        f = VALID / "single-cell.slk"
        if not f.exists():
            pytest.skip("SYLK corpus not present")
        result = probe_sylk(str(f))
        assert result["exists"] is True

    def test_probe_missing_file_returns_exists_false(self, tmp_path):
        result = probe_sylk(str(tmp_path / "ghost.slk"))
        assert result["exists"] is False

    def test_probe_valid_file_has_valid_header(self):
        f = VALID / "single-cell.slk"
        if not f.exists():
            pytest.skip("SYLK corpus not present")
        result = probe_sylk(str(f))
        assert result.get("valid_header") is True


class TestSylkDictApi:
    """R73-SYLK-002: parse_sylk dict API shape."""

    def test_dict_api_ok_true_for_valid(self):
        f = VALID / "numeric-row.slk"
        if not f.exists():
            pytest.skip("SYLK corpus not present")
        result = parse_sylk(str(f))
        assert result["ok"] is True

    def test_dict_api_has_cell_count(self):
        f = VALID / "numeric-row.slk"
        if not f.exists():
            pytest.skip("SYLK corpus not present")
        result = parse_sylk(str(f))
        assert "cell_count" in result
        assert result["cell_count"] == 3

    def test_dict_api_ok_false_on_missing(self, tmp_path):
        result = parse_sylk(str(tmp_path / "gone.slk"))
        assert result["ok"] is False

    def test_dict_api_has_rows_cols(self):
        f = VALID / "minimal-2x2.slk"
        if not f.exists():
            pytest.skip("SYLK corpus not present")
        result = parse_sylk(str(f))
        assert result["rows"] == 2
        assert result["cols"] == 2


class TestSylkCellValueTypes:
    """R73-SYLK-003: cell value_type discrimination."""

    def test_numeric_cell_value_type(self):
        f = VALID / "numeric-row.slk"
        if not f.exists():
            pytest.skip("SYLK corpus not present")
        doc = parse_sylk_strict(str(f))
        numeric_cells = [c for c in doc.cells if c.value_type == "numeric"]
        assert len(numeric_cells) > 0, "Expected at least one numeric cell"

    def test_single_cell_has_value(self):
        f = VALID / "single-cell.slk"
        if not f.exists():
            pytest.skip("SYLK corpus not present")
        doc = parse_sylk_strict(str(f))
        assert len(doc.cells) == 1
        assert doc.cells[0].value is not None


class TestSylkCapabilities:
    """R73-SYLK-004: capabilities API."""

    def test_capabilities_format_is_sylk(self):
        caps = get_capabilities()
        assert caps["format"] == "sylk"

    def test_capabilities_commercial_ready_false(self):
        caps = get_capabilities()
        assert caps["commercial_product_ready"] is False

    def test_capabilities_has_supported_list(self):
        caps = get_capabilities()
        assert isinstance(caps.get("supported"), list)
        assert len(caps["supported"]) > 0


class TestSylkSyntheticEdgeCases:
    """R73-SYLK-005: synthetic edge cases."""

    def _write_sylk(self, tmp_dir: Path, name: str, content: str) -> Path:
        p = tmp_dir / name
        p.write_text(content, encoding="ascii")
        return p

    def test_empty_file_rejected(self, tmp_path):
        f = self._write_sylk(tmp_path, "empty.slk", "")
        with pytest.raises(SylkError):
            parse_sylk_strict(str(f))

    def test_missing_id_record_rejected(self, tmp_path):
        f = self._write_sylk(tmp_path, "bad.slk", "C;X1;Y1;K42\nE\n")
        with pytest.raises(SylkInvalidFormatError):
            parse_sylk_strict(str(f))

    def test_minimal_valid_sylk(self, tmp_path):
        content = "ID;PWXL\nC;X1;Y1;K99\nE\n"
        f = self._write_sylk(tmp_path, "min.slk", content)
        doc = parse_sylk_strict(str(f))
        assert doc.rows == 1
        assert doc.cols == 1
        assert doc.cells[0].value == 99
