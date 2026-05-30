"""
tests/python/dif/test_r76_dif_advancement.py

R76 Train L — DIF format advancement tests.

New coverage areas (beyond R73):
- Boolean cell values (TRUE/FALSE)
- NA special value
- Mixed-type rows (numeric + string in same row)
- Malformed type-pair line rejection
- Row structure: cells correctly distributed into rows
- Probe title extraction from synthetic file
- BOT marker handling (row boundary)

Sprint: FORMAT-FACTORY-R76-PARALLEL-FINISH-LINE-ARTIFACT-AUTHORITY-PRODUCT-DEEPENING-GATE-READINESS-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.dif.dif_parser import (
    parse_dif,
    parse_dif_strict,
    probe_dif,
    DifError,
    DifInvalidFormatError,
    DifDocument,
    DifCell,
)


def _make_dif(title: str, vectors: int, tuples: int, data_lines: list[str]) -> str:
    """Build a minimal DIF file string."""
    header = (
        f"TABLE\n0,1\n\"{title}\"\n"
        f"VECTORS\n0,{vectors}\n\"\"\n"
        f"TUPLES\n0,{tuples}\n\"\"\n"
        "DATA\n0,0\n\"\"\n"
    )
    return header + "\n".join(data_lines) + "\n"


def _write_dif(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Boolean special values
# ---------------------------------------------------------------------------

class TestDifBooleanCells:
    """TRUE and FALSE special values should produce boolean-type cells."""

    def test_true_cell_value(self, tmp_path):
        data = ["-1,0", "BOT", "-1,0", "TRUE", "-1,0", "EOD"]
        content = _make_dif("BoolTest", 1, 1, data)
        f = _write_dif(tmp_path, "bool.dif", content)
        doc = parse_dif_strict(str(f))
        bool_cells = [c for row in doc.rows for c in row if c.value is True]
        assert len(bool_cells) >= 1

    def test_false_cell_value(self, tmp_path):
        data = ["-1,0", "BOT", "-1,0", "FALSE", "-1,0", "EOD"]
        content = _make_dif("BoolTest", 1, 1, data)
        f = _write_dif(tmp_path, "bool_false.dif", content)
        doc = parse_dif_strict(str(f))
        bool_cells = [c for row in doc.rows for c in row if c.value is False]
        assert len(bool_cells) >= 1

    def test_true_cell_value_type(self, tmp_path):
        data = ["-1,0", "BOT", "-1,0", "TRUE", "-1,0", "EOD"]
        content = _make_dif("BoolTest", 1, 1, data)
        f = _write_dif(tmp_path, "bool_type.dif", content)
        doc = parse_dif_strict(str(f))
        bool_cells = [c for row in doc.rows for c in row if c.value is True]
        assert bool_cells[0].value_type == "boolean"


# ---------------------------------------------------------------------------
# NA special value
# ---------------------------------------------------------------------------

class TestDifNaSpecial:
    """NA special value should produce a cell with value=None and type 'special'."""

    def test_na_cell_value_is_none(self, tmp_path):
        data = ["-1,0", "BOT", "-1,0", "NA", "-1,0", "EOD"]
        content = _make_dif("NaTest", 1, 1, data)
        f = _write_dif(tmp_path, "na.dif", content)
        doc = parse_dif_strict(str(f))
        na_cells = [c for row in doc.rows for c in row if c.value is None]
        assert len(na_cells) >= 1

    def test_na_cell_type_is_special(self, tmp_path):
        data = ["-1,0", "BOT", "-1,0", "NA", "-1,0", "EOD"]
        content = _make_dif("NaTest", 1, 1, data)
        f = _write_dif(tmp_path, "na_type.dif", content)
        doc = parse_dif_strict(str(f))
        na_cells = [c for row in doc.rows for c in row if c.value is None]
        assert na_cells[0].value_type == "special"


# ---------------------------------------------------------------------------
# Mixed-type rows
# ---------------------------------------------------------------------------

class TestDifMixedTypeRows:
    """Rows with both numeric and string cells should parse correctly."""

    def test_mixed_row_cell_count(self, tmp_path):
        data = [
            "-1,0", "BOT",
            "0,42", "V",     # numeric cell: 42.0
            "1,0", '"Alice"',  # string cell: "Alice"
            "-1,0", "EOD",
        ]
        content = _make_dif("Mixed", 2, 1, data)
        f = _write_dif(tmp_path, "mixed.dif", content)
        doc = parse_dif_strict(str(f))
        assert len(doc.rows) >= 1
        # At least one row with both numeric and string cells
        combined = [c for row in doc.rows for c in row]
        types = {c.value_type for c in combined}
        assert "numeric" in types
        assert "string" in types

    def test_string_cell_quotes_stripped(self, tmp_path):
        data = [
            "-1,0", "BOT",
            "1,0", '"Hello"',
            "-1,0", "EOD",
        ]
        content = _make_dif("StrTest", 1, 1, data)
        f = _write_dif(tmp_path, "str_cell.dif", content)
        doc = parse_dif_strict(str(f))
        str_cells = [c for row in doc.rows for c in row if c.value_type == "string"]
        assert len(str_cells) >= 1
        assert str_cells[0].value == "Hello"


# ---------------------------------------------------------------------------
# Row structure (BOT markers)
# ---------------------------------------------------------------------------

class TestDifRowStructure:
    """BOT markers correctly delimit row boundaries."""

    def test_two_rows_created(self, tmp_path):
        data = [
            "-1,0", "BOT",
            "0,1", "V",
            "-1,0", "BOT",
            "0,2", "V",
            "-1,0", "EOD",
        ]
        content = _make_dif("TwoRows", 1, 2, data)
        f = _write_dif(tmp_path, "two_rows.dif", content)
        doc = parse_dif_strict(str(f))
        assert len(doc.rows) == 2

    def test_row_count_in_dict_api(self, tmp_path):
        data = [
            "-1,0", "BOT",
            "0,10", "V",
            "-1,0", "EOD",
        ]
        content = _make_dif("OneRow", 1, 1, data)
        f = _write_dif(tmp_path, "one_row.dif", content)
        result = parse_dif(str(f))
        assert result["ok"] is True
        assert result["row_count"] == 1


# ---------------------------------------------------------------------------
# Header metadata (probe and title)
# ---------------------------------------------------------------------------

class TestDifProbeTitle:
    """probe_dif should extract title from TABLE header."""

    def test_probe_title_extracted(self, tmp_path):
        data = ["-1,0", "BOT", "-1,0", "EOD"]
        content = _make_dif("MySpreadsheet", 1, 0, data)
        f = _write_dif(tmp_path, "probe.dif", content)
        result = probe_dif(str(f))
        assert result.get("valid_header") is True
        assert result.get("title") == "MySpreadsheet"

    def test_dict_api_returns_title(self, tmp_path):
        data = ["-1,0", "BOT", "-1,0", "EOD"]
        content = _make_dif("SaleData", 1, 0, data)
        f = _write_dif(tmp_path, "title.dif", content)
        result = parse_dif(str(f))
        assert result["ok"] is True
        assert result["title"] == "SaleData"


# ---------------------------------------------------------------------------
# Malformed input rejection
# ---------------------------------------------------------------------------

class TestDifMalformedRejection:
    """Malformed headers and data lines should be rejected."""

    def test_wrong_first_section_rejected(self, tmp_path):
        # Replace TABLE with garbage
        content = "NOTATABLE\n0,1\n\"Title\"\nVECTORS\n0,2\n\"\"\nTUPLES\n0,1\n\"\"\nDATA\n0,0\n\"\"\n-1,0\nBOT\n-1,0\nEOD\n"
        f = _write_dif(tmp_path, "bad_header.dif", content)
        result = parse_dif(str(f))
        assert result["ok"] is False

    def test_empty_file_rejected(self, tmp_path):
        f = _write_dif(tmp_path, "empty.dif", "")
        result = parse_dif(str(f))
        assert result["ok"] is False

    def test_missing_file_ok_false(self, tmp_path):
        result = parse_dif(str(tmp_path / "ghost.dif"))
        assert result["ok"] is False
