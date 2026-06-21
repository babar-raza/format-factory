"""Sprint R290: TOML analytics deepening — unique_value_count, file_size_bytes, max_key_length, avg_value_length."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml.toml_codec import (
    toml_unique_value_count,
    toml_file_size_bytes,
    toml_max_key_length,
    toml_avg_value_length,
)


def _write_toml(tmp_path, content, name="test.toml"):
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# --- toml_unique_value_count ---

class TestTomlUniqueValueCount:
    def test_returns_int(self, tmp_path):
        p = _write_toml(tmp_path, 'a = 1\nb = 2\n')
        assert isinstance(toml_unique_value_count(p), int)

    def test_nonnegative(self, tmp_path):
        p = _write_toml(tmp_path, 'a = 1\n')
        assert toml_unique_value_count(p) >= 0

    def test_distinct_values(self, tmp_path):
        p = _write_toml(tmp_path, 'a = 1\nb = 2\nc = 1\n')
        assert toml_unique_value_count(p) == 2

    def test_all_same(self, tmp_path):
        p = _write_toml(tmp_path, 'x = "same"\ny = "same"\n')
        assert toml_unique_value_count(p) == 1


# --- toml_file_size_bytes ---

class TestTomlFileSizeBytes:
    def test_returns_int(self, tmp_path):
        p = _write_toml(tmp_path, 'key = "val"\n')
        assert isinstance(toml_file_size_bytes(p), int)

    def test_positive_for_file(self, tmp_path):
        p = _write_toml(tmp_path, 'key = "val"\n')
        assert toml_file_size_bytes(p) > 0


# --- toml_max_key_length ---

class TestTomlMaxKeyLength:
    def test_returns_int(self, tmp_path):
        p = _write_toml(tmp_path, 'a = 1\n')
        assert isinstance(toml_max_key_length(p), int)

    def test_simple_keys(self, tmp_path):
        p = _write_toml(tmp_path, 'ab = 1\nabcde = 2\n')
        assert toml_max_key_length(p) == 5


# --- toml_avg_value_length ---

class TestTomlAvgValueLength:
    def test_returns_float(self, tmp_path):
        p = _write_toml(tmp_path, 'a = 1\n')
        assert isinstance(toml_avg_value_length(p), float)

    def test_nonnegative(self, tmp_path):
        p = _write_toml(tmp_path, 'a = 1\n')
        assert toml_avg_value_length(p) >= 0.0

    def test_known_values(self, tmp_path):
        p = _write_toml(tmp_path, 'a = "hi"\nb = "bye"\n')
        assert toml_avg_value_length(p) > 0.0
