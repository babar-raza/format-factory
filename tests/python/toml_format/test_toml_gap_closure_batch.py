"""Gap closure tests for TOML — covering 15 open gaps.

Gaps cover: load_toml, write_toml, probe_toml, get_keys, get_value,
    set_value, has_key, list_sections, get_section_keys, has_section,
    count_keys, to_json_str, flatten, merge_toml,
    TomlError, TomlInputError, TomlParseError, TomlWriteError
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml import (
    TomlError,
    TomlInputError,
    TomlParseError,
    TomlWriteError,
    count_keys,
    flatten,
    get_keys,
    get_section_keys,
    get_value,
    has_key,
    has_section,
    list_sections,
    load_toml,
    merge_toml,
    probe_toml,
    set_value,
    to_json_str,
    write_toml,
)


@pytest.fixture
def toml_file(tmp_path):
    content = '[server]\nhost = "localhost"\nport = 8080\n\n[database]\nname = "mydb"\nport = 5432\n'
    f = tmp_path / "config.toml"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture
def toml_doc(toml_file):
    return load_toml(str(toml_file))


class TestErrorClasses:
    def test_toml_error_is_exception(self):
        assert issubclass(TomlError, Exception)

    def test_toml_input_error_subclass(self):
        assert issubclass(TomlInputError, TomlError)

    def test_toml_parse_error_subclass(self):
        assert issubclass(TomlParseError, TomlError)

    def test_toml_write_error_subclass(self):
        assert issubclass(TomlWriteError, TomlError)

    def test_message_preserved(self):
        err = TomlError("bad toml")
        assert "bad toml" in str(err)


class TestLoadToml:
    def test_returns_dict(self, toml_file):
        doc = load_toml(str(toml_file))
        assert isinstance(doc, dict)


class TestWriteToml:
    def test_creates_file(self, toml_doc, tmp_path):
        out = tmp_path / "out.toml"
        write_toml(toml_doc, str(out))
        assert out.exists()
        assert out.stat().st_size > 0


class TestProbeToml:
    def test_returns_dict(self, toml_file):
        result = probe_toml(str(toml_file))
        assert isinstance(result, dict)


class TestGetKeys:
    def test_returns_list(self, toml_file):
        keys = get_keys(str(toml_file))
        assert isinstance(keys, list)
        assert len(keys) > 0


class TestGetValue:
    def test_gets_known_value(self, toml_file):
        val = get_value(str(toml_file), "server.host")
        assert val == "localhost"


class TestSetValue:
    def test_sets_value(self, tmp_path):
        content = 'title = "hello"\n'
        f = tmp_path / "simple.toml"
        f.write_text(content, encoding="utf-8")
        model = load_toml(f)
        result = set_value(model["data"], "title", "world")
        assert result is not None
        assert result["title"] == "world"


class TestHasKey:
    def test_existing_key(self, toml_file):
        assert has_key(str(toml_file), "server") is True

    def test_missing_key(self, toml_file):
        assert has_key(str(toml_file), "nonexistent_key_xyz") is False


class TestListSections:
    def test_returns_list(self, toml_file):
        sections = list_sections(str(toml_file))
        assert isinstance(sections, list)
        assert "server" in sections


class TestGetSectionKeys:
    def test_returns_list(self, toml_file):
        keys = get_section_keys(str(toml_file), "server")
        assert isinstance(keys, list)
        assert "host" in keys


class TestHasSection:
    def test_existing(self, toml_file):
        assert has_section(str(toml_file), "server") is True

    def test_missing(self, toml_file):
        assert has_section(str(toml_file), "nonexistent") is False


class TestCountKeys:
    def test_returns_int(self, toml_file):
        count = count_keys(str(toml_file))
        assert isinstance(count, int)
        assert count >= 2


class TestToJsonStr:
    def test_returns_json(self, toml_file):
        json_str = to_json_str(str(toml_file))
        assert isinstance(json_str, str)
        assert "localhost" in json_str


class TestFlatten:
    def test_returns_dict(self, toml_file):
        flat = flatten(str(toml_file))
        assert isinstance(flat, dict)
        assert len(flat) > 0


class TestMergeToml:
    def test_merge(self, toml_file, tmp_path):
        other_content = '[extra]\nkey = "value"\n'
        other = tmp_path / "other.toml"
        other.write_text(other_content, encoding="utf-8")
        result = merge_toml(str(toml_file), str(other))
        assert result is not None
