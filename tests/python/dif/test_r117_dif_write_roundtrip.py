"""
test_r117_dif_write_roundtrip.py — DIF write_dif + roundtrip proof tests.

Iteration 4 — FOSS closure gap for DIF.
Tests:
  1. write_dif produces a file that parse_dif_strict can read back
  2. roundtrip preserves title
  3. roundtrip preserves row/column counts
  4. roundtrip preserves numeric cell values
  5. roundtrip preserves string cell values
  6. write_dif handles empty document
  7. write_dif then dif_to_csv pipeline
  8. write_dif with unicode title
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.python.dif.dif_parser import (
    DifCell,
    DifDocument,
    write_dif,
    parse_dif_strict,
    dif_to_csv,
)


def make_doc(title: str = "TestDoc", rows: list | None = None) -> DifDocument:
    if rows is None:
        rows = [
            [DifCell(value=1.0, value_type="numeric"), DifCell(value="Alpha", value_type="string")],
            [DifCell(value=2.0, value_type="numeric"), DifCell(value="Beta", value_type="string")],
        ]
    doc = DifDocument(title=title, vectors=2, tuples=len(rows), rows=rows)
    return doc


class TestWriteDifRoundtrip:
    def test_roundtrip_file_exists(self, tmp_path):
        doc = make_doc()
        out = tmp_path / "test.dif"
        write_dif(doc, out)
        assert out.exists()

    def test_roundtrip_preserves_title(self, tmp_path):
        doc = make_doc(title="MySheet")
        out = tmp_path / "test.dif"
        write_dif(doc, out)
        reloaded = parse_dif_strict(out)
        assert reloaded.title == "MySheet"

    def test_roundtrip_preserves_row_count(self, tmp_path):
        doc = make_doc()
        out = tmp_path / "test.dif"
        write_dif(doc, out)
        reloaded = parse_dif_strict(out)
        assert len(reloaded.rows) == 2

    def test_roundtrip_preserves_numeric_values(self, tmp_path):
        rows = [
            [DifCell(value=42.0, value_type="numeric")],
            [DifCell(value=3.14, value_type="numeric")],
        ]
        doc = DifDocument(title="Nums", vectors=1, tuples=2, rows=rows)
        out = tmp_path / "nums.dif"
        write_dif(doc, out)
        reloaded = parse_dif_strict(out)
        assert reloaded.rows[0][0].value == 42.0
        assert abs(reloaded.rows[1][0].value - 3.14) < 0.001

    def test_roundtrip_preserves_string_values(self, tmp_path):
        rows = [
            [DifCell(value="Hello World", value_type="string")],
            [DifCell(value="Foo, Bar", value_type="string")],
        ]
        doc = DifDocument(title="Strings", vectors=1, tuples=2, rows=rows)
        out = tmp_path / "strings.dif"
        write_dif(doc, out)
        reloaded = parse_dif_strict(out)
        assert reloaded.rows[0][0].value == "Hello World"
        assert reloaded.rows[1][0].value == "Foo, Bar"

    def test_roundtrip_empty_document(self, tmp_path):
        doc = DifDocument(title="Empty", vectors=0, tuples=0, rows=[])
        out = tmp_path / "empty.dif"
        write_dif(doc, out)
        reloaded = parse_dif_strict(out)
        assert reloaded.title == "Empty"
        assert len(reloaded.rows) == 0

    def test_write_then_csv_pipeline(self, tmp_path):
        doc = make_doc(title="Pipeline")
        out = tmp_path / "pipeline.dif"
        write_dif(doc, out)
        csv_text = dif_to_csv(out)
        assert isinstance(csv_text, str)
        assert len(csv_text) > 0
        lines = csv_text.strip().split("\n")
        assert len(lines) == 2

    def test_roundtrip_unicode_title(self, tmp_path):
        doc = make_doc(title="Data — 2026")
        out = tmp_path / "unicode.dif"
        write_dif(doc, out)
        reloaded = parse_dif_strict(out)
        assert "2026" in reloaded.title

    def test_roundtrip_column_count(self, tmp_path):
        rows = [
            [
                DifCell(value=1.0, value_type="numeric"),
                DifCell(value="A", value_type="string"),
                DifCell(value=2.0, value_type="numeric"),
            ]
        ]
        doc = DifDocument(title="Cols", vectors=3, tuples=1, rows=rows)
        out = tmp_path / "cols.dif"
        write_dif(doc, out)
        reloaded = parse_dif_strict(out)
        assert len(reloaded.rows[0]) == 3

    def test_dogfood_pipeline_full(self, tmp_path):
        """Build doc → write → probe → parse_strict → csv — all passing."""
        from src.python.dif.dif_parser import probe_dif
        rows = [
            [DifCell(value=10.0, value_type="numeric"), DifCell(value="Alpha", value_type="string")],
            [DifCell(value=20.0, value_type="numeric"), DifCell(value="Beta", value_type="string")],
            [DifCell(value=30.0, value_type="numeric"), DifCell(value="Gamma", value_type="string")],
        ]
        doc = DifDocument(title="DogfoodSheet", vectors=2, tuples=3, rows=rows)
        out = tmp_path / "dogfood.dif"
        write_dif(doc, out)

        probe = probe_dif(out)
        assert probe["exists"] is True
        assert probe["valid_header"] is True

        reloaded = parse_dif_strict(out)
        assert len(reloaded.rows) == 3

        csv_text = dif_to_csv(out)
        csv_lines = [ln for ln in csv_text.strip().split("\n") if ln.strip()]
        assert len(csv_lines) == 3
        assert "Alpha" in csv_text
        assert "30" in csv_text
