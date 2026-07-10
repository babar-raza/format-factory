"""
Tests for toml_to_ndjson dogfood export.

Verifies that TOML top-level keys are converted to NDJSON records using
Format Factory's toml reader and ndjson writer libraries.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

SAMPLE_TOML = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"

from toml.toml_to_ndjson import toml_to_ndjson


class TestTomlToNdjsonBasic:
    """Basic conversion tests."""

    def test_returns_record_count(self, tmp_path: Path) -> None:
        """Returns an integer count of records written."""
        dest = tmp_path / "out.ndjson"
        count = toml_to_ndjson(SAMPLE_TOML, dest)
        assert isinstance(count, int)
        assert count > 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ndjson file is created at the specified path."""
        dest = tmp_path / "out.ndjson"
        toml_to_ndjson(SAMPLE_TOML, dest)
        assert dest.exists()

    def test_output_is_valid_ndjson(self, tmp_path: Path) -> None:
        """Each line of output is valid JSON."""
        dest = tmp_path / "out.ndjson"
        toml_to_ndjson(SAMPLE_TOML, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_minimal_toml_produces_five_records(self, tmp_path: Path) -> None:
        """minimal.toml has 5 top-level keys -> 5 records."""
        dest = tmp_path / "out.ndjson"
        count = toml_to_ndjson(SAMPLE_TOML, dest)
        assert count == 5

    def test_records_have_key_field(self, tmp_path: Path) -> None:
        """Every record has a 'key' field."""
        dest = tmp_path / "out.ndjson"
        toml_to_ndjson(SAMPLE_TOML, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            assert "key" in json.loads(line)

    def test_records_have_value_field(self, tmp_path: Path) -> None:
        """Every record has a 'value' field."""
        dest = tmp_path / "out.ndjson"
        toml_to_ndjson(SAMPLE_TOML, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            assert "value" in json.loads(line)

    def test_records_have_value_type_field(self, tmp_path: Path) -> None:
        """Every record has a 'value_type' field."""
        dest = tmp_path / "out.ndjson"
        toml_to_ndjson(SAMPLE_TOML, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            assert "value_type" in json.loads(line)


class TestTomlToNdjsonContent:
    """Content accuracy tests."""

    def test_string_key_has_string_type(self, tmp_path: Path) -> None:
        """String values have value_type='string'."""
        dest = tmp_path / "out.ndjson"
        toml_to_ndjson(SAMPLE_TOML, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        records = [json.loads(l) for l in lines]
        title_rec = next((r for r in records if r["key"] == "title"), None)
        assert title_rec is not None
        assert title_rec["value_type"] == "string"
        assert "Format Factory" in title_rec["value"]

    def test_boolean_key_has_boolean_type(self, tmp_path: Path) -> None:
        """Boolean values have value_type='boolean'."""
        dest = tmp_path / "out.ndjson"
        toml_to_ndjson(SAMPLE_TOML, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        records = [json.loads(l) for l in lines]
        bool_rec = next((r for r in records if r["key"] == "enabled"), None)
        assert bool_rec is not None
        assert bool_rec["value_type"] == "boolean"

    def test_table_key_has_table_type(self, tmp_path: Path) -> None:
        """Table values have value_type='table'."""
        dest = tmp_path / "out.ndjson"
        toml_to_ndjson(SAMPLE_TOML, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        records = [json.loads(l) for l in lines]
        server_rec = next((r for r in records if r["key"] == "server"), None)
        assert server_rec is not None
        assert server_rec["value_type"] == "table"
        # Value is valid JSON dict
        nested = json.loads(server_rec["value"])
        assert isinstance(nested, dict)
        assert "host" in nested

    def test_key_index_sequential(self, tmp_path: Path) -> None:
        """key_index values are sequential from 0."""
        dest = tmp_path / "out.ndjson"
        count = toml_to_ndjson(SAMPLE_TOML, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        indices = [json.loads(l)["key_index"] for l in lines]
        assert indices == list(range(count))


class TestTomlToNdjsonOptions:
    """Option and parameter tests."""

    def test_key_index_omitted_when_disabled(self, tmp_path: Path) -> None:
        """key_index absent when include_key_index=False."""
        dest = tmp_path / "out.ndjson"
        toml_to_ndjson(SAMPLE_TOML, dest, include_key_index=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            assert "key_index" not in json.loads(line)

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ndjson"
        count = toml_to_ndjson(str(SAMPLE_TOML), str(dest))
        assert isinstance(count, int)
        assert dest.exists()


class TestTomlToNdjsonPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ndjson"
        toml_to_ndjson(SAMPLE_TOML, dest)
        assert dest.exists()
