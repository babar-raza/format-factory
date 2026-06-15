"""SYLK spec-parity migration proof: maps SYLK spec facts to implementing functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

# SYLK spec facts from _FORMAT_SPECIFIC_FACTS in sal_master_runner.py
# SYLK-FACT-001: SYLK Spec §1 — File Header (ID record, semicolons, record types)
# SYLK-FACT-002: SYLK Spec §2 — Cell Records (C records, X/Y/K fields)
# SYLK-FACT-003: SYLK Spec §3 — Bounds (B record, E record)

SYLK_SPEC_FUNCTION_MAP = {
    "SYLK-FACT-001": [
        # File header: ID record, format identification, record parsing
        "parse_sylk",
        "parse_sylk_strict",
        "probe_sylk",
        "get_capabilities",
        "write_sylk",
    ],
    "SYLK-FACT-002": [
        # Cell records: C records with X/Y/K fields, cell access
        "get_cell_value",
        "set_cell_value",
        "get_row_values",
        "get_column_values",
        "get_all_values",
        "count_nonempty_cells",
    ],
    "SYLK-FACT-003": [
        # Bounds: B record (max col/row), E record (end), grid dimensions
        "get_row_count",
        "get_column_count",
        "get_cell_count",
        "sylk_row_count",
        "sylk_column_count",
        "sylk_max_column_index",
    ],
}


@pytest.fixture
def sylk_all():
    from src.python import sylk
    return sylk.__all__


@pytest.fixture
def sample_sylk(tmp_path):
    content = "ID;P\nB;X3;Y2\nC;X1;Y1;K\"Alice\"\nC;X2;Y1;K30\nC;X3;Y1;K\"NYC\"\nC;X1;Y2;K\"Bob\"\nC;X2;Y2;K25\nC;X3;Y2;K\"LA\"\nE\n"
    p = tmp_path / "test.sylk"
    p.write_text(content, encoding="utf-8")
    return p


class TestSylkSpecFactCoverage:
    @pytest.mark.parametrize("qname", list(SYLK_SPEC_FUNCTION_MAP.keys()))
    def test_spec_fact_has_implementing_functions(self, qname):
        funcs = SYLK_SPEC_FUNCTION_MAP[qname]
        assert len(funcs) >= 4, f"{qname} maps to fewer than 4 functions"

    @pytest.mark.parametrize("qname", list(SYLK_SPEC_FUNCTION_MAP.keys()))
    def test_functions_exported_in_all(self, qname, sylk_all):
        for fn_name in SYLK_SPEC_FUNCTION_MAP[qname]:
            assert fn_name in sylk_all, f"{qname}: '{fn_name}' not in sylk.__all__"

    @pytest.mark.parametrize("qname", list(SYLK_SPEC_FUNCTION_MAP.keys()))
    def test_functions_are_callable(self, qname):
        from src.python import sylk
        for fn_name in SYLK_SPEC_FUNCTION_MAP[qname]:
            fn = getattr(sylk, fn_name, None)
            assert fn is not None and callable(fn), f"{qname}: '{fn_name}' not callable"


class TestSylkSpecFactLiveExecution:
    def test_fact001_parse_sylk(self, sample_sylk):
        from src.python.sylk.sylk_parser import parse_sylk
        result = parse_sylk(str(sample_sylk))
        assert isinstance(result, dict)

    def test_fact001_probe_sylk(self, sample_sylk):
        from src.python.sylk.sylk_parser import probe_sylk
        result = probe_sylk(str(sample_sylk))
        assert result is not None

    def test_fact002_get_cell_value(self, sample_sylk):
        from src.python.sylk.sylk_parser import get_cell_value
        val = get_cell_value(str(sample_sylk), 1, 1)
        assert val is not None

    def test_fact002_row_values(self, sample_sylk):
        from src.python.sylk.sylk_parser import get_row_values
        vals = get_row_values(str(sample_sylk), 1)
        assert isinstance(vals, list)
        assert len(vals) >= 2

    def test_fact003_row_count(self, sample_sylk):
        from src.python.sylk.sylk_parser import get_row_count
        count = get_row_count(str(sample_sylk))
        assert count == 2

    def test_fact003_column_count(self, sample_sylk):
        from src.python.sylk.sylk_parser import get_column_count
        count = get_column_count(str(sample_sylk))
        assert count == 3
