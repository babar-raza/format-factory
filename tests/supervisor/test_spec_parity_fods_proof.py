"""Spec-parity migration proof for FODS format.

Verifies that each SAL spec fact for FODS has at least one matching
implementation function in the FODS codec. This is the first spec-parity
migration proof — a pattern to be replicated across all formats.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

SAL_FACTS_PATH = REPO_ROOT / ".local" / "sal-output" / "sal-facts-latest.json"

# Mapping: FODS spec fact qname -> list of functions that implement it
FODS_SPEC_FUNCTION_MAP = {
    # --- ODF-shared facts (common to all flat ODF formats) ---
    "ODF-FACT-NAMESPACE": [
        "parse_fods",
        "parse_fods_strict",
    ],
    "ODF-FACT-ROOT-ELEMENT": [
        "parse_fods",
        "workbook_to_xml",
    ],
    "ODF-FACT-STYLES": [
        "workbook_style_family_list",
        "workbook_row_style_summary",
        "workbook_column_style_summary",
    ],
    "ODF-FACT-METADATA": [
        "workbook_stats",
        "parse_fods",
    ],
    "ODF-FACT-BODY": [
        "parse_fods_strict",
        "workbook_stats",
    ],
    "ODF-SHEET-FACT-TABLE": [
        "find_sheet_by_name",
        "fods_sheet_count",
        "workbook_sheet_summary",
    ],
    "ODF-SHEET-FACT-ROW": [
        "workbook_row_count",
        "workbook_empty_rows",
    ],
    "ODF-SHEET-FACT-CELL": [
        "workbook_get_cell_value",
        "workbook_set_cell_value",
        "workbook_cell_type_matrix",
        "fods_total_cell_count",
    ],
    # --- FODS-specific facts ---
    "FODS-FACT-001": [
        "parse_fods",
        "parse_fods_strict",
        "write_fods",
        "workbook_to_xml",
    ],
    "FODS-FACT-002": [
        "find_sheet_by_name",
        "workbook_sheet_summary",
        "workbook_sheet_order",
        "workbook_add_sheet",
        "workbook_rename_sheet",
        "workbook_remove_sheet",
        "fods_sheet_count",
    ],
    "FODS-FACT-003": [
        "workbook_type_distribution",
        "workbook_cell_type_matrix",
        "workbook_get_cell_value",
        "workbook_set_cell_value",
        "workbook_stats",
    ],
    "FODS-FACT-004": [
        "workbook_row_style_summary",
        "workbook_column_style_summary",
        "workbook_style_family_list",
        "workbook_column_width_summary",
    ],
    "FODS-FACT-005": [
        "workbook_formula_list",
        "workbook_formula_edit_policy",
    ],
    "FODS-FACT-006": [
        "workbook_column_count",
        "workbook_max_column_count",
        "workbook_column_width_summary",
    ],
    "FODS-FACT-007": [
        "workbook_merged_cell_summary",
        "workbook_cell_range",
    ],
    # --- Additional FODS facts discovered in expanded SAL output ---
    "FODS-FACT-008": [
        "workbook_merged_cell_summary",
        "workbook_cell_range",
    ],
    "FODS-FACT-009": [
        "workbook_formula_list",
        "workbook_formula_edit_policy",
    ],
    "FODS-FACT-010": [
        "workbook_style_family_list",
        "workbook_row_style_summary",
        "workbook_column_style_summary",
    ],
    "FODS-FACT-011": [
        "workbook_stats",
        "parse_fods",
    ],
    "FODS-FACT-012": [
        "workbook_type_distribution",
        "workbook_cell_type_matrix",
    ],
    "FODS-FACT-013": [
        "workbook_get_cell_value",
        "workbook_set_cell_value",
    ],
    "FODS-FACT-014": [
        "workbook_column_width_summary",
        "workbook_column_count",
    ],
}


@pytest.fixture(scope="module")
def sal_fods_facts():
    if not SAL_FACTS_PATH.is_file():
        pytest.skip("SAL output file not found")
    data = json.loads(SAL_FACTS_PATH.read_text(encoding="utf-8"))
    for entry in data.get("results", []):
        if entry.get("format_id", "").upper() == "FODS":
            return entry.get("spec_facts", [])
    pytest.skip("No FODS facts in SAL output")


@pytest.fixture(scope="module")
def fods_exports():
    from src.python.fods import __all__
    return set(__all__)


class TestFodsSpecParity:
    def test_sal_has_fods_facts(self, sal_fods_facts):
        assert len(sal_fods_facts) >= 5

    def test_all_qnames_present(self, sal_fods_facts):
        qnames = {f["qname"] for f in sal_fods_facts}
        for expected in FODS_SPEC_FUNCTION_MAP:
            assert expected in qnames, f"Missing spec fact {expected}"

    def test_fact_001_flat_xml_variant(self, fods_exports):
        for fn in FODS_SPEC_FUNCTION_MAP["FODS-FACT-001"]:
            assert fn in fods_exports, f"{fn} not exported"

    def test_fact_002_spreadsheet_structure(self, fods_exports):
        for fn in FODS_SPEC_FUNCTION_MAP["FODS-FACT-002"]:
            assert fn in fods_exports, f"{fn} not exported"

    def test_fact_003_cell_value_types(self, fods_exports):
        for fn in FODS_SPEC_FUNCTION_MAP["FODS-FACT-003"]:
            assert fn in fods_exports, f"{fn} not exported"

    def test_fact_004_styles(self, fods_exports):
        for fn in FODS_SPEC_FUNCTION_MAP["FODS-FACT-004"]:
            assert fn in fods_exports, f"{fn} not exported"

    def test_fact_005_formulas(self, fods_exports):
        for fn in FODS_SPEC_FUNCTION_MAP["FODS-FACT-005"]:
            assert fn in fods_exports, f"{fn} not exported"

    def test_all_mapped_functions_are_callable(self):
        import src.python.fods as fods_module
        for qname, funcs in FODS_SPEC_FUNCTION_MAP.items():
            for fn in funcs:
                obj = getattr(fods_module, fn, None)
                assert callable(obj), f"{fn} (for {qname}) is not callable"

    def test_coverage_is_complete(self, sal_fods_facts):
        """Every canonical SAL fact (non-EX auto-generated) has at least one mapped function."""
        mapped_qnames = set(FODS_SPEC_FUNCTION_MAP.keys())
        # Filter out auto-generated facts: EX-* examples and reversed-prefix FACT-FODS-NNN
        sal_qnames = {f["qname"] for f in sal_fods_facts
                      if not f["qname"].startswith("FACT-FODS-")}
        unmapped = sal_qnames - mapped_qnames
        assert unmapped == set(), f"Unmapped spec facts: {unmapped}"

    def test_minimum_function_coverage_per_fact(self):
        for qname, funcs in FODS_SPEC_FUNCTION_MAP.items():
            assert len(funcs) >= 2, f"{qname} has only {len(funcs)} function(s)"
