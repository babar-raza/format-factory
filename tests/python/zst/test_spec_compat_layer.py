"""Behavioral tests for ZST spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.zst.Compat import ZstFrame, ZstBlock
from src.python.zst.spec.frame.frame import Frame as SpecFrame
from src.python.zst.spec.frame.block import Block as SpecBlock


_SAMPLE_FRAME = {
    "frame_type": "zstandard",
    "content_size": 1024,
    "checksum_flag": False,
    "block_count": 3,
}
_SAMPLE_BLOCK = {
    "block_type": "compressed",
    "block_size": 512,
    "is_last": False,
}


class TestZstFrameMetadata:
    def test_spec_qname(self):
        assert ZstFrame.spec_qname == "zst:frame"

    def test_spec_fact_ref(self):
        assert ZstFrame.spec_fact_ref == "SAL-ZST-00001"

    def test_magic_constant(self):
        assert ZstFrame.MAGIC == 0xFD2FB528

    def test_namespace_uri_present(self):
        assert ZstFrame.namespace_uri


class TestZstFrameBehavior:
    def test_instantiation(self):
        f = ZstFrame(_SAMPLE_FRAME)
        assert f is not None

    def test_frame_type(self):
        f = ZstFrame(_SAMPLE_FRAME)
        assert f.frame_type == "zstandard"

    def test_content_size(self):
        f = ZstFrame(_SAMPLE_FRAME)
        assert f.content_size == 1024

    def test_block_count(self):
        f = ZstFrame(_SAMPLE_FRAME)
        assert f.block_count == 3

    def test_to_dict(self):
        f = ZstFrame(_SAMPLE_FRAME)
        d = f.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        f = ZstFrame(_SAMPLE_FRAME)
        assert repr(f)

    def test_inherits_spec_class(self):
        f = ZstFrame(_SAMPLE_FRAME)
        assert isinstance(f, SpecFrame)


class TestZstBlockBehavior:
    def test_instantiation(self):
        b = ZstBlock(_SAMPLE_BLOCK)
        assert b is not None

    def test_spec_qname(self):
        assert ZstBlock.spec_qname == "zst:block"

    def test_block_type(self):
        b = ZstBlock(_SAMPLE_BLOCK)
        assert b.block_type == "compressed"

    def test_block_size(self):
        b = ZstBlock(_SAMPLE_BLOCK)
        assert b.block_size == 512

    def test_is_last(self):
        b = ZstBlock(_SAMPLE_BLOCK)
        assert b.is_last is False

    def test_inherits_spec_class(self):
        b = ZstBlock(_SAMPLE_BLOCK)
        assert isinstance(b, SpecBlock)

    def test_repr_nonempty(self):
        b = ZstBlock(_SAMPLE_BLOCK)
        assert repr(b)
