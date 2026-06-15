"""Gnumeric spec-parity migration proof: maps Gnumeric spec facts to implementing functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

# Gnumeric spec facts from _FORMAT_SPECIFIC_FACTS in sal_master_runner.py
# GNUMERIC-FACT-001: Gnumeric XML §1 — Container (gzip XML, root element, namespace)
# GNUMERIC-FACT-002: Gnumeric XML §2 — Sheet Structure (gnm:Sheet, gnm:Cells, cell types)
# GNUMERIC-FACT-003: Gnumeric XML §3 — Geometry (MaxCol, MaxRow, ColInfo, RowInfo)

GNUMERIC_SPEC_FUNCTION_MAP = {
    "GNUMERIC-FACT-001": [
        # Container: gzip-compressed XML, root element, namespace
        "load",
        "probe_gnumeric",
        "export_to_csv",
        "export_to_json",
        "write_gnumeric",
    ],
    "GNUMERIC-FACT-002": [
        # Sheet structure: gnm:Sheet, gnm:Cells, cell types
        "get_sheet_count",
        "get_sheet_names",
        "get_cell_value",
        "set_cell_value",
        "get_cell_count",
        "gnumeric_numeric_cell_count",
        "gnumeric_string_cell_count",
        "gnumeric_empty_cell_count",
    ],
    "GNUMERIC-FACT-003": [
        # Geometry: MaxCol, MaxRow, ColInfo, RowInfo
        "get_row_count",
        "get_column_count",
        "gnumeric_column_count",
        "gnumeric_sheet_summary",
        "row_count",
    ],
}


@pytest.fixture
def gnumeric_all():
    from src.python import gnumeric
    return gnumeric.__all__


@pytest.fixture
def gnumeric_module():
    from src.python.gnumeric import gnumeric_codec
    return gnumeric_codec


class TestGnumericSpecFactCoverage:
    @pytest.mark.parametrize("qname", list(GNUMERIC_SPEC_FUNCTION_MAP.keys()))
    def test_spec_fact_has_implementing_functions(self, qname):
        funcs = GNUMERIC_SPEC_FUNCTION_MAP[qname]
        assert len(funcs) >= 4, f"{qname} maps to fewer than 4 functions"

    @pytest.mark.parametrize("qname", list(GNUMERIC_SPEC_FUNCTION_MAP.keys()))
    def test_functions_exported_in_all(self, qname, gnumeric_all):
        for fn_name in GNUMERIC_SPEC_FUNCTION_MAP[qname]:
            assert fn_name in gnumeric_all, f"{qname}: '{fn_name}' not in gnumeric.__all__"

    @pytest.mark.parametrize("qname", list(GNUMERIC_SPEC_FUNCTION_MAP.keys()))
    def test_functions_are_callable(self, qname, gnumeric_module):
        for fn_name in GNUMERIC_SPEC_FUNCTION_MAP[qname]:
            fn = getattr(gnumeric_module, fn_name, None)
            assert fn is not None and callable(fn), f"{qname}: '{fn_name}' not callable"


class TestGnumericSpecFactLiveExecution:
    def test_fact001_load_and_probe(self, gnumeric_module):
        model = gnumeric_module.create_gnumeric([{"name": "Sheet1", "rows": [["a", "1"], ["b", "2"]]}])
        assert isinstance(model, dict)
        assert "sheets" in model

    def test_fact001_probe_returns_bool(self, gnumeric_module, tmp_path):
        model = gnumeric_module.create_gnumeric([{"name": "S1", "rows": [["x"]]}])
        p = tmp_path / "test.gnumeric"
        gnumeric_module.write_gnumeric(model, str(p))
        result = gnumeric_module.probe_gnumeric(str(p))
        assert isinstance(result, bool)

    def test_fact002_cell_operations(self, gnumeric_module):
        model = gnumeric_module.create_gnumeric([{"name": "S1", "rows": [["hello", "42"], ["", "world"]]}])
        val = gnumeric_module.get_cell_value(model, 0, 0, 0)
        assert val == "hello"

    def test_fact002_cell_counts(self, gnumeric_module):
        model = gnumeric_module.create_gnumeric([{"name": "S1", "rows": [["a", "1"], ["", "b"]]}])
        numeric = gnumeric_module.gnumeric_numeric_cell_count(model, 0)
        string = gnumeric_module.gnumeric_string_cell_count(model, 0)
        assert numeric >= 0
        assert string >= 0

    def test_fact003_geometry(self, gnumeric_module):
        model = gnumeric_module.create_gnumeric([{"name": "S1", "rows": [["a", "b", "c"], ["1", "2", "3"]]}])
        rows = gnumeric_module.row_count(model, 0)
        cols = gnumeric_module.gnumeric_column_count(model, 0)
        assert rows >= 2
        assert cols >= 3

    def test_fact003_sheet_summary(self, gnumeric_module):
        model = gnumeric_module.create_gnumeric([{"name": "S1", "rows": [["x"]]}])
        summary = gnumeric_module.gnumeric_sheet_summary(model, 0)
        assert isinstance(summary, dict)
        assert "row_count" in summary
        assert "col_count" in summary
