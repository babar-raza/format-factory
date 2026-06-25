"""Sprint 134 — PPM/NDJSON/SYLK/DIF cycle 16 product deepening tests."""
import sys
import tempfile
import json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

_PPM = next((_REPO / "samples" / "by-format" / "ppm" / "valid").glob("*.ppm"))
_SYLK = next((_REPO / "samples" / "by-format" / "sylk" / "valid").glob("*.slk"))
_DIF = next((_REPO / "samples" / "by-format" / "dif" / "valid").glob("*.dif"))


def _ndjson_tmp():
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False)
    for rec in [{"a": 1, "b": {"c": 2}}, {"a": 3, "d": [4, 5]}]:
        f.write(json.dumps(rec) + "\n")
    f.close()
    return f.name


# ---------- PPM ----------
class TestPpmPixelValueSum:
    def test_returns_int(self):
        from src.python.ppm import ppm_pixel_value_sum
        assert isinstance(ppm_pixel_value_sum(_PPM), int)

    def test_non_negative(self):
        from src.python.ppm import ppm_pixel_value_sum
        assert ppm_pixel_value_sum(_PPM) >= 0


class TestPpmChannelContrastSum:
    def test_returns_int(self):
        from src.python.ppm import ppm_channel_contrast_sum
        assert isinstance(ppm_channel_contrast_sum(_PPM), int)

    def test_non_negative(self):
        from src.python.ppm import ppm_channel_contrast_sum
        assert ppm_channel_contrast_sum(_PPM) >= 0


# ---------- NDJSON ----------
class TestNdjsonMaxKeyDepth:
    def test_returns_int(self):
        from src.python.ndjson import ndjson_max_key_depth
        assert isinstance(ndjson_max_key_depth(_ndjson_tmp()), int)

    def test_nested_depth(self):
        from src.python.ndjson import ndjson_max_key_depth
        assert ndjson_max_key_depth(_ndjson_tmp()) >= 2


class TestNdjsonFieldValueMean:
    def test_returns_float(self):
        from src.python.ndjson import ndjson_field_value_mean
        assert isinstance(ndjson_field_value_mean(_ndjson_tmp()), (int, float))

    def test_positive(self):
        from src.python.ndjson import ndjson_field_value_mean
        assert ndjson_field_value_mean(_ndjson_tmp()) > 0


# ---------- SYLK ----------
class TestSylkCellTextLengthSum:
    def test_returns_int(self):
        from src.python.sylk import sylk_cell_text_length_sum
        assert isinstance(sylk_cell_text_length_sum(_SYLK), int)

    def test_non_negative(self):
        from src.python.sylk import sylk_cell_text_length_sum
        assert sylk_cell_text_length_sum(_SYLK) >= 0


class TestSylkNumericValueSum:
    def test_returns_float(self):
        from src.python.sylk import sylk_numeric_value_sum
        assert isinstance(sylk_numeric_value_sum(_SYLK), (int, float))

    def test_non_negative(self):
        from src.python.sylk import sylk_numeric_value_sum
        assert sylk_numeric_value_sum(_SYLK) >= 0


# ---------- DIF ----------
class TestDifStringCellTotalLength:
    def test_returns_int(self):
        from src.python.dif import dif_string_cell_total_length
        assert isinstance(dif_string_cell_total_length(_DIF), int)

    def test_non_negative(self):
        from src.python.dif import dif_string_cell_total_length
        assert dif_string_cell_total_length(_DIF) >= 0


class TestDifNumericValueTotal:
    def test_returns_float(self):
        from src.python.dif import dif_numeric_value_total
        assert isinstance(dif_numeric_value_total(_DIF), (int, float))

    def test_non_negative(self):
        from src.python.dif import dif_numeric_value_total
        assert dif_numeric_value_total(_DIF) >= 0
