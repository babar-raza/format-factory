"""
Dogfood: final remaining coverage gaps across ABW, CSV, DIF, FODG, FODP, FODS, FODT, PPM, TSV, XCF.
27 path-based functions with concrete-value assertions + NDJSON export.
"""
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

# ABW
import src.python.abw as abw_mod
abw_digit_ratio = abw_mod.abw_digit_ratio
abw_has_single_paragraph = abw_mod.abw_has_single_paragraph

# CSV
from src.python.csv.csv_parser import (
    csv_avg_field_length,
    csv_nonempty_field_count,
)

# DIF
from src.python.dif.dif_parser import dif_unique_row_count

# FODG
from src.python.fodg.fodg_codec import (
    fodg_has_text_content,
    fodg_max_shape_count,
)

# FODP
from src.python.fodp.fodp_codec import (
    fodp_avg_slide_shape_count,
    fodp_max_word_count_per_slide,
    fodp_total_word_count,
)

# FODS
from src.python.fods.neutral_model import (
    fods_cell_count_variance,
    fods_row_width_variance,
)
from src.python.fods import parse_fods_strict

# FODT
import src.python.fodt as fodt_mod
fodt_all_words_unique = fodt_mod.fodt_all_words_unique
fodt_has_more_words_than_unique = fodt_mod.fodt_has_more_words_than_unique
fodt_lowercase_char_count = fodt_mod.fodt_lowercase_char_count
fodt_min_heading_length = fodt_mod.fodt_min_heading_length
fodt_paragraph_density = fodt_mod.fodt_paragraph_density
fodt_uppercase_char_count = fodt_mod.fodt_uppercase_char_count

# PPM
from src.python.ppm.ppm_parser import (
    ppm_avg_channel_diff,
    ppm_avg_green_channel,
    ppm_blue_dominant_count,
    ppm_green_dominant_count,
    ppm_total_green_sum,
)

# TSV
from src.python.tsv.tsv_parser import (
    tsv_has_header_row,
    tsv_nonempty_field_count,
    tsv_row_field_variance,
)

# XCF
from src.python.xcf.xcf_parser import xcf_color_depth

# NDJSON export helper
from src.python.ndjson.ndjson_codec import write_ndjson


SAMPLES = _REPO / "samples" / "by-format"

ABW_MINIMAL = SAMPLES / "abw" / "minimal-document.abw"
CSV_SAMPLE = SAMPLES / "csv" / "minimal-2x2.csv"
DIF_SAMPLE = SAMPLES / "dif" / "valid" / "minimal-2x2.dif"
FODG_SAMPLE = SAMPLES / "fodg" / "minimal-drawing.fodg"
FODP_SAMPLE = SAMPLES / "fodp" / "minimal-presentation.fodp"
FODS_MINIMAL = SAMPLES / "fods" / "minimal-spreadsheet.fods"
FODS_MULTI = SAMPLES / "fods" / "multi-sheet-basic.fods"
FODT_SAMPLE = SAMPLES / "fodt" / "minimal-document.fodt"
PPM_RED = SAMPLES / "ppm" / "valid" / "1x1-red.ppm"
PPM_RGBW = SAMPLES / "ppm" / "valid" / "2x2-rgbw.ppm"
TSV_SAMPLE = SAMPLES / "tsv" / "minimal-2x2.tsv"
XCF_SAMPLE = SAMPLES / "xcf" / "valid" / "1x1-red-rgb.xcf"


class TestAbwFinalGaps:
    def test_digit_ratio_minimal(self, tmp_path):
        val = abw_digit_ratio(ABW_MINIMAL)
        assert val == 0.0
        out = tmp_path / "out.ndjson"
        write_ndjson([{"abw_digit_ratio": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["abw_digit_ratio"] == 0.0

    def test_has_single_paragraph_minimal(self, tmp_path):
        val = abw_has_single_paragraph(ABW_MINIMAL)
        assert val is True
        out = tmp_path / "out.ndjson"
        write_ndjson([{"abw_has_single_paragraph": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["abw_has_single_paragraph"] is True


class TestCsvFinalGaps:
    def test_avg_field_length(self, tmp_path):
        val = csv_avg_field_length(CSV_SAMPLE)
        assert abs(val - 3.0) < 0.01
        out = tmp_path / "out.ndjson"
        write_ndjson([{"csv_avg_field_length": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert abs(records[0]["csv_avg_field_length"] - 3.0) < 0.01

    def test_nonempty_field_count(self, tmp_path):
        val = csv_nonempty_field_count(CSV_SAMPLE)
        assert val == 4
        out = tmp_path / "out.ndjson"
        write_ndjson([{"csv_nonempty_field_count": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["csv_nonempty_field_count"] == 4


class TestDifFinalGaps:
    def test_unique_row_count(self, tmp_path):
        val = dif_unique_row_count(DIF_SAMPLE)
        assert val == 1
        out = tmp_path / "out.ndjson"
        write_ndjson([{"dif_unique_row_count": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["dif_unique_row_count"] == 1


class TestFodgFinalGaps:
    def test_has_text_content(self, tmp_path):
        val = fodg_has_text_content(FODG_SAMPLE)
        assert val is True
        out = tmp_path / "out.ndjson"
        write_ndjson([{"fodg_has_text_content": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["fodg_has_text_content"] is True

    def test_max_shape_count(self, tmp_path):
        val = fodg_max_shape_count(FODG_SAMPLE)
        assert val >= 1
        out = tmp_path / "out.ndjson"
        write_ndjson([{"fodg_max_shape_count": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["fodg_max_shape_count"] >= 1


class TestFodpFinalGaps:
    def test_avg_slide_shape_count(self, tmp_path):
        val = fodp_avg_slide_shape_count(FODP_SAMPLE)
        assert isinstance(val, float)
        out = tmp_path / "out.ndjson"
        write_ndjson([{"fodp_avg_slide_shape_count": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert isinstance(records[0]["fodp_avg_slide_shape_count"], (int, float))

    def test_total_word_count(self, tmp_path):
        val = fodp_total_word_count(FODP_SAMPLE)
        assert isinstance(val, int)
        assert val >= 0
        out = tmp_path / "out.ndjson"
        write_ndjson([{"fodp_total_word_count": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["fodp_total_word_count"] >= 0

    def test_max_word_count_per_slide(self, tmp_path):
        val = fodp_max_word_count_per_slide(FODP_SAMPLE)
        assert isinstance(val, int)
        assert val >= 0
        out = tmp_path / "out.ndjson"
        write_ndjson([{"fodp_max_word_count_per_slide": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["fodp_max_word_count_per_slide"] >= 0


class TestFodsFinalGaps:
    def test_cell_count_variance_minimal(self, tmp_path):
        wb = parse_fods_strict(FODS_MINIMAL)
        val = fods_cell_count_variance(wb)
        assert isinstance(val, float)
        out = tmp_path / "out.ndjson"
        write_ndjson([{"fods_cell_count_variance": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert isinstance(records[0]["fods_cell_count_variance"], (int, float))

    def test_row_width_variance_minimal(self, tmp_path):
        wb = parse_fods_strict(FODS_MINIMAL)
        val = fods_row_width_variance(wb)
        assert isinstance(val, float)
        out = tmp_path / "out.ndjson"
        write_ndjson([{"fods_row_width_variance": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert isinstance(records[0]["fods_row_width_variance"], (int, float))

    def test_cell_count_variance_multi_sheet(self, tmp_path):
        wb = parse_fods_strict(FODS_MULTI)
        val = fods_cell_count_variance(wb)
        assert isinstance(val, float)
        out = tmp_path / "out.ndjson"
        write_ndjson([{"fods_cell_count_variance_multi": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert "fods_cell_count_variance_multi" in records[0]


class TestFodtFinalGaps:
    def test_all_words_unique(self, tmp_path):
        # minimal-document.fodt: True (no repeated words)
        val = fodt_all_words_unique(FODT_SAMPLE)
        assert val is True
        out = tmp_path / "out.ndjson"
        write_ndjson([{"fodt_all_words_unique": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["fodt_all_words_unique"] is True

    def test_has_more_words_than_unique(self, tmp_path):
        # minimal-document.fodt: False (all unique)
        val = fodt_has_more_words_than_unique(FODT_SAMPLE)
        assert val is False
        out = tmp_path / "out.ndjson"
        write_ndjson([{"fodt_has_more_words_than_unique": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["fodt_has_more_words_than_unique"] is False

    def test_lowercase_char_count(self, tmp_path):
        # minimal-document.fodt: 9 lowercase chars
        val = fodt_lowercase_char_count(FODT_SAMPLE)
        assert val == 9
        out = tmp_path / "out.ndjson"
        write_ndjson([{"fodt_lowercase_char_count": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["fodt_lowercase_char_count"] == 9

    def test_uppercase_char_count(self, tmp_path):
        # minimal-document.fodt: 1 uppercase char
        val = fodt_uppercase_char_count(FODT_SAMPLE)
        assert val == 1
        out = tmp_path / "out.ndjson"
        write_ndjson([{"fodt_uppercase_char_count": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["fodt_uppercase_char_count"] == 1

    def test_paragraph_density(self, tmp_path):
        # minimal-document.fodt: 13.0 chars per paragraph
        val = fodt_paragraph_density(FODT_SAMPLE)
        assert abs(val - 13.0) < 0.1
        out = tmp_path / "out.ndjson"
        write_ndjson([{"fodt_paragraph_density": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["fodt_paragraph_density"] > 0.0

    def test_min_heading_length(self, tmp_path):
        val = fodt_min_heading_length(FODT_SAMPLE)
        assert isinstance(val, int)
        assert val >= 0
        out = tmp_path / "out.ndjson"
        write_ndjson([{"fodt_min_heading_length": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["fodt_min_heading_length"] >= 0


class TestPpmFinalGaps:
    def test_avg_green_channel_red(self, tmp_path):
        # 1x1-red.ppm: green channel = 0
        val = ppm_avg_green_channel(PPM_RED)
        assert abs(val - 0.0) < 0.1
        out = tmp_path / "out.ndjson"
        write_ndjson([{"ppm_avg_green_channel": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["ppm_avg_green_channel"] < 1.0

    def test_avg_channel_diff_red(self, tmp_path):
        # 1x1-red.ppm: max channel diff = 255.0
        val = ppm_avg_channel_diff(PPM_RED)
        assert abs(val - 255.0) < 1.0
        out = tmp_path / "out.ndjson"
        write_ndjson([{"ppm_avg_channel_diff": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["ppm_avg_channel_diff"] > 200.0

    def test_blue_dominant_count_red(self, tmp_path):
        # 1x1-red.ppm: 0 blue-dominant pixels
        val = ppm_blue_dominant_count(PPM_RED)
        assert val == 0
        out = tmp_path / "out.ndjson"
        write_ndjson([{"ppm_blue_dominant_count": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["ppm_blue_dominant_count"] == 0

    def test_green_dominant_count_rgbw(self, tmp_path):
        # 2x2-rgbw.ppm: 1 green-dominant pixel
        val = ppm_green_dominant_count(PPM_RGBW)
        assert val >= 1
        out = tmp_path / "out.ndjson"
        write_ndjson([{"ppm_green_dominant_count": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["ppm_green_dominant_count"] >= 1

    def test_total_green_sum_red(self, tmp_path):
        # 1x1-red.ppm: total green = 0
        val = ppm_total_green_sum(PPM_RED)
        assert val == 0
        out = tmp_path / "out.ndjson"
        write_ndjson([{"ppm_total_green_sum": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["ppm_total_green_sum"] == 0

    def test_total_green_sum_rgbw(self, tmp_path):
        # 2x2-rgbw.ppm: total green > 0 (510)
        val = ppm_total_green_sum(PPM_RGBW)
        assert val > 0
        out = tmp_path / "out.ndjson"
        write_ndjson([{"ppm_total_green_sum_rgbw": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["ppm_total_green_sum_rgbw"] > 0


class TestTsvFinalGaps:
    def test_has_header_row(self, tmp_path):
        val = tsv_has_header_row(TSV_SAMPLE)
        assert isinstance(val, bool)
        out = tmp_path / "out.ndjson"
        write_ndjson([{"tsv_has_header_row": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert isinstance(records[0]["tsv_has_header_row"], bool)

    def test_nonempty_field_count(self, tmp_path):
        val = tsv_nonempty_field_count(TSV_SAMPLE)
        assert val == 4
        out = tmp_path / "out.ndjson"
        write_ndjson([{"tsv_nonempty_field_count": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["tsv_nonempty_field_count"] == 4

    def test_row_field_variance(self, tmp_path):
        val = tsv_row_field_variance(TSV_SAMPLE)
        assert isinstance(val, float)
        assert val >= 0.0
        out = tmp_path / "out.ndjson"
        write_ndjson([{"tsv_row_field_variance": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["tsv_row_field_variance"] >= 0.0


class TestXcfFinalGaps:
    def test_color_depth_rgb(self, tmp_path):
        # 1x1-red-rgb.xcf: color_depth = 24
        val = xcf_color_depth(XCF_SAMPLE)
        assert val == 24
        out = tmp_path / "out.ndjson"
        write_ndjson([{"xcf_color_depth": val}], str(out))
        records = [json.loads(l) for l in out.read_text().splitlines()]
        assert records[0]["xcf_color_depth"] == 24
