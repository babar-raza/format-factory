"""Sprint 114 — PPM/NDJSON/SYLK/DIF cycle 11: 8 new analytics functions."""
import sys, tempfile, json
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_blue_dominance_ratio, ppm_channel_entropy
from src.python.ndjson.ndjson_codec import ndjson_max_list_length, ndjson_record_key_overlap
from src.python.sylk.sylk_parser import sylk_has_only_strings, sylk_value_length_variance
from src.python.dif.dif_parser import dif_numeric_cell_sum, dif_empty_row_ratio

_PPM = next((_REPO / "samples" / "by-format" / "ppm" / "valid").glob("*.ppm"))
_SYLK = next((_REPO / "samples" / "by-format" / "sylk" / "valid").glob("*.slk"))
_DIF = next((_REPO / "samples" / "by-format" / "dif" / "valid").glob("*.dif"))


def _ndjson_file():
    tf = tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False)
    tf.write(json.dumps({"a": 1, "b": "x", "c": [1, 2]}) + "\n")
    tf.write(json.dumps({"a": 2, "b": "y"}) + "\n")
    tf.close()
    return tf.name


# --- PPM ---
def test_ppm_blue_dominance_ratio_importable():
    assert callable(ppm_blue_dominance_ratio)

def test_ppm_blue_dominance_ratio_returns_float():
    result = ppm_blue_dominance_ratio(_PPM)
    assert isinstance(result, float) and 0.0 <= result <= 1.0

def test_ppm_channel_entropy_importable():
    assert callable(ppm_channel_entropy)

def test_ppm_channel_entropy_returns_float():
    result = ppm_channel_entropy(_PPM)
    assert isinstance(result, float) and result >= 0


# --- NDJSON ---
def test_ndjson_max_list_length_importable():
    assert callable(ndjson_max_list_length)

def test_ndjson_max_list_length_returns_int():
    result = ndjson_max_list_length(_ndjson_file())
    assert isinstance(result, int) and result >= 0

def test_ndjson_record_key_overlap_importable():
    assert callable(ndjson_record_key_overlap)

def test_ndjson_record_key_overlap_returns_float():
    result = ndjson_record_key_overlap(_ndjson_file())
    assert isinstance(result, float) and 0.0 <= result <= 1.0


# --- SYLK ---
def test_sylk_has_only_strings_importable():
    assert callable(sylk_has_only_strings)

def test_sylk_has_only_strings_returns_bool():
    result = sylk_has_only_strings(_SYLK)
    assert isinstance(result, bool)

def test_sylk_value_length_variance_importable():
    assert callable(sylk_value_length_variance)

def test_sylk_value_length_variance_returns_float():
    result = sylk_value_length_variance(_SYLK)
    assert isinstance(result, (int, float)) and result >= 0


# --- DIF ---
def test_dif_numeric_cell_sum_importable():
    assert callable(dif_numeric_cell_sum)

def test_dif_numeric_cell_sum_returns_float():
    result = dif_numeric_cell_sum(_DIF)
    assert isinstance(result, (int, float))

def test_dif_empty_row_ratio_importable():
    assert callable(dif_empty_row_ratio)

def test_dif_empty_row_ratio_returns_float():
    result = dif_empty_row_ratio(_DIF)
    assert isinstance(result, float) and 0.0 <= result <= 1.0
