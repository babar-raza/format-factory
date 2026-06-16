"""R267 – ODT, FODG, TOML, Gnumeric product deepening: 8 new analytics functions.

Sprint 15: 2 functions each across 4 formats.
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
FODG_DIR = _REPO / "samples" / "by-format" / "fodg"
GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


class TestOdtHeadingDensity:
    def test_returns_float(self):
        from odt import odt_heading_density
        f = sorted(ODT_DIR.glob("*.odt"))[0]
        assert isinstance(odt_heading_density(str(f)), float)

    def test_nonnegative(self):
        from odt import odt_heading_density
        for f in ODT_DIR.glob("*.odt"):
            assert odt_heading_density(str(f)) >= 0.0

    def test_le_one(self):
        from odt import odt_heading_density
        for f in ODT_DIR.glob("*.odt"):
            assert odt_heading_density(str(f)) <= 1.0


class TestOdtLongestWord:
    def test_returns_int(self):
        from odt import odt_longest_word
        f = sorted(ODT_DIR.glob("*.odt"))[0]
        assert isinstance(odt_longest_word(str(f)), int)

    def test_ge_shortest(self):
        from odt import odt_longest_word, odt_shortest_word
        for f in ODT_DIR.glob("*.odt"):
            assert odt_longest_word(str(f)) >= odt_shortest_word(str(f))


class TestFodgMinShapesPerPage:
    def test_returns_int(self):
        from fodg import fodg_min_shapes_per_page
        assert isinstance(fodg_min_shapes_per_page(str(FODG_DIR / "minimal-drawing.fodg")), int)

    def test_le_max(self):
        from fodg import fodg_min_shapes_per_page, fodg_max_shapes_per_page
        for f in FODG_DIR.glob("*.fodg"):
            assert fodg_min_shapes_per_page(str(f)) <= fodg_max_shapes_per_page(str(f))


class TestFodgShapeDensity:
    def test_returns_float(self):
        from fodg import fodg_shape_density
        assert isinstance(fodg_shape_density(str(FODG_DIR / "minimal-drawing.fodg")), float)

    def test_nonnegative(self):
        from fodg import fodg_shape_density
        for f in FODG_DIR.glob("*.fodg"):
            assert fodg_shape_density(str(f)) >= 0.0


class TestTomlTableCount:
    def test_returns_int(self):
        from src.python.toml import toml_table_count
        assert isinstance(toml_table_count(b'name = "Alice"\n'), int)

    def test_no_tables(self):
        from src.python.toml import toml_table_count
        assert toml_table_count(b'name = "Alice"\nage = 30\n') == 0

    def test_with_table(self):
        from src.python.toml import toml_table_count
        assert toml_table_count(b'[server]\nhost = "localhost"\nport = 8080\n') == 1


class TestTomlTotalKeys:
    def test_returns_int(self):
        from src.python.toml import toml_total_keys
        assert isinstance(toml_total_keys(b'key = "val"\n'), int)

    def test_count(self):
        from src.python.toml import toml_total_keys
        assert toml_total_keys(b'a = 1\nb = 2\nc = 3\n') == 3


class TestGnumericIsSingleSheet:
    def test_returns_bool(self):
        from gnumeric import gnumeric_is_single_sheet
        f = sorted(GNUMERIC_DIR.glob("*.gnumeric"))[0]
        assert isinstance(gnumeric_is_single_sheet(str(f)), bool)


class TestGnumericEmptySheetCount:
    def test_returns_int(self):
        from gnumeric import gnumeric_empty_sheet_count
        f = sorted(GNUMERIC_DIR.glob("*.gnumeric"))[0]
        assert isinstance(gnumeric_empty_sheet_count(str(f)), int)

    def test_nonnegative(self):
        from gnumeric import gnumeric_empty_sheet_count
        for f in GNUMERIC_DIR.glob("*.gnumeric"):
            assert gnumeric_empty_sheet_count(str(f)) >= 0
