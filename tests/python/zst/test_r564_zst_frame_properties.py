"""R564: ZST additional frame properties — is_single_frame, decompressed_size_kb, is_large.

Tests for ZstDocument frame properties added in R564.
Spec refs: FACT-ZST-001 (zst:frame), FACT-ZST-002 (zst:block).
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst.models import ZstDocument

SAMPLES = Path("samples/by-format/zst/valid")


def _make_doc(frame_count=1, compressed_size=100, decompressed_size=200):
    """Build a ZstDocument with injected data (no file I/O)."""
    data = {
        "compressed_size": compressed_size,
        "decompressed_size": decompressed_size,
        "frame_count": frame_count,
    }
    return ZstDocument(path="test.zst", data=data)


class TestIsSingleFrame:
    def test_one_frame_is_single(self):
        doc = _make_doc(frame_count=1)
        assert doc.is_single_frame is True

    def test_zero_frames_not_single(self):
        doc = _make_doc(frame_count=0)
        assert doc.is_single_frame is False

    def test_two_frames_not_single(self):
        doc = _make_doc(frame_count=2)
        assert doc.is_single_frame is False

    def test_is_single_frame_type(self):
        doc = _make_doc(frame_count=1)
        assert isinstance(doc.is_single_frame, bool)

    def test_single_frame_inverse_of_has_multiple(self):
        doc = _make_doc(frame_count=1)
        assert doc.is_single_frame is True
        assert doc.has_multiple_frames is False

    def test_multi_frame_inverse(self):
        doc = _make_doc(frame_count=3)
        assert doc.is_single_frame is False
        assert doc.has_multiple_frames is True


class TestDecompressedSizeKb:
    def test_zero_decompressed_size(self):
        doc = _make_doc(decompressed_size=0)
        assert doc.decompressed_size_kb == 0.0

    def test_exactly_1024_bytes(self):
        doc = _make_doc(decompressed_size=1024)
        assert doc.decompressed_size_kb == 1.0

    def test_512_bytes_is_half_kb(self):
        doc = _make_doc(decompressed_size=512)
        assert doc.decompressed_size_kb == pytest.approx(0.5)

    def test_2048_bytes_is_2_kb(self):
        doc = _make_doc(decompressed_size=2048)
        assert doc.decompressed_size_kb == pytest.approx(2.0)

    def test_decompressed_size_kb_type(self):
        doc = _make_doc(decompressed_size=1024)
        assert isinstance(doc.decompressed_size_kb, float)

    def test_consistent_with_decompressed_size(self):
        doc = _make_doc(decompressed_size=4096)
        assert doc.decompressed_size_kb == doc.decompressed_size / 1024.0


class TestIsLarge:
    def test_small_file_not_large(self):
        doc = _make_doc(compressed_size=100)
        assert doc.is_large is False

    def test_exactly_1mb_is_large(self):
        doc = _make_doc(compressed_size=1_048_576)
        assert doc.is_large is True

    def test_just_under_1mb_not_large(self):
        doc = _make_doc(compressed_size=1_048_575)
        assert doc.is_large is False

    def test_zero_not_large(self):
        doc = _make_doc(compressed_size=0)
        assert doc.is_large is False

    def test_is_large_type(self):
        doc = _make_doc(compressed_size=2_000_000)
        assert isinstance(doc.is_large, bool)

    def test_2mb_is_large(self):
        doc = _make_doc(compressed_size=2_097_152)
        assert doc.is_large is True


class TestFramePropertyConsistency:
    def test_empty_doc_single_frame_false(self):
        doc = _make_doc(frame_count=0)
        assert doc.is_empty is True
        assert doc.is_single_frame is False

    def test_single_frame_not_empty(self):
        doc = _make_doc(frame_count=1)
        assert doc.is_empty is False
        assert doc.is_single_frame is True

    def test_from_file(self):
        doc = ZstDocument.from_file(SAMPLES / "minimal-synthetic.zst")
        assert isinstance(doc.is_single_frame, bool)
        assert isinstance(doc.decompressed_size_kb, float)
        assert isinstance(doc.is_large, bool)
        assert doc.decompressed_size_kb == doc.decompressed_size / 1024.0
