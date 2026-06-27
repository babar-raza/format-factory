"""
tests/python/dogfood/test_dogfood_xcf_qoi_zst_remaining_analytics_ndjson_export.py

Dogfood export: XCF remaining (is_tall) + QOI remaining (is_small, megapixels) +
ZST remaining (is_single_frame, max_frame_size, decompressed_to_compressed_ratio)
-> NDJSON -> verify.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import xcf_is_tall
from qoi.qoi_parser import qoi_is_small, qoi_megapixels
from ndjson.ndjson_codec import write_ndjson, load_ndjson
from zst.compression_metrics import (
    zst_is_single_frame,
    zst_max_frame_size,
    zst_decompressed_to_compressed_ratio,
)

_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
_QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid"


def test_xcf_is_tall(tmp_path):
    path = str(_XCF / "2x2-gray.xcf")
    result = xcf_is_tall(path)
    assert result is False  # 2x2 is square, not tall
    record = {"file": "2x2-gray.xcf", "xcf_is_tall": result}
    out = tmp_path / "xcf_tall.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["xcf_is_tall"] is False


def test_qoi_is_small(tmp_path):
    path = str(_QOI / "1x1-red.qoi")
    result = qoi_is_small(path)
    assert result is True
    record = {"file": "1x1-red.qoi", "qoi_is_small": result}
    out = tmp_path / "qoi_small.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["qoi_is_small"] is True


def test_qoi_megapixels(tmp_path):
    path = str(_QOI / "1x1-red.qoi")
    mp = qoi_megapixels(path)
    assert mp == 1e-6
    record = {"file": "1x1-red.qoi", "qoi_megapixels": mp}
    out = tmp_path / "qoi_mp.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["qoi_megapixels"] == 1e-6


def test_zst_is_single_frame(tmp_path):
    path = str(_ZST / "minimal-synthetic.zst")
    result = zst_is_single_frame(path)
    assert result is True
    record = {"file": "minimal-synthetic.zst", "zst_is_single_frame": result}
    out = tmp_path / "zst_single.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["zst_is_single_frame"] is True


def test_zst_max_frame_size(tmp_path):
    path = str(_ZST / "minimal-synthetic.zst")
    size = zst_max_frame_size(path)
    assert size == 10
    record = {"file": "minimal-synthetic.zst", "zst_max_frame_size": size}
    out = tmp_path / "zst_maxframe.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert rows[0]["zst_max_frame_size"] == 10


def test_zst_decompressed_to_compressed_ratio(tmp_path):
    path = str(_ZST / "minimal-synthetic.zst")
    ratio = zst_decompressed_to_compressed_ratio(path)
    assert isinstance(ratio, float)
    assert ratio > 0.0
    record = {"file": "minimal-synthetic.zst", "zst_decompressed_to_compressed_ratio": ratio}
    out = tmp_path / "zst_ratio.ndjson"
    write_ndjson([record], str(out))
    rows = load_ndjson(str(out))
    assert isinstance(rows[0]["zst_decompressed_to_compressed_ratio"], float)
