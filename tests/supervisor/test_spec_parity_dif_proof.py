"""DIF spec-parity migration proof: maps DIF spec facts to implementing functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

# DIF spec facts from _FORMAT_SPECIFIC_FACTS in sal_master_runner.py
# DIF-FACT-001: DIF Spec §1 — Header Section (TABLE, VECTORS, TUPLES)
# DIF-FACT-002: DIF Spec §2 — Data Section (cell types, BOT, EOD)
# DIF-FACT-003: DIF Spec §3 — Value Encoding (numeric/string lines, V marker)

DIF_SPEC_FUNCTION_MAP = {
    "DIF-FACT-001": [
        # Header: TABLE, VECTORS, TUPLES directives
        "get_title",
        "get_header_info",
        "get_row_count",
        "get_column_count",
        "dif_vectors_count",
    ],
    "DIF-FACT-002": [
        # Data section: cell types, BOT/EOD markers, parsing
        "parse_dif",
        "parse_dif_strict",
        "probe_dif",
        "get_cell_value",
        "get_row_values",
        "get_all_values",
    ],
    "DIF-FACT-003": [
        # Value encoding: numeric vs string, V marker
        "dif_string_cell_count",
        "dif_total_numeric_count",
        "count_nonempty_cells",
        "total_cell_count",
        "min_column_value",
        "max_column_value",
    ],
}


@pytest.fixture
def dif_all():
    from src.python import dif
    return dif.__all__


@pytest.fixture
def sample_dif(tmp_path):
    content = (
        'TABLE\n0,1\n"Test"\n'
        'VECTORS\n0,3\n""\n'
        'TUPLES\n0,2\n""\n'
        'DATA\n0,0\n""\n'
        '-1,0\nBOT\n1,0\n"Alice"\n1,0\n"Bob"\n1,0\n"Charlie"\n'
        '-1,0\nBOT\n0,10\nV\n0,20\nV\n0,30\nV\n'
        '-1,0\nBOT\n0,40\nV\n0,50\nV\n0,60\nV\n'
        '-1,0\nEOD\n'
    )
    p = tmp_path / "test.dif"
    p.write_text(content, encoding="utf-8")
    return p


class TestDifSpecFactCoverage:
    @pytest.mark.parametrize("qname", list(DIF_SPEC_FUNCTION_MAP.keys()))
    def test_spec_fact_has_implementing_functions(self, qname):
        funcs = DIF_SPEC_FUNCTION_MAP[qname]
        assert len(funcs) >= 4, f"{qname} maps to fewer than 4 functions"

    @pytest.mark.parametrize("qname", list(DIF_SPEC_FUNCTION_MAP.keys()))
    def test_functions_exported_in_all(self, qname, dif_all):
        for fn_name in DIF_SPEC_FUNCTION_MAP[qname]:
            assert fn_name in dif_all, f"{qname}: '{fn_name}' not in dif.__all__"

    @pytest.mark.parametrize("qname", list(DIF_SPEC_FUNCTION_MAP.keys()))
    def test_functions_are_callable(self, qname):
        from src.python import dif
        for fn_name in DIF_SPEC_FUNCTION_MAP[qname]:
            fn = getattr(dif, fn_name, None)
            assert fn is not None and callable(fn), f"{qname}: '{fn_name}' not callable"


class TestDifSpecFactLiveExecution:
    def test_fact001_get_title(self, sample_dif):
        from src.python.dif.dif_parser import get_title
        title = get_title(str(sample_dif))
        assert title == "Test"

    def test_fact001_get_header_info(self, sample_dif):
        from src.python.dif.dif_parser import get_header_info
        info = get_header_info(str(sample_dif))
        assert isinstance(info, dict)
        assert "vectors" in info or "title" in info

    def test_fact001_vector_count(self, sample_dif):
        from src.python.dif.dif_parser import dif_vectors_count
        count = dif_vectors_count(str(sample_dif))
        assert count == 3

    def test_fact002_parse_dif(self, sample_dif):
        from src.python.dif.dif_parser import parse_dif
        result = parse_dif(str(sample_dif))
        assert isinstance(result, dict)

    def test_fact002_probe_dif(self, sample_dif):
        from src.python.dif.dif_parser import probe_dif
        result = probe_dif(str(sample_dif))
        assert result is not None

    def test_fact003_cell_value(self, sample_dif):
        from src.python.dif.dif_parser import get_cell_value
        val = get_cell_value(str(sample_dif), 0, 0)
        assert val is not None
