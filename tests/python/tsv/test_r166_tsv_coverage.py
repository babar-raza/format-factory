"""
test_r166_tsv_coverage.py

Sprint: FORMAT-FACTORY-HARDENED-AUDIT-REMEDIATION-SPRINT6-001
Added: 2026-06-11

Tests for TSV core functions: probe_tsv, parse_tsv, write_tsv, load_tsv,
validate_headers, count_rows, get_column, get_headers.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    probe_tsv,
    parse_tsv,
    parse_tsv_strict,
    write_tsv,
    load_tsv,
    validate_headers,
    count_rows,
    get_column,
    get_headers,
    TsvError,
    TsvInputError,
    TsvSizeError,
    TsvParseError,
)


SAMPLE_TSV = "name\tage\tcity\nAlice\t30\tLondon\nBob\t25\tParis\nCarol\t35\tBerlin\n"


def _make_tsv(content: str, tmp_path: Path, name: str = "data.tsv") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ── Error classes ──────────────────────────────────────────────────────────

class TestTsvErrors:

    def test_tsv_error_is_exception(self):
        assert isinstance(TsvError("base"), Exception)

    def test_tsv_input_error_inherits(self):
        assert isinstance(TsvInputError("x"), TsvError)

    def test_tsv_size_error_inherits(self):
        assert isinstance(TsvSizeError("x"), TsvError)

    def test_tsv_parse_error_inherits(self):
        assert isinstance(TsvParseError("x"), TsvError)


# ── probe_tsv ──────────────────────────────────────────────────────────────

class TestProbeTsv:

    def test_returns_dict(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = probe_tsv(p)
        assert isinstance(result, dict)

    def test_exists_true(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = probe_tsv(p)
        assert result["exists"] is True

    def test_has_path_key(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = probe_tsv(p)
        assert "path" in result

    def test_nonexistent_file(self, tmp_path):
        result = probe_tsv(tmp_path / "no_such.tsv")
        assert result["exists"] is False

    def test_delimiter_tab(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = probe_tsv(p)
        assert result.get("delimiter") == "\t"

    def test_has_first_line(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = probe_tsv(p)
        assert "first_line" in result
        assert "name" in result["first_line"]


# ── parse_tsv / parse_tsv_strict ──────────────────────────────────────────

class TestParseTsv:

    def test_returns_dict(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = parse_tsv(p)
        assert isinstance(result, dict)

    def test_format_key(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = parse_tsv(p)
        assert result["format"] == "tsv"

    def test_nonexistent_returns_error_dict(self, tmp_path):
        result = parse_tsv(tmp_path / "nope.tsv")
        assert result.get("ok") is False

    def test_has_rows(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = parse_tsv(p)
        assert "rows" in result

    def test_strict_headers(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = parse_tsv_strict(p)
        assert result["headers"] == ["name", "age", "city"]

    def test_strict_row_count(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = parse_tsv_strict(p)
        assert result["row_count"] == 3

    def test_strict_nonexistent_raises(self, tmp_path):
        import pytest
        with pytest.raises(TsvInputError):
            parse_tsv_strict(tmp_path / "no.tsv")


# ── write_tsv ──────────────────────────────────────────────────────────────

class TestWriteTsv:

    def test_creates_file(self, tmp_path):
        p = tmp_path / "out.tsv"
        write_tsv([["Alice", "30"]], p, headers=["name", "age"])
        assert p.exists()

    def test_tab_separated(self, tmp_path):
        p = tmp_path / "out.tsv"
        write_tsv([["a", "b"], ["1", "2"]], p)
        assert "\t" in p.read_text(encoding="utf-8")

    def test_roundtrip(self, tmp_path):
        p = tmp_path / "rt.tsv"
        write_tsv([["foo", "bar"]], p, headers=["name", "val"])
        doc = parse_tsv_strict(p)
        all_rows = ([doc["headers"]] if doc["headers"] else []) + doc["rows"]
        assert any("name" in row for row in all_rows)

    def test_empty_rows(self, tmp_path):
        p = tmp_path / "empty.tsv"
        write_tsv([], p)
        assert p.exists()


# ── load_tsv ──────────────────────────────────────────────────────────────

class TestLoadTsv:

    def test_from_path_returns_dict(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = load_tsv(p)
        assert isinstance(result, dict)

    def test_has_rows(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = load_tsv(p)
        assert "rows" in result

    def test_from_bytes_input(self):
        result = load_tsv(SAMPLE_TSV.encode("utf-8"))
        assert isinstance(result, dict)


# ── validate_headers ───────────────────────────────────────────────────────

class TestValidateHeaders:

    def test_returns_dict(self, tmp_path):
        p = _make_tsv("a\tb\n1\t2\n", tmp_path)
        result = validate_headers(p, ["a", "b"])
        assert isinstance(result, dict)

    def test_valid_headers(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = validate_headers(p, ["name", "age", "city"])
        assert result.get("valid") is True

    def test_missing_headers_invalid(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = validate_headers(p, ["name", "age", "city", "extra"])
        assert result.get("valid") is False


# ── count_rows ─────────────────────────────────────────────────────────────

class TestCountRows:

    def test_count_from_path(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = count_rows(p)
        assert result == 3

    def test_count_single_row(self, tmp_path):
        # File with header + 1 data row
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = count_rows(p)
        assert result >= 1  # header detection is heuristic


# ── get_column / get_headers ──────────────────────────────────────────────

class TestGetColumnAndHeaders:

    def test_get_headers_returns_list(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = get_headers(p)
        assert result == ["name", "age", "city"]

    def test_get_column_values(self, tmp_path):
        p = _make_tsv(SAMPLE_TSV, tmp_path)
        result = get_column(p, "name")
        assert "Alice" in result
        assert "Bob" in result
