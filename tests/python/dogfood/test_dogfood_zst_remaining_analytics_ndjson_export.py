"""
tests/python/dogfood/test_dogfood_zst_remaining_analytics_ndjson_export.py

Sprint: PRODUCT-DEEPENING-SPRINT-57
Dogfood export: ZST remaining uncovered analytics -> NDJSON -> verify.
Uses: zst_frame_count_is_one, zst_frame_size_variance, zst_has_multiple_frames,
      zst_is_small_file, zst_largest_frame_ratio, zst_min_frame_size,
      zst_smallest_frame_ratio, zst_total_frame_size.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("zst_codec", str(_REPO / "src" / "python" / "zst" / "zst_codec.py"))
_zst = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_zst)

zst_frame_count_is_one = _zst.zst_frame_count_is_one
zst_frame_size_variance = _zst.zst_frame_size_variance
zst_has_multiple_frames = _zst.zst_has_multiple_frames
zst_is_small_file = _zst.zst_is_small_file
zst_largest_frame_ratio = _zst.zst_largest_frame_ratio
zst_min_frame_size = _zst.zst_min_frame_size
zst_smallest_frame_ratio = _zst.zst_smallest_frame_ratio
zst_total_frame_size = _zst.zst_total_frame_size

from ndjson.ndjson_codec import write_ndjson, load_ndjson


_ZST_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"


def _valid_zst_files():
    return sorted(_ZST_DIR.glob("*.zst"))


class TestZstRemainingAnalyticsNdjsonExport:
    """ZST remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_zst_remaining_basics(self):
        s_min = str(_ZST_DIR / "minimal-synthetic.zst")
        s_big = str(_ZST_DIR / "block-128k.zst")
        s_empty = str(_ZST_DIR / "empty-block.zst")
        assert zst_frame_count_is_one(s_min) is True
        assert zst_frame_size_variance(s_min) == 0.0
        assert zst_has_multiple_frames(s_min) is False
        assert zst_is_small_file(s_min) is True
        assert zst_largest_frame_ratio(s_min) == 1.0
        assert zst_min_frame_size(s_min) == 10
        assert zst_total_frame_size(s_min) == 10
        assert zst_is_small_file(s_big) is False
        assert zst_min_frame_size(s_big) == 131081
        assert zst_total_frame_size(s_big) == 131081
        assert zst_frame_count_is_one(s_empty) is True
        assert zst_is_small_file(s_empty) is True

    def test_single_vs_multiple_frames(self):
        for f in _valid_zst_files():
            path = str(f)
            is_one = zst_frame_count_is_one(path)
            has_multi = zst_has_multiple_frames(path)
            assert isinstance(is_one, bool), f"frame_count_is_one must be bool for {f.name}"
            assert isinstance(has_multi, bool), f"has_multiple_frames must be bool for {f.name}"
            # These are complementary for single-frame files
            if is_one:
                assert not has_multi, f"single-frame file should not have multiple frames: {f.name}"

    def test_zst_remaining_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_zst_files():
            path = str(f)
            records.append({
                "file": f.name,
                "frame_count_is_one": zst_frame_count_is_one(path),
                "frame_size_variance": zst_frame_size_variance(path),
                "has_multiple_frames": zst_has_multiple_frames(path),
                "is_small_file": zst_is_small_file(path),
                "largest_frame_ratio": zst_largest_frame_ratio(path),
                "min_frame_size": zst_min_frame_size(path),
                "smallest_frame_ratio": zst_smallest_frame_ratio(path),
                "total_frame_size": zst_total_frame_size(path),
                "source_format": "zst",
            })
        dest = tmp_path / "zst-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists() and dest.stat().st_size > 0
        assert len(records) >= 4

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_zst_files():
            path = str(f)
            records.append({
                "file": f.name,
                "frame_count_is_one": zst_frame_count_is_one(path),
                "total_frame_size": zst_total_frame_size(path),
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["frame_count_is_one"] == back["frame_count_is_one"]
            assert orig["total_frame_size"] == back["total_frame_size"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(_ZST_DIR / "minimal-synthetic.zst")
        records = [{
            "file": "minimal-synthetic.zst",
            "is_small_file": zst_is_small_file(sample),
            "total_frame_size": zst_total_frame_size(sample),
            "format": "zst",
        }]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
