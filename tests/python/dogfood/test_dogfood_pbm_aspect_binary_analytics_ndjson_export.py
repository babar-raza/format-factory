"""
tests/python/dogfood/test_dogfood_pbm_aspect_binary_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-72
Dogfood export: PBM parse -> aspect/binary analytics -> write as NDJSON -> verify.
Uses: pbm_aspect_ratio, pbm_is_binary, pbm_black_pixel_ratio,
pbm_row_count, pbm_has_any_black, pbm_is_uniform.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm import (
    pbm_aspect_ratio,
    pbm_is_binary,
    pbm_black_pixel_ratio,
    pbm_row_count,
    pbm_has_any_black,
    pbm_is_uniform,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"


def _valid_pbm_files():
    return sorted(_PBM_DIR.glob("*.pbm"))


class TestPbmAspectBinaryAnalyticsNdjsonExport:
    """PBM -> aspect/binary analytics -> NDJSON export -> roundtrip verification."""

    def test_aspect_binary_basics(self):
        sample = str(next(_PBM_DIR.glob("*.pbm")))
        aspect = pbm_aspect_ratio(sample)
        is_binary = pbm_is_binary(sample)
        ratio = pbm_black_pixel_ratio(sample)
        assert isinstance(aspect, float)
        assert isinstance(is_binary, bool)
        assert isinstance(ratio, float)

    def test_row_and_uniform_basics(self):
        sample = str(next(_PBM_DIR.glob("*.pbm")))
        row_count = pbm_row_count(sample)
        has_black = pbm_has_any_black(sample)
        is_uniform = pbm_is_uniform(sample)
        assert row_count >= 0
        assert isinstance(has_black, bool)
        assert isinstance(is_uniform, bool)

    def test_aspect_binary_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_pbm_files():
            path = str(f)
            aspect = pbm_aspect_ratio(path)
            is_binary = pbm_is_binary(path)
            ratio = pbm_black_pixel_ratio(path)
            row_count = pbm_row_count(path)
            has_black = pbm_has_any_black(path)
            is_uniform = pbm_is_uniform(path)
            assert isinstance(aspect, float), f"pbm_aspect_ratio must be float for {f.name}"
            assert isinstance(is_binary, bool), f"pbm_is_binary must be bool for {f.name}"
            assert isinstance(ratio, float), f"pbm_black_pixel_ratio must be float for {f.name}"
            assert row_count >= 0, f"pbm_row_count must be >= 0 for {f.name}"
            assert isinstance(has_black, bool), f"pbm_has_any_black must be bool for {f.name}"
            assert isinstance(is_uniform, bool), f"pbm_is_uniform must be bool for {f.name}"
            records.append({
                "file": f.name,
                "aspect_ratio": aspect,
                "is_binary": is_binary,
                "black_pixel_ratio": ratio,
                "row_count": row_count,
                "has_any_black": has_black,
                "is_uniform": is_uniform,
                "source_format": "pbm",
            })
        dest = tmp_path / "pbm-aspect-binary.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_pbm_files():
            path = str(f)
            aspect = pbm_aspect_ratio(path)
            ratio = pbm_black_pixel_ratio(path)
            records.append({
                "file": f.name,
                "aspect_ratio": aspect,
                "black_pixel_ratio": ratio,
            })
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]
            assert orig["aspect_ratio"] == back["aspect_ratio"]
            assert orig["black_pixel_ratio"] == back["black_pixel_ratio"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_PBM_DIR.glob("*.pbm")))
        aspect = pbm_aspect_ratio(sample)
        has_black = pbm_has_any_black(sample)
        records = [{"file": "sample.pbm", "aspect_ratio": aspect, "has_any_black": has_black}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_binary_uniform_export(self, tmp_path):
        records = []
        for f in _valid_pbm_files():
            path = str(f)
            is_binary = pbm_is_binary(path)
            is_uniform = pbm_is_uniform(path)
            has_black = pbm_has_any_black(path)
            aspect = pbm_aspect_ratio(path)
            assert isinstance(is_binary, bool)
            assert isinstance(is_uniform, bool)
            assert isinstance(has_black, bool)
            assert isinstance(aspect, float)
            records.append({
                "file": f.name,
                "is_binary": is_binary,
                "is_uniform": is_uniform,
                "has_any_black": has_black,
                "aspect_ratio": aspect,
                "format": "pbm",
            })
        dest = tmp_path / "binary-uniform.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
        assert all(r["format"] == "pbm" for r in loaded)
        assert all(isinstance(r["is_binary"], bool) for r in loaded)
