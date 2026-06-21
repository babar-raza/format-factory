"""Dogfood: CSV(6)+TSV(4)+FODP(3)+ODT(3)+XCF(4) final analytics gap functions -> NDJSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import write_ndjson
from src.python.csv.csv_parser import (
    csv_avg_string_field_length,
    csv_nonempty_column_count,
    csv_numeric_field_mean,
    csv_row_length_min,
    csv_string_length_sum,
    csv_value_variance,
)
from tsv.tsv_parser import (
    tsv_header_field_count,
    tsv_numeric_row_count,
    tsv_total_header_length,
    tsv_value_variance,
)
from fodp.fodp_codec import (
    fodp_avg_word_count_per_slide,
    fodp_longest_slide_text,
    fodp_shortest_slide_text,
)
from odt.odt_parser import (
    odt_digit_ratio,
    odt_paragraph_length_variance,
    odt_shortest_paragraph,
)
from xcf.xcf_parser import (
    xcf_canvas_fill_ratio,
    xcf_canvas_half_perimeter,
    xcf_is_tiny,
    xcf_layer_count_ratio,
)

_CSV = str(_REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv")
_TSV = str(_REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv")
_FODP = str(_REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp")
_ODT = str(_REPO / "samples" / "by-format" / "odt" / "valid" / "minimal-document.odt")
_XCF = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")


def _w(tmp_path, metric, val, suffix=""):
    out = tmp_path / f"{metric}{suffix}.ndjson"
    write_ndjson([{"metric": metric, "value": val}], str(out))
    return json.loads(out.read_text().strip())["value"]


# --- CSV ---

def test_csv_avg_string_field_length(tmp_path):
    val = csv_avg_string_field_length(_CSV)
    assert isinstance(val, float) and val == 4.0
    assert _w(tmp_path, "csv_avg_string_field_length", val) == 4.0


def test_csv_nonempty_column_count(tmp_path):
    val = csv_nonempty_column_count(_CSV)
    assert isinstance(val, int) and val == 2
    assert _w(tmp_path, "csv_nonempty_column_count", val) == 2


def test_csv_numeric_field_mean(tmp_path):
    val = csv_numeric_field_mean(_CSV)
    assert isinstance(val, float) and val == 27.5
    assert _w(tmp_path, "csv_numeric_field_mean", val) == 27.5


def test_csv_row_length_min(tmp_path):
    val = csv_row_length_min(_CSV)
    assert isinstance(val, int) and val == 2
    assert _w(tmp_path, "csv_row_length_min", val) == 2


def test_csv_string_length_sum(tmp_path):
    val = csv_string_length_sum(_CSV)
    assert isinstance(val, int) and val == 8
    assert _w(tmp_path, "csv_string_length_sum", val) == 8


def test_csv_value_variance(tmp_path):
    val = csv_value_variance(_CSV)
    assert isinstance(val, float) and val == 6.25
    assert _w(tmp_path, "csv_value_variance", val) == 6.25


# --- TSV ---

def test_tsv_header_field_count(tmp_path):
    val = tsv_header_field_count(_TSV)
    assert isinstance(val, int) and val == 2
    assert _w(tmp_path, "tsv_header_field_count", val) == 2


def test_tsv_numeric_row_count(tmp_path):
    val = tsv_numeric_row_count(_TSV)
    assert isinstance(val, int) and val == 0
    assert _w(tmp_path, "tsv_numeric_row_count", val) == 0


def test_tsv_total_header_length(tmp_path):
    val = tsv_total_header_length(_TSV)
    assert isinstance(val, int) and val == 7
    assert _w(tmp_path, "tsv_total_header_length", val) == 7


def test_tsv_value_variance(tmp_path):
    val = tsv_value_variance(_TSV)
    assert isinstance(val, float) and val == 6.25
    assert _w(tmp_path, "tsv_value_variance", val) == 6.25


# --- FODP ---

def test_fodp_avg_word_count_per_slide(tmp_path):
    val = fodp_avg_word_count_per_slide(_FODP)
    assert isinstance(val, float) and val == 0.0
    assert _w(tmp_path, "fodp_avg_word_count_per_slide", val) == 0.0


def test_fodp_longest_slide_text(tmp_path):
    val = fodp_longest_slide_text(_FODP)
    assert isinstance(val, int) and val == 0
    assert _w(tmp_path, "fodp_longest_slide_text", val) == 0


def test_fodp_shortest_slide_text(tmp_path):
    val = fodp_shortest_slide_text(_FODP)
    assert isinstance(val, int) and val == 0
    assert _w(tmp_path, "fodp_shortest_slide_text", val) == 0


# --- ODT ---

def test_odt_digit_ratio(tmp_path):
    val = odt_digit_ratio(_ODT)
    assert isinstance(val, float) and val == 0.0
    assert _w(tmp_path, "odt_digit_ratio", val) == 0.0


def test_odt_paragraph_length_variance(tmp_path):
    val = odt_paragraph_length_variance(_ODT)
    assert isinstance(val, float) and val == 0.0
    assert _w(tmp_path, "odt_paragraph_length_variance", val) == 0.0


def test_odt_shortest_paragraph(tmp_path):
    val = odt_shortest_paragraph(_ODT)
    assert isinstance(val, int) and val == 13
    assert _w(tmp_path, "odt_shortest_paragraph", val) == 13


# --- XCF ---

def test_xcf_canvas_fill_ratio(tmp_path):
    val = xcf_canvas_fill_ratio(_XCF)
    assert isinstance(val, float) and val == 1.0
    assert _w(tmp_path, "xcf_canvas_fill_ratio", val) == 1.0


def test_xcf_canvas_half_perimeter(tmp_path):
    val = xcf_canvas_half_perimeter(_XCF)
    assert isinstance(val, int) and val == 2
    assert _w(tmp_path, "xcf_canvas_half_perimeter", val) == 2


def test_xcf_is_tiny(tmp_path):
    val = xcf_is_tiny(_XCF)
    assert isinstance(val, bool) and val is True
    assert _w(tmp_path, "xcf_is_tiny", val) is True


def test_xcf_layer_count_ratio(tmp_path):
    val = xcf_layer_count_ratio(_XCF)
    assert isinstance(val, float) and val == 1.0
    assert _w(tmp_path, "xcf_layer_count_ratio", val) == 1.0


def test_batch_ndjson_export(tmp_path):
    records = [
        {"fmt": "csv", "m": "csv_numeric_field_mean", "v": csv_numeric_field_mean(_CSV)},
        {"fmt": "tsv", "m": "tsv_value_variance", "v": tsv_value_variance(_TSV)},
        {"fmt": "fodp", "m": "fodp_avg_word_count_per_slide", "v": fodp_avg_word_count_per_slide(_FODP)},
        {"fmt": "odt", "m": "odt_shortest_paragraph", "v": odt_shortest_paragraph(_ODT)},
        {"fmt": "xcf", "m": "xcf_canvas_fill_ratio", "v": xcf_canvas_fill_ratio(_XCF)},
    ]
    out = tmp_path / "final_gaps_batch.ndjson"
    write_ndjson(records, str(out))
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 5
    fmts = {json.loads(ln)["fmt"] for ln in lines}
    assert {"csv", "tsv", "fodp", "odt", "xcf"} == fmts
