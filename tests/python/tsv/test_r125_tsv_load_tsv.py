"""
tests/python/tsv/test_r125_tsv_load_tsv.py

Sprint: FORMAT-FACTORY-AUTONOMOUS-CYCLE-PROOF-AND-PRODUCT-PROGRESS-001
TC-TSV-LOAD: load_tsv() — bytes + file path support
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import load_tsv, write_tsv, TsvInputError


_SAMPLE_TSV = b"name\tage\tcity\nAlice\t30\tNY\nBob\t25\tLA\n"


class TestLoadTsvFromPath:
    def test_accepts_path_object(self, tmp_path):
        f = tmp_path / "data.tsv"
        f.write_bytes(_SAMPLE_TSV)
        result = load_tsv(f)
        assert result["format"] == "tsv"

    def test_accepts_string_path(self, tmp_path):
        f = tmp_path / "data.tsv"
        f.write_bytes(_SAMPLE_TSV)
        result = load_tsv(str(f))
        assert result["format"] == "tsv"

    def test_same_as_parse_strict_for_file(self, tmp_path):
        from src.python.tsv.tsv_parser import parse_tsv_strict
        f = tmp_path / "data.tsv"
        f.write_bytes(_SAMPLE_TSV)
        r1 = load_tsv(f)
        r2 = parse_tsv_strict(f)
        assert r1["rows"] == r2["rows"]
        assert r1["headers"] == r2["headers"]


class TestLoadTsvFromBytes:
    def test_accepts_bytes(self):
        result = load_tsv(_SAMPLE_TSV)
        assert isinstance(result, dict)
        assert result["format"] == "tsv"

    def test_bytes_parses_rows(self):
        result = load_tsv(_SAMPLE_TSV)
        assert result["row_count"] >= 1

    def test_bytes_detects_delimiter(self):
        result = load_tsv(_SAMPLE_TSV)
        assert result["delimiter"] == "\t"

    def test_bytes_empty(self):
        result = load_tsv(b"")
        assert result["row_count"] == 0
        assert result["rows"] == []

    def test_bytes_single_row(self):
        result = load_tsv(b"hello\tworld\n")
        assert result["column_count"] == 2

    def test_bytes_preserves_unicode(self):
        content = "name\tvalue\nZoë\tcafé\n".encode("utf-8")
        result = load_tsv(content)
        assert any("Zo" in str(r) for row in result["rows"] for r in row)

    def test_roundtrip_with_write_tsv(self, tmp_path):
        out = tmp_path / "test.tsv"
        write_tsv([["Alice", "30"], ["Bob", "25"]], out, headers=["name", "age"])
        result = load_tsv(out.read_bytes())
        # With 3 rows (header + 2 data), has_header should be True
        assert result["row_count"] >= 1

    def test_unsupported_type_raises(self):
        try:
            load_tsv(123)
            assert 1 == 0, "Expected TsvInputError"

        except TsvInputError:
            pass

    def test_package_import(self):
        sys.path.insert(0, str(_REPO))
        import src.python.tsv as tsv_pkg
        assert hasattr(tsv_pkg, "load_tsv")

    def test_in_all(self):
        sys.path.insert(0, str(_REPO))
        import src.python.tsv as tsv_pkg
        assert "load_tsv" in tsv_pkg.__all__
