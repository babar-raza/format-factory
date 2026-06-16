"""
tests/python/dogfood/test_dogfood_fodp_fodg_remaining_analytics_ndjson_export.py

Sprint: IDEMPOTENT-SWARM-SPRINT-64
Dogfood export: FODP+FODG parse -> remaining analytics -> write as NDJSON -> verify.
FODP uses: fodp_nonempty_slide_count, fodp_text_to_slide_ratio.
FODG uses: fodg_avg_shapes_per_page, fodg_has_empty_pages, fodg_page_shape_count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp import (
    load as fodp_load,
    fodp_nonempty_slide_count,
    fodp_text_to_slide_ratio,
    fodp_slide_count,
)
from fodg import (
    load as fodg_load,
    fodg_avg_shapes_per_page,
    fodg_has_empty_pages,
    fodg_page_shape_count,
    fodg_total_shape_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson


_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _valid_fodp_files():
    return sorted(_FODP_DIR.glob("*.fodp"))


def _valid_fodg_files():
    return sorted(_FODG_DIR.glob("*.fodg"))


class TestFodpFodgRemainingAnalyticsNdjsonExport:
    """FODP+FODG -> remaining analytics -> NDJSON export -> roundtrip verification."""

    def test_fodp_nonempty_and_ratio(self):
        sample = str(next(_FODP_DIR.glob("*.fodp")))
        nonempty = fodp_nonempty_slide_count(sample)
        ratio = fodp_text_to_slide_ratio(sample)
        assert nonempty >= 0
        assert isinstance(ratio, float)

    def test_fodg_avg_shapes_and_empty_pages(self):
        sample = str(next(_FODG_DIR.glob("*.fodg")))
        model = fodg_load(sample)
        avg = fodg_avg_shapes_per_page(sample)
        has_empty = fodg_has_empty_pages(sample)
        page_shapes = fodg_page_shape_count(model, 0)
        assert isinstance(avg, float)
        assert isinstance(has_empty, bool)
        assert page_shapes >= 0

    def test_remaining_analytics_to_ndjson(self, tmp_path):
        records = []
        for f in _valid_fodp_files():
            path = str(f)
            nonempty = fodp_nonempty_slide_count(path)
            ratio = fodp_text_to_slide_ratio(path)
            total = fodp_slide_count(path)
            assert nonempty >= 0, f"nonempty_slide_count must be >= 0 for {f.name}"
            assert isinstance(ratio, float), f"text_to_slide_ratio must be float for {f.name}"
            assert total >= 0
            records.append({
                "file": f.name,
                "nonempty_slide_count": nonempty,
                "text_to_slide_ratio": ratio,
                "slide_count": total,
                "source_format": "fodp",
            })
        for f in _valid_fodg_files():
            path = str(f)
            model = fodg_load(path)
            avg = fodg_avg_shapes_per_page(path)
            has_empty = fodg_has_empty_pages(path)
            page_shapes = fodg_page_shape_count(model, 0)
            total = fodg_total_shape_count(path)
            assert isinstance(avg, float), f"avg_shapes_per_page must be float for {f.name}"
            assert isinstance(has_empty, bool), f"has_empty_pages must be bool for {f.name}"
            assert page_shapes >= 0, f"page_shape_count must be >= 0 for {f.name}"
            assert total >= 0
            records.append({
                "file": f.name,
                "avg_shapes_per_page": avg,
                "has_empty_pages": has_empty,
                "page0_shape_count": page_shapes,
                "total_shapes": total,
                "source_format": "fodg",
            })
        dest = tmp_path / "fodp-fodg-remaining.ndjson"
        write_ndjson(records, str(dest))
        assert dest.exists()
        assert dest.stat().st_size > 0
        assert len(records) >= 3

    def test_ndjson_roundtrip(self, tmp_path):
        records = []
        for f in _valid_fodp_files():
            path = str(f)
            nonempty = fodp_nonempty_slide_count(path)
            ratio = fodp_text_to_slide_ratio(path)
            records.append({"file": f.name, "nonempty_slide_count": nonempty, "text_to_slide_ratio": ratio})
        for f in _valid_fodg_files():
            path = str(f)
            avg = fodg_avg_shapes_per_page(path)
            has_empty = fodg_has_empty_pages(path)
            records.append({"file": f.name, "avg_shapes_per_page": avg, "has_empty_pages": has_empty})
        dest = tmp_path / "roundtrip.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == len(records)
        for orig, back in zip(records, loaded):
            assert orig["file"] == back["file"]

    def test_json_lines_valid(self, tmp_path):
        sample = str(next(_FODP_DIR.glob("*.fodp")))
        nonempty = fodp_nonempty_slide_count(sample)
        records = [{"file": "sample.fodp", "nonempty_slide_count": nonempty}]
        dest = tmp_path / "valid.ndjson"
        write_ndjson(records, str(dest))
        for line in dest.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_ratio_and_shapes_export(self, tmp_path):
        records = []
        for f in _valid_fodp_files():
            path = str(f)
            ratio = fodp_text_to_slide_ratio(path)
            nonempty = fodp_nonempty_slide_count(path)
            assert isinstance(ratio, float)
            assert nonempty >= 0
            records.append({
                "file": f.name,
                "text_to_slide_ratio": ratio,
                "nonempty_slide_count": nonempty,
                "format": "fodp",
            })
        for f in _valid_fodg_files():
            path = str(f)
            avg = fodg_avg_shapes_per_page(path)
            has_empty = fodg_has_empty_pages(path)
            assert isinstance(avg, float)
            assert isinstance(has_empty, bool)
            records.append({
                "file": f.name,
                "avg_shapes_per_page": avg,
                "has_empty_pages": has_empty,
                "format": "fodg",
            })
        dest = tmp_path / "ratio-shapes.ndjson"
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) >= 3
