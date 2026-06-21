"""Dogfood export: QOI(12) + NDJSON(11) + PBM(10) remaining gap functions → NDJSON."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import (
    ndjson_all_records_are_dicts,
    ndjson_dict_field_total,
    ndjson_file_size_bytes,
    ndjson_key_count_variance,
    ndjson_max_record_key_count,
    ndjson_numeric_sum,
    ndjson_numeric_value_mean,
    ndjson_record_depth_max,
    ndjson_string_length_sum,
    ndjson_string_value_count,
    ndjson_value_variance,
    write_ndjson,
)
from pbm.pbm_parser import (
    pbm_center_region_density,
    pbm_column_density_avg,
    pbm_diagonal_pixel_sum,
    pbm_edge_black_count,
    pbm_height,
    pbm_is_single_row,
    pbm_quadrant_black_ratio,
    pbm_row_white_ratio,
    pbm_total_black_count,
    pbm_width,
)
from qoi.qoi_parser import (
    qoi_avg_saturation,
    qoi_dark_ratio,
    qoi_grayscale_pixel_count,
    qoi_green_mean_value,
    qoi_height,
    qoi_is_multi_row,
    qoi_light_ratio,
    qoi_max_red_value,
    qoi_pixel_uniformity,
    qoi_red_channel_mean,
    qoi_white_pixel_count,
    qoi_width,
)

_QOI = str(_REPO / "samples" / "by-format" / "qoi" / "valid" / "1x1-red.qoi")
_PBM = str(_REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm")


def _ndjson_sample(tmp_path):
    p = str(tmp_path / "sample.ndjson")
    write_ndjson([{"name": "Alice", "age": 30, "score": 95.5},
                  {"name": "Bob", "age": 25, "score": 87.0}], p)
    return p


def _w(tmp_path, metric, val, fname=None):
    out = tmp_path / (fname or f"{metric}.ndjson")
    write_ndjson([{"metric": metric, "value": val}], str(out))
    return json.loads(out.read_text().strip())["value"]


# --- QOI tests ---

def test_qoi_avg_saturation(tmp_path):
    val = qoi_avg_saturation(_QOI)
    assert isinstance(val, float) and val == 1.0
    assert _w(tmp_path, "qoi_avg_saturation", val) == 1.0


def test_qoi_dark_ratio(tmp_path):
    val = qoi_dark_ratio(_QOI)
    assert isinstance(val, float) and val == 0.0
    assert _w(tmp_path, "qoi_dark_ratio", val) == 0.0


def test_qoi_grayscale_pixel_count(tmp_path):
    val = qoi_grayscale_pixel_count(_QOI)
    assert isinstance(val, int) and val == 0
    assert _w(tmp_path, "qoi_grayscale_pixel_count", val) == 0


def test_qoi_green_mean_value(tmp_path):
    val = qoi_green_mean_value(_QOI)
    assert isinstance(val, float) and val == 0.0
    assert _w(tmp_path, "qoi_green_mean_value", val) == 0.0


def test_qoi_height(tmp_path):
    val = qoi_height(_QOI)
    assert isinstance(val, int) and val == 1
    assert _w(tmp_path, "qoi_height", val) == 1


def test_qoi_is_multi_row(tmp_path):
    val = qoi_is_multi_row(_QOI)
    assert isinstance(val, bool) and val is False
    assert _w(tmp_path, "qoi_is_multi_row", val) is False


def test_qoi_light_ratio(tmp_path):
    val = qoi_light_ratio(_QOI)
    assert isinstance(val, float) and val == 0.0
    assert _w(tmp_path, "qoi_light_ratio", val) == 0.0


def test_qoi_max_red_value(tmp_path):
    val = qoi_max_red_value(_QOI)
    assert isinstance(val, int) and val == 255
    assert _w(tmp_path, "qoi_max_red_value", val) == 255


def test_qoi_pixel_uniformity(tmp_path):
    val = qoi_pixel_uniformity(_QOI)
    assert isinstance(val, float) and val == 1.0
    assert _w(tmp_path, "qoi_pixel_uniformity", val) == 1.0


def test_qoi_red_channel_mean(tmp_path):
    val = qoi_red_channel_mean(_QOI)
    assert isinstance(val, float) and val == 255.0
    assert _w(tmp_path, "qoi_red_channel_mean", val) == 255.0


def test_qoi_white_pixel_count(tmp_path):
    val = qoi_white_pixel_count(_QOI)
    assert isinstance(val, int) and val == 0
    assert _w(tmp_path, "qoi_white_pixel_count", val) == 0


def test_qoi_width(tmp_path):
    val = qoi_width(_QOI)
    assert isinstance(val, int) and val == 1
    assert _w(tmp_path, "qoi_width", val) == 1


# --- NDJSON tests ---

def test_ndjson_all_records_are_dicts(tmp_path):
    s = _ndjson_sample(tmp_path)
    val = ndjson_all_records_are_dicts(s)
    assert isinstance(val, bool) and val is True
    assert _w(tmp_path, "ndjson_all_records_are_dicts", val, "out1.ndjson") is True


def test_ndjson_dict_field_total(tmp_path):
    s = _ndjson_sample(tmp_path)
    val = ndjson_dict_field_total(s)
    assert isinstance(val, int) and val == 6
    assert _w(tmp_path, "ndjson_dict_field_total", val, "out2.ndjson") == 6


def test_ndjson_file_size_bytes(tmp_path):
    s = _ndjson_sample(tmp_path)
    val = ndjson_file_size_bytes(s)
    assert isinstance(val, int) and val == 88
    assert _w(tmp_path, "ndjson_file_size_bytes", val, "out3.ndjson") == 88


def test_ndjson_key_count_variance(tmp_path):
    s = _ndjson_sample(tmp_path)
    val = ndjson_key_count_variance(s)
    assert isinstance(val, float) and val == 0.0
    assert _w(tmp_path, "ndjson_key_count_variance", val, "out4.ndjson") == 0.0


def test_ndjson_max_record_key_count(tmp_path):
    s = _ndjson_sample(tmp_path)
    val = ndjson_max_record_key_count(s)
    assert isinstance(val, int) and val == 3
    assert _w(tmp_path, "ndjson_max_record_key_count", val, "out5.ndjson") == 3


def test_ndjson_numeric_sum(tmp_path):
    s = _ndjson_sample(tmp_path)
    val = ndjson_numeric_sum(s)
    assert isinstance(val, float) and val == 237.5
    assert _w(tmp_path, "ndjson_numeric_sum", val, "out6.ndjson") == 237.5


def test_ndjson_numeric_value_mean(tmp_path):
    s = _ndjson_sample(tmp_path)
    val = ndjson_numeric_value_mean(s)
    assert isinstance(val, float) and val == 59.375
    assert _w(tmp_path, "ndjson_numeric_value_mean", val, "out7.ndjson") == 59.375


def test_ndjson_record_depth_max(tmp_path):
    s = _ndjson_sample(tmp_path)
    val = ndjson_record_depth_max(s)
    assert isinstance(val, int) and val == 1
    assert _w(tmp_path, "ndjson_record_depth_max", val, "out8.ndjson") == 1


def test_ndjson_string_length_sum(tmp_path):
    s = _ndjson_sample(tmp_path)
    val = ndjson_string_length_sum(s)
    assert isinstance(val, int) and val == 8
    assert _w(tmp_path, "ndjson_string_length_sum", val, "out9.ndjson") == 8


def test_ndjson_string_value_count(tmp_path):
    s = _ndjson_sample(tmp_path)
    val = ndjson_string_value_count(s)
    assert isinstance(val, int) and val == 2
    assert _w(tmp_path, "ndjson_string_value_count", val, "out10.ndjson") == 2


def test_ndjson_value_variance(tmp_path):
    s = _ndjson_sample(tmp_path)
    val = ndjson_value_variance(s)
    assert isinstance(val, float) and val == 1028.171875
    assert _w(tmp_path, "ndjson_value_variance", val, "out11.ndjson") == 1028.171875


# --- PBM tests ---

def test_pbm_center_region_density(tmp_path):
    val = pbm_center_region_density(_PBM)
    assert isinstance(val, float) and val == 1.0
    assert _w(tmp_path, "pbm_center_region_density", val) == 1.0


def test_pbm_column_density_avg(tmp_path):
    val = pbm_column_density_avg(_PBM)
    assert isinstance(val, float) and val == 0.5
    assert _w(tmp_path, "pbm_column_density_avg", val) == 0.5


def test_pbm_diagonal_pixel_sum(tmp_path):
    val = pbm_diagonal_pixel_sum(_PBM)
    assert isinstance(val, int) and val == 2
    assert _w(tmp_path, "pbm_diagonal_pixel_sum", val) == 2


def test_pbm_edge_black_count(tmp_path):
    val = pbm_edge_black_count(_PBM)
    assert isinstance(val, int) and val == 2
    assert _w(tmp_path, "pbm_edge_black_count", val) == 2


def test_pbm_height(tmp_path):
    val = pbm_height(_PBM)
    assert isinstance(val, int) and val == 2
    assert _w(tmp_path, "pbm_height", val) == 2


def test_pbm_is_single_row(tmp_path):
    val = pbm_is_single_row(_PBM)
    assert isinstance(val, bool) and val is False
    assert _w(tmp_path, "pbm_is_single_row", val) is False


def test_pbm_quadrant_black_ratio(tmp_path):
    val = pbm_quadrant_black_ratio(_PBM)
    assert isinstance(val, list) and len(val) == 4
    out = tmp_path / "pbm_quadrant_black_ratio.ndjson"
    write_ndjson([{"metric": "pbm_quadrant_black_ratio", "value": val}], str(out))
    result = json.loads(out.read_text().strip())["value"]
    assert result == [1.0, 0.0, 0.0, 1.0]


def test_pbm_row_white_ratio(tmp_path):
    val = pbm_row_white_ratio(_PBM)
    assert isinstance(val, float) and val == 0.5
    assert _w(tmp_path, "pbm_row_white_ratio", val) == 0.5


def test_pbm_total_black_count(tmp_path):
    val = pbm_total_black_count(_PBM)
    assert isinstance(val, int) and val == 2
    assert _w(tmp_path, "pbm_total_black_count", val) == 2


def test_pbm_width(tmp_path):
    val = pbm_width(_PBM)
    assert isinstance(val, int) and val == 2
    assert _w(tmp_path, "pbm_width", val) == 2


def test_all_batch_ndjson_export(tmp_path):
    s = _ndjson_sample(tmp_path)
    records = [
        {"fmt": "qoi", "metric": "qoi_red_channel_mean", "value": qoi_red_channel_mean(_QOI)},
        {"fmt": "ndjson", "metric": "ndjson_numeric_sum", "value": ndjson_numeric_sum(s)},
        {"fmt": "pbm", "metric": "pbm_width", "value": pbm_width(_PBM)},
    ]
    out = tmp_path / "qoi_ndjson_pbm_batch.ndjson"
    write_ndjson(records, str(out))
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 3
    fmts = {json.loads(ln)["fmt"] for ln in lines}
    assert {"qoi", "ndjson", "pbm"} == fmts
