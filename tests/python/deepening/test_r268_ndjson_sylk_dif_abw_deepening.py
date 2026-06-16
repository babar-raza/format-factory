"""R268 – NDJSON, SYLK, DIF, ABW product deepening: 8 new analytics functions.

Sprint 16: 2 functions each across 4 formats.
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
ABW_DIR = _REPO / "samples" / "by-format" / "abw"


import pytest


@pytest.fixture
def ndjson_file(tmp_path):
    f = tmp_path / "test.ndjson"
    f.write_text('{"name":"Alice","age":30}\n{"name":"Bob","age":25}\n{"name":"Carol","age":35}\n')
    return str(f)


@pytest.fixture
def ndjson_mixed_file(tmp_path):
    f = tmp_path / "mixed.ndjson"
    f.write_text('{"name":"Alice","age":30}\n{"city":"London"}\n')
    return str(f)


class TestNdjsonIsHomogeneous:
    def test_returns_bool(self, ndjson_file):
        from ndjson import ndjson_is_homogeneous
        assert isinstance(ndjson_is_homogeneous(ndjson_file), bool)

    def test_homogeneous_file(self, ndjson_file):
        from ndjson import ndjson_is_homogeneous
        assert ndjson_is_homogeneous(ndjson_file) is True

    def test_heterogeneous_file(self, ndjson_mixed_file):
        from ndjson import ndjson_is_homogeneous
        assert ndjson_is_homogeneous(ndjson_mixed_file) is False


class TestNdjsonUniqueFieldCount:
    def test_returns_int(self, ndjson_file):
        from ndjson import ndjson_unique_field_count
        assert isinstance(ndjson_unique_field_count(ndjson_file), int)

    def test_count(self, ndjson_file):
        from ndjson import ndjson_unique_field_count
        assert ndjson_unique_field_count(ndjson_file) == 2

    def test_mixed(self, ndjson_mixed_file):
        from ndjson import ndjson_unique_field_count
        assert ndjson_unique_field_count(ndjson_mixed_file) == 3


class TestSylkIsRectangular:
    def test_returns_bool(self):
        from sylk import sylk_is_rectangular
        f = sorted(SYLK_DIR.glob("*.slk"))[0]
        assert isinstance(sylk_is_rectangular(str(f)), bool)


class TestSylkMinRowLength:
    def test_returns_int(self):
        from sylk import sylk_min_row_length
        f = sorted(SYLK_DIR.glob("*.slk"))[0]
        assert isinstance(sylk_min_row_length(str(f)), int)

    def test_le_max(self):
        from sylk import sylk_min_row_length, sylk_max_row_length
        for f in SYLK_DIR.glob("*.slk"):
            assert sylk_min_row_length(str(f)) <= sylk_max_row_length(str(f))


class TestDifNumericDensity:
    def test_returns_float(self):
        from dif import dif_numeric_density
        f = sorted(DIF_DIR.glob("*.dif"))[0]
        assert isinstance(dif_numeric_density(str(f)), float)

    def test_range(self):
        from dif import dif_numeric_density
        for f in DIF_DIR.glob("*.dif"):
            v = dif_numeric_density(str(f))
            assert 0.0 <= v <= 1.0


class TestDifMinCellLength:
    def test_returns_int(self):
        from dif import dif_min_cell_length
        f = sorted(DIF_DIR.glob("*.dif"))[0]
        assert isinstance(dif_min_cell_length(str(f)), int)

    def test_nonnegative(self):
        from dif import dif_min_cell_length
        for f in DIF_DIR.glob("*.dif"):
            assert dif_min_cell_length(str(f)) >= 0


class TestAbwHeadingCount:
    def test_returns_int(self):
        from abw import abw_heading_count
        f = ABW_DIR / "minimal-document.abw"
        assert isinstance(abw_heading_count(str(f)), int)

    def test_nonnegative(self):
        from abw import abw_heading_count
        for f in ABW_DIR.glob("*.abw"):
            assert abw_heading_count(str(f)) >= 0


class TestAbwVocabularyRichness:
    def test_returns_float(self):
        from abw import abw_vocabulary_richness
        f = ABW_DIR / "two-paragraphs.abw"
        assert isinstance(abw_vocabulary_richness(str(f)), float)

    def test_range(self):
        from abw import abw_vocabulary_richness
        for f in ABW_DIR.glob("*.abw"):
            v = abw_vocabulary_richness(str(f))
            assert 0.0 <= v <= 1.0
