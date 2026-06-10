"""
tests/python/ndjson/test_r126_ndjson_export_csv.py

Sprint: FORMAT-FACTORY-AUTONOMOUS-EXECUTION-SPINE-BROAD-PRODUCT-MEGA-TRAIN-001
TC-NDJSON-EXPORT-CSV: export_to_csv() — dict records to RFC 4180 CSV
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import export_to_csv, write_ndjson


class TestNdjsonExportCsv:
    def test_returns_string(self):
        result = export_to_csv(b'{"a":1,"b":2}\n')
        assert isinstance(result, str)

    def test_header_row_present(self):
        result = export_to_csv(b'{"name":"Alice","age":"30"}\n')
        lines = result.strip().splitlines()
        assert lines[0] == "age,name"

    def test_data_row_present(self):
        result = export_to_csv(b'{"name":"Alice","age":"30"}\n')
        lines = result.strip().splitlines()
        assert lines[1] == "30,Alice"

    def test_multiple_records(self):
        data = b'{"id":"1","val":"A"}\n{"id":"2","val":"B"}\n'
        result = export_to_csv(data)
        lines = result.strip().splitlines()
        assert len(lines) == 3  # header + 2 data rows

    def test_sorted_headers(self):
        result = export_to_csv(b'{"z":"1","a":"2","m":"3"}\n')
        lines = result.strip().splitlines()
        assert lines[0] == "a,m,z"

    def test_union_of_keys(self):
        data = b'{"x":"1"}\n{"y":"2"}\n'
        result = export_to_csv(data)
        lines = result.strip().splitlines()
        assert lines[0] == "x,y"

    def test_missing_key_becomes_empty(self):
        data = b'{"a":"1","b":"2"}\n{"a":"3"}\n'
        result = export_to_csv(data)
        lines = result.strip().splitlines()
        assert lines[2] == "3,"

    def test_non_dict_records_excluded(self):
        data = b'{"a":"1"}\n[1,2]\n"hello"\n'
        result = export_to_csv(data)
        lines = result.strip().splitlines()
        assert len(lines) == 2  # header + 1 dict record

    def test_empty_source_returns_header_only(self):
        result = export_to_csv(b"")
        assert result.strip() == ""

    def test_csv_quoting_for_comma(self):
        data = b'{"v":"hello, world"}\n'
        result = export_to_csv(data)
        assert '"hello, world"' in result

    def test_from_file(self, tmp_path):
        out = tmp_path / "data.ndjson"
        write_ndjson([{"x": "1", "y": "2"}, {"x": "3", "y": "4"}], out)
        result = export_to_csv(out)
        lines = result.strip().splitlines()
        assert lines[0] == "x,y"
        assert len(lines) == 3

    def test_package_import(self):
        sys.path.insert(0, str(_REPO))
        import src.python.ndjson as ndjson_pkg
        assert hasattr(ndjson_pkg, "export_to_csv")

    def test_in_all(self):
        sys.path.insert(0, str(_REPO))
        import src.python.ndjson as ndjson_pkg
        assert "export_to_csv" in ndjson_pkg.__all__
