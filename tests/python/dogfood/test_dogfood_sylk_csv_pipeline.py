"""
test_dogfood_sylk_csv_pipeline.py -- SYLK->CSV dogfood export pipeline.

Sprint: REWORK-MEGATRAIN-FINAL-001
Added: 2026-06-10

Creates SYLK document, exports to CSV, parses the CSV back.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    SylkDocument,
    SylkCell,
    write_sylk,
    sylk_to_csv,
)

sys.path.insert(0, str(_REPO))
from src.python.ff_csv.csv_parser import parse_csv


def _make_doc(*cells_data) -> SylkDocument:
    cells = [SylkCell(row=r, col=c, value=v, value_type=t) for r, c, v, t in cells_data]
    max_row = max(c.row for c in cells) if cells else 0
    max_col = max(c.col for c in cells) if cells else 0
    return SylkDocument(cells=cells, rows=max_row, cols=max_col)


def test_sylk_to_csv_dogfood():
    """Write SYLK, export to CSV, parse CSV back."""
    doc = _make_doc(
        (1, 1, "Name", "string"),
        (1, 2, "Score", "string"),
        (2, 1, "Alice", "string"),
        (2, 2, "95", "number"),
        (3, 1, "Bob", "string"),
        (3, 2, "87", "number"),
    )
    with tempfile.TemporaryDirectory() as tmp:
        sylk_path = Path(tmp) / "data.sylk"
        write_sylk(doc, sylk_path)

        csv_text = sylk_to_csv(sylk_path)
        assert isinstance(csv_text, str)
        assert "Alice" in csv_text

        csv_path = Path(tmp) / "data.csv"
        csv_path.write_text(csv_text, encoding="utf-8")
        result = parse_csv(csv_path)
        assert isinstance(result, dict)
        assert result["row_count"] >= 2


def test_sylk_csv_roundtrip_content():
    """Verify CSV export preserves cell content."""
    doc = _make_doc(
        (1, 1, "Product", "string"),
        (1, 2, "Price", "string"),
        (2, 1, "Widget", "string"),
        (2, 2, "19.99", "number"),
    )
    with tempfile.TemporaryDirectory() as tmp:
        sylk_path = Path(tmp) / "prices.sylk"
        write_sylk(doc, sylk_path)
        csv_text = sylk_to_csv(sylk_path)
        assert "Widget" in csv_text
        assert "19.99" in csv_text
