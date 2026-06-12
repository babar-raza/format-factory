"""
test_r56_tsv_gate5_neutral_model.py — TSV Gate 5: Neutral Model Tests.

Verifies the canonical dict schema returned by parse_tsv_strict() and
the capability descriptor from get_capabilities().

Gate 5 requirements:
- Result dict has all required keys: format, path, row_count, column_count,
  headers, rows, has_header, delimiter
- delimiter must be tab character
- Each row is a list of string values
- Capability descriptor lists supported/unsupported features
- Capability descriptor explicitly states commercial_product_ready: False

R56 Sprint: FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.tsv.tsv_parser import parse_tsv_strict, get_capabilities


def _write_tsv(tmp_path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


class TestTsvNeutralModelSchema:
    """Gate 5: canonical dict schema compliance for TSV."""

    def test_result_has_required_keys(self, tmp_path):
        p = _write_tsv(tmp_path, "a.tsv", "Name\tAge\nAlice\t30\nBob\t25\n")
        result = parse_tsv_strict(p)
        required = {"format", "path", "row_count", "column_count", "headers", "rows", "has_header", "delimiter"}
        missing = required - set(result.keys())
        assert not missing, f"Missing keys in neutral model: {missing}"

    def test_format_key_is_tsv(self, tmp_path):
        p = _write_tsv(tmp_path, "a.tsv", "x\ty\n1\t2\n")
        result = parse_tsv_strict(p)
        assert result["format"] == "tsv"

    def test_delimiter_is_tab(self, tmp_path):
        p = _write_tsv(tmp_path, "a.tsv", "Name\tAge\nAlice\t30\n")
        result = parse_tsv_strict(p)
        assert result["delimiter"] == "\t"

    def test_row_count_correct(self, tmp_path):
        p = _write_tsv(tmp_path, "a.tsv", "Name\tAge\nAlice\t30\nBob\t25\n")
        result = parse_tsv_strict(p)
        assert result["row_count"] == 2

    def test_column_count_correct(self, tmp_path):
        p = _write_tsv(tmp_path, "a.tsv", "Name\tAge\tCity\nAlice\t30\tNY\n")
        result = parse_tsv_strict(p)
        assert result["column_count"] == 3

    def test_headers_as_list(self, tmp_path):
        p = _write_tsv(tmp_path, "a.tsv", "Name\tAge\nAlice\t30\n")
        result = parse_tsv_strict(p)
        assert isinstance(result["headers"], list)
        assert result["headers"] == ["Name", "Age"]

    def test_rows_is_list_of_lists(self, tmp_path):
        p = _write_tsv(tmp_path, "a.tsv", "Name\tAge\nAlice\t30\nBob\t25\n")
        result = parse_tsv_strict(p)
        rows = result["rows"]
        assert isinstance(rows, list)
        assert all(isinstance(row, list) for row in rows)

    def test_row_values_are_strings(self, tmp_path):
        p = _write_tsv(tmp_path, "a.tsv", "Name\tAge\nAlice\t30\n")
        result = parse_tsv_strict(p)
        for row in result["rows"]:
            for val in row:
                assert isinstance(val, str), f"Cell value must be string, got {type(val)}"

    def test_has_header_is_bool(self, tmp_path):
        p = _write_tsv(tmp_path, "a.tsv", "Name\tAge\nAlice\t30\n")
        result = parse_tsv_strict(p)
        assert isinstance(result["has_header"], bool)

    def test_path_key_is_string(self, tmp_path):
        p = _write_tsv(tmp_path, "a.tsv", "x\n1\n")
        result = parse_tsv_strict(p)
        assert isinstance(result["path"], str)


class TestTsvCapabilityDescriptor:
    """Gate 5: capability descriptor from get_capabilities()."""

    def test_capabilities_has_required_keys(self):
        caps = get_capabilities()
        assert "format" in caps
        assert "supported" in caps
        assert "unsupported" in caps
        assert "commercial_product_ready" in caps

    def test_format_is_tsv(self):
        caps = get_capabilities()
        assert caps["format"] == "tsv"

    def test_commercial_product_ready_false(self):
        caps = get_capabilities()
        assert caps["commercial_product_ready"] is False

    def test_supported_features_nonempty(self):
        caps = get_capabilities()
        assert len(caps["supported"]) >= 3

    def test_unsupported_features_nonempty(self):
        caps = get_capabilities()
        assert len(caps["unsupported"]) >= 3

    def test_supported_includes_tab_delimiter(self):
        caps = get_capabilities()
        supported = set(caps["supported"])
        assert "tab_delimiter" in supported or "tsv_parse" in supported, \
            f"TSV-specific feature missing: {caps['supported']}"

    def test_unsupported_includes_formula(self):
        caps = get_capabilities()
        unsupported = set(caps["unsupported"])
        assert "formula_cells" in unsupported or "formula" in " ".join(unsupported), \
            f"formula_cells should be in unsupported: {caps['unsupported']}"
