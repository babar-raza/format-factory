"""Tests for fodt_heading_count and fodt_has_tables.

Product deepening: FODT analytics — TC-H3-002-FODT / PDC-FODT-HEADING-TABLES-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import write_fodt, fodt_heading_count, fodt_has_tables


def _make_fodt(tmp_path, name, blocks, tables=None):
    doc = {
        "format_id": "fodt",
        "spec_version": "ODF 1.3",
        "odf_version": "1.3",
        "blocks": blocks,
        "lists": [],
        "tables": tables or [],
        "warnings": [],
        "unsupported_features": [],
        "parse_errors": [],
    }
    p = tmp_path / f"{name}.fodt"
    write_fodt(doc, str(p))
    return p


class TestFodtHeadingCount:
    def test_no_headings(self, tmp_path):
        blocks = [{"type": "paragraph", "runs": [{"text": "Hello"}]}]
        p = _make_fodt(tmp_path, "no_head", blocks)
        assert fodt_heading_count(str(p)) == 0

    def test_one_heading(self, tmp_path):
        blocks = [{"type": "heading", "level": 1, "runs": [{"text": "Title"}]}]
        p = _make_fodt(tmp_path, "one_head", blocks)
        assert fodt_heading_count(str(p)) == 1

    def test_two_headings(self, tmp_path):
        blocks = [
            {"type": "heading", "level": 1, "runs": [{"text": "H1"}]},
            {"type": "paragraph", "runs": [{"text": "body"}]},
            {"type": "heading", "level": 2, "runs": [{"text": "H2"}]},
        ]
        p = _make_fodt(tmp_path, "two_head", blocks)
        assert fodt_heading_count(str(p)) == 2

    def test_returns_int(self, tmp_path):
        blocks = [{"type": "paragraph", "runs": [{"text": "x"}]}]
        p = _make_fodt(tmp_path, "int_test", blocks)
        assert isinstance(fodt_heading_count(str(p)), int)

    def test_non_negative(self, tmp_path):
        blocks = []
        p = _make_fodt(tmp_path, "empty", blocks)
        assert fodt_heading_count(str(p)) >= 0


class TestFodtHasTables:
    def test_no_tables(self, tmp_path):
        blocks = [{"type": "paragraph", "runs": [{"text": "No tables"}]}]
        p = _make_fodt(tmp_path, "no_tbl", blocks)
        assert fodt_has_tables(str(p)) is False

    def test_one_table(self, tmp_path):
        blocks = [{"type": "paragraph", "runs": [{"text": "With table"}]}]
        tables = [{"name": "T1", "rows": [{"cells": [{"text": "A"}]}]}]
        p = _make_fodt(tmp_path, "one_tbl", blocks, tables=tables)
        assert fodt_has_tables(str(p)) is True

    def test_returns_bool(self, tmp_path):
        blocks = [{"type": "paragraph", "runs": [{"text": "x"}]}]
        p = _make_fodt(tmp_path, "bool_test", blocks)
        assert isinstance(fodt_has_tables(str(p)), bool)

    def test_sample_headings(self):
        samples = _REPO / "samples" / "by-format" / "fodt"
        p = samples / "headings-and-paragraphs.fodt"
        count = fodt_heading_count(str(p))
        assert isinstance(count, int)
        assert count >= 1

    def test_sample_table(self):
        samples = _REPO / "samples" / "by-format" / "fodt"
        p = samples / "table-basic.fodt"
        assert fodt_has_tables(str(p)) is True
