"""
Tests for DIF total_cell_count function.
Sprint: FORMAT-FACTORY-ROUTE-AWARE-PRODUCT-REENTRY-HARDENING-001
Taskcard: RRH-TC-003
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest

_here = Path(__file__).resolve().parent
_REPO = _here.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    DifCell,
    DifDocument,
    total_cell_count,
    write_dif,
)


def _make_dif(rows: list[list[DifCell]], title: str = "test") -> Path:
    """Write a DIF document to a temp file and return the path."""
    doc = DifDocument(
        title=title,
        vectors=max((len(r) for r in rows), default=0),
        tuples=len(rows),
        rows=rows,
    )
    p = Path(tempfile.mktemp(suffix=".dif"))
    write_dif(doc, p)
    return p


class TestTotalCellCount:
    def test_empty_document(self, tmp_path):
        p = _make_dif([])
        try:
            assert total_cell_count(p) == 0
        finally:
            os.unlink(p)

    def test_single_row(self, tmp_path):
        row = [DifCell(value=1.0, value_type="numeric"),
               DifCell(value="hello", value_type="string")]
        p = _make_dif([row])
        try:
            assert total_cell_count(p) == 2
        finally:
            os.unlink(p)

    def test_multiple_rows(self, tmp_path):
        rows = [
            [DifCell(value=1.0, value_type="numeric"),
             DifCell(value=2.0, value_type="numeric")],
            [DifCell(value="a", value_type="string"),
             DifCell(value="b", value_type="string"),
             DifCell(value="c", value_type="string")],
        ]
        p = _make_dif(rows)
        try:
            assert total_cell_count(p) == 5
        finally:
            os.unlink(p)

    def test_single_cell(self, tmp_path):
        row = [DifCell(value="only", value_type="string")]
        p = _make_dif([row])
        try:
            assert total_cell_count(p) == 1
        finally:
            os.unlink(p)

    def test_consistency_with_get_all_values(self, tmp_path):
        from dif.dif_parser import get_all_values
        rows = [
            [DifCell(value=1.0, value_type="numeric"),
             DifCell(value=None, value_type="special")],
            [DifCell(value="x", value_type="string")],
        ]
        p = _make_dif(rows)
        try:
            assert total_cell_count(p) == len(get_all_values(p))
        finally:
            os.unlink(p)
