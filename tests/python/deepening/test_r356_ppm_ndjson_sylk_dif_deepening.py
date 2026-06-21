"""Sprint 126 — PPM/NDJSON/SYLK/DIF cycle 14 product deepening tests."""
import sys, json, tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_red_mean_value, ppm_pixel_count_total
from src.python.ndjson.ndjson_codec import ndjson_record_depth_max, ndjson_dict_field_total
from src.python.sylk.sylk_parser import sylk_value_type_variety, sylk_min_cell_text_length
from src.python.dif.dif_parser import dif_max_cell_text_length, dif_column_count_avg

_PPM = next((_REPO / "samples" / "by-format" / "ppm" / "valid").glob("*.ppm"))
_SYLK = next((_REPO / "samples" / "by-format" / "sylk" / "valid").glob("*.slk"))
_DIF = next((_REPO / "samples" / "by-format" / "dif" / "valid").glob("*.dif"))


def _ndjson_file():
    data = [
        {"name": "alice", "age": 30, "tags": [1, 2]},
        {"name": "bob", "age": 25, "nested": {"x": 1}},
    ]
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False)
    for rec in data:
        f.write(json.dumps(rec) + "\n")
    f.close()
    return f.name


class TestPpmRedMeanValue:
    def test_returns_float(self):
        assert isinstance(ppm_red_mean_value(_PPM), float)

    def test_non_negative(self):
        assert ppm_red_mean_value(_PPM) >= 0.0


class TestPpmPixelCountTotal:
    def test_returns_int(self):
        assert isinstance(ppm_pixel_count_total(_PPM), int)

    def test_non_negative(self):
        assert ppm_pixel_count_total(_PPM) >= 0


class TestNdjsonRecordDepthMax:
    def test_returns_int(self):
        path = _ndjson_file()
        assert isinstance(ndjson_record_depth_max(path), int)

    def test_positive(self):
        path = _ndjson_file()
        assert ndjson_record_depth_max(path) >= 1


class TestNdjsonDictFieldTotal:
    def test_returns_int(self):
        path = _ndjson_file()
        assert isinstance(ndjson_dict_field_total(path), int)

    def test_correct_value(self):
        path = _ndjson_file()
        assert ndjson_dict_field_total(path) == 6  # 3 + 3


class TestSylkValueTypeVariety:
    def test_returns_int(self):
        assert isinstance(sylk_value_type_variety(_SYLK), int)

    def test_non_negative(self):
        assert sylk_value_type_variety(_SYLK) >= 0


class TestSylkMinCellTextLength:
    def test_returns_int(self):
        assert isinstance(sylk_min_cell_text_length(_SYLK), int)

    def test_non_negative(self):
        assert sylk_min_cell_text_length(_SYLK) >= 0


class TestDifMaxCellTextLength:
    def test_returns_int(self):
        assert isinstance(dif_max_cell_text_length(_DIF), int)

    def test_non_negative(self):
        assert dif_max_cell_text_length(_DIF) >= 0


class TestDifColumnCountAvg:
    def test_returns_float(self):
        assert isinstance(dif_column_count_avg(_DIF), float)

    def test_non_negative(self):
        assert dif_column_count_avg(_DIF) >= 0.0
