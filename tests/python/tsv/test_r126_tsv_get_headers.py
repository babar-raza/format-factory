"""
tests/python/tsv/test_r126_tsv_get_headers.py

Sprint: FORMAT-FACTORY-AUTONOMOUS-EXECUTION-SPINE-BROAD-PRODUCT-MEGA-TRAIN-001
TC-TSV-GET-HEADERS: get_headers() — extract detected header row
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import get_headers, write_tsv

_SAMPLE_TSV = b"name\tage\tcity\nAlice\t30\tNY\nBob\t25\tLA\n"


class TestGetHeaders:
    def test_returns_list_for_headed_file(self, tmp_path):
        f = tmp_path / "data.tsv"
        f.write_bytes(_SAMPLE_TSV)
        result = get_headers(f)
        assert isinstance(result, list)

    def test_returns_correct_headers(self, tmp_path):
        f = tmp_path / "data.tsv"
        f.write_bytes(_SAMPLE_TSV)
        result = get_headers(f)
        assert result == ["name", "age", "city"]

    def test_accepts_string_path(self, tmp_path):
        f = tmp_path / "data.tsv"
        f.write_bytes(_SAMPLE_TSV)
        result = get_headers(str(f))
        assert result == ["name", "age", "city"]

    def test_accepts_path_object(self, tmp_path):
        f = tmp_path / "data.tsv"
        f.write_bytes(_SAMPLE_TSV)
        result = get_headers(Path(f))
        assert result == ["name", "age", "city"]

    def test_three_column_file(self, tmp_path):
        f = tmp_path / "data.tsv"
        write_tsv([["Alice", "30", "NY"]], f, headers=["name", "age", "city"])
        result = get_headers(f)
        assert len(result) == 3

    def test_single_column_with_header(self, tmp_path):
        content = b"fruit\napple\nbanana\n"
        f = tmp_path / "data.tsv"
        f.write_bytes(content)
        result = get_headers(f)
        # Single column: has_header True when >=2 rows and col count matches
        assert result is None or result == ["fruit"]

    def test_no_header_returns_none_or_list(self, tmp_path):
        # Single row only — no header detected (only 1 row)
        content = b"alice\t30\n"
        f = tmp_path / "data.tsv"
        f.write_bytes(content)
        result = get_headers(f)
        # Documented: single row has no header
        assert result is None

    def test_package_import(self):
        sys.path.insert(0, str(_REPO))
        import src.python.tsv as tsv_pkg
        assert hasattr(tsv_pkg, "get_headers")

    def test_in_all(self):
        sys.path.insert(0, str(_REPO))
        import src.python.tsv as tsv_pkg
        assert "get_headers" in tsv_pkg.__all__
