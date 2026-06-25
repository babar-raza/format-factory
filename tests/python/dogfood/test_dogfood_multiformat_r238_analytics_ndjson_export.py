"""Dogfood: Multi-format R238 analytics → NDJSON export.

Collects new R238 analytics from QOI, XCF, CSV, ODS, ODT, SYLK, PGM, PPM
and exports them as NDJSON records.
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi import qoi_aspect_ratio, qoi_color_concentration
from xcf import xcf_compression_ratio, xcf_layers_per_dimension
from ods import ods_data_density, ods_max_cell_value_length
from odt import odt_vocabulary_richness, odt_chars_per_word
from sylk import sylk_data_sparsity, sylk_max_cell_value_length
from pgm import pgm_standard_deviation, pgm_brightness_ratio
from ppm import ppm_luminance_average, ppm_green_channel_sum
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_QOI = sorted((_REPO / "samples" / "by-format" / "qoi" / "valid").glob("*.qoi"))
_XCF = sorted((_REPO / "samples" / "by-format" / "xcf" / "valid").glob("*.xcf"))
_ODS = sorted((_REPO / "samples" / "by-format" / "ods" / "valid").glob("*.ods"))
_ODT = sorted((_REPO / "samples" / "by-format" / "odt" / "valid").glob("*.odt"))
_SYLK = sorted((_REPO / "samples" / "by-format" / "sylk" / "valid").glob("*.slk"))
_PGM = sorted((_REPO / "samples" / "by-format" / "pgm" / "valid").glob("*.pgm"))
_PPM = sorted((_REPO / "samples" / "by-format" / "ppm" / "valid").glob("*.ppm"))


class TestDogfoodMultiformatR238AnalyticsNdjsonExport:
    def test_collect_all_formats(self, tmp_path):
        records = []
        if _QOI:
            s = str(_QOI[0])
            records.append({"format": "qoi", "file": _QOI[0].name,
                            "aspect_ratio": qoi_aspect_ratio(s),
                            "color_concentration": qoi_color_concentration(s)})
        if _XCF:
            s = str(_XCF[0])
            records.append({"format": "xcf", "file": _XCF[0].name,
                            "compression_ratio": xcf_compression_ratio(s),
                            "layers_per_dim": xcf_layers_per_dimension(s)})
        if _ODS:
            s = str(_ODS[0])
            records.append({"format": "ods", "file": _ODS[0].name,
                            "data_density": ods_data_density(s),
                            "max_cell_len": ods_max_cell_value_length(s)})
        if _ODT:
            s = str(_ODT[0])
            records.append({"format": "odt", "file": _ODT[0].name,
                            "vocab_richness": odt_vocabulary_richness(s),
                            "chars_per_word": odt_chars_per_word(s)})
        if _SYLK:
            s = str(_SYLK[0])
            records.append({"format": "sylk", "file": _SYLK[0].name,
                            "sparsity": sylk_data_sparsity(s),
                            "max_cell_len": sylk_max_cell_value_length(s)})
        if _PGM:
            s = str(_PGM[0])
            records.append({"format": "pgm", "file": _PGM[0].name,
                            "std_dev": pgm_standard_deviation(s),
                            "brightness_ratio": pgm_brightness_ratio(s)})
        if _PPM:
            s = str(_PPM[0])
            records.append({"format": "ppm", "file": _PPM[0].name,
                            "luminance_avg": ppm_luminance_average(s),
                            "green_sum": ppm_green_channel_sum(s)})
        assert len(records) >= 5

        ndjson_path = tmp_path / "r238-analytics.ndjson"
        write_ndjson(records, str(ndjson_path))
        loaded = load_ndjson(str(ndjson_path))
        assert len(loaded) == len(records)
        formats = {r["format"] for r in loaded}
        assert len(formats) >= 5

    def test_ndjson_records_valid_json(self, tmp_path):
        records = [
            {"format": "qoi", "aspect_ratio": qoi_aspect_ratio(str(_QOI[0]))},
            {"format": "pgm", "std_dev": pgm_standard_deviation(str(_PGM[0]))},
        ]
        path = tmp_path / "check.ndjson"
        write_ndjson(records, str(path))
        for line in path.read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert isinstance(obj, dict)
            assert "format" in obj
