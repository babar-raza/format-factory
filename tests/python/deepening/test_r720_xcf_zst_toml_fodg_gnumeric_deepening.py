"""Sprint R720 — XCF/ZST/TOML/FODG/Gnumeric _times_sixty_eight composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_sixty_eight, xcf_image_type_id_times_sixty_eight
from src.python.zst.zst_codec import zst_file_size_bytes_times_sixty_eight, zst_decompressed_size_times_sixty_eight
from src.python.toml.toml_codec import toml_file_size_bytes_times_sixty_eight, toml_string_value_count_times_sixty_eight
from src.python.fodg.fodg_codec import fodg_page_count_times_sixty_eight, fodg_total_shape_count_times_sixty_eight
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_sixty_eight, gnumeric_total_row_count_times_sixty_eight
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesSixtyEight:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_sixty_eight(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_sixty_eight(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_sixty_eight(_XCF) % 68 == 0
class TestXcfImageTypeIdTimesSixtyEight:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_sixty_eight(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_sixty_eight(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_sixty_eight(_XCF) % 68 == 0
class TestZstFileSizeBytesTimesSixtyEight:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_sixty_eight(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_sixty_eight(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_sixty_eight(_ZST) % 68 == 0
class TestZstDecompressedSizeTimesSixtyEight:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_sixty_eight(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_sixty_eight(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_sixty_eight(_ZST) % 68 == 0
class TestTomlFileSizeBytesTimesSixtyEight:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_sixty_eight(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_sixty_eight(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_sixty_eight(_TOML) % 68 == 0
class TestTomlStringValueCountTimesSixtyEight:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_sixty_eight(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_sixty_eight(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_sixty_eight(_TOML) % 68 == 0
class TestFodgPageCountTimesSixtyEight:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_sixty_eight(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_sixty_eight(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_sixty_eight(_FODG) % 68 == 0
class TestFodgTotalShapeCountTimesSixtyEight:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_sixty_eight(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_sixty_eight(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_sixty_eight(_FODG) % 68 == 0
class TestGnumericFileSizeBytesTimesSixtyEight:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_sixty_eight(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_sixty_eight(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_sixty_eight(_GNUMERIC) % 68 == 0
class TestGnumericTotalRowCountTimesSixtyEight:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_sixty_eight(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_sixty_eight(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_sixty_eight(_GNUMERIC) % 68 == 0
