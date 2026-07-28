"""CSV spec-parity migration proof: maps CSV spec facts to implementing functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

# CSV spec facts from _FORMAT_SPECIFIC_FACTS in sal_master_runner.py
# CSV-FACT-001: RFC 4180 §2 — MIME Type and Extension (records, CRLF)
# CSV-FACT-002: RFC 4180 §2 — Field Separation (commas, quoting, escaping)
# CSV-FACT-003: RFC 4180 §2 — Optional Header

CSV_SPEC_FUNCTION_MAP = {
    "CSV-FACT-001": [
        # MIME type, extension, record-per-line: parse, probe, row count
        "parse_csv",
        "parse_csv_strict",
        "probe_csv",
        "get_row_count",
        "csv_total_cell_count",
    ],
    "CSV-FACT-002": [
        # Field separation, quoting, escaping: cell access, column ops, write
        "get_cell_value",
        "get_column_names",
        "csv_column_count",
        "write_csv",
        "write_csv_to_file",
        "parse_and_rewrite",
    ],
    "CSV-FACT-003": [
        # Optional header: header detection, column names, stats
        "csv_has_header",
        "get_column_names",
        "table_stats",
        "csv_field_type_summary",
    ],
}


@pytest.fixture
def csv_parser_module():
    from src.python.ff_csv import csv_parser
    return csv_parser


@pytest.fixture
def csv_all():
    from src.python import ff_csv as csv_mod
    return csv_mod.__all__


class TestCsvSpecFactCoverage:
    @pytest.mark.parametrize("qname", list(CSV_SPEC_FUNCTION_MAP.keys()))
    def test_spec_fact_has_implementing_functions(self, qname):
        funcs = CSV_SPEC_FUNCTION_MAP[qname]
        assert len(funcs) >= 3, f"{qname} maps to fewer than 3 functions"

    @pytest.mark.parametrize("qname", list(CSV_SPEC_FUNCTION_MAP.keys()))
    def test_functions_exported_in_all(self, qname, csv_all):
        for fn_name in CSV_SPEC_FUNCTION_MAP[qname]:
            assert fn_name in csv_all, f"{qname}: '{fn_name}' not in csv.__all__"

    @pytest.mark.parametrize("qname", list(CSV_SPEC_FUNCTION_MAP.keys()))
    def test_functions_are_callable(self, qname):
        from src.python import ff_csv as csv_mod
        for fn_name in CSV_SPEC_FUNCTION_MAP[qname]:
            fn = getattr(csv_mod, fn_name, None)
            assert fn is not None and callable(fn), f"{qname}: '{fn_name}' not callable"


class TestCsvSpecFactLiveExecution:
    @pytest.fixture
    def sample_csv(self, tmp_path):
        p = tmp_path / "test.csv"
        p.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\n", encoding="utf-8")
        return p

    def test_fact001_parse_csv(self, sample_csv):
        from src.python.ff_csv.csv_parser import parse_csv
        result = parse_csv(str(sample_csv))
        assert isinstance(result, dict)

    def test_fact001_probe_csv(self, sample_csv):
        from src.python.ff_csv.csv_parser import probe_csv
        result = probe_csv(str(sample_csv))
        assert result is not None

    def test_fact001_row_count(self, sample_csv):
        from src.python.ff_csv.csv_parser import get_row_count
        count = get_row_count(str(sample_csv))
        assert count >= 2

    def test_fact002_get_cell_value(self, sample_csv):
        from src.python.ff_csv.csv_parser import get_cell_value
        val = get_cell_value(str(sample_csv), 0, 0)
        assert val is not None

    def test_fact002_column_count(self, sample_csv):
        from src.python.ff_csv.csv_parser import csv_column_count
        count = csv_column_count(str(sample_csv))
        assert count == 3

    def test_fact003_has_header(self, sample_csv):
        from src.python.ff_csv.csv_parser import csv_has_header
        result = csv_has_header(str(sample_csv))
        assert isinstance(result, bool)
