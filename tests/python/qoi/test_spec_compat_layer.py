"""Behavioral tests for QOI spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.qoi.Compat import QoiHeader, QoiChunk
from src.python.qoi.spec.chunk.header import Header as SpecHeader
from src.python.qoi.spec.chunk.chunk import Chunk as SpecChunk


_SAMPLE_HEADER = {"width": 640, "height": 480, "channels": 3, "colorspace": 0}
_SAMPLE_CHUNK_DATA = {"byte_length": 3}  # Chunk data dict, not raw bytes


class TestQoiHeaderMetadata:
    def test_spec_qname(self):
        assert QoiHeader.spec_qname == "qoi:header"

    def test_spec_fact_ref(self):
        assert QoiHeader.spec_fact_ref == "SAL-QOI-00001"

    def test_magic_constant(self):
        assert QoiHeader.MAGIC == b"qoif"

    def test_namespace_uri_present(self):
        assert QoiHeader.namespace_uri


class TestQoiHeaderBehavior:
    def test_instantiation(self):
        h = QoiHeader(_SAMPLE_HEADER)
        assert h is not None

    def test_width_property(self):
        h = QoiHeader(_SAMPLE_HEADER)
        assert h.width == 640

    def test_height_property(self):
        h = QoiHeader(_SAMPLE_HEADER)
        assert h.height == 480

    def test_pixel_count(self):
        h = QoiHeader(_SAMPLE_HEADER)
        assert h.pixel_count == 640 * 480

    def test_channels(self):
        h = QoiHeader(_SAMPLE_HEADER)
        assert h.channels == 3

    def test_to_dict(self):
        h = QoiHeader(_SAMPLE_HEADER)
        d = h.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        h = QoiHeader(_SAMPLE_HEADER)
        assert repr(h)

    def test_inherits_spec_class(self):
        h = QoiHeader(_SAMPLE_HEADER)
        assert isinstance(h, SpecHeader)


class TestQoiChunkBehavior:
    def test_instantiation(self):
        c = QoiChunk("QOI_OP_RGB", _SAMPLE_CHUNK_DATA)
        assert c is not None

    def test_spec_qname(self):
        assert QoiChunk.spec_qname == "qoi:chunk"

    def test_chunk_type(self):
        c = QoiChunk("QOI_OP_RGB", _SAMPLE_CHUNK_DATA)
        assert c.chunk_type == "QOI_OP_RGB"

    def test_byte_length(self):
        c = QoiChunk("QOI_OP_RGB", _SAMPLE_CHUNK_DATA)
        assert c.byte_length == 3

    def test_inherits_spec_class(self):
        c = QoiChunk("QOI_OP_RGB", _SAMPLE_CHUNK_DATA)
        assert isinstance(c, SpecChunk)

    def test_repr_nonempty(self):
        c = QoiChunk("QOI_OP_RGB", _SAMPLE_CHUNK_DATA)
        assert repr(c)
