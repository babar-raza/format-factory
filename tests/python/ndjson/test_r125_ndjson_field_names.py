"""
tests/python/ndjson/test_r125_ndjson_field_names.py

Sprint: FORMAT-FACTORY-AUTONOMOUS-CYCLE-PROOF-AND-PRODUCT-PROGRESS-001
TC-NDJSON-FIELD-NAMES: get_field_names()
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    get_field_names,
)


class TestGetFieldNames:
    def test_returns_list(self):
        result = get_field_names(b'{"a":1}\n{"b":2}\n')
        assert isinstance(result, list)

    def test_returns_sorted(self):
        result = get_field_names(b'{"z":1,"a":2,"m":3}\n')
        assert result == ["a", "m", "z"]

    def test_unique_keys(self):
        result = get_field_names(b'{"x":1}\n{"x":2}\n{"x":3}\n')
        assert result == ["x"]

    def test_multiple_records_union(self):
        result = get_field_names(b'{"id":1,"name":"A"}\n{"id":2,"role":"admin"}\n')
        assert result == ["id", "name", "role"]

    def test_non_dict_records_excluded(self):
        result = get_field_names(b'{"a":1}\n[1,2]\n"hello"\n42\n')
        assert result == ["a"]

    def test_empty_source_returns_empty(self):
        result = get_field_names(b"")
        assert result == []

    def test_no_dict_records_returns_empty(self):
        result = get_field_names(b'[1,2]\n"hello"\n42\n')
        assert result == []

    def test_nested_fields_not_flattened(self):
        result = get_field_names(b'{"user":{"name":"Alice"},"id":1}\n')
        assert "user" in result
        assert "id" in result
        assert "name" not in result  # nested keys not extracted

    def test_from_file(self, tmp_path):
        out = tmp_path / "data.ndjson"
        write_ndjson([
            {"x": 1, "y": 2},
            {"x": 3, "z": 4},
        ], out)
        result = get_field_names(out)
        assert result == ["x", "y", "z"]

    def test_package_import(self):
        sys.path.insert(0, str(_REPO))
        import src.python.ndjson as ndjson_pkg
        assert hasattr(ndjson_pkg, "get_field_names")

    def test_in_all(self):
        sys.path.insert(0, str(_REPO))
        import src.python.ndjson as ndjson_pkg
        assert "get_field_names" in ndjson_pkg.__all__
