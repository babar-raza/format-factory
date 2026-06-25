"""Dogfood: FODP + QOI + XCF deepening analytics -> NDJSON export.

Collects analytics from 3 format deepening functions and exports as NDJSON.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))


class TestFodpQoiXcfDeepeningExport:
    def test_multiformat_analytics_export(self, tmp_path):
        from ndjson.ndjson_codec import write_ndjson, load_ndjson
        records = []

        # FODP
        fodp_files = sorted((_REPO / "samples" / "by-format" / "fodp").glob("*.fodp"))
        if fodp_files:
            from fodp import fodp_nonempty_slide_count, fodp_text_to_slide_ratio
            s = str(fodp_files[0])
            records.append({
                "format": "fodp",
                "nonempty_slides": fodp_nonempty_slide_count(s),
                "text_to_slide_ratio": fodp_text_to_slide_ratio(s),
            })

        # QOI
        qoi_files = sorted((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi"))
        if qoi_files:
            from qoi import qoi_blue_dominant, qoi_green_dominant, qoi_avg_rgb
            s = str(qoi_files[0])
            avg = qoi_avg_rgb(s)
            records.append({
                "format": "qoi",
                "blue_dominant": qoi_blue_dominant(s),
                "green_dominant": qoi_green_dominant(s),
                "avg_r": avg[0], "avg_g": avg[1], "avg_b": avg[2],
            })

        # XCF
        xcf_files = sorted((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf"))
        if xcf_files:
            from xcf import xcf_perimeter, xcf_diagonal
            s = str(xcf_files[0])
            records.append({
                "format": "xcf",
                "perimeter": xcf_perimeter(s),
                "diagonal": xcf_diagonal(s),
            })

        assert len(records) >= 2
        out = tmp_path / "deepening-export.ndjson"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == len(records)
        formats = {r["format"] for r in loaded}
        assert len(formats) >= 2

    def test_all_records_valid_json(self, tmp_path):
        from ndjson.ndjson_codec import write_ndjson
        from fodp import fodp_nonempty_slide_count
        from xcf import xcf_perimeter

        records = []
        fodp_files = sorted((_REPO / "samples" / "by-format" / "fodp").glob("*.fodp"))
        if fodp_files:
            records.append({"metric": "fodp_nonempty", "value": fodp_nonempty_slide_count(str(fodp_files[0]))})
        xcf_files = sorted((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf"))
        if xcf_files:
            records.append({"metric": "xcf_perimeter", "value": xcf_perimeter(str(xcf_files[0]))})

        out = tmp_path / "metrics.ndjson"
        write_ndjson(records, str(out))
        for line in out.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert "metric" in obj
            assert "value" in obj
