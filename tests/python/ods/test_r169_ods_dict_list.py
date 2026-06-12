"""R169 — ODS get_sheet_as_dict_list tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from src.python.ods.ods_parser import get_sheet_as_dict_list, get_row_values, get_row_count


_SAMPLES = Path("samples/by-format/ods/valid")
_MINIMAL = _SAMPLES / "minimal-spreadsheet.ods"


class TestGetSheetAsDictListBasic:
    def test_returns_list(self):
        result = get_sheet_as_dict_list(_MINIMAL)
        assert isinstance(result, list)

    def test_each_item_is_dict(self):
        result = get_sheet_as_dict_list(_MINIMAL)
        for item in result:
            assert isinstance(item, dict)

    def test_header_row_not_in_result(self):
        """Row count in result is total_rows - 1 (header excluded)."""
        row_count = get_row_count(_MINIMAL)
        result = get_sheet_as_dict_list(_MINIMAL)
        if row_count >= 2:
            assert len(result) == row_count - 1
        else:
            assert result == []


class TestGetSheetAsDictListKeys:
    def test_keys_match_header_row(self):
        headers = [str(v) if v is not None else "" for v in get_row_values(_MINIMAL, 0, 0)]
        result = get_sheet_as_dict_list(_MINIMAL)
        if result:
            assert list(result[0].keys()) == headers

    def test_minimal_values_present(self):
        result = get_sheet_as_dict_list(_MINIMAL)
        assert len(result) >= 1

    def test_name_key_present(self):
        result = get_sheet_as_dict_list(_MINIMAL)
        assert "Name" in result[0]

    def test_value_key_present(self):
        result = get_sheet_as_dict_list(_MINIMAL)
        assert "Value" in result[0]

    def test_name_value_correct(self):
        result = get_sheet_as_dict_list(_MINIMAL)
        assert result[0]["Name"] == "Alpha"

    def test_value_is_numeric(self):
        result = get_sheet_as_dict_list(_MINIMAL)
        assert result[0]["Value"] == pytest.approx(42.0)


class TestGetSheetAsDictListEdge:
    def test_invalid_sheet_index_returns_empty(self):
        result = get_sheet_as_dict_list(_MINIMAL, sheet_index=999)
        assert result == []

    def test_negative_sheet_index_returns_empty(self):
        result = get_sheet_as_dict_list(_MINIMAL, sheet_index=-1)
        assert result == []
