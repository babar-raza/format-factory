"""Sprint 118 — PPM/NDJSON/SYLK/DIF cycle 12 product deepening tests."""
import sys, tempfile, json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_saturation_mean, ppm_pixel_brightness_sum
from src.python.ndjson.ndjson_codec import ndjson_total_values_count, ndjson_boolean_ratio_total
from src.python.sylk.sylk_parser import sylk_max_cell_text_length, sylk_row_density_avg
from src.python.dif.dif_parser import dif_nonempty_cell_density, dif_cell_value_length_sum

_PPM = next((_REPO / "samples" / "by-format" / "ppm" / "valid").glob("*.ppm"))
_SYLK = next((_REPO / "samples" / "by-format" / "sylk" / "valid").glob("*.slk"))
_DIF = next((_REPO / "samples" / "by-format" / "dif" / "valid").glob("*.dif"))


def _ndjson_file():
    tf = tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False)
    tf.write(json.dumps({"a": 1, "b": "x", "c": True}) + "\n")
    tf.write(json.dumps({"a": 2, "b": "y", "d": [1, 2]}) + "\n")
    tf.close()
    return tf.name


class TestPpmSaturationMean:
    def test_returns_float(self):
        result = ppm_saturation_mean(_PPM)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert ppm_saturation_mean(_PPM) >= 0.0


class TestPpmPixelBrightnessSum:
    def test_returns_int(self):
        result = ppm_pixel_brightness_sum(_PPM)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert ppm_pixel_brightness_sum(_PPM) >= 0


class TestNdjsonTotalValuesCount:
    def test_returns_int(self):
        result = ndjson_total_values_count(_ndjson_file())
        assert isinstance(result, int)

    def test_positive(self):
        assert ndjson_total_values_count(_ndjson_file()) > 0


class TestNdjsonBooleanRatioTotal:
    def test_returns_float(self):
        result = ndjson_boolean_ratio_total(_ndjson_file())
        assert isinstance(result, float)

    def test_range(self):
        result = ndjson_boolean_ratio_total(_ndjson_file())
        assert 0.0 <= result <= 1.0


class TestSylkMaxCellTextLength:
    def test_returns_int(self):
        result = sylk_max_cell_text_length(_SYLK)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert sylk_max_cell_text_length(_SYLK) >= 0


class TestSylkRowDensityAvg:
    def test_returns_float(self):
        result = sylk_row_density_avg(_SYLK)
        assert isinstance(result, float)

    def test_range(self):
        result = sylk_row_density_avg(_SYLK)
        assert 0.0 <= result <= 1.0


class TestDifNonemptyCellDensity:
    def test_returns_float(self):
        result = dif_nonempty_cell_density(_DIF)
        assert isinstance(result, float)

    def test_range(self):
        result = dif_nonempty_cell_density(_DIF)
        assert 0.0 <= result <= 1.0


class TestDifCellValueLengthSum:
    def test_returns_int(self):
        result = dif_cell_value_length_sum(_DIF)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert dif_cell_value_length_sum(_DIF) >= 0
