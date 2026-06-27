"""
tests/python/qoi/test_r305_qoi_iter_chunks.py

Sprint: ff-sprint-s305-qoi-chunk-iterator-20260626
Authority: QOI specification — chunk types (QOI_OP_*)

Tests for qoi_iter_chunks() in qoi_chunk_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_VALID_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_MINIMAL = _VALID_DIR / "1x1-red.qoi"
_BLACK = _VALID_DIR / "2x2-black.qoi"


class TestQoiIterChunksImport:
    def test_importable_from_qoi_chunk_iterator(self):
        from qoi.qoi_chunk_iterator import qoi_iter_chunks
        assert callable(qoi_iter_chunks)

    def test_importable_from_package(self):
        import qoi
        assert hasattr(qoi, "qoi_iter_chunks")


class TestQoiIterChunksOutput:
    def test_returns_iterator(self):
        from qoi.qoi_chunk_iterator import qoi_iter_chunks
        result = qoi_iter_chunks(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_chunks(self):
        from qoi.qoi_chunk_iterator import qoi_iter_chunks
        chunks = list(qoi_iter_chunks(str(_MINIMAL)))
        assert len(chunks) >= 1

    def test_chunk_type_is_spec_chunk(self):
        from qoi.qoi_chunk_iterator import qoi_iter_chunks
        from qoi.spec.chunk.chunk import Chunk
        chunks = list(qoi_iter_chunks(str(_MINIMAL)))
        assert all(isinstance(c, Chunk) for c in chunks)

    def test_chunk_has_spec_qname(self):
        from qoi.qoi_chunk_iterator import qoi_iter_chunks
        chunks = list(qoi_iter_chunks(str(_MINIMAL)))
        assert all(hasattr(c, "spec_qname") for c in chunks)

    def test_chunk_qname_value(self):
        from qoi.qoi_chunk_iterator import qoi_iter_chunks
        chunks = list(qoi_iter_chunks(str(_MINIMAL)))
        assert all(c.spec_qname == "qoi:chunk" for c in chunks)

    def test_chunk_has_chunk_type(self):
        from qoi.qoi_chunk_iterator import qoi_iter_chunks
        chunks = list(qoi_iter_chunks(str(_MINIMAL)))
        for c in chunks:
            assert c.chunk_type in ("QOI_OP_RGB", "QOI_OP_RGBA", "QOI_OP_INDEX", "QOI_OP_DIFF", "QOI_OP_LUMA", "QOI_OP_RUN")

    def test_pixel_count_matches_dimensions(self):
        from qoi.qoi_chunk_iterator import qoi_iter_chunks
        # 1x1 image should yield exactly 1 chunk
        chunks = list(qoi_iter_chunks(str(_MINIMAL)))
        assert len(chunks) == 1

    def test_2x2_yields_4_chunks(self):
        from qoi.qoi_chunk_iterator import qoi_iter_chunks
        chunks = list(qoi_iter_chunks(str(_BLACK)))
        assert len(chunks) == 4

    def test_consistent(self):
        from qoi.qoi_chunk_iterator import qoi_iter_chunks
        r1 = [c.chunk_type for c in qoi_iter_chunks(str(_MINIMAL))]
        r2 = [c.chunk_type for c in qoi_iter_chunks(str(_MINIMAL))]
        assert r1 == r2
