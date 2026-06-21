"""Sprint 122 — PPM/NDJSON/SYLK/DIF cycle 13 product deepening tests."""
import sys, json, tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_luminance_mean, ppm_channel_range_sum
from src.python.ndjson.ndjson_codec import ndjson_null_density, ndjson_numeric_value_mean
from src.python.sylk.sylk_parser import sylk_numeric_cell_sum, sylk_cell_fill_ratio
from src.python.dif.dif_parser import dif_numeric_cell_mean, dif_row_cell_count_avg

_PPM = next((_REPO / "samples" / "by-format" / "ppm" / "valid").glob("*.ppm"))
_SYLK = next((_REPO / "samples" / "by-format" / "sylk" / "valid").glob("*.slk"))
_DIF = next((_REPO / "samples" / "by-format" / "dif" / "valid").glob("*.dif"))


def _ndjson_file():
    data = [
        {"name": "alice", "age": 30, "active": True},
        {"name": "bob", "age": None, "active": False},
        {"name": "charlie", "age": 25, "active": True},
    ]
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False)
    for rec in data:
        f.write(json.dumps(rec) + "\n")
    f.close()
    return f.name


class TestPpmLuminanceMean:
    def test_returns_float(self):
        assert isinstance(ppm_luminance_mean(_PPM), float)

    def test_non_negative(self):
        assert ppm_luminance_mean(_PPM) >= 0.0


class TestPpmChannelRangeSum:
    def test_returns_int(self):
        assert isinstance(ppm_channel_range_sum(_PPM), int)

    def test_non_negative(self):
        assert ppm_channel_range_sum(_PPM) >= 0


class TestNdjsonNullDensity:
    def test_returns_float(self):
        path = _ndjson_file()
        assert isinstance(ndjson_null_density(path), float)

    def test_range(self):
        path = _ndjson_file()
        r = ndjson_null_density(path)
        assert 0.0 <= r <= 1.0


class TestNdjsonNumericValueMean:
    def test_returns_float(self):
        path = _ndjson_file()
        assert isinstance(ndjson_numeric_value_mean(path), float)

    def test_correct_value(self):
        path = _ndjson_file()
        r = ndjson_numeric_value_mean(path)
        assert r == (30 + 25) / 2


class TestSylkNumericCellSum:
    def test_returns_float(self):
        assert isinstance(sylk_numeric_cell_sum(_SYLK), float)


class TestSylkCellFillRatio:
    def test_returns_float(self):
        assert isinstance(sylk_cell_fill_ratio(_SYLK), float)

    def test_range(self):
        assert 0.0 <= sylk_cell_fill_ratio(_SYLK) <= 1.0


class TestDifNumericCellMean:
    def test_returns_float(self):
        assert isinstance(dif_numeric_cell_mean(_DIF), float)


class TestDifRowCellCountAvg:
    def test_returns_float(self):
        assert isinstance(dif_row_cell_count_avg(_DIF), float)

    def test_non_negative(self):
        assert dif_row_cell_count_avg(_DIF) >= 0.0
