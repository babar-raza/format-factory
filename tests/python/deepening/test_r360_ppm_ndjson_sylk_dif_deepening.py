"""Sprint 130 — PPM/NDJSON/SYLK/DIF cycle 15: 8 new analytics functions."""
import sys, json, tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_green_mean_value, ppm_blue_mean_value
from src.python.ndjson.ndjson_codec import ndjson_array_field_total, ndjson_key_count_total
from src.python.sylk.sylk_parser import sylk_cell_count_per_row_avg, sylk_text_cell_ratio
from src.python.dif.dif_parser import dif_value_text_total_length, dif_cell_text_variance

_PPM = next((_REPO / "samples" / "by-format" / "ppm" / "valid").glob("*.ppm"))
_SYLK = next((_REPO / "samples" / "by-format" / "sylk" / "valid").glob("*.slk"))
_DIF = next((_REPO / "samples" / "by-format" / "dif" / "valid").glob("*.dif"))

# NDJSON needs inline temp file
_data = [{"a": 1, "b": [2, 3], "c": {"d": 4}}, {"x": "hi"}]
_nf = tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False)
for rec in _data:
    _nf.write(json.dumps(rec) + "\n")
_nf.close()
_NDJSON = _nf.name


class TestPpmGreenMeanValue:
    def test_returns_float(self):
        result = ppm_green_mean_value(_PPM)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert ppm_green_mean_value(_PPM) >= 0.0


class TestPpmBlueMeanValue:
    def test_returns_float(self):
        result = ppm_blue_mean_value(_PPM)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert ppm_blue_mean_value(_PPM) >= 0.0


class TestNdjsonArrayFieldTotal:
    def test_returns_int(self):
        result = ndjson_array_field_total(_NDJSON)
        assert isinstance(result, int)

    def test_correct_count(self):
        # First record has "b": [2,3] = 1 array field
        assert ndjson_array_field_total(_NDJSON) >= 1


class TestNdjsonKeyCountTotal:
    def test_returns_int(self):
        result = ndjson_key_count_total(_NDJSON)
        assert isinstance(result, int)

    def test_correct_count(self):
        # rec1: a,b,c + nested d = 4 keys; rec2: x = 1 key; total = 5
        assert ndjson_key_count_total(_NDJSON) == 5


class TestSylkCellCountPerRowAvg:
    def test_returns_float(self):
        result = sylk_cell_count_per_row_avg(_SYLK)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert sylk_cell_count_per_row_avg(_SYLK) >= 0.0


class TestSylkTextCellRatio:
    def test_returns_float(self):
        result = sylk_text_cell_ratio(_SYLK)
        assert isinstance(result, float)

    def test_in_range(self):
        r = sylk_text_cell_ratio(_SYLK)
        assert 0.0 <= r <= 1.0


class TestDifValueTextTotalLength:
    def test_returns_int(self):
        result = dif_value_text_total_length(_DIF)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert dif_value_text_total_length(_DIF) >= 0


class TestDifCellTextVariance:
    def test_returns_float(self):
        result = dif_cell_text_variance(_DIF)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert dif_cell_text_variance(_DIF) >= 0.0
