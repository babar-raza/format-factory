"""
test_r165_dif_csv_edge_cases.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT31-001
Added: 2026-06-10

Deepening tests for DIF dif_to_csv and get_capabilities with edge cases.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    dif_to_csv,
    get_capabilities,
    write_dif,
    DifError,
    DifDocument,
    DifCell,
)


def _make_dif(tmp_path: Path, title: str, rows: list[list], name="test.dif") -> Path:
    """Create a DIF file from rows of values."""
    doc = DifDocument(title=title, vectors=len(rows[0]) if rows else 0, tuples=len(rows))
    for row in rows:
        dif_row = []
        for val in row:
            vtype = "numeric" if isinstance(val, (int, float)) else "string"
            dif_row.append(DifCell(value=val, value_type=vtype))
        doc.rows.append(dif_row)
    p = tmp_path / name
    write_dif(doc, p)
    return p


# ── get_capabilities deepening ──────────────────────────────────────────

class TestGetCapabilitiesDeepening:

    def test_format_is_dif(self):
        result = get_capabilities()
        assert result["format"] == "dif"

    def test_gate_number(self):
        result = get_capabilities()
        assert isinstance(result["gate"], int)

    def test_supported_nonempty(self):
        result = get_capabilities()
        assert len(result["supported"]) > 0

    def test_idempotent(self):
        a = get_capabilities()
        b = get_capabilities()
        assert a == b


# ── dif_to_csv deepening ────────────────────────────────────────────────

class TestDifToCsvDeepening:

    def test_single_cell(self, tmp_path):
        src = _make_dif(tmp_path, "T", [["hello"]])
        csv_str = dif_to_csv(src)
        assert "hello" in csv_str

    def test_numeric_values(self, tmp_path):
        src = _make_dif(tmp_path, "Nums", [[1.0, 2.0, 3.0]])
        csv_str = dif_to_csv(src)
        assert "1" in csv_str

    def test_multiple_rows(self, tmp_path):
        src = _make_dif(tmp_path, "Multi", [["A", "B"], ["C", "D"]])
        csv_str = dif_to_csv(src)
        assert "A" in csv_str
        assert "D" in csv_str

    def test_returns_string(self, tmp_path):
        src = _make_dif(tmp_path, "T", [["x"]])
        assert isinstance(dif_to_csv(src), str)

    def test_nonempty_output(self, tmp_path):
        src = _make_dif(tmp_path, "T", [["val"]])
        assert len(dif_to_csv(src)) > 0

    def test_nonexistent_raises(self, tmp_path):
        with pytest.raises(DifError):
            dif_to_csv(tmp_path / "ghost.dif")

    def test_mixed_types(self, tmp_path):
        src = _make_dif(tmp_path, "Mix", [["text", 42.0]])
        csv_str = dif_to_csv(src)
        assert "text" in csv_str
