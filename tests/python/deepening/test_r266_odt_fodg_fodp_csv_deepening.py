"""R266 – ODT, FODG, FODP, CSV product deepening: 8 new analytics functions.

Sprint 14: 2 functions each across 4 formats.
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
FODG_DIR = _REPO / "samples" / "by-format" / "fodg"
FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
CSV_DIR = _REPO / "samples" / "by-format" / "csv"
CSV_VALID = [CSV_DIR / "minimal-2x2.csv", CSV_DIR / "single-cell.csv", CSV_DIR / "quoted-fields.csv"]


class TestOdtShortestWord:
    def test_returns_int(self):
        from odt import odt_shortest_word
        f = sorted(ODT_DIR.glob("*.odt"))[0]
        assert isinstance(odt_shortest_word(str(f)), int)

    def test_nonnegative(self):
        from odt import odt_shortest_word
        for f in ODT_DIR.glob("*.odt"):
            assert odt_shortest_word(str(f)) >= 0


class TestOdtParagraphDensity:
    def test_returns_float(self):
        from odt import odt_paragraph_density
        f = sorted(ODT_DIR.glob("*.odt"))[0]
        assert isinstance(odt_paragraph_density(str(f)), float)

    def test_nonnegative(self):
        from odt import odt_paragraph_density
        for f in ODT_DIR.glob("*.odt"):
            assert odt_paragraph_density(str(f)) >= 0.0


class TestFodgTextToShapeRatio:
    def test_returns_float(self):
        from fodg import fodg_text_to_shape_ratio
        assert isinstance(fodg_text_to_shape_ratio(str(FODG_DIR / "minimal-drawing.fodg")), float)

    def test_nonnegative(self):
        from fodg import fodg_text_to_shape_ratio
        for f in FODG_DIR.glob("*.fodg"):
            assert fodg_text_to_shape_ratio(str(f)) >= 0.0

    def test_le_one(self):
        from fodg import fodg_text_to_shape_ratio
        for f in FODG_DIR.glob("*.fodg"):
            assert fodg_text_to_shape_ratio(str(f)) <= 1.0


class TestFodgMaxShapesPerPage:
    def test_returns_int(self):
        from fodg import fodg_max_shapes_per_page
        assert isinstance(fodg_max_shapes_per_page(str(FODG_DIR / "minimal-drawing.fodg")), int)

    def test_nonnegative(self):
        from fodg import fodg_max_shapes_per_page
        for f in FODG_DIR.glob("*.fodg"):
            assert fodg_max_shapes_per_page(str(f)) >= 0

    def test_ge_avg(self):
        from fodg import fodg_max_shapes_per_page, fodg_avg_shapes_per_page
        for f in FODG_DIR.glob("*.fodg"):
            assert fodg_max_shapes_per_page(str(f)) >= fodg_avg_shapes_per_page(str(f))


class TestFodpHasEmptySlides:
    def test_returns_bool(self):
        from fodp import fodp_has_empty_slides
        f = sorted(FODP_DIR.glob("*.fodp"))[0]
        assert isinstance(fodp_has_empty_slides(str(f)), bool)


class TestFodpTitleCoverage:
    def test_returns_float(self):
        from fodp import fodp_title_coverage
        f = sorted(FODP_DIR.glob("*.fodp"))[0]
        assert isinstance(fodp_title_coverage(str(f)), float)

    def test_range_zero_to_one(self):
        from fodp import fodp_title_coverage
        for f in FODP_DIR.glob("*.fodp"):
            v = fodp_title_coverage(str(f))
            assert 0.0 <= v <= 1.0


class TestCsvHeaderCount:
    def test_returns_int(self):
        from src.python.csv.csv_parser import csv_header_count
        assert isinstance(csv_header_count(str(CSV_VALID[0])), int)

    def test_nonnegative(self):
        from src.python.csv.csv_parser import csv_header_count
        for f in CSV_VALID:
            assert csv_header_count(str(f)) >= 0


class TestCsvIsRectangular:
    def test_returns_bool(self):
        from src.python.csv.csv_parser import csv_is_rectangular
        assert isinstance(csv_is_rectangular(str(CSV_VALID[0])), bool)

    def test_valid_csvs_rectangular(self):
        from src.python.csv.csv_parser import csv_is_rectangular
        for f in CSV_VALID:
            assert csv_is_rectangular(str(f)) is True
