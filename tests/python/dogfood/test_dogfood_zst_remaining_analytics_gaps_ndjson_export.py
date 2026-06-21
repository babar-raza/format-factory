"""test_dogfood_zst_remaining_analytics_gaps_ndjson_export.py

Dogfood export path: ZST remaining 13 analytics gap functions -> NDJSON.

Covers:
  zst_compressed_ratio, zst_compression_efficiency, zst_compression_saving,
  zst_decompressed_per_frame, zst_file_size_bytes, zst_frame_size_range,
  zst_is_compressible, zst_is_empty_content, zst_is_highly_compressed,
  zst_is_multi_frame, zst_is_rle_efficient, zst_is_uniform_frames, zst_savings_ratio

Concrete values:
  minimal-synthetic: file_size=10, compressed_ratio=10.0, is_compressible=False,
                     is_highly_compressed=True, is_empty_content=False, is_uniform_frames=True,
                     is_multi_frame=False, savings_ratio=-0.9
  text-compressed:   file_size=272, compressed_ratio=0.6974, compression_efficiency=0.3026,
                     compression_saving=118, decompressed_per_frame=390.0, is_compressible=True,
                     is_highly_compressed=False, savings_ratio=0.4338
  rle-first-block:   is_rle_efficient=True, compression_saving=1048531, decompressed_per_frame=1048576.0
  empty-block:       is_empty_content=True, file_size=11, decompressed_per_frame=0.0, savings_ratio=-1.0

Sprint: product-deepening-dogfood-zst-remaining-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst.zst_codec import (
    zst_compressed_ratio,
    zst_compression_efficiency,
    zst_compression_saving,
    zst_decompressed_per_frame,
    zst_file_size_bytes,
    zst_frame_size_range,
    zst_is_compressible,
    zst_is_empty_content,
    zst_is_highly_compressed,
    zst_is_multi_frame,
    zst_is_rle_efficient,
    zst_is_uniform_frames,
    zst_savings_ratio,
)
from src.python.ndjson.ndjson_codec import write_ndjson

ZST_DIR = (_REPO / "samples" / "by-format" / "zst" / "valid").resolve()
ZST_MINIMAL = ZST_DIR / "minimal-synthetic.zst"
ZST_TEXT = ZST_DIR / "text-compressed.zst"
ZST_RLE = ZST_DIR / "rle-first-block.zst"
ZST_RANDOM = ZST_DIR / "random-data.zst"
ZST_EMPTY = ZST_DIR / "empty-block.zst"


class TestZstRemainingAnalyticsGapsNdjsonExport:

    # file_size_bytes
    def test_zst_minimal_file_size_bytes(self):
        assert zst_file_size_bytes(ZST_MINIMAL) == 10

    def test_zst_text_file_size_bytes(self):
        assert zst_file_size_bytes(ZST_TEXT) == 272

    def test_zst_empty_file_size_bytes(self):
        assert zst_file_size_bytes(ZST_EMPTY) == 11

    # compressed_ratio
    def test_zst_text_compressed_ratio(self):
        assert abs(zst_compressed_ratio(ZST_TEXT) - 0.6974) < 0.01

    def test_zst_minimal_compressed_ratio_high(self):
        assert zst_compressed_ratio(ZST_MINIMAL) > 1.0

    # compression_efficiency
    def test_zst_text_compression_efficiency(self):
        assert abs(zst_compression_efficiency(ZST_TEXT) - 0.3026) < 0.01

    def test_zst_minimal_compression_efficiency_zero(self):
        assert abs(zst_compression_efficiency(ZST_MINIMAL)) < 0.01

    # compression_saving
    def test_zst_text_compression_saving(self):
        assert zst_compression_saving(ZST_TEXT) == 118

    def test_zst_rle_compression_saving_large(self):
        assert zst_compression_saving(ZST_RLE) > 1000000

    def test_zst_empty_compression_saving_zero(self):
        assert zst_compression_saving(ZST_EMPTY) == 0

    # decompressed_per_frame
    def test_zst_text_decompressed_per_frame(self):
        assert abs(zst_decompressed_per_frame(ZST_TEXT) - 390.0) < 1.0

    def test_zst_empty_decompressed_per_frame_zero(self):
        assert abs(zst_decompressed_per_frame(ZST_EMPTY)) < 0.01

    def test_zst_rle_decompressed_per_frame_large(self):
        assert zst_decompressed_per_frame(ZST_RLE) > 1000000

    # frame_size_range
    def test_zst_minimal_frame_size_range_zero(self):
        assert zst_frame_size_range(ZST_MINIMAL) == 0

    def test_zst_text_frame_size_range_zero(self):
        assert zst_frame_size_range(ZST_TEXT) == 0

    # is_compressible
    def test_zst_minimal_is_compressible_false(self):
        assert zst_is_compressible(ZST_MINIMAL) is False

    def test_zst_text_is_compressible_true(self):
        assert zst_is_compressible(ZST_TEXT) is True

    def test_zst_rle_is_compressible_true(self):
        assert zst_is_compressible(ZST_RLE) is True

    # is_empty_content
    def test_zst_empty_is_empty_content_true(self):
        assert zst_is_empty_content(ZST_EMPTY) is True

    def test_zst_minimal_is_empty_content_false(self):
        assert zst_is_empty_content(ZST_MINIMAL) is False

    # is_highly_compressed
    def test_zst_minimal_is_highly_compressed_true(self):
        assert zst_is_highly_compressed(ZST_MINIMAL) is True

    def test_zst_text_is_highly_compressed_false(self):
        assert zst_is_highly_compressed(ZST_TEXT) is False

    # is_multi_frame
    def test_zst_minimal_is_multi_frame_false(self):
        assert zst_is_multi_frame(ZST_MINIMAL) is False

    def test_zst_text_is_multi_frame_false(self):
        assert zst_is_multi_frame(ZST_TEXT) is False

    # is_rle_efficient
    def test_zst_rle_is_rle_efficient_true(self):
        assert zst_is_rle_efficient(ZST_RLE) is True

    def test_zst_text_is_rle_efficient_false(self):
        assert zst_is_rle_efficient(ZST_TEXT) is False

    # is_uniform_frames
    def test_zst_minimal_is_uniform_frames_true(self):
        assert zst_is_uniform_frames(ZST_MINIMAL) is True

    def test_zst_text_is_uniform_frames_true(self):
        assert zst_is_uniform_frames(ZST_TEXT) is True

    # savings_ratio
    def test_zst_text_savings_ratio(self):
        assert abs(zst_savings_ratio(ZST_TEXT) - 0.4338) < 0.01

    def test_zst_empty_savings_ratio_negative(self):
        assert zst_savings_ratio(ZST_EMPTY) < 0

    def test_zst_rle_savings_ratio_large(self):
        assert zst_savings_ratio(ZST_RLE) > 100

    # NDJSON export pipeline
    def test_ndjson_export_zst_analytics(self, tmp_path):
        records = [
            {
                "file": ZST_TEXT.name,
                "file_size_bytes": zst_file_size_bytes(ZST_TEXT),
                "is_compressible": zst_is_compressible(ZST_TEXT),
                "compression_saving": zst_compression_saving(ZST_TEXT),
                "savings_ratio": round(zst_savings_ratio(ZST_TEXT), 4),
            },
            {
                "file": ZST_EMPTY.name,
                "is_empty_content": zst_is_empty_content(ZST_EMPTY),
                "is_highly_compressed": zst_is_highly_compressed(ZST_EMPTY),
                "compression_saving": zst_compression_saving(ZST_EMPTY),
            },
        ]
        out = tmp_path / "zst_remaining_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0])["is_compressible"] is True
        assert json.loads(lines[1])["is_empty_content"] is True
