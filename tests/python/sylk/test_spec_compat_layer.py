"""Behavioral tests for SYLK spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.sylk.Compat import SylkHeader, SylkRow, SylkCell
from src.python.sylk.spec.row.header import Header as SpecHeader
from src.python.sylk.spec.row.row import Row as SpecRow
from src.python.sylk.spec.row.cell import Cell as SpecCell


_SAMPLE_HEADER = {"program": "MULTIPLAN", "row_count": 10, "col_count": 5}
_SAMPLE_ROW = {"index": 1, "cells": []}


class TestSylkHeaderMetadata:
    def test_spec_qname(self):
        assert SylkHeader.spec_qname == "sylk:header"

    def test_spec_fact_ref(self):
        assert SylkHeader.spec_fact_ref == "FACT-SYLK-001"

    def test_namespace_uri_present(self):
        assert SylkHeader.namespace_uri


class TestSylkHeaderBehavior:
    def test_instantiation(self):
        h = SylkHeader(_SAMPLE_HEADER)
        assert h is not None

    def test_program_property(self):
        h = SylkHeader(_SAMPLE_HEADER)
        assert h.program == "MULTIPLAN"

    def test_row_count(self):
        h = SylkHeader(_SAMPLE_HEADER)
        assert h.row_count == 10

    def test_to_dict(self):
        h = SylkHeader(_SAMPLE_HEADER)
        d = h.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        h = SylkHeader(_SAMPLE_HEADER)
        assert repr(h)

    def test_inherits_spec_class(self):
        h = SylkHeader(_SAMPLE_HEADER)
        assert isinstance(h, SpecHeader)


class TestSylkRowBehavior:
    def test_instantiation(self):
        r = SylkRow(1, [])
        assert r is not None

    def test_spec_qname(self):
        assert SylkRow.spec_qname == "sylk:row"

    def test_index_property(self):
        r = SylkRow(3, [])
        assert r.index == 3

    def test_cell_count(self):
        r = SylkRow(1, [])
        assert r.cell_count == 0

    def test_inherits_spec_class(self):
        r = SylkRow(1, [])
        assert isinstance(r, SpecRow)

    def test_repr_nonempty(self):
        r = SylkRow(1, [])
        assert repr(r)


class TestSylkCellBehavior:
    def test_instantiation(self):
        c = SylkCell(1, 2, "Hello")
        assert c is not None

    def test_spec_qname(self):
        assert SylkCell.spec_qname == "sylk:cell"

    def test_row_property(self):
        c = SylkCell(3, 4, 42)
        assert c.row == 3

    def test_col_property(self):
        c = SylkCell(3, 4, 42)
        assert c.col == 4

    def test_value_property(self):
        c = SylkCell(1, 1, "Hello")
        assert c.value == "Hello"

    def test_inherits_spec_class(self):
        c = SylkCell(1, 1, "x")
        assert isinstance(c, SpecCell)

    def test_repr_nonempty(self):
        c = SylkCell(1, 1, "x")
        assert repr(c)
