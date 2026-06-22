"""Behavioral tests for DIF spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.dif.Compat import DifHeader, DifVector, DifDatum
from src.python.dif.spec.table.header import Header as SpecHeader
from src.python.dif.spec.table.vector import Vector as SpecVector
from src.python.dif.spec.table.datum import Datum as SpecDatum


_SAMPLE_HEADER = {"rows": 5, "cols": 3, "format_version": "0,1"}
_SAMPLE_VECTOR = ["a", "b", "c"]  # Vector takes a list directly


class TestDifHeaderMetadata:
    def test_spec_qname(self):
        assert DifHeader.spec_qname == "dif:header"

    def test_spec_fact_ref(self):
        assert DifHeader.spec_fact_ref == "FACT-DIF-001"

    def test_namespace_uri_present(self):
        assert DifHeader.namespace_uri


class TestDifHeaderBehavior:
    def test_instantiation(self):
        h = DifHeader(_SAMPLE_HEADER)
        assert h is not None

    def test_rows_property(self):
        h = DifHeader(_SAMPLE_HEADER)
        assert h.rows == 5

    def test_cols_property(self):
        h = DifHeader(_SAMPLE_HEADER)
        assert h.cols == 3

    def test_to_dict(self):
        h = DifHeader(_SAMPLE_HEADER)
        d = h.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        h = DifHeader(_SAMPLE_HEADER)
        assert repr(h)

    def test_inherits_spec_class(self):
        h = DifHeader(_SAMPLE_HEADER)
        assert isinstance(h, SpecHeader)


class TestDifVectorBehavior:
    def test_instantiation(self):
        v = DifVector(_SAMPLE_VECTOR)
        assert v is not None

    def test_spec_qname(self):
        assert DifVector.spec_qname == "dif:vector"

    def test_length_property(self):
        v = DifVector(_SAMPLE_VECTOR)
        assert v.length == 3

    def test_inherits_spec_class(self):
        v = DifVector(_SAMPLE_VECTOR)
        assert isinstance(v, SpecVector)


class TestDifDatumBehavior:
    def test_instantiation(self):
        d = DifDatum(42.0, "V")
        assert d is not None

    def test_spec_qname(self):
        assert DifDatum.spec_qname == "dif:datum"

    def test_spec_fact_ref(self):
        assert DifDatum.spec_fact_ref == "FACT-DIF-003"

    def test_value_property(self):
        d = DifDatum(42.0, "V")
        assert d.value == 42.0

    def test_is_numeric_with_V_indicator(self):
        d = DifDatum(42.0, "V")
        assert d.is_numeric()

    def test_inherits_spec_class(self):
        d = DifDatum(42.0, "V")
        assert isinstance(d, SpecDatum)

    def test_repr_nonempty(self):
        d = DifDatum(42.0, "V")
        assert repr(d)
