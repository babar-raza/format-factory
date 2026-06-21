"""Tests for TOML roundtrip capability.

Closes:
  GAP-TOML-FOSS-ROUNDTRIP-001  (Toml Roundtrip)
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.toml import roundtrip as toml_roundtrip


@pytest.fixture
def simple_toml(tmp_path):
    p = tmp_path / "simple.toml"
    p.write_text("x = 42\nname = \"hello\"\n")
    return str(p)


@pytest.fixture
def list_toml(tmp_path):
    p = tmp_path / "lists.toml"
    p.write_text("items = [1, 2, 3]\ntitle = \"test\"\n")
    return str(p)


class TestTomlRoundtrip:
    def test_return_type(self, simple_toml, tmp_path):
        dest = str(tmp_path / "out.toml")
        result = toml_roundtrip(simple_toml, dest)
        assert isinstance(result, dict)

    def test_format_is_toml(self, simple_toml, tmp_path):
        dest = str(tmp_path / "out.toml")
        result = toml_roundtrip(simple_toml, dest)
        assert result["format"] == "toml"

    def test_key_count_2_for_simple(self, simple_toml, tmp_path):
        dest = str(tmp_path / "out.toml")
        result = toml_roundtrip(simple_toml, dest)
        assert result["key_count"] == 2

    def test_data_preserves_numeric(self, simple_toml, tmp_path):
        dest = str(tmp_path / "out.toml")
        result = toml_roundtrip(simple_toml, dest)
        assert result["data"]["x"] == 42

    def test_data_preserves_string(self, simple_toml, tmp_path):
        dest = str(tmp_path / "out.toml")
        result = toml_roundtrip(simple_toml, dest)
        assert result["data"]["name"] == "hello"

    def test_output_file_created(self, simple_toml, tmp_path):
        dest = str(tmp_path / "out.toml")
        toml_roundtrip(simple_toml, dest)
        assert Path(dest).exists()

    def test_consistent_across_calls(self, simple_toml, tmp_path):
        dest1 = str(tmp_path / "out1.toml")
        dest2 = str(tmp_path / "out2.toml")
        r1 = toml_roundtrip(simple_toml, dest1)
        r2 = toml_roundtrip(simple_toml, dest2)
        assert r1["key_count"] == r2["key_count"]
