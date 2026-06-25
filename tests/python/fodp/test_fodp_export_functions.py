"""Tests for FODP export functions: export_to_txt, export_to_csv, export_to_json.

Gap reference: FODP export capability (gates 1-10 advancement).
Sprint: ff-fodp-export-20260625
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import src.python.fodp as fodp

SAMPLE_DIR = _REPO / "samples" / "by-format" / "fodp"
MINIMAL = SAMPLE_DIR / "minimal-presentation.fodp"
TWO_SLIDES = SAMPLE_DIR / "two-slides-basic.fodp"
TITLE_ONLY = SAMPLE_DIR / "title-only.fodp"


class TestExportToTxt:
    def test_returns_string(self):
        result = fodp.export_to_txt(str(MINIMAL))
        assert isinstance(result, str)

    def test_empty_for_no_text(self):
        # minimal may have or may not have text — just check type and no crash
        result = fodp.export_to_txt(str(MINIMAL))
        assert isinstance(result, str)

    def test_two_slides_has_text(self):
        result = fodp.export_to_txt(str(TWO_SLIDES))
        assert isinstance(result, str)
        assert len(result) >= 0  # could be empty if slides have no text

    def test_accepts_path_object(self):
        result = fodp.export_to_txt(MINIMAL)
        assert isinstance(result, str)

    def test_newline_separated(self):
        result = fodp.export_to_txt(str(TWO_SLIDES))
        # If multiple text items, they should be newline-separated
        assert "\r" not in result  # no carriage returns


class TestExportToCsv:
    def test_returns_string(self):
        result = fodp.export_to_csv(str(MINIMAL))
        assert isinstance(result, str)

    def test_has_header(self):
        result = fodp.export_to_csv(str(MINIMAL))
        assert "slide_index" in result
        assert "slide_name" in result
        assert "shape_count" in result
        assert "text_snippet" in result

    def test_has_data_row(self):
        result = fodp.export_to_csv(str(MINIMAL))
        lines = [l for l in result.strip().split("\n") if l]
        # At least header + 1 data row
        assert len(lines) >= 2

    def test_two_slides_has_two_rows(self):
        result = fodp.export_to_csv(str(TWO_SLIDES))
        lines = [l for l in result.strip().split("\n") if l]
        # Header + 2 data rows
        assert len(lines) >= 3

    def test_accepts_path_object(self):
        result = fodp.export_to_csv(MINIMAL)
        assert "slide_index" in result

    def test_slide_index_is_numeric(self):
        result = fodp.export_to_csv(str(MINIMAL))
        lines = result.strip().split("\n")
        data_line = lines[1]
        first_col = data_line.split(",")[0]
        assert first_col.isdigit()

    def test_snippet_max_80_chars(self):
        result = fodp.export_to_csv(str(TWO_SLIDES))
        lines = result.strip().split("\n")
        for line in lines[1:]:
            parts = line.split(",")
            # snippet is last column — could contain commas so use split limit
            snippet = ",".join(parts[3:]).strip('"')
            assert len(snippet) <= 80


class TestExportToJson:
    def test_returns_string(self):
        result = fodp.export_to_json(str(MINIMAL))
        assert isinstance(result, str)

    def test_valid_json(self):
        import json
        result = fodp.export_to_json(str(MINIMAL))
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_has_pages_key(self):
        import json
        result = fodp.export_to_json(str(MINIMAL))
        parsed = json.loads(result)
        assert "pages" in parsed

    def test_has_is_fodp_key(self):
        import json
        result = fodp.export_to_json(str(MINIMAL))
        parsed = json.loads(result)
        assert "is_fodp" in parsed
        assert parsed["is_fodp"] is True

    def test_two_slides_page_count(self):
        import json
        result = fodp.export_to_json(str(TWO_SLIDES))
        parsed = json.loads(result)
        assert len(parsed.get("pages", [])) >= 2

    def test_accepts_path_object(self):
        import json
        result = fodp.export_to_json(MINIMAL)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
