"""Dogfood export: Sprint 76 gap-closure functions → NDJSON pipeline.

Demonstrates real usage of the 10 Sprint 76 analytics functions
(CSV, QOI, SYLK, TSV, XCF) exported as NDJSON records.
"""
import json
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_header_field_count, csv_field_text_mean_length
from src.python.qoi import qoi_red_mean_value
from src.python.sylk import sylk_col_count_exceeds_row_count
from src.python.tsv.tsv_parser import tsv_field_count_variance, tsv_min_header_length
from src.python.xcf import (
    xcf_area_to_layer_ratio, xcf_min_side_length,
    xcf_avg_layer_area, xcf_height_to_layer_ratio,
)
from src.python.ndjson import write_ndjson

_CSV = str(_REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv")
_QOI = str(_REPO / "samples" / "by-format" / "qoi" / "valid" / "4x1-gradient.qoi")
_SYLK = str(_REPO / "samples" / "by-format" / "sylk" / "valid" / "numeric-row.slk")
_TSV = str(_REPO / "samples" / "by-format" / "tsv" / "multi-column.tsv")
_XCF = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf")


def _build_records():
    return [
        {
            "format": "csv", "file": "minimal-2x2.csv",
            "header_field_count": csv_header_field_count(_CSV),
            "field_text_mean_length": csv_field_text_mean_length(_CSV),
        },
        {
            "format": "qoi", "file": "4x1-gradient.qoi",
            "red_mean_value": qoi_red_mean_value(_QOI),
        },
        {
            "format": "sylk", "file": "numeric-row.slk",
            "col_count_exceeds_row_count": sylk_col_count_exceeds_row_count(_SYLK),
        },
        {
            "format": "tsv", "file": "multi-column.tsv",
            "field_count_variance": tsv_field_count_variance(_TSV),
            "min_header_length": tsv_min_header_length(_TSV),
        },
        {
            "format": "xcf", "file": "2x2-gray.xcf",
            "area_to_layer_ratio": xcf_area_to_layer_ratio(_XCF),
            "min_side_length": xcf_min_side_length(_XCF),
            "avg_layer_area": xcf_avg_layer_area(_XCF),
            "height_to_layer_ratio": xcf_height_to_layer_ratio(_XCF),
        },
    ]


class TestSprint76AnalyticsNdjsonExport:
    def test_records_build(self):
        records = _build_records()
        assert len(records) == 5

    def test_csv_record_values(self):
        records = _build_records()
        csv_rec = next(r for r in records if r["format"] == "csv")
        assert csv_rec["header_field_count"] == 2
        assert csv_rec["field_text_mean_length"] == 3.0

    def test_qoi_record_values(self):
        records = _build_records()
        qoi_rec = next(r for r in records if r["format"] == "qoi")
        assert qoi_rec["red_mean_value"] == 127.5

    def test_sylk_record_values(self):
        records = _build_records()
        sylk_rec = next(r for r in records if r["format"] == "sylk")
        assert sylk_rec["col_count_exceeds_row_count"] is True

    def test_tsv_record_values(self):
        records = _build_records()
        tsv_rec = next(r for r in records if r["format"] == "tsv")
        assert tsv_rec["field_count_variance"] == 0.0
        assert tsv_rec["min_header_length"] == 2

    def test_xcf_record_values(self):
        records = _build_records()
        xcf_rec = next(r for r in records if r["format"] == "xcf")
        assert xcf_rec["area_to_layer_ratio"] == 4.0
        assert xcf_rec["min_side_length"] == 2
        assert xcf_rec["avg_layer_area"] == 4.0
        assert xcf_rec["height_to_layer_ratio"] == 2.0

    def test_ndjson_export_roundtrip(self):
        records = _build_records()
        with tempfile.NamedTemporaryFile(suffix=".ndjson", delete=False, mode="w") as f:
            tmp = f.name
        write_ndjson(records, tmp)
        lines = Path(tmp).read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 5
        parsed = [json.loads(line) for line in lines]
        assert parsed[0]["format"] == "csv"
        assert parsed[1]["format"] == "qoi"
        assert parsed[4]["format"] == "xcf"

    def test_ndjson_each_line_is_valid_json(self):
        records = _build_records()
        with tempfile.NamedTemporaryFile(suffix=".ndjson", delete=False, mode="w") as f:
            tmp = f.name
        write_ndjson(records, tmp)
        for line in Path(tmp).read_text(encoding="utf-8").strip().splitlines():
            obj = json.loads(line)
            assert "format" in obj
