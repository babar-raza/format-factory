"""Sprint R444 — XCF/ZST/TOML/FODG/Gnumeric deepening round 7 (composite analytics)."""
import sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

# ── XCF ───────────────────────────────────────────────────────────────
from src.python.xcf.xcf_parser import (
    xcf_height_squared,
    xcf_width_squared,
    xcf_height,
    xcf_width,
)

_xcf_path = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")

class TestXcfHeightSquared:
    def test_type(self):
        assert isinstance(xcf_height_squared(_xcf_path), int)
    def test_value(self):
        h = xcf_height(_xcf_path)
        assert xcf_height_squared(_xcf_path) == h * h
    def test_nonneg(self):
        assert xcf_height_squared(_xcf_path) >= 0

class TestXcfWidthSquared:
    def test_type(self):
        assert isinstance(xcf_width_squared(_xcf_path), int)
    def test_value(self):
        w = xcf_width(_xcf_path)
        assert xcf_width_squared(_xcf_path) == w * w
    def test_nonneg(self):
        assert xcf_width_squared(_xcf_path) >= 0

# ── ZST ───────────────────────────────────────────────────────────────
from src.python.zst.zst_codec import (
    zst_frame_count_times_two,
    zst_byte_count_squared,
    zst_frame_count,
    zst_decompressed_byte_sum,
)

_zst_path = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")

class TestZstFrameCountTimesTwo:
    def test_type(self):
        assert isinstance(zst_frame_count_times_two(_zst_path), int)
    def test_value(self):
        assert zst_frame_count_times_two(_zst_path) == zst_frame_count(_zst_path) * 2
    def test_nonneg(self):
        assert zst_frame_count_times_two(_zst_path) >= 0

class TestZstByteCountSquared:
    def test_type(self):
        assert isinstance(zst_byte_count_squared(_zst_path), int)
    def test_value(self):
        bc = zst_decompressed_byte_sum(_zst_path)
        assert zst_byte_count_squared(_zst_path) == bc * bc
    def test_nonneg(self):
        assert zst_byte_count_squared(_zst_path) >= 0

# ── TOML ──────────────────────────────────────────────────────────────
from src.python.toml.toml_codec import (
    toml_key_count_times_two,
    toml_value_count_squared,
    toml_total_keys,
)

_toml_path = str(SAMPLES / "toml" / "minimal.toml")

class TestTomlKeyCountTimesTwo:
    def test_type(self):
        assert isinstance(toml_key_count_times_two(_toml_path), int)
    def test_value(self):
        assert toml_key_count_times_two(_toml_path) == toml_total_keys(_toml_path) * 2
    def test_nonneg(self):
        assert toml_key_count_times_two(_toml_path) >= 0

class TestTomlValueCountSquared:
    def test_type(self):
        assert isinstance(toml_value_count_squared(_toml_path), int)
    def test_value(self):
        vc = toml_total_keys(_toml_path)
        assert toml_value_count_squared(_toml_path) == vc * vc
    def test_nonneg(self):
        assert toml_value_count_squared(_toml_path) >= 0

# ── FODG ──────────────────────────────────────────────────────────────
from src.python.fodg.fodg_codec import (
    fodg_page_count_times_two,
    fodg_total_shape_count_times_three,
    fodg_page_count,
    fodg_total_shape_count,
)

_fodg_path = str(SAMPLES / "fodg" / "minimal-drawing.fodg")

class TestFodgPageCountTimesTwo:
    def test_type(self):
        assert isinstance(fodg_page_count_times_two(_fodg_path), int)
    def test_value(self):
        assert fodg_page_count_times_two(_fodg_path) == fodg_page_count(_fodg_path) * 2
    def test_nonneg(self):
        assert fodg_page_count_times_two(_fodg_path) >= 0

class TestFodgTotalShapeCountTimesThree:
    def test_type(self):
        assert isinstance(fodg_total_shape_count_times_three(_fodg_path), int)
    def test_value(self):
        assert fodg_total_shape_count_times_three(_fodg_path) == fodg_total_shape_count(_fodg_path) * 3
    def test_nonneg(self):
        assert fodg_total_shape_count_times_three(_fodg_path) >= 0

# ── Gnumeric ──────────────────────────────────────────────────────────
from src.python.gnumeric.gnumeric_codec import (
    gnumeric_row_count_squared,
    gnumeric_cell_count_squared,
    gnumeric_total_row_count,
    gnumeric_total_cell_count,
)

_gnumeric_path = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestGnumericRowCountSquared:
    def test_type(self):
        assert isinstance(gnumeric_row_count_squared(_gnumeric_path), int)
    def test_value(self):
        rc = gnumeric_total_row_count(_gnumeric_path)
        assert gnumeric_row_count_squared(_gnumeric_path) == rc * rc
    def test_nonneg(self):
        assert gnumeric_row_count_squared(_gnumeric_path) >= 0

class TestGnumericCellCountSquared:
    def test_type(self):
        assert isinstance(gnumeric_cell_count_squared(_gnumeric_path), int)
    def test_value(self):
        cc = gnumeric_total_cell_count(_gnumeric_path)
        assert gnumeric_cell_count_squared(_gnumeric_path) == cc * cc
    def test_nonneg(self):
        assert gnumeric_cell_count_squared(_gnumeric_path) >= 0
