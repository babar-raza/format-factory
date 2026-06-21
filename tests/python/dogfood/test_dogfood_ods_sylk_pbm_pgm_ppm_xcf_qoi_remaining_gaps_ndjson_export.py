"""Dogfood export: ODS(6) + SYLK(3) + PBM(2) + PGM(3) + PPM(4) + XCF(4) + QOI(4) → NDJSON.

Functions covered (previously uncovered):
  ODS:   ods_avg_row_length, ods_file_size_bytes, ods_is_single_cell,
         ods_nonempty_cell_count, ods_string_cell_ratio, ods_total_row_count
  SYLK:  sylk_avg_numeric_value, sylk_avg_string_length, sylk_cell_fill_ratio
  PBM:   pbm_aspect_ratio, pbm_border_white_count
  PGM:   pgm_aspect_ratio, pgm_center_brightness, pgm_is_multi_row
  PPM:   ppm_aspect_ratio, ppm_channel_range_sum, ppm_grayscale_pixel_count,
         ppm_has_multi_channel_pixels
  XCF:   xcf_aspect_ratio, xcf_diagonal, xcf_is_color, xcf_is_grayscale
  QOI:   qoi_aspect_ratio, qoi_avg_rgb_per_pixel, qoi_black_pixel_count, qoi_blue_mean_value
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import write_ndjson
from ods.ods_parser import (
    ods_avg_row_length,
    ods_file_size_bytes,
    ods_is_single_cell,
    ods_nonempty_cell_count,
    ods_string_cell_ratio,
    ods_total_row_count,
)
from pbm.pbm_parser import pbm_aspect_ratio, pbm_border_white_count
from pgm.pgm_parser import pgm_aspect_ratio, pgm_center_brightness, pgm_is_multi_row
from ppm.ppm_parser import (
    ppm_aspect_ratio,
    ppm_channel_range_sum,
    ppm_grayscale_pixel_count,
    ppm_has_multi_channel_pixels,
)
from qoi.qoi_parser import (
    qoi_aspect_ratio,
    qoi_avg_rgb_per_pixel,
    qoi_black_pixel_count,
    qoi_blue_mean_value,
)
from sylk.sylk_parser import sylk_avg_numeric_value, sylk_avg_string_length, sylk_cell_fill_ratio
from xcf.xcf_parser import xcf_aspect_ratio, xcf_diagonal, xcf_is_color, xcf_is_grayscale

_ODS = str(_REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods")
_SYLK = str(_REPO / "samples" / "by-format" / "sylk" / "valid" / "numeric-row.slk")
_PBM = str(_REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm")
_PGM = str(_REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm")
_PPM = str(_REPO / "samples" / "by-format" / "ppm" / "valid" / "1x1-red.ppm")
_XCF = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_QOI = str(_REPO / "samples" / "by-format" / "qoi" / "valid" / "1x1-red.qoi")


# --- ODS tests ---

def test_ods_avg_row_length(tmp_path):
    val = ods_avg_row_length(_ODS)
    assert isinstance(val, float)
    assert val == 2.0
    out = tmp_path / "ods_avg_row_length.ndjson"
    write_ndjson([{"metric": "ods_avg_row_length", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2.0


def test_ods_file_size_bytes(tmp_path):
    val = ods_file_size_bytes(_ODS)
    assert isinstance(val, int)
    assert val == 1338
    out = tmp_path / "ods_file_size_bytes.ndjson"
    write_ndjson([{"metric": "ods_file_size_bytes", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1338


def test_ods_is_single_cell(tmp_path):
    val = ods_is_single_cell(_ODS)
    assert isinstance(val, bool)
    assert val is False
    out = tmp_path / "ods_is_single_cell.ndjson"
    write_ndjson([{"metric": "ods_is_single_cell", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] is False


def test_ods_nonempty_cell_count(tmp_path):
    val = ods_nonempty_cell_count(_ODS)
    assert isinstance(val, int)
    assert val == 4
    out = tmp_path / "ods_nonempty_cell_count.ndjson"
    write_ndjson([{"metric": "ods_nonempty_cell_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 4


def test_ods_string_cell_ratio(tmp_path):
    val = ods_string_cell_ratio(_ODS)
    assert isinstance(val, float)
    assert val == 0.75
    out = tmp_path / "ods_string_cell_ratio.ndjson"
    write_ndjson([{"metric": "ods_string_cell_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.75


def test_ods_total_row_count(tmp_path):
    val = ods_total_row_count(_ODS)
    assert isinstance(val, int)
    assert val == 2
    out = tmp_path / "ods_total_row_count.ndjson"
    write_ndjson([{"metric": "ods_total_row_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2


# --- SYLK tests ---

def test_sylk_avg_numeric_value(tmp_path):
    val = sylk_avg_numeric_value(_SYLK)
    assert isinstance(val, float)
    assert val == 2.0
    out = tmp_path / "sylk_avg_numeric_value.ndjson"
    write_ndjson([{"metric": "sylk_avg_numeric_value", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2.0


def test_sylk_avg_string_length(tmp_path):
    val = sylk_avg_string_length(_SYLK)
    assert isinstance(val, float)
    assert val == 0.0
    out = tmp_path / "sylk_avg_string_length.ndjson"
    write_ndjson([{"metric": "sylk_avg_string_length", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.0


def test_sylk_cell_fill_ratio(tmp_path):
    val = sylk_cell_fill_ratio(_SYLK)
    assert isinstance(val, float)
    assert val == 1.0
    out = tmp_path / "sylk_cell_fill_ratio.ndjson"
    write_ndjson([{"metric": "sylk_cell_fill_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1.0


# --- PBM tests ---

def test_pbm_aspect_ratio(tmp_path):
    val = pbm_aspect_ratio(_PBM)
    assert isinstance(val, float)
    assert val == 1.0
    out = tmp_path / "pbm_aspect_ratio.ndjson"
    write_ndjson([{"metric": "pbm_aspect_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1.0


def test_pbm_border_white_count(tmp_path):
    val = pbm_border_white_count(_PBM)
    assert isinstance(val, int)
    assert val == 2
    out = tmp_path / "pbm_border_white_count.ndjson"
    write_ndjson([{"metric": "pbm_border_white_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2


# --- PGM tests ---

def test_pgm_aspect_ratio(tmp_path):
    val = pgm_aspect_ratio(_PGM)
    assert isinstance(val, float)
    assert val == 1.0
    out = tmp_path / "pgm_aspect_ratio.ndjson"
    write_ndjson([{"metric": "pgm_aspect_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1.0


def test_pgm_center_brightness(tmp_path):
    val = pgm_center_brightness(_PGM)
    assert isinstance(val, float)
    assert val == 0.0
    out = tmp_path / "pgm_center_brightness.ndjson"
    write_ndjson([{"metric": "pgm_center_brightness", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.0


def test_pgm_is_multi_row(tmp_path):
    val = pgm_is_multi_row(_PGM)
    assert isinstance(val, bool)
    assert val is True
    out = tmp_path / "pgm_is_multi_row.ndjson"
    write_ndjson([{"metric": "pgm_is_multi_row", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] is True


# --- PPM tests ---

def test_ppm_aspect_ratio(tmp_path):
    val = ppm_aspect_ratio(_PPM)
    assert isinstance(val, float)
    assert val == 1.0
    out = tmp_path / "ppm_aspect_ratio.ndjson"
    write_ndjson([{"metric": "ppm_aspect_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1.0


def test_ppm_channel_range_sum(tmp_path):
    val = ppm_channel_range_sum(_PPM)
    assert isinstance(val, int)
    assert val >= 0
    out = tmp_path / "ppm_channel_range_sum.ndjson"
    write_ndjson([{"metric": "ppm_channel_range_sum", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] >= 0


def test_ppm_grayscale_pixel_count(tmp_path):
    val = ppm_grayscale_pixel_count(_PPM)
    assert isinstance(val, int)
    assert val == 0
    out = tmp_path / "ppm_grayscale_pixel_count.ndjson"
    write_ndjson([{"metric": "ppm_grayscale_pixel_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0


def test_ppm_has_multi_channel_pixels(tmp_path):
    val = ppm_has_multi_channel_pixels(_PPM)
    assert isinstance(val, bool)
    out = tmp_path / "ppm_has_multi_channel_pixels.ndjson"
    write_ndjson([{"metric": "ppm_has_multi_channel_pixels", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == val


# --- XCF tests ---

def test_xcf_aspect_ratio(tmp_path):
    val = xcf_aspect_ratio(_XCF)
    assert isinstance(val, float)
    assert val == 1.0
    out = tmp_path / "xcf_aspect_ratio.ndjson"
    write_ndjson([{"metric": "xcf_aspect_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1.0


def test_xcf_diagonal(tmp_path):
    val = xcf_diagonal(_XCF)
    assert isinstance(val, float)
    assert abs(val - math.sqrt(2)) < 1e-9
    out = tmp_path / "xcf_diagonal.ndjson"
    write_ndjson([{"metric": "xcf_diagonal", "value": val}], str(out))
    assert abs(json.loads(out.read_text().strip())["value"] - math.sqrt(2)) < 1e-9


def test_xcf_is_color(tmp_path):
    val = xcf_is_color(_XCF)
    assert isinstance(val, bool)
    assert val is True
    out = tmp_path / "xcf_is_color.ndjson"
    write_ndjson([{"metric": "xcf_is_color", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] is True


def test_xcf_is_grayscale(tmp_path):
    val = xcf_is_grayscale(_XCF)
    assert isinstance(val, bool)
    assert val is False
    out = tmp_path / "xcf_is_grayscale.ndjson"
    write_ndjson([{"metric": "xcf_is_grayscale", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] is False


# --- QOI tests ---

def test_qoi_aspect_ratio(tmp_path):
    val = qoi_aspect_ratio(_QOI)
    assert isinstance(val, float)
    assert val == 1.0
    out = tmp_path / "qoi_aspect_ratio.ndjson"
    write_ndjson([{"metric": "qoi_aspect_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1.0


def test_qoi_avg_rgb_per_pixel(tmp_path):
    val = qoi_avg_rgb_per_pixel(_QOI)
    assert isinstance(val, float)
    assert val == 255.0
    out = tmp_path / "qoi_avg_rgb_per_pixel.ndjson"
    write_ndjson([{"metric": "qoi_avg_rgb_per_pixel", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 255.0


def test_qoi_black_pixel_count(tmp_path):
    val = qoi_black_pixel_count(_QOI)
    assert isinstance(val, int)
    assert val == 0
    out = tmp_path / "qoi_black_pixel_count.ndjson"
    write_ndjson([{"metric": "qoi_black_pixel_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0


def test_qoi_blue_mean_value(tmp_path):
    val = qoi_blue_mean_value(_QOI)
    assert isinstance(val, float)
    assert val == 0.0
    out = tmp_path / "qoi_blue_mean_value.ndjson"
    write_ndjson([{"metric": "qoi_blue_mean_value", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.0


def test_all_formats_batch_ndjson_export(tmp_path):
    records = [
        {"fmt": "ods", "metric": "ods_avg_row_length", "value": ods_avg_row_length(_ODS)},
        {"fmt": "ods", "metric": "ods_nonempty_cell_count", "value": ods_nonempty_cell_count(_ODS)},
        {"fmt": "sylk", "metric": "sylk_avg_numeric_value", "value": sylk_avg_numeric_value(_SYLK)},
        {"fmt": "pbm", "metric": "pbm_aspect_ratio", "value": pbm_aspect_ratio(_PBM)},
        {"fmt": "pgm", "metric": "pgm_is_multi_row", "value": pgm_is_multi_row(_PGM)},
        {"fmt": "xcf", "metric": "xcf_is_color", "value": xcf_is_color(_XCF)},
        {"fmt": "qoi", "metric": "qoi_avg_rgb_per_pixel", "value": qoi_avg_rgb_per_pixel(_QOI)},
    ]
    out = tmp_path / "multi_format_gaps_batch.ndjson"
    write_ndjson(records, str(out))
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 7
    parsed = [json.loads(ln) for ln in lines]
    fmts = {r["fmt"] for r in parsed}
    assert "ods" in fmts
    assert "sylk" in fmts
    assert "qoi" in fmts
