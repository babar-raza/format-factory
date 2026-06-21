"""
XCF FOSS gap closure tests.

Closes:
  GAP-XCF-FOSS-XCF_IS_MULTI-001   — xcf_is_multi_pixel
  GAP-XCF-FOSS-XCF_FILE_BYT-001   — xcf_file_bytes_per_layer
  GAP-XCF-FOSS-XCF_COLOR_MO-001   — xcf_color_mode_name
  GAP-XCF-FOSS-XCF_LAYER_SI-001   — xcf_layer_size_variance
  GAP-XCF-FOSS-XCF_TOTAL_PI-001   — xcf_total_pixels
  GAP-XCF-FOSS-XCF_FILE_HEA-001   — xcf_file_header_overhead
  GAP-XCF-FOSS-XCF_VERSION_-001   — xcf_version_number
  GAP-XCF-FOSS-XCF_IS_HIGH_-001   — xcf_is_high_res
  GAP-XCF-FOSS-XCF_MEGAPIXE-001   — xcf_megapixel_count
  GAP-XCF-FOSS-XCF_IS_SQUAR-001   — xcf_is_square_canvas
  GAP-XCF-FOSS-XCF_WIDTH_TO-001   — xcf_width_to_height_ratio
  GAP-XCF-FOSS-XCF_HAS_SING-001   — xcf_has_single_layer
  GAP-XCF-FOSS-XCF_ASPECT_R-001   — xcf_aspect_ratio_string
  GAP-XCF-FOSS-XCF_LAYER_WI-001   — xcf_layer_width_sum
  GAP-XCF-FOSS-XCF_TOTAL_CA-001   — xcf_total_canvas_pixels
  GAP-XCF-FOSS-XCF_HEIGHT_S-001   — xcf_height_squared
  GAP-XCF-FOSS-XCF_MAX_SIDE-001   — xcf_max_side_length
  GAP-XCF-FOSS-XCF_AREA_TO_-001   — xcf_area_to_layer_ratio
  GAP-XCF-FOSS-XCF_MIN_SIDE-001   — xcf_min_side_length
  GAP-XCF-FOSS-XCF_CANVAS_H-001   — xcf_canvas_half_perimeter
  GAP-XCF-FOSS-XCF_WIDTH_HE-001   — xcf_width_height_sum
  GAP-XCF-FOSS-XCF_CANVAS_D-001   — xcf_canvas_diagonal
  GAP-XCF-FOSS-XCF_WIDTH_SQ-001   — xcf_width_squared
  GAP-XCF-FOSS-XCF_LAYER_NA-001   — xcf_layer_name_list
  GAP-XCF-FOSS-XCF_COLOR_DE-001   — xcf_color_depth
  GAP-XCF-FOSS-XCF_WIDTH_PL-001   — xcf_width_plus_height
  GAP-XCF-FOSS-XCF_LAYER_PI-001   — xcf_layer_pixel_count
  GAP-XCF-FOSS-XCF_IS_COLOR-001   — xcf_is_color
  GAP-XCF-FOSS-XCF_PIXELS_E-001   — xcf_pixels_exceed_layers
  GAP-XCF-FOSS-XCF_CANVAS_F-001   — xcf_canvas_fill_ratio
  GAP-XCF-FOSS-XCF_IS_TINY-001    — xcf_is_tiny
  GAP-XCF-FOSS-XCF_AVG_LAYE-001   — xcf_avg_layer_area
  GAP-XCF-FOSS-XCF_HEIGHT_T-001   — xcf_height_to_layer_ratio
  GAP-XCF-FOSS-XCF_NUM_LAYE-001   — xcf_num_layers_plus_image_type_id
  GAP-XCF-FOSS-XCF_WIDTH_TI-001   — xcf_width_times_file_size
  GAP-XCF-FOSS-XCF_WIDTH_PE-001   — xcf_width_per_layer
  GAP-XCF-FOSS-XCF_HEIGHT_P-001   — xcf_height_plus_num_layers
  GAP-XCF-FOSS-XCF_PIXEL_CO-001   — xcf_pixel_count_times_two
  GAP-XCF-FOSS-XCF_BYTES_PE-001   — xcf_bytes_per_layer
  GAP-XCF-FOSS-XCF_PIXEL_AR-001   — xcf_pixel_area
  GAP-XCF-FOSS-XCF_WH_TIMES-001   — xcf_wh_times_400_plus_image_type_times_300_plus_file_size_mod_31_times_100
  GAP-XCF-FOSS-XCF_AREA_PLU-001   — xcf_area_plus_file_size
  GAP-XCF-FOSS-XCF_LAYERS_T-001   — xcf_layers_times_width

Run from repo root:
    python -m pytest tests/python/xcf/test_xcf_gap_closure_foss.py -v
"""

import sys
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from xcf.xcf_parser import (
    xcf_is_multi_pixel,
    xcf_file_bytes_per_layer,
    xcf_color_mode_name,
    xcf_layer_size_variance,
    xcf_total_pixels,
    xcf_file_header_overhead,
    xcf_version_number,
    xcf_is_high_res,
    xcf_megapixel_count,
    xcf_is_square_canvas,
    xcf_width_to_height_ratio,
    xcf_has_single_layer,
    xcf_aspect_ratio_string,
    xcf_layer_width_sum,
    xcf_total_canvas_pixels,
    xcf_height_squared,
    xcf_max_side_length,
    xcf_area_to_layer_ratio,
    xcf_min_side_length,
    xcf_canvas_half_perimeter,
    xcf_width_height_sum,
    xcf_canvas_diagonal,
    xcf_width_squared,
    xcf_layer_name_list,
    xcf_color_depth,
    xcf_width_plus_height,
    xcf_layer_pixel_count,
    xcf_is_color,
    xcf_pixels_exceed_layers,
    xcf_canvas_fill_ratio,
    xcf_is_tiny,
    xcf_avg_layer_area,
    xcf_height_to_layer_ratio,
    xcf_num_layers_plus_image_type_id,
    xcf_width_times_file_size,
    xcf_width_per_layer,
    xcf_height_plus_num_layers,
    xcf_pixel_count_times_two,
    xcf_bytes_per_layer,
    xcf_pixel_area,
    xcf_wh_times_400_plus_image_type_times_300_plus_file_size_mod_31_times_100,
    xcf_area_plus_file_size,
    xcf_layers_times_width,
)

SAMPLES = REPO_ROOT / "samples" / "by-format" / "xcf" / "valid"
RED = SAMPLES / "1x1-red-rgb.xcf"
RGBA = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


class TestXcfIsMultiPixel:
    def test_1x1_not_multi(self):
        assert xcf_is_multi_pixel(RED) is False

    def test_2x2_is_multi(self):
        assert xcf_is_multi_pixel(GRAY) is True

    def test_returns_bool(self):
        assert isinstance(xcf_is_multi_pixel(RED), bool)


class TestXcfFileBytesPerLayer:
    def test_returns_numeric(self):
        assert isinstance(xcf_file_bytes_per_layer(RED), (int, float))

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_file_bytes_per_layer(p) > 0


class TestXcfColorModeName:
    def test_rgb_name(self):
        assert xcf_color_mode_name(RED) == 'RGB'

    def test_returns_str(self):
        assert isinstance(xcf_color_mode_name(RED), str)

    def test_non_empty(self):
        for p in [RED, GRAY]:
            assert len(xcf_color_mode_name(p)) > 0


class TestXcfLayerSizeVariance:
    def test_single_layer_zero_variance(self):
        assert xcf_layer_size_variance(RED) == pytest.approx(0.0, abs=0.001)

    def test_returns_numeric(self):
        assert isinstance(xcf_layer_size_variance(RED), (int, float))

    def test_non_negative(self):
        for p in [RED, GRAY]:
            assert xcf_layer_size_variance(p) >= 0


class TestXcfTotalPixels:
    def test_1x1_is_one(self):
        assert xcf_total_pixels(RED) == 1

    def test_2x2_is_four(self):
        assert xcf_total_pixels(GRAY) == 4

    def test_returns_int(self):
        assert isinstance(xcf_total_pixels(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_total_pixels(p) > 0


class TestXcfFileHeaderOverhead:
    def test_returns_int(self):
        assert isinstance(xcf_file_header_overhead(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_file_header_overhead(p) > 0


class TestXcfVersionNumber:
    def test_returns_int(self):
        assert isinstance(xcf_version_number(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_version_number(p) >= 0


class TestXcfIsHighRes:
    def test_1x1_not_high_res(self):
        assert xcf_is_high_res(RED) is False

    def test_returns_bool(self):
        assert isinstance(xcf_is_high_res(RED), bool)


class TestXcfMegapixelCount:
    def test_returns_numeric(self):
        assert isinstance(xcf_megapixel_count(RED), (int, float))

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_megapixel_count(p) > 0


class TestXcfIsSquareCanvas:
    def test_1x1_is_square(self):
        assert xcf_is_square_canvas(RED) is True

    def test_returns_bool(self):
        assert isinstance(xcf_is_square_canvas(RED), bool)


class TestXcfWidthToHeightRatio:
    def test_1x1_is_one(self):
        assert xcf_width_to_height_ratio(RED) == pytest.approx(1.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(xcf_width_to_height_ratio(RED), (int, float))

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_width_to_height_ratio(p) > 0


class TestXcfHasSingleLayer:
    def test_1x1_single_layer(self):
        assert xcf_has_single_layer(RED) is True

    def test_returns_bool(self):
        assert isinstance(xcf_has_single_layer(RED), bool)


class TestXcfAspectRatioString:
    def test_1x1_ratio(self):
        assert xcf_aspect_ratio_string(RED) == '1:1'

    def test_returns_str(self):
        assert isinstance(xcf_aspect_ratio_string(RED), str)

    def test_contains_colon(self):
        assert ':' in xcf_aspect_ratio_string(RED)


class TestXcfLayerWidthSum:
    def test_1x1_is_one(self):
        assert xcf_layer_width_sum(RED) == 1

    def test_returns_int(self):
        assert isinstance(xcf_layer_width_sum(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_layer_width_sum(p) > 0


class TestXcfTotalCanvasPixels:
    def test_1x1_is_one(self):
        assert xcf_total_canvas_pixels(RED) == 1

    def test_2x2_is_four(self):
        assert xcf_total_canvas_pixels(GRAY) == 4

    def test_returns_int(self):
        assert isinstance(xcf_total_canvas_pixels(RED), int)


class TestXcfHeightSquared:
    def test_1x1_is_one(self):
        assert xcf_height_squared(RED) == 1

    def test_returns_int(self):
        assert isinstance(xcf_height_squared(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_height_squared(p) > 0


class TestXcfMaxSideLength:
    def test_1x1_is_one(self):
        assert xcf_max_side_length(RED) == 1

    def test_returns_int(self):
        assert isinstance(xcf_max_side_length(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_max_side_length(p) > 0


class TestXcfAreaToLayerRatio:
    def test_1x1_is_one(self):
        assert xcf_area_to_layer_ratio(RED) == pytest.approx(1.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(xcf_area_to_layer_ratio(RED), (int, float))

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_area_to_layer_ratio(p) > 0


class TestXcfMinSideLength:
    def test_1x1_is_one(self):
        assert xcf_min_side_length(RED) == 1

    def test_returns_int(self):
        assert isinstance(xcf_min_side_length(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_min_side_length(p) > 0


class TestXcfCanvasHalfPerimeter:
    def test_1x1_is_two(self):
        assert xcf_canvas_half_perimeter(RED) == 2

    def test_returns_int(self):
        assert isinstance(xcf_canvas_half_perimeter(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_canvas_half_perimeter(p) > 0


class TestXcfWidthHeightSum:
    def test_1x1_is_two(self):
        assert xcf_width_height_sum(RED) == 2

    def test_returns_int(self):
        assert isinstance(xcf_width_height_sum(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_width_height_sum(p) > 0


class TestXcfCanvasDiagonal:
    def test_1x1_approx(self):
        assert xcf_canvas_diagonal(RED) == pytest.approx(1.414, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(xcf_canvas_diagonal(RED), (int, float))

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_canvas_diagonal(p) > 0


class TestXcfWidthSquared:
    def test_1x1_is_one(self):
        assert xcf_width_squared(RED) == 1

    def test_returns_int(self):
        assert isinstance(xcf_width_squared(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_width_squared(p) > 0


class TestXcfLayerNameList:
    def test_returns_list(self):
        assert isinstance(xcf_layer_name_list(RED), list)

    def test_non_empty(self):
        for p in [RED, GRAY]:
            assert len(xcf_layer_name_list(p)) > 0

    def test_contains_strings(self):
        names = xcf_layer_name_list(RED)
        for name in names:
            assert isinstance(name, str)


class TestXcfColorDepth:
    def test_returns_int(self):
        assert isinstance(xcf_color_depth(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_color_depth(p) > 0


class TestXcfWidthPlusHeight:
    def test_1x1_is_two(self):
        assert xcf_width_plus_height(RED) == 2

    def test_returns_int(self):
        assert isinstance(xcf_width_plus_height(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_width_plus_height(p) > 0


class TestXcfLayerPixelCount:
    def test_1x1_is_one(self):
        assert xcf_layer_pixel_count(RED) == 1

    def test_returns_int(self):
        assert isinstance(xcf_layer_pixel_count(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_layer_pixel_count(p) > 0


class TestXcfIsColor:
    def test_rgb_is_color(self):
        assert xcf_is_color(RED) is True

    def test_returns_bool(self):
        assert isinstance(xcf_is_color(RED), bool)


class TestXcfPixelsExceedLayers:
    def test_1x1_single_layer_false(self):
        assert xcf_pixels_exceed_layers(RED) is False

    def test_returns_bool(self):
        assert isinstance(xcf_pixels_exceed_layers(RED), bool)


class TestXcfCanvasFillRatio:
    def test_single_layer_one(self):
        assert xcf_canvas_fill_ratio(RED) == pytest.approx(1.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(xcf_canvas_fill_ratio(RED), (int, float))

    def test_bounded(self):
        for p in [RED, GRAY]:
            r = xcf_canvas_fill_ratio(p)
            assert r >= 0


class TestXcfIsTiny:
    def test_1x1_is_tiny(self):
        assert xcf_is_tiny(RED) is True

    def test_returns_bool(self):
        assert isinstance(xcf_is_tiny(RED), bool)


class TestXcfAvgLayerArea:
    def test_1x1_is_one(self):
        assert xcf_avg_layer_area(RED) == pytest.approx(1.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(xcf_avg_layer_area(RED), (int, float))

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_avg_layer_area(p) > 0


class TestXcfHeightToLayerRatio:
    def test_1x1_single_layer_one(self):
        assert xcf_height_to_layer_ratio(RED) == pytest.approx(1.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(xcf_height_to_layer_ratio(RED), (int, float))

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_height_to_layer_ratio(p) > 0


class TestXcfNumLayersPlusImageTypeId:
    def test_returns_int(self):
        assert isinstance(xcf_num_layers_plus_image_type_id(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_num_layers_plus_image_type_id(p) >= 0


class TestXcfWidthTimesFileSize:
    def test_returns_int(self):
        assert isinstance(xcf_width_times_file_size(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_width_times_file_size(p) > 0


class TestXcfWidthPerLayer:
    def test_1x1_single_layer_one(self):
        assert xcf_width_per_layer(RED) == pytest.approx(1.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(xcf_width_per_layer(RED), (int, float))

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_width_per_layer(p) > 0


class TestXcfHeightPlusNumLayers:
    def test_1x1_single_layer_two(self):
        assert xcf_height_plus_num_layers(RED) == 2

    def test_returns_int(self):
        assert isinstance(xcf_height_plus_num_layers(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_height_plus_num_layers(p) > 0


class TestXcfPixelCountTimesTwo:
    def test_1x1_is_two(self):
        assert xcf_pixel_count_times_two(RED) == 2

    def test_returns_int(self):
        assert isinstance(xcf_pixel_count_times_two(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_pixel_count_times_two(p) > 0


class TestXcfBytesPerLayer:
    def test_returns_numeric(self):
        assert isinstance(xcf_bytes_per_layer(RED), (int, float))

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_bytes_per_layer(p) > 0


class TestXcfPixelArea:
    def test_1x1_is_one(self):
        assert xcf_pixel_area(RED) == 1

    def test_returns_int(self):
        assert isinstance(xcf_pixel_area(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_pixel_area(p) > 0


class TestXcfWhTimes400PlusImageTypeTimes300PlusFileSizeMod31Times100:
    def test_returns_numeric(self):
        result = xcf_wh_times_400_plus_image_type_times_300_plus_file_size_mod_31_times_100(RED)
        assert isinstance(result, (int, float))

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_wh_times_400_plus_image_type_times_300_plus_file_size_mod_31_times_100(p) >= 0


class TestXcfAreaPlusFileSize:
    def test_returns_int(self):
        assert isinstance(xcf_area_plus_file_size(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_area_plus_file_size(p) > 0


class TestXcfLayersTimesWidth:
    def test_1x1_single_layer_one(self):
        assert xcf_layers_times_width(RED) == 1

    def test_returns_int(self):
        assert isinstance(xcf_layers_times_width(RED), int)

    def test_positive(self):
        for p in [RED, GRAY]:
            assert xcf_layers_times_width(p) > 0
