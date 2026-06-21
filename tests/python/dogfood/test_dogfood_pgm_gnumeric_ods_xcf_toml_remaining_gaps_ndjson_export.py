"""Dogfood: PGM(7)+Gnumeric(8)+ODS(8)+XCF(4)+TOML(4) remaining gap functions → NDJSON."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import write_ndjson
from gnumeric.gnumeric_codec import (
    gnumeric_avg_row_per_sheet, gnumeric_cell_text_total_length,
    gnumeric_col_count_variance, gnumeric_fill_rate, gnumeric_max_string_cell_count,
    gnumeric_min_cell_value_length, gnumeric_multi_sheet_ratio, gnumeric_sheet_name_total_length,
)
from ods.ods_parser import (
    ods_cell_text_avg_length, ods_cell_type_count, ods_cells_exceed_sheets,
    ods_max_cells_per_sheet, ods_multi_sheet_cell_ratio, ods_row_col_ratio,
    ods_string_length_sum, ods_value_variance,
)
from pgm.pgm_parser import (
    pgm_center_pixel_value, pgm_gradient_magnitude, pgm_left_column_mean,
    pgm_maxval_exceeds_avg, pgm_percentile_value, pgm_pixel_variance, pgm_right_column_mean,
)
from toml.toml_codec import toml_bool_count, toml_has_boolean_value, toml_numeric_count, toml_string_count
from xcf.xcf_parser import xcf_canvas_diagonal, xcf_pixels_exceed_layers, xcf_width_height_sum, xcf_width_squared

_PGM = str(_REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm")
_GN = str(_REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric")
_ODS = str(_REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods")
_XCF = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_TOML = str(_REPO / "samples" / "by-format" / "toml" / "minimal.toml")


def _w(tmp_path, metric, val, suffix=""):
    out = tmp_path / f"{metric}{suffix}.ndjson"
    write_ndjson([{"metric": metric, "value": val}], str(out))
    return json.loads(out.read_text().strip())["value"]


# --- PGM ---

def test_pgm_center_pixel_value(tmp_path):
    val = pgm_center_pixel_value(_PGM)
    assert isinstance(val, int) and val == 255
    assert _w(tmp_path, "pgm_center_pixel_value", val) == 255


def test_pgm_gradient_magnitude(tmp_path):
    val = pgm_gradient_magnitude(_PGM)
    assert isinstance(val, float) and val == 85.0
    assert _w(tmp_path, "pgm_gradient_magnitude", val) == 85.0


def test_pgm_left_column_mean(tmp_path):
    val = pgm_left_column_mean(_PGM)
    assert isinstance(val, float) and val == 85.0
    assert _w(tmp_path, "pgm_left_column_mean", val) == 85.0


def test_pgm_maxval_exceeds_avg(tmp_path):
    val = pgm_maxval_exceeds_avg(_PGM)
    assert isinstance(val, bool) and val is True
    assert _w(tmp_path, "pgm_maxval_exceeds_avg", val) is True


def test_pgm_percentile_value(tmp_path):
    val = pgm_percentile_value(_PGM)
    assert isinstance(val, int) and val == 170
    assert _w(tmp_path, "pgm_percentile_value", val) == 170


def test_pgm_pixel_variance(tmp_path):
    val = pgm_pixel_variance(_PGM)
    assert isinstance(val, float) and val == 9031.25
    assert _w(tmp_path, "pgm_pixel_variance", val) == 9031.25


def test_pgm_right_column_mean(tmp_path):
    val = pgm_right_column_mean(_PGM)
    assert isinstance(val, float) and val == 170.0
    assert _w(tmp_path, "pgm_right_column_mean", val) == 170.0


# --- Gnumeric ---

def test_gnumeric_avg_row_per_sheet(tmp_path):
    val = gnumeric_avg_row_per_sheet(_GN)
    assert isinstance(val, float) and val == 1.0
    assert _w(tmp_path, "gnumeric_avg_row_per_sheet", val) == 1.0


def test_gnumeric_cell_text_total_length(tmp_path):
    val = gnumeric_cell_text_total_length(_GN)
    assert isinstance(val, int) and val == 5
    assert _w(tmp_path, "gnumeric_cell_text_total_length", val) == 5


def test_gnumeric_col_count_variance(tmp_path):
    val = gnumeric_col_count_variance(_GN)
    assert isinstance(val, float) and val == 0.0
    assert _w(tmp_path, "gnumeric_col_count_variance", val) == 0.0


def test_gnumeric_fill_rate(tmp_path):
    val = gnumeric_fill_rate(_GN)
    assert isinstance(val, float) and val == 1.0
    assert _w(tmp_path, "gnumeric_fill_rate", val) == 1.0


def test_gnumeric_max_string_cell_count(tmp_path):
    val = gnumeric_max_string_cell_count(_GN)
    assert isinstance(val, int) and val == 1
    assert _w(tmp_path, "gnumeric_max_string_cell_count", val) == 1


def test_gnumeric_min_cell_value_length(tmp_path):
    val = gnumeric_min_cell_value_length(_GN)
    assert isinstance(val, int) and val == 5
    assert _w(tmp_path, "gnumeric_min_cell_value_length", val) == 5


def test_gnumeric_multi_sheet_ratio(tmp_path):
    val = gnumeric_multi_sheet_ratio(_GN)
    assert isinstance(val, float) and val == 0.0
    assert _w(tmp_path, "gnumeric_multi_sheet_ratio", val) == 0.0


def test_gnumeric_sheet_name_total_length(tmp_path):
    val = gnumeric_sheet_name_total_length(_GN)
    assert isinstance(val, int) and val == 6
    assert _w(tmp_path, "gnumeric_sheet_name_total_length", val) == 6


# --- ODS ---

def test_ods_cell_text_avg_length(tmp_path):
    val = ods_cell_text_avg_length(_ODS)
    assert isinstance(val, float) and val == 4.5
    assert _w(tmp_path, "ods_cell_text_avg_length", val) == 4.5


def test_ods_cell_type_count(tmp_path):
    val = ods_cell_type_count(_ODS)
    assert isinstance(val, int) and val == 2
    assert _w(tmp_path, "ods_cell_type_count", val) == 2


def test_ods_cells_exceed_sheets(tmp_path):
    val = ods_cells_exceed_sheets(_ODS)
    assert isinstance(val, bool) and val is True
    assert _w(tmp_path, "ods_cells_exceed_sheets", val) is True


def test_ods_max_cells_per_sheet(tmp_path):
    val = ods_max_cells_per_sheet(_ODS)
    assert isinstance(val, int) and val == 4
    assert _w(tmp_path, "ods_max_cells_per_sheet", val) == 4


def test_ods_multi_sheet_cell_ratio(tmp_path):
    val = ods_multi_sheet_cell_ratio(_ODS)
    assert isinstance(val, float) and val == 1.0
    assert _w(tmp_path, "ods_multi_sheet_cell_ratio", val) == 1.0


def test_ods_row_col_ratio(tmp_path):
    val = ods_row_col_ratio(_ODS)
    assert isinstance(val, float) and val == 1.0
    assert _w(tmp_path, "ods_row_col_ratio", val) == 1.0


def test_ods_string_length_sum(tmp_path):
    val = ods_string_length_sum(_ODS)
    assert isinstance(val, int) and val == 14
    assert _w(tmp_path, "ods_string_length_sum", val) == 14


def test_ods_value_variance(tmp_path):
    val = ods_value_variance(_ODS)
    assert isinstance(val, float) and val == 0.0
    assert _w(tmp_path, "ods_value_variance", val) == 0.0


# --- XCF ---

def test_xcf_canvas_diagonal(tmp_path):
    val = xcf_canvas_diagonal(_XCF)
    assert isinstance(val, float)
    assert abs(val - math.sqrt(2)) < 1e-9
    result = _w(tmp_path, "xcf_canvas_diagonal", val)
    assert abs(result - math.sqrt(2)) < 1e-9


def test_xcf_pixels_exceed_layers(tmp_path):
    val = xcf_pixels_exceed_layers(_XCF)
    assert isinstance(val, bool) and val is False
    assert _w(tmp_path, "xcf_pixels_exceed_layers", val) is False


def test_xcf_width_height_sum(tmp_path):
    val = xcf_width_height_sum(_XCF)
    assert isinstance(val, int) and val == 2
    assert _w(tmp_path, "xcf_width_height_sum", val) == 2


def test_xcf_width_squared(tmp_path):
    val = xcf_width_squared(_XCF)
    assert isinstance(val, int) and val == 1
    assert _w(tmp_path, "xcf_width_squared", val) == 1


# --- TOML ---

def test_toml_bool_count(tmp_path):
    val = toml_bool_count(_TOML)
    assert isinstance(val, int) and val == 1
    assert _w(tmp_path, "toml_bool_count", val) == 1


def test_toml_has_boolean_value(tmp_path):
    val = toml_has_boolean_value(_TOML)
    assert isinstance(val, bool) and val is True
    assert _w(tmp_path, "toml_has_boolean_value", val) is True


def test_toml_numeric_count(tmp_path):
    val = toml_numeric_count(_TOML)
    assert isinstance(val, int) and val == 0
    assert _w(tmp_path, "toml_numeric_count", val) == 0


def test_toml_string_count(tmp_path):
    val = toml_string_count(_TOML)
    assert isinstance(val, int) and val == 2
    assert _w(tmp_path, "toml_string_count", val) == 2


def test_batch_ndjson_export(tmp_path):
    records = [
        {"fmt": "pgm", "m": "pgm_gradient_magnitude", "v": pgm_gradient_magnitude(_PGM)},
        {"fmt": "gnumeric", "m": "gnumeric_fill_rate", "v": gnumeric_fill_rate(_GN)},
        {"fmt": "ods", "m": "ods_cell_type_count", "v": ods_cell_type_count(_ODS)},
        {"fmt": "xcf", "m": "xcf_width_height_sum", "v": xcf_width_height_sum(_XCF)},
        {"fmt": "toml", "m": "toml_bool_count", "v": toml_bool_count(_TOML)},
    ]
    out = tmp_path / "pgm_gn_ods_xcf_toml_batch.ndjson"
    write_ndjson(records, str(out))
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 5
    fmts = {json.loads(ln)["fmt"] for ln in lines}
    assert {"pgm", "gnumeric", "ods", "xcf", "toml"} == fmts
