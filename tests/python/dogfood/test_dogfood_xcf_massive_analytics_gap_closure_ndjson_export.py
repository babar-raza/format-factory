"""
tests/python/dogfood/test_dogfood_xcf_massive_analytics_gap_closure_ndjson_export.py

Sprint: dogfood-analytics-gap-closure-batch3-20260617
Dogfood export: XCF analytics -> NDJSON roundtrip.
Covers 100 previously-untested xcf_* analytics functions on 2x2-gray.xcf.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import (
    xcf_area_to_layer_ratio,
    xcf_aspect_ratio,
    xcf_aspect_ratio_string,
    xcf_average_dimension,
    xcf_average_layer_size,
    xcf_avg_layer_area,
    xcf_bytes_per_pixel,
    xcf_canvas_area,
    xcf_canvas_aspect_ratio,
    xcf_canvas_diagonal,
    xcf_canvas_fill_ratio,
    xcf_canvas_half_perimeter,
    xcf_canvas_perimeter,
    xcf_canvas_size_bytes,
    xcf_color_depth,
    xcf_color_mode_name,
    xcf_column_count,
    xcf_compression_ratio,
    xcf_diagonal,
    xcf_diagonal_length,
    xcf_dimension_product,
    xcf_dimension_ratio,
    xcf_dimension_sum,
    xcf_file_bytes_per_layer,
    xcf_file_header_overhead,
    xcf_file_size,
    xcf_file_size_bytes,
    xcf_file_size_kb,
    xcf_file_size_per_pixel,
    xcf_has_alpha,
    xcf_has_multiple_layers,
    xcf_has_single_layer,
    xcf_height,
    xcf_height_squared,
    xcf_height_to_layer_ratio,
    xcf_image_dimensions,
    xcf_image_type_code,
    xcf_image_type_name,
    xcf_is_color,
    xcf_is_grayscale,
    xcf_is_high_res,
    xcf_is_indexed,
    xcf_is_landscape,
    xcf_is_multi_layer,
    xcf_is_multi_pixel,
    xcf_is_portrait,
    xcf_is_rgb,
    xcf_is_single_layer,
    xcf_is_square,
    xcf_is_square_canvas,
    xcf_is_tall,
    xcf_is_tiny,
    xcf_is_wide,
    xcf_layer_area_sum,
    xcf_layer_area_variance,
    xcf_layer_count,
    xcf_layer_count_per_megapixel,
    xcf_layer_count_ratio,
    xcf_layer_count_squared,
    xcf_layer_density,
    xcf_layer_name_count,
    xcf_layer_name_list,
    xcf_layer_pixel_count,
    xcf_layer_size_variance,
    xcf_layer_to_canvas_ratio,
    xcf_layer_to_pixel_ratio,
    xcf_layer_width_sum,
    xcf_layers_per_dimension,
    xcf_layers_per_pixel,
    xcf_max_dimension,
    xcf_max_layer_area,
    xcf_max_layer_dimension,
    xcf_megapixel_count,
    xcf_megapixels,
    xcf_min_dimension,
    xcf_min_layer_area,
    xcf_min_layer_dimension,
    xcf_min_side_length,
    xcf_perimeter,
    xcf_pixel_count,
    xcf_pixel_count_per_layer,
    xcf_pixel_density,
    xcf_pixel_per_layer_avg,
    xcf_pixels_exceed_layers,
    xcf_row_count,
    xcf_summary,
    xcf_total_canvas_pixels,
    xcf_total_layer_area,
    xcf_total_layer_pixels,
    xcf_total_layers_area,
    xcf_total_pixel_count,
    xcf_total_pixels,
    xcf_version,
    xcf_version_number,
    xcf_width,
    xcf_width_height_sum,
    xcf_width_plus_height,
    xcf_width_squared,
    xcf_width_to_height_ratio,
    xcf_width_to_layer_ratio,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_S = str(_XCF_DIR / "2x2-gray.xcf")


class TestXcfMassiveAnalyticsGapClosureNdjsonExport:
    """100 XCF analytics functions -> NDJSON dogfood export on 2x2-gray.xcf."""

    # --- numeric analytics ---

    def test_area_to_layer_ratio(self):
        assert xcf_area_to_layer_ratio(_S) == 4.0

    def test_aspect_ratio(self):
        assert xcf_aspect_ratio(_S) == 1.0

    def test_aspect_ratio_string(self):
        assert xcf_aspect_ratio_string(_S) == "1:1"

    def test_average_dimension(self):
        assert xcf_average_dimension(_S) == 2.0

    def test_average_layer_size(self):
        assert xcf_average_layer_size(_S) == 4.0

    def test_avg_layer_area(self):
        assert xcf_avg_layer_area(_S) == 4.0

    def test_bytes_per_pixel(self):
        assert xcf_bytes_per_pixel(_S) == 44.5

    def test_canvas_area(self):
        assert xcf_canvas_area(_S) == 4

    def test_canvas_aspect_ratio(self):
        assert xcf_canvas_aspect_ratio(_S) == 1.0

    def test_canvas_diagonal(self):
        val = xcf_canvas_diagonal(_S)
        assert abs(val - 2.8284) < 0.001

    def test_canvas_fill_ratio(self):
        assert xcf_canvas_fill_ratio(_S) == 0.25

    def test_canvas_half_perimeter(self):
        assert xcf_canvas_half_perimeter(_S) == 4

    def test_canvas_perimeter(self):
        assert xcf_canvas_perimeter(_S) == 8

    def test_canvas_size_bytes(self):
        assert xcf_canvas_size_bytes(_S) == 8

    def test_color_depth(self):
        assert xcf_color_depth(_S) == 8

    def test_color_mode_name(self):
        assert xcf_color_mode_name(_S) == "Grayscale"

    def test_column_count(self):
        assert xcf_column_count(_S) == 2

    def test_compression_ratio(self):
        val = xcf_compression_ratio(_S)
        assert val > 0

    def test_diagonal(self):
        val = xcf_diagonal(_S)
        assert abs(val - 2.8284) < 0.001

    def test_diagonal_length(self):
        val = xcf_diagonal_length(_S)
        assert abs(val - 2.8284) < 0.001

    def test_dimension_product(self):
        assert xcf_dimension_product(_S) == 4

    def test_dimension_ratio(self):
        assert xcf_dimension_ratio(_S) == 1.0

    def test_dimension_sum(self):
        assert xcf_dimension_sum(_S) == 4

    def test_file_bytes_per_layer(self):
        assert xcf_file_bytes_per_layer(_S) == 178.0

    def test_file_header_overhead(self):
        assert xcf_file_header_overhead(_S) == 174

    def test_file_size(self):
        assert xcf_file_size(_S) == 178

    def test_file_size_bytes(self):
        assert xcf_file_size_bytes(_S) == 178

    def test_file_size_kb(self):
        val = xcf_file_size_kb(_S)
        assert abs(val - 0.1738) < 0.001

    def test_file_size_per_pixel(self):
        assert xcf_file_size_per_pixel(_S) == 44.5

    def test_height(self):
        assert xcf_height(_S) == 2

    def test_height_squared(self):
        assert xcf_height_squared(_S) == 4

    def test_height_to_layer_ratio(self):
        assert xcf_height_to_layer_ratio(_S) == 2.0

    def test_image_dimensions(self):
        dims = xcf_image_dimensions(_S)
        assert dims["width"] == 2
        assert dims["height"] == 2

    def test_image_type_code(self):
        assert xcf_image_type_code(_S) == 1

    def test_image_type_name(self):
        assert xcf_image_type_name(_S) == "Grayscale"

    def test_layer_area_sum(self):
        assert xcf_layer_area_sum(_S) == 4

    def test_layer_area_variance(self):
        assert xcf_layer_area_variance(_S) == 0.0

    def test_layer_count(self):
        assert xcf_layer_count(_S) == 1

    def test_layer_count_per_megapixel(self):
        assert xcf_layer_count_per_megapixel(_S) == 250000.0

    def test_layer_count_ratio(self):
        assert xcf_layer_count_ratio(_S) == 0.25

    def test_layer_count_squared(self):
        assert xcf_layer_count_squared(_S) == 1

    def test_layer_density(self):
        assert xcf_layer_density(_S) == 250000.0

    def test_layer_name_count(self):
        assert xcf_layer_name_count(_S) == 1

    def test_layer_name_list(self):
        names = xcf_layer_name_list(_S)
        assert "Layer 0" in names

    def test_layer_pixel_count(self):
        assert xcf_layer_pixel_count(_S) == 4

    def test_layer_size_variance(self):
        assert xcf_layer_size_variance(_S) == 0.0

    def test_layer_to_canvas_ratio(self):
        assert xcf_layer_to_canvas_ratio(_S) == 250000.0

    def test_layer_to_pixel_ratio(self):
        assert xcf_layer_to_pixel_ratio(_S) == 0.25

    def test_layer_width_sum(self):
        assert xcf_layer_width_sum(_S) == 2

    def test_layers_per_dimension(self):
        assert xcf_layers_per_dimension(_S) == 0.5

    def test_layers_per_pixel(self):
        assert xcf_layers_per_pixel(_S) == 0.25

    def test_max_dimension(self):
        assert xcf_max_dimension(_S) == 2

    def test_max_layer_area(self):
        assert xcf_max_layer_area(_S) == 4

    def test_max_layer_dimension(self):
        assert xcf_max_layer_dimension(_S) == 2

    def test_megapixel_count(self):
        val = xcf_megapixel_count(_S)
        assert val < 0.001  # 4 pixels

    def test_megapixels(self):
        val = xcf_megapixels(_S)
        assert val < 0.001

    def test_min_dimension(self):
        assert xcf_min_dimension(_S) == 2

    def test_min_layer_area(self):
        assert xcf_min_layer_area(_S) == 4

    def test_min_layer_dimension(self):
        assert xcf_min_layer_dimension(_S) == 2

    def test_min_side_length(self):
        assert xcf_min_side_length(_S) == 2

    def test_perimeter(self):
        assert xcf_perimeter(_S) == 8

    def test_pixel_count(self):
        assert xcf_pixel_count(_S) == 4

    def test_pixel_count_per_layer(self):
        assert xcf_pixel_count_per_layer(_S) == 4.0

    def test_pixel_density(self):
        val = xcf_pixel_density(_S)
        assert val > 0

    def test_pixel_per_layer_avg(self):
        assert xcf_pixel_per_layer_avg(_S) == 4.0

    def test_row_count(self):
        assert xcf_row_count(_S) == 2

    def test_summary(self):
        s = xcf_summary(_S)
        assert s["width"] == 2
        assert s["height"] == 2
        assert s["image_type_name"] == "Grayscale"
        assert s["num_layers"] == 1

    def test_total_canvas_pixels(self):
        assert xcf_total_canvas_pixels(_S) == 4

    def test_total_layer_area(self):
        assert xcf_total_layer_area(_S) == 4

    def test_total_layer_pixels(self):
        assert xcf_total_layer_pixels(_S) == 4

    def test_total_layers_area(self):
        assert xcf_total_layers_area(_S) == 4

    def test_total_pixel_count(self):
        assert xcf_total_pixel_count(_S) == 4

    def test_total_pixels(self):
        assert xcf_total_pixels(_S) == 4

    def test_version(self):
        assert xcf_version(_S) == "v011"

    def test_version_number(self):
        assert xcf_version_number(_S) == 11

    def test_width(self):
        assert xcf_width(_S) == 2

    def test_width_height_sum(self):
        assert xcf_width_height_sum(_S) == 4

    def test_width_plus_height(self):
        assert xcf_width_plus_height(_S) == 4

    def test_width_squared(self):
        assert xcf_width_squared(_S) == 4

    def test_width_to_height_ratio(self):
        assert xcf_width_to_height_ratio(_S) == 1.0

    def test_width_to_layer_ratio(self):
        assert xcf_width_to_layer_ratio(_S) == 2.0

    # --- boolean analytics ---

    def test_has_alpha_false(self):
        assert xcf_has_alpha(_S) is False

    def test_has_multiple_layers_false(self):
        assert xcf_has_multiple_layers(_S) is False

    def test_has_single_layer_true(self):
        assert xcf_has_single_layer(_S) is True

    def test_is_color_false(self):
        assert xcf_is_color(_S) is False

    def test_is_grayscale_true(self):
        assert xcf_is_grayscale(_S) is True

    def test_is_high_res_false(self):
        assert xcf_is_high_res(_S) is False

    def test_is_indexed_false(self):
        assert xcf_is_indexed(_S) is False

    def test_is_landscape_false(self):
        assert xcf_is_landscape(_S) is False

    def test_is_multi_layer_false(self):
        assert xcf_is_multi_layer(_S) is False

    def test_is_multi_pixel_true(self):
        assert xcf_is_multi_pixel(_S) is True

    def test_is_portrait_false(self):
        assert xcf_is_portrait(_S) is False

    def test_is_rgb_false(self):
        assert xcf_is_rgb(_S) is False

    def test_is_single_layer_true(self):
        assert xcf_is_single_layer(_S) is True

    def test_is_square_true(self):
        assert xcf_is_square(_S) is True

    def test_is_square_canvas_true(self):
        assert xcf_is_square_canvas(_S) is True

    def test_is_tall_false(self):
        assert xcf_is_tall(_S) is False

    def test_is_tiny_true(self):
        assert xcf_is_tiny(_S) is True

    def test_is_wide_false(self):
        assert xcf_is_wide(_S) is False

    def test_pixels_exceed_layers_true(self):
        assert xcf_pixels_exceed_layers(_S) is True

    # --- NDJSON roundtrip ---

    def test_ndjson_roundtrip(self, tmp_path):
        out = tmp_path / "xcf_analytics.ndjson"
        records = [
            {"fn": "pixel_count", "value": xcf_pixel_count(_S)},
            {"fn": "layer_count", "value": xcf_layer_count(_S)},
            {"fn": "canvas_area", "value": xcf_canvas_area(_S)},
            {"fn": "file_size", "value": xcf_file_size(_S)},
            {"fn": "color_mode_name", "value": xcf_color_mode_name(_S)},
        ]
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 5
        assert loaded[0]["value"] == 4
        assert loaded[1]["value"] == 1
        assert loaded[2]["value"] == 4
        assert loaded[3]["value"] == 178
        assert loaded[4]["value"] == "Grayscale"
