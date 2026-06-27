"""
tests/python/dif/test_r303_dif_iter_vectors.py

Sprint: ff-sprint-s303-dif-vector-iterator-20260626
Authority: DIF specification — data vector

Tests for dif_iter_vectors() in dif_vector_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_MINIMAL = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"
_NUMERIC = _REPO / "samples" / "by-format" / "dif" / "valid" / "numeric-row.dif"


class TestDifIterVectorsImport:
    def test_importable_from_dif_vector_iterator(self):
        from dif.dif_vector_iterator import dif_iter_vectors
        assert callable(dif_iter_vectors)

    def test_importable_from_package(self):
        import dif
        assert hasattr(dif, "dif_iter_vectors")


class TestDifIterVectorsOutput:
    def test_returns_iterator(self):
        from dif.dif_vector_iterator import dif_iter_vectors
        result = dif_iter_vectors(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_vectors(self):
        from dif.dif_vector_iterator import dif_iter_vectors
        vectors = list(dif_iter_vectors(str(_MINIMAL)))
        assert len(vectors) >= 1

    def test_vector_type_is_spec_vector(self):
        from dif.dif_vector_iterator import dif_iter_vectors
        from dif.spec.table.vector import Vector
        vectors = list(dif_iter_vectors(str(_MINIMAL)))
        assert all(isinstance(v, Vector) for v in vectors)

    def test_vector_has_spec_qname(self):
        from dif.dif_vector_iterator import dif_iter_vectors
        vectors = list(dif_iter_vectors(str(_MINIMAL)))
        assert all(hasattr(v, "spec_qname") for v in vectors)

    def test_vector_qname_value(self):
        from dif.dif_vector_iterator import dif_iter_vectors
        vectors = list(dif_iter_vectors(str(_MINIMAL)))
        assert all(v.spec_qname == "dif:vector" for v in vectors)

    def test_vector_has_items(self):
        from dif.dif_vector_iterator import dif_iter_vectors
        vectors = list(dif_iter_vectors(str(_MINIMAL)))
        for v in vectors:
            assert isinstance(v.items, list)

    def test_vector_has_length(self):
        from dif.dif_vector_iterator import dif_iter_vectors
        vectors = list(dif_iter_vectors(str(_MINIMAL)))
        for v in vectors:
            assert isinstance(v.length, int) and v.length >= 0

    def test_consistent(self):
        from dif.dif_vector_iterator import dif_iter_vectors
        r1 = [v.length for v in dif_iter_vectors(str(_MINIMAL))]
        r2 = [v.length for v in dif_iter_vectors(str(_MINIMAL))]
        assert r1 == r2
