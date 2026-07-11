"""
Tests for toml_to_csv dogfood export.

Verifies that TOML key-value pairs are converted to CSV rows using
Format Factory's TOML codec and CSV writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_TOML = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"

from toml.toml_to_csv import toml_to_csv


class TestTomlToCsvBasic:
    """Basic conversion tests."""

    def test_returns_data_row_count(self, tmp_path: Path) -> None:
        """Returns count of data rows (excluding header)."""
        dest = tmp_path / "out.csv"
        count = toml_to_csv(MINIMAL_TOML, dest)
        assert isinstance(count, int)
        assert count > 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .csv file is created."""
        dest = tmp_path / "out.csv"
        toml_to_csv(MINIMAL_TOML, dest)
        assert dest.exists()

    def test_minimal_toml_has_five_keys(self, tmp_path: Path) -> None:
        """minimal.toml has 5 top-level keys → 5 data rows."""
        dest = tmp_path / "out.csv"
        count = toml_to_csv(MINIMAL_TOML, dest)
        assert count == 5

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """CSV output is non-empty."""
        dest = tmp_path / "out.csv"
        toml_to_csv(MINIMAL_TOML, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0


class TestTomlToCsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row 'key,value' is present by default."""
        dest = tmp_path / "out.csv"
        toml_to_csv(MINIMAL_TOML, dest)
        content = dest.read_text(encoding="utf-8")
        first_line = content.splitlines()[0]
        assert "key" in first_line
        assert "value" in first_line

    def test_known_keys_in_output(self, tmp_path: Path) -> None:
        """Known TOML keys appear in the CSV output."""
        dest = tmp_path / "out.csv"
        toml_to_csv(MINIMAL_TOML, dest)
        content = dest.read_text(encoding="utf-8")
        # minimal.toml has title, version, enabled, server, database
        assert "title" in content
        assert "version" in content
        assert "enabled" in content

    def test_line_count_matches_data_plus_header(self, tmp_path: Path) -> None:
        """Total line count = data rows + 1 header."""
        dest = tmp_path / "out.csv"
        count = toml_to_csv(MINIMAL_TOML, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1  # data + header


class TestTomlToCsvOptions:
    """Option flag tests."""

    def test_no_header_excludes_header_row(self, tmp_path: Path) -> None:
        """include_header=False excludes the header row."""
        dest = tmp_path / "out.csv"
        count = toml_to_csv(MINIMAL_TOML, dest, include_header=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count
        # First line should be a data row, not "key,value"
        assert not lines[0].startswith("key,")

    def test_value_type_column_absent_by_default(self, tmp_path: Path) -> None:
        """include_value_type=False by default → 2 columns per row."""
        dest = tmp_path / "out.csv"
        toml_to_csv(MINIMAL_TOML, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        # Header line should have exactly 2 comma-separated fields
        header = lines[0]
        assert header.count(",") == 1

    def test_value_type_column_present_when_enabled(self, tmp_path: Path) -> None:
        """include_value_type=True adds a 'type' column."""
        dest = tmp_path / "out.csv"
        toml_to_csv(MINIMAL_TOML, dest, include_value_type=True)
        content = dest.read_text(encoding="utf-8")
        assert "type" in content
        # Should have type values like 'string', 'boolean', 'table'
        assert any(t in content for t in ["string", "boolean", "table", "integer"])


class TestTomlToCsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.csv"
        toml_to_csv(MINIMAL_TOML, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.csv"
        count = toml_to_csv(str(MINIMAL_TOML), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
