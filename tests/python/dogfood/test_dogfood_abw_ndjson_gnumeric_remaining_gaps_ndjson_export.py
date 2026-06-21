"""Dogfood export: ABW (6) + NDJSON (7) + Gnumeric (8) analytics gap functions → NDJSON.

Functions covered (previously uncovered by dogfood tests):
  ABW:     abw_avg_sentence_length, abw_avg_words_per_paragraph, abw_lowercase_ratio,
           abw_numeric_word_count, abw_total_char_count, abw_unique_word_count
  NDJSON:  ndjson_has_uniform_types, ndjson_max_field_count, ndjson_min_field_count,
           ndjson_null_density, ndjson_numeric_field_count, ndjson_string_field_count,
           ndjson_total_field_count
  Gnumeric: gnumeric_total_cell_count, gnumeric_string_cell_count,
            gnumeric_nonempty_cell_ratio, gnumeric_numeric_cell_ratio,
            gnumeric_file_size_bytes, gnumeric_is_all_string,
            gnumeric_cells_exceed_rows, gnumeric_max_row_cell_count
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    abw_avg_sentence_length,
    abw_avg_words_per_paragraph,
    abw_lowercase_ratio,
    abw_numeric_word_count,
    abw_total_char_count,
    abw_unique_word_count,
)
from gnumeric.gnumeric_codec import (
    gnumeric_cells_exceed_rows,
    gnumeric_file_size_bytes,
    gnumeric_is_all_string,
    gnumeric_max_row_cell_count,
    gnumeric_nonempty_cell_ratio,
    gnumeric_numeric_cell_ratio,
    gnumeric_string_cell_count,
    gnumeric_total_cell_count,
)
from ndjson.ndjson_codec import (
    ndjson_has_uniform_types,
    ndjson_max_field_count,
    ndjson_min_field_count,
    ndjson_null_density,
    ndjson_numeric_field_count,
    ndjson_string_field_count,
    ndjson_total_field_count,
    write_ndjson,
)

_ABW = str(_REPO / "samples" / "by-format" / "abw" / "minimal-document.abw")
_GNUMERIC = str(_REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric")


def _make_ndjson(tmp_path):
    """Create a 2-record NDJSON file for testing."""
    path = str(tmp_path / "test_sample.ndjson")
    write_ndjson(
        [{"name": "Alice", "age": 30, "score": 95.5}, {"name": "Bob", "age": 25, "score": 87.0}],
        path,
    )
    return path


# --- ABW tests ---

def test_abw_avg_sentence_length(tmp_path):
    val = abw_avg_sentence_length(_ABW)
    assert isinstance(val, float)
    assert val == 5.0
    out = tmp_path / "abw_avg_sentence_length.ndjson"
    write_ndjson([{"metric": "abw_avg_sentence_length", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 5.0


def test_abw_avg_words_per_paragraph(tmp_path):
    val = abw_avg_words_per_paragraph(_ABW)
    assert isinstance(val, float)
    assert val == 1.0
    out = tmp_path / "abw_avg_words_per_paragraph.ndjson"
    write_ndjson([{"metric": "abw_avg_words_per_paragraph", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1.0


def test_abw_lowercase_ratio(tmp_path):
    val = abw_lowercase_ratio(_ABW)
    assert isinstance(val, float)
    assert val == 0.8
    out = tmp_path / "abw_lowercase_ratio.ndjson"
    write_ndjson([{"metric": "abw_lowercase_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.8


def test_abw_numeric_word_count(tmp_path):
    val = abw_numeric_word_count(_ABW)
    assert isinstance(val, int)
    assert val == 0
    out = tmp_path / "abw_numeric_word_count.ndjson"
    write_ndjson([{"metric": "abw_numeric_word_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0


def test_abw_total_char_count(tmp_path):
    val = abw_total_char_count(_ABW)
    assert isinstance(val, int)
    assert val == 5
    out = tmp_path / "abw_total_char_count.ndjson"
    write_ndjson([{"metric": "abw_total_char_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 5


def test_abw_unique_word_count(tmp_path):
    val = abw_unique_word_count(_ABW)
    assert isinstance(val, int)
    assert val == 1
    out = tmp_path / "abw_unique_word_count.ndjson"
    write_ndjson([{"metric": "abw_unique_word_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1


# --- NDJSON tests ---

def test_ndjson_has_uniform_types(tmp_path):
    ndjson_path = _make_ndjson(tmp_path)
    val = ndjson_has_uniform_types(ndjson_path)
    assert isinstance(val, bool)
    assert val is True
    out = tmp_path / "ndjson_has_uniform_types.ndjson"
    write_ndjson([{"metric": "ndjson_has_uniform_types", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] is True


def test_ndjson_max_field_count(tmp_path):
    ndjson_path = _make_ndjson(tmp_path)
    val = ndjson_max_field_count(ndjson_path)
    assert isinstance(val, int)
    assert val == 3
    out = tmp_path / "ndjson_max_field_count.ndjson"
    write_ndjson([{"metric": "ndjson_max_field_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 3


def test_ndjson_min_field_count(tmp_path):
    ndjson_path = _make_ndjson(tmp_path)
    val = ndjson_min_field_count(ndjson_path)
    assert isinstance(val, int)
    assert val == 3
    out = tmp_path / "ndjson_min_field_count.ndjson"
    write_ndjson([{"metric": "ndjson_min_field_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 3


def test_ndjson_null_density(tmp_path):
    ndjson_path = _make_ndjson(tmp_path)
    val = ndjson_null_density(ndjson_path)
    assert isinstance(val, float)
    assert val == 0.0
    out = tmp_path / "ndjson_null_density.ndjson"
    write_ndjson([{"metric": "ndjson_null_density", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.0


def test_ndjson_numeric_field_count(tmp_path):
    ndjson_path = _make_ndjson(tmp_path)
    val = ndjson_numeric_field_count(ndjson_path)
    assert isinstance(val, int)
    assert val == 4
    out = tmp_path / "ndjson_numeric_field_count.ndjson"
    write_ndjson([{"metric": "ndjson_numeric_field_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 4


def test_ndjson_string_field_count(tmp_path):
    ndjson_path = _make_ndjson(tmp_path)
    val = ndjson_string_field_count(ndjson_path)
    assert isinstance(val, int)
    assert val == 2
    out = tmp_path / "ndjson_string_field_count.ndjson"
    write_ndjson([{"metric": "ndjson_string_field_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 2


def test_ndjson_total_field_count(tmp_path):
    ndjson_path = _make_ndjson(tmp_path)
    val = ndjson_total_field_count(ndjson_path)
    assert isinstance(val, int)
    assert val == 6
    out = tmp_path / "ndjson_total_field_count.ndjson"
    write_ndjson([{"metric": "ndjson_total_field_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 6


# --- Gnumeric tests ---

def test_gnumeric_total_cell_count(tmp_path):
    val = gnumeric_total_cell_count(_GNUMERIC)
    assert isinstance(val, int)
    assert val == 1
    out = tmp_path / "gnumeric_total_cell_count.ndjson"
    write_ndjson([{"metric": "gnumeric_total_cell_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1


def test_gnumeric_string_cell_count(tmp_path):
    val = gnumeric_string_cell_count(_GNUMERIC)
    assert isinstance(val, int)
    assert val == 1
    out = tmp_path / "gnumeric_string_cell_count.ndjson"
    write_ndjson([{"metric": "gnumeric_string_cell_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1


def test_gnumeric_nonempty_cell_ratio(tmp_path):
    val = gnumeric_nonempty_cell_ratio(_GNUMERIC)
    assert isinstance(val, float)
    assert val == 1.0
    out = tmp_path / "gnumeric_nonempty_cell_ratio.ndjson"
    write_ndjson([{"metric": "gnumeric_nonempty_cell_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1.0


def test_gnumeric_numeric_cell_ratio(tmp_path):
    val = gnumeric_numeric_cell_ratio(_GNUMERIC)
    assert isinstance(val, float)
    assert val == 0.0
    out = tmp_path / "gnumeric_numeric_cell_ratio.ndjson"
    write_ndjson([{"metric": "gnumeric_numeric_cell_ratio", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 0.0


def test_gnumeric_file_size_bytes(tmp_path):
    val = gnumeric_file_size_bytes(_GNUMERIC)
    assert isinstance(val, int)
    assert val == 307
    out = tmp_path / "gnumeric_file_size_bytes.ndjson"
    write_ndjson([{"metric": "gnumeric_file_size_bytes", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 307


def test_gnumeric_is_all_string(tmp_path):
    val = gnumeric_is_all_string(_GNUMERIC)
    assert isinstance(val, bool)
    assert val is True
    out = tmp_path / "gnumeric_is_all_string.ndjson"
    write_ndjson([{"metric": "gnumeric_is_all_string", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] is True


def test_gnumeric_cells_exceed_rows(tmp_path):
    val = gnumeric_cells_exceed_rows(_GNUMERIC)
    assert isinstance(val, bool)
    assert val is False
    out = tmp_path / "gnumeric_cells_exceed_rows.ndjson"
    write_ndjson([{"metric": "gnumeric_cells_exceed_rows", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] is False


def test_gnumeric_max_row_cell_count(tmp_path):
    val = gnumeric_max_row_cell_count(_GNUMERIC)
    assert isinstance(val, int)
    assert val == 1
    out = tmp_path / "gnumeric_max_row_cell_count.ndjson"
    write_ndjson([{"metric": "gnumeric_max_row_cell_count", "value": val}], str(out))
    assert json.loads(out.read_text().strip())["value"] == 1


def test_all_formats_batch_ndjson_export(tmp_path):
    ndjson_path = _make_ndjson(tmp_path)
    records = [
        {"metric": "abw_avg_sentence_length", "value": abw_avg_sentence_length(_ABW)},
        {"metric": "abw_unique_word_count", "value": abw_unique_word_count(_ABW)},
        {"metric": "ndjson_has_uniform_types", "value": ndjson_has_uniform_types(ndjson_path)},
        {"metric": "ndjson_total_field_count", "value": ndjson_total_field_count(ndjson_path)},
        {"metric": "gnumeric_total_cell_count", "value": gnumeric_total_cell_count(_GNUMERIC)},
        {"metric": "gnumeric_is_all_string", "value": gnumeric_is_all_string(_GNUMERIC)},
    ]
    out = tmp_path / "abw_ndjson_gnumeric_gaps_batch.ndjson"
    write_ndjson(records, str(out))
    lines = out.read_text().strip().splitlines()
    assert len(lines) == 6
    parsed = [json.loads(ln) for ln in lines]
    metrics = {r["metric"] for r in parsed}
    assert "abw_avg_sentence_length" in metrics
    assert "ndjson_has_uniform_types" in metrics
    assert "gnumeric_total_cell_count" in metrics
