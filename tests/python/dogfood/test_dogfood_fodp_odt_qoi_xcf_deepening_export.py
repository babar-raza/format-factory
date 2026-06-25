"""Dogfood: FODP + ODT + QOI + XCF deepening analytics -> NDJSON export."""
from __future__ import annotations
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))


class TestFodpOdtQoiXcfDeepeningExport:
    def test_multiformat_analytics_export(self, tmp_path):
        from ndjson.ndjson_codec import write_ndjson, load_ndjson
        records = []

        fodp_files = sorted((_REPO / "samples" / "by-format" / "fodp").glob("*.fodp"))
        if fodp_files:
            from fodp import fodp_average_text_per_slide, fodp_shape_to_slide_ratio
            s = str(fodp_files[0])
            records.append({
                "format": "fodp",
                "avg_text_per_slide": fodp_average_text_per_slide(s),
                "shape_to_slide_ratio": fodp_shape_to_slide_ratio(s),
            })

        odt_files = sorted((_REPO / "samples" / "by-format" / "odt" / "valid").glob("*.odt"))
        if odt_files:
            from odt import odt_min_paragraph_length, odt_heading_to_paragraph_ratio
            s = str(odt_files[0])
            records.append({
                "format": "odt",
                "min_para_length": odt_min_paragraph_length(s),
                "heading_to_para_ratio": odt_heading_to_paragraph_ratio(s),
            })

        qoi_files = sorted((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi"))
        if qoi_files:
            from qoi import qoi_perimeter, qoi_color_variance
            s = str(qoi_files[0])
            records.append({
                "format": "qoi",
                "perimeter": qoi_perimeter(s),
                "color_variance": qoi_color_variance(s),
            })

        xcf_files = sorted((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf"))
        if xcf_files:
            from xcf import xcf_dimension_ratio, xcf_layer_density
            s = str(xcf_files[0])
            records.append({
                "format": "xcf",
                "dimension_ratio": xcf_dimension_ratio(s),
                "layer_density": xcf_layer_density(s),
            })

        assert len(records) == 4
        out = tmp_path / "deepening-4format.ndjson"
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 4
        assert {r["format"] for r in loaded} == {"fodp", "odt", "qoi", "xcf"}
