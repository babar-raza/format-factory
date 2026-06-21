"""Sprint 102 — PPM/NDJSON/SYLK/DIF cycle 8: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"
_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid"
_DIF = _REPO / "samples" / "by-format" / "dif" / "valid"

_NDJSON_DATA = b'{"a":1,"b":"hello"}\n{"a":2,"c":true}\n{"a":3,"b":"","d":null}\n'


@pytest.fixture
def ppm_sample():
    return next(_PPM.glob("*.ppm"))


@pytest.fixture
def sylk_sample():
    return next(_SYLK.glob("*.slk"))


@pytest.fixture
def dif_sample():
    return next(_DIF.glob("*.dif"))


# ── PPM ──

def test_ppm_max_channel_value_importable():
    from src.python.ppm import ppm_max_channel_value
    assert callable(ppm_max_channel_value)


def test_ppm_max_channel_value_returns_int(ppm_sample):
    from src.python.ppm import ppm_max_channel_value
    result = ppm_max_channel_value(ppm_sample)
    assert isinstance(result, int)
    assert result >= 0


def test_ppm_min_channel_value_importable():
    from src.python.ppm import ppm_min_channel_value
    assert callable(ppm_min_channel_value)


def test_ppm_min_channel_value_returns_int(ppm_sample):
    from src.python.ppm import ppm_min_channel_value
    result = ppm_min_channel_value(ppm_sample)
    assert isinstance(result, int)
    assert result >= 0


# ── NDJSON ──

def test_ndjson_avg_key_count_importable():
    from src.python.ndjson import ndjson_avg_key_count
    assert callable(ndjson_avg_key_count)


def test_ndjson_avg_key_count_returns_float():
    from src.python.ndjson import ndjson_avg_key_count
    result = ndjson_avg_key_count(_NDJSON_DATA)
    assert isinstance(result, float)
    assert result > 0.0


def test_ndjson_distinct_key_count_importable():
    from src.python.ndjson import ndjson_distinct_key_count
    assert callable(ndjson_distinct_key_count)


def test_ndjson_distinct_key_count_returns_int():
    from src.python.ndjson import ndjson_distinct_key_count
    result = ndjson_distinct_key_count(_NDJSON_DATA)
    assert isinstance(result, int)
    assert result == 4  # a, b, c, d


# ── SYLK ──

def test_sylk_column_fill_rate_importable():
    from src.python.sylk import sylk_column_fill_rate
    assert callable(sylk_column_fill_rate)


def test_sylk_column_fill_rate_returns_float(sylk_sample):
    from src.python.sylk import sylk_column_fill_rate
    result = sylk_column_fill_rate(sylk_sample)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_sylk_distinct_string_count_importable():
    from src.python.sylk import sylk_distinct_string_count
    assert callable(sylk_distinct_string_count)


def test_sylk_distinct_string_count_returns_int(sylk_sample):
    from src.python.sylk import sylk_distinct_string_count
    result = sylk_distinct_string_count(sylk_sample)
    assert isinstance(result, int)
    assert result >= 0


# ── DIF ──

def test_dif_max_row_width_importable():
    from src.python.dif import dif_max_row_width
    assert callable(dif_max_row_width)


def test_dif_max_row_width_returns_int(dif_sample):
    from src.python.dif import dif_max_row_width
    result = dif_max_row_width(dif_sample)
    assert isinstance(result, int)
    assert result >= 0


def test_dif_empty_cell_ratio_importable():
    from src.python.dif import dif_empty_cell_ratio
    assert callable(dif_empty_cell_ratio)


def test_dif_empty_cell_ratio_returns_float(dif_sample):
    from src.python.dif import dif_empty_cell_ratio
    result = dif_empty_cell_ratio(dif_sample)
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


# ── Cross-format ──

def test_all_eight_functions_callable():
    """Verify all 8 Sprint 102 functions are importable."""
    from src.python.ppm import ppm_max_channel_value, ppm_min_channel_value
    from src.python.ndjson import ndjson_avg_key_count, ndjson_distinct_key_count
    from src.python.sylk import sylk_column_fill_rate, sylk_distinct_string_count
    from src.python.dif import dif_max_row_width, dif_empty_cell_ratio
    for fn in [
        ppm_max_channel_value, ppm_min_channel_value,
        ndjson_avg_key_count, ndjson_distinct_key_count,
        sylk_column_fill_rate, sylk_distinct_string_count,
        dif_max_row_width, dif_empty_cell_ratio,
    ]:
        assert callable(fn)
