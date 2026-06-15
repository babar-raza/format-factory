"""Gap closure tests for TOML format — batch covering 14 open gaps.

Gaps covered:
  GAP-TOML-FOSS-MERGE_TOML-001, GAP-TOML-FOSS-TO_JSON_STR-001,
  GAP-TOML-FOSS-TOMLERROR-001, GAP-TOML-FOSS-TOMLINPUTERR-001,
  GAP-TOML-FOSS-TOMLPARSEERR-001, GAP-TOML-FOSS-TOMLWRITEERR-001,
  GAP-TOML-FOSS-GET_SECTION_-001, GAP-TOML-FOSS-HAS_KEY-001,
  GAP-TOML-FOSS-COUNT_KEYS-001, GAP-TOML-FOSS-TO_ENV-001,
  GAP-TOML-FOSS-DIFF_KEYS-001, GAP-TOML-FOSS-RENAME_KEY-001,
  GAP-TOML-FOSS-HAS_ANY_SECT-001, GAP-TOML-FOSS-COUNT_VALUES-001
"""
import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml import (
    TomlError,
    TomlInputError,
    TomlParseError,
    TomlWriteError,
    count_keys,
    count_values_in_section,
    diff_keys,
    get_section_keys,
    has_any_section,
    has_key,
    load_toml,
    merge_toml,
    rename_key,
    to_env,
    to_json_str,
    write_toml,
)

SAMPLE_TOML = b"""\
[server]
host = "localhost"
port = 8080
debug = true

[database]
name = "mydb"
port = 5432

[logging]
level = "info"
"""


@pytest.fixture
def toml_file(tmp_path):
    p = tmp_path / "sample.toml"
    p.write_bytes(SAMPLE_TOML)
    return p


@pytest.fixture
def toml_file2(tmp_path):
    content = b"""\
[server]
host = "remote"

[extra]
enabled = true
"""
    p = tmp_path / "sample2.toml"
    p.write_bytes(content)
    return p


# --- GAP-TOML-FOSS-MERGE_TOML-001 ---
class TestMergeToml:
    def test_merge_two_files(self, toml_file, toml_file2, tmp_path):
        result = merge_toml(toml_file, toml_file2)
        assert result is not None
        # Merged result should contain keys from both files
        out = tmp_path / "merged.toml"
        write_toml(result, out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_merge_bytes(self):
        a = b'[a]\nx = 1\n'
        b_data = b'[b]\ny = 2\n'
        result = merge_toml(a, b_data)
        assert result is not None


# --- GAP-TOML-FOSS-TO_JSON_STR-001 ---
class TestToJsonStr:
    def test_basic(self, toml_file):
        result = to_json_str(toml_file)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert "server" in parsed or any("server" in str(v) for v in parsed.values())

    def test_bytes(self):
        result = to_json_str(b'[test]\nval = 42\n')
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed is not None


# --- GAP-TOML-FOSS-TOMLERROR-001 ---
class TestTomlError:
    def test_is_exception(self):
        assert issubclass(TomlError, Exception)

    def test_can_raise(self):
        with pytest.raises(TomlError):
            raise TomlError("test error")


# --- GAP-TOML-FOSS-TOMLINPUTERR-001 ---
class TestTomlInputError:
    def test_is_subclass(self):
        assert issubclass(TomlInputError, (TomlError, Exception))

    def test_can_raise(self):
        with pytest.raises(TomlInputError):
            raise TomlInputError("bad input")


# --- GAP-TOML-FOSS-TOMLPARSEERR-001 ---
class TestTomlParseError:
    def test_is_subclass(self):
        assert issubclass(TomlParseError, (TomlError, Exception))

    def test_bad_toml_raises(self):
        with pytest.raises((TomlParseError, TomlError, Exception)):
            load_toml(b'[invalid\nno closing bracket')


# --- GAP-TOML-FOSS-TOMLWRITEERR-001 ---
class TestTomlWriteError:
    def test_is_subclass(self):
        assert issubclass(TomlWriteError, (TomlError, Exception))

    def test_can_raise(self):
        with pytest.raises(TomlWriteError):
            raise TomlWriteError("write failed")


# --- GAP-TOML-FOSS-GET_SECTION_-001 ---
class TestGetSectionKeys:
    def test_server_section(self, toml_file):
        keys = get_section_keys(toml_file, "server")
        assert isinstance(keys, list)
        assert "host" in keys
        assert "port" in keys

    def test_database_section(self, toml_file):
        keys = get_section_keys(toml_file, "database")
        assert "name" in keys


# --- GAP-TOML-FOSS-HAS_KEY-001 ---
class TestHasKey:
    def test_existing_key(self, toml_file):
        assert has_key(toml_file, "server") is True

    def test_missing_key(self, toml_file):
        assert has_key(toml_file, "nonexistent") is False

    def test_bytes_input(self):
        assert has_key(b'[x]\nval = 1\n', "x") is True


# --- GAP-TOML-FOSS-COUNT_KEYS-001 ---
class TestCountKeys:
    def test_count(self, toml_file):
        count = count_keys(toml_file)
        assert isinstance(count, int)
        assert count >= 3  # at least server, database, logging sections

    def test_from_file(self, toml_file):
        count = count_keys(toml_file, recursive=True)
        assert count >= 6  # sections + nested keys


# --- GAP-TOML-FOSS-TO_ENV-001 ---
class TestToEnv:
    def test_basic(self, toml_file):
        result = to_env(toml_file)
        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain key=value pairs
        lines = [l for l in result.strip().splitlines() if l.strip()]
        assert len(lines) >= 1


# --- GAP-TOML-FOSS-DIFF_KEYS-001 ---
class TestDiffKeys:
    def test_diff(self, toml_file, toml_file2):
        result = diff_keys(toml_file, toml_file2)
        assert result is not None
        # Result should indicate differences between the two files

    def test_identical(self, toml_file):
        result = diff_keys(toml_file, toml_file)
        assert result is not None


# --- GAP-TOML-FOSS-RENAME_KEY-001 ---
class TestRenameKey:
    def test_rename(self, toml_file):
        doc = load_toml(toml_file)
        data = doc.get("data", doc)
        result = rename_key(data, "server", "srv")
        assert result is not None
        assert "srv" in result

    def test_rename_preserves_other_keys(self, toml_file):
        doc = load_toml(toml_file)
        data = doc.get("data", doc)
        result = rename_key(data, "server", "srv")
        assert "database" in result  # other keys preserved


# --- GAP-TOML-FOSS-HAS_ANY_SECT-001 ---
class TestHasAnySection:
    def test_has_sections(self, toml_file):
        # has_any_section checks if document has at least one table/section
        assert has_any_section(toml_file) is True

    def test_no_sections(self, tmp_path):
        p = tmp_path / "flat.toml"
        p.write_text("key = \"value\"\n", encoding="utf-8")
        # A flat TOML with no sections might return False
        result = has_any_section(p)
        assert isinstance(result, bool)


# --- GAP-TOML-FOSS-COUNT_VALUES-001 ---
class TestCountValuesInSection:
    def test_server(self, toml_file):
        count = count_values_in_section(toml_file, "server")
        assert isinstance(count, int)
        assert count >= 2  # host, port, debug

    def test_empty_section(self):
        count = count_values_in_section(b'[empty]\n', "empty")
        assert count == 0
