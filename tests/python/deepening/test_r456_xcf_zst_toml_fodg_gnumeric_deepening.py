"""Sprint R456 — XCF/ZST/TOML/FODG/Gnumeric round 10 deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_file_size_times_three, xcf_image_type_id_times_three, xcf_file_size_bytes, xcf_image_type_id
from src.python.zst import zst_decompressed_size_times_three, zst_file_size_times_three, zst_decompressed_size, zst_file_size_bytes
from src.python.toml import toml_file_size_times_three, toml_string_value_count_times_three, toml_file_size_bytes, toml_string_value_count
from src.python.fodg import fodg_max_shapes_per_page_times_three, fodg_non_text_shape_count_times_three, fodg_max_shapes_per_page, fodg_non_text_shape_count
from src.python.gnumeric import gnumeric_file_size_times_three, gnumeric_total_row_count_times_three, gnumeric_file_size_bytes, gnumeric_total_row_count

SAMPLES = _REPO / "samples" / "by-format"
XCF_SAMPLE = SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf"
ZST_SAMPLE = SAMPLES / "zst" / "valid" / "text-compressed.zst"
TOML_SAMPLE = SAMPLES / "toml" / "minimal.toml"
FODG_SAMPLE = SAMPLES / "fodg" / "minimal-drawing.fodg"
GNUMERIC_SAMPLE = SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric"


class TestXcfFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_times_three(XCF_SAMPLE), int)
    def test_is_triple(self):
        assert xcf_file_size_times_three(XCF_SAMPLE) == xcf_file_size_bytes(XCF_SAMPLE) * 3
    def test_non_negative(self):
        assert xcf_file_size_times_three(XCF_SAMPLE) >= 0


class TestXcfImageTypeIdTimesThree:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_three(XCF_SAMPLE), int)
    def test_is_triple(self):
        assert xcf_image_type_id_times_three(XCF_SAMPLE) == xcf_image_type_id(XCF_SAMPLE) * 3
    def test_non_negative(self):
        assert xcf_image_type_id_times_three(XCF_SAMPLE) >= 0


class TestZstDecompressedSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_three(ZST_SAMPLE), int)
    def test_is_triple(self):
        assert zst_decompressed_size_times_three(ZST_SAMPLE) == zst_decompressed_size(ZST_SAMPLE) * 3
    def test_non_negative(self):
        assert zst_decompressed_size_times_three(ZST_SAMPLE) >= 0


class TestZstFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(zst_file_size_times_three(ZST_SAMPLE), int)
    def test_is_triple(self):
        assert zst_file_size_times_three(ZST_SAMPLE) == zst_file_size_bytes(ZST_SAMPLE) * 3
    def test_non_negative(self):
        assert zst_file_size_times_three(ZST_SAMPLE) >= 0


class TestTomlFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(toml_file_size_times_three(TOML_SAMPLE), int)
    def test_is_triple(self):
        assert toml_file_size_times_three(TOML_SAMPLE) == toml_file_size_bytes(TOML_SAMPLE) * 3
    def test_non_negative(self):
        assert toml_file_size_times_three(TOML_SAMPLE) >= 0


class TestTomlStringValueCountTimesThree:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_three(TOML_SAMPLE), int)
    def test_is_triple(self):
        assert toml_string_value_count_times_three(TOML_SAMPLE) == toml_string_value_count(TOML_SAMPLE) * 3
    def test_non_negative(self):
        assert toml_string_value_count_times_three(TOML_SAMPLE) >= 0


class TestFodgMaxShapesPerPageTimesThree:
    def test_returns_int(self):
        assert isinstance(fodg_max_shapes_per_page_times_three(FODG_SAMPLE), int)
    def test_is_triple(self):
        assert fodg_max_shapes_per_page_times_three(FODG_SAMPLE) == fodg_max_shapes_per_page(FODG_SAMPLE) * 3
    def test_non_negative(self):
        assert fodg_max_shapes_per_page_times_three(FODG_SAMPLE) >= 0


class TestFodgNonTextShapeCountTimesThree:
    def test_returns_int(self):
        assert isinstance(fodg_non_text_shape_count_times_three(FODG_SAMPLE), int)
    def test_is_triple(self):
        assert fodg_non_text_shape_count_times_three(FODG_SAMPLE) == fodg_non_text_shape_count(FODG_SAMPLE) * 3
    def test_non_negative(self):
        assert fodg_non_text_shape_count_times_three(FODG_SAMPLE) >= 0


class TestGnumericFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_times_three(GNUMERIC_SAMPLE), int)
    def test_is_triple(self):
        assert gnumeric_file_size_times_three(GNUMERIC_SAMPLE) == gnumeric_file_size_bytes(GNUMERIC_SAMPLE) * 3
    def test_non_negative(self):
        assert gnumeric_file_size_times_three(GNUMERIC_SAMPLE) >= 0


class TestGnumericTotalRowCountTimesThree:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_three(GNUMERIC_SAMPLE), int)
    def test_is_triple(self):
        assert gnumeric_total_row_count_times_three(GNUMERIC_SAMPLE) == gnumeric_total_row_count(GNUMERIC_SAMPLE) * 3
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_three(GNUMERIC_SAMPLE) >= 0
