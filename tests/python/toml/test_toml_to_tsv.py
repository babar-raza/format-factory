"""
Tests for toml_to_tsv dogfood export.

Verifies that TOML top-level keys are converted to TSV rows using
Format Factory's TOML codec and TSV writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_TOML = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"

from toml.toml_to_tsv import toml_to_tsv


class TestTomlToTsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.tsv"
        count = toml_to_tsv(MINIMAL_TOML, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .tsv file is created at the specified path."""
        dest = tmp_path / "out.tsv"
        toml_to_tsv(MINIMAL_TOML, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """TSV output is non-empty."""
        dest = tmp_path / "out.tsv"
        toml_to_tsv(MINIMAL_TOML, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_minimal_toml_returns_five_rows(self, tmp_path: Path) -> None:
        """minimal.toml has 5 top-level keys → 5 data rows."""
        dest = tmp_path / "out.tsv"
        count = toml_to_tsv(MINIMAL_TOML, dest)
        assert count == 5


class TestTomlToTsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row with key and value is written by default."""
        dest = tmp_path / "out.tsv"
        toml_to_tsv(MINIMAL_TOML, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "key" in first_line
        assert "value" in first_line

    def test_header_uses_tabs(self, tmp_path: Path) -> None:
        """Header fields are tab-separated."""
        dest = tmp_path / "out.tsv"
        toml_to_tsv(MINIMAL_TOML, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "\t" in first_line

    def test_toml_keys_in_output(self, tmp_path: Path) -> None:
        """TOML top-level keys appear in the TSV output."""
        dest = tmp_path / "out.tsv"
        toml_to_tsv(MINIMAL_TOML, dest)
        content = dest.read_text(encoding="utf-8")
        assert "title" in content

    def test_line_count_is_data_plus_header(self, tmp_path: Path) -> None:
        """Total non-empty lines = data rows + 1 header."""
        dest = tmp_path / "out.tsv"
        count = toml_to_tsv(MINIMAL_TOML, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1

    def test_boolean_serialized_as_lowercase(self, tmp_path: Path) -> None:
        """Boolean values serialized as 'true' or 'false'."""
        dest = tmp_path / "out.tsv"
        toml_to_tsv(MINIMAL_TOML, dest)
        content = dest.read_text(encoding="utf-8")
        assert "true" in content or "false" in content


class TestTomlToTsvOptions:
    """Option flag tests."""

    def test_no_headers_excludes_header_row(self, tmp_path: Path) -> None:
        """include_headers=False excludes the header row."""
        dest = tmp_path / "out.tsv"
        count = toml_to_tsv(MINIMAL_TOML, dest, include_headers=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count


class TestTomlToTsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.tsv"
        toml_to_tsv(MINIMAL_TOML, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.tsv"
        count = toml_to_tsv(str(MINIMAL_TOML), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
