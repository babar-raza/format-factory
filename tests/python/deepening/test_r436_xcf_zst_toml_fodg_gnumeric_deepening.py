"""Sprint R436 — XCF/ZST/TOML/FODG/Gnumeric deepening round 5.

Functions under test (10 total, 2 per format):
  XCF:      xcf_pixel_count_times_two, xcf_file_size_times_two
  ZST:      zst_frame_count_times_two, zst_header_size_squared
  TOML:     toml_table_count_times_two, toml_file_size_squared
  FODG:     fodg_file_size_squared, fodg_page_count_times_three
  Gnumeric: gnumeric_cell_count_times_two, gnumeric_file_size_times_two
"""
import pathlib, sys, pytest

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

# --- sample paths ---
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf"
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid" / "text-compressed.zst"
_TOML = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"
_FODG = _REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg"
_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"

# ── XCF ──────────────────────────────────────────────────────────────
from src.python.xcf.xcf_parser import (
    xcf_total_pixel_count,
    xcf_file_size_bytes,
    xcf_pixel_count_times_two,
    xcf_file_size_times_two,
)

class TestXcfPixelCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(xcf_pixel_count_times_two(_XCF), int)
    def test_double_of_base(self):
        assert xcf_pixel_count_times_two(_XCF) == xcf_total_pixel_count(_XCF) * 2
    def test_non_negative(self):
        assert xcf_pixel_count_times_two(_XCF) >= 0

class TestXcfFileSizeTimesTwo:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_times_two(_XCF), int)
    def test_double_of_base(self):
        assert xcf_file_size_times_two(_XCF) == xcf_file_size_bytes(_XCF) * 2
    def test_positive(self):
        assert xcf_file_size_times_two(_XCF) > 0

# ── ZST ──────────────────────────────────────────────────────────────
from src.python.zst.zst_codec import (
    zst_frame_count,
    zst_header_size,
    zst_frame_count_times_two,
    zst_header_size_squared,
)

class TestZstFrameCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(zst_frame_count_times_two(_ZST), int)
    def test_double_of_base(self):
        assert zst_frame_count_times_two(_ZST) == zst_frame_count(_ZST) * 2
    def test_non_negative(self):
        assert zst_frame_count_times_two(_ZST) >= 0

class TestZstHeaderSizeSquared:
    def test_returns_int(self):
        assert isinstance(zst_header_size_squared(_ZST), int)
    def test_square_of_base(self):
        hs = zst_header_size(_ZST)
        assert zst_header_size_squared(_ZST) == hs * hs
    def test_non_negative(self):
        assert zst_header_size_squared(_ZST) >= 0

# ── TOML ─────────────────────────────────────────────────────────────
from src.python.toml.toml_codec import (
    toml_table_count,
    toml_file_size_bytes as toml_file_size_bytes_fn,
    toml_table_count_times_two,
    toml_file_size_squared,
)

class TestTomlTableCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(toml_table_count_times_two(_TOML), int)
    def test_double_of_base(self):
        assert toml_table_count_times_two(_TOML) == toml_table_count(_TOML) * 2
    def test_non_negative(self):
        assert toml_table_count_times_two(_TOML) >= 0

class TestTomlFileSizeSquared:
    def test_returns_int(self):
        assert isinstance(toml_file_size_squared(_TOML), int)
    def test_square_of_base(self):
        fs = toml_file_size_bytes_fn(_TOML)
        assert toml_file_size_squared(_TOML) == fs * fs
    def test_positive(self):
        assert toml_file_size_squared(_TOML) > 0

# ── FODG ─────────────────────────────────────────────────────────────
from src.python.fodg.fodg_codec import (
    fodg_file_size_bytes,
    fodg_page_count,
    fodg_file_size_squared,
    fodg_page_count_times_three,
)

class TestFodgFileSizeSquared:
    def test_returns_int(self):
        assert isinstance(fodg_file_size_squared(_FODG), int)
    def test_square_of_base(self):
        fs = fodg_file_size_bytes(_FODG)
        assert fodg_file_size_squared(_FODG) == fs * fs
    def test_positive(self):
        assert fodg_file_size_squared(_FODG) > 0

class TestFodgPageCountTimesThree:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_three(_FODG), int)
    def test_triple_of_base(self):
        assert fodg_page_count_times_three(_FODG) == fodg_page_count(_FODG) * 3
    def test_positive(self):
        assert fodg_page_count_times_three(_FODG) > 0

# ── Gnumeric ─────────────────────────────────────────────────────────
from src.python.gnumeric.gnumeric_codec import (
    gnumeric_total_cell_count,
    gnumeric_file_size_bytes,
    gnumeric_cell_count_times_two,
    gnumeric_file_size_times_two,
)

class TestGnumericCellCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(gnumeric_cell_count_times_two(_GNUMERIC), int)
    def test_double_of_base(self):
        assert gnumeric_cell_count_times_two(_GNUMERIC) == gnumeric_total_cell_count(_GNUMERIC) * 2
    def test_non_negative(self):
        assert gnumeric_cell_count_times_two(_GNUMERIC) >= 0

class TestGnumericFileSizeTimesTwo:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_times_two(_GNUMERIC), int)
    def test_double_of_base(self):
        assert gnumeric_file_size_times_two(_GNUMERIC) == gnumeric_file_size_bytes(_GNUMERIC) * 2
    def test_positive(self):
        assert gnumeric_file_size_times_two(_GNUMERIC) > 0
