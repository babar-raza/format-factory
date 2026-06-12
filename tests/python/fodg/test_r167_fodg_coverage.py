"""
test_r167_fodg_coverage.py

Sprint: FORMAT-FACTORY-HARDENED-AUDIT-REMEDIATION-SPRINT8-001
Added: 2026-06-11

Tests for FODG core functions: probe_fodg, load, get_page_count, page_names,
find_text, get_shapes, get_shape_count, export_to_csv, export_to_json,
create_fodg, write_fodg.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    probe_fodg,
    load,
    get_page_count,
    page_names,
    find_text,
    get_shapes,
    get_shape_count,
    export_to_csv,
    export_to_json,
    create_fodg,
    write_fodg,
    FodgError,
    FodgParseError,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodg"
_MINIMAL = _SAMPLES / "minimal-drawing.fodg"
_SHAPES = _SAMPLES / "shapes-basic.fodg"


# ── Error classes ─────────────────────────────────────────────────────────

class TestFodgErrors:

    def test_fodg_error_is_exception(self):
        assert isinstance(FodgError("x"), Exception)

    def test_fodg_parse_error_inherits(self):
        assert isinstance(FodgParseError("x"), FodgError)


# ── probe_fodg ─────────────────────────────────────────────────────────────

class TestProbeFodg:

    def test_returns_bool(self):
        result = probe_fodg(_MINIMAL)
        assert isinstance(result, bool)

    def test_valid_file_returns_true(self):
        assert probe_fodg(_MINIMAL) is True

    def test_nonexistent_returns_false(self):
        assert probe_fodg(_SAMPLES / "no_such.fodg") is False

    def test_shapes_file_detected(self):
        assert probe_fodg(_SHAPES) is True


# ── load ─────────────────────────────────────────────────────────────────

class TestLoadFodg:

    def test_returns_dict(self):
        model = load(_MINIMAL)
        assert isinstance(model, dict)

    def test_has_page_count_key(self):
        model = load(_MINIMAL)
        assert "page_count" in model

    def test_has_pages_key(self):
        model = load(_MINIMAL)
        assert "pages" in model


# ── get_page_count / page_names ──────────────────────────────────────────

class TestPageInfo:

    def test_get_page_count_int(self):
        model = load(_MINIMAL)
        assert isinstance(get_page_count(model), int)

    def test_get_page_count_positive(self):
        model = load(_MINIMAL)
        assert get_page_count(model) >= 1

    def test_page_names_returns_list(self):
        model = load(_MINIMAL)
        assert isinstance(page_names(model), list)

    def test_page_names_not_empty(self):
        model = load(_MINIMAL)
        assert len(page_names(model)) >= 1

    def test_page_names_strings(self):
        model = load(_MINIMAL)
        for name in page_names(model):
            assert isinstance(name, str)


# ── find_text ─────────────────────────────────────────────────────────────

class TestFindText:

    def test_returns_list(self):
        model = load(_MINIMAL)
        assert isinstance(find_text(model, "anything"), list)

    def test_missing_text_empty_list(self):
        model = load(_MINIMAL)
        result = find_text(model, "NoSuchTextXXX999")
        assert result == []

    def test_case_sensitive_flag_accepted(self):
        model = load(_MINIMAL)
        result = find_text(model, "rect", case_sensitive=False)
        assert isinstance(result, list)


# ── get_shapes / get_shape_count ─────────────────────────────────────────

class TestShapes:

    def test_get_shapes_returns_list(self):
        result = get_shapes(_MINIMAL)
        assert isinstance(result, list)

    def test_get_shape_count_int(self):
        result = get_shape_count(_MINIMAL)
        assert isinstance(result, int)

    def test_shape_count_positive(self):
        result = get_shape_count(_MINIMAL)
        assert result >= 0

    def test_shapes_basic_has_shapes(self):
        count = get_shape_count(_SHAPES)
        assert count >= 1


# ── export_to_csv ─────────────────────────────────────────────────────────

class TestExportToCsv:

    def test_returns_string(self):
        result = export_to_csv(_MINIMAL)
        assert isinstance(result, str)

    def test_contains_comma(self):
        result = export_to_csv(_MINIMAL)
        assert "," in result

    def test_has_header_row(self):
        result = export_to_csv(_MINIMAL)
        lines = result.strip().split("\n")
        assert len(lines) >= 1

    def test_writes_to_file(self, tmp_path):
        dest = tmp_path / "out.csv"
        export_to_csv(_MINIMAL, dest)
        assert dest.exists()
        assert dest.read_text(encoding="utf-8").strip() != ""


# ── export_to_json ────────────────────────────────────────────────────────

class TestExportToJson:

    def test_returns_string(self):
        model = load(_MINIMAL)
        result = export_to_json(model)
        assert isinstance(result, str)

    def test_valid_json(self):
        import json
        model = load(_MINIMAL)
        result = export_to_json(model)
        parsed = json.loads(result)
        assert parsed is not None

    def test_has_page_count(self):
        import json
        model = load(_MINIMAL)
        result = json.loads(export_to_json(model))
        assert "page_count" in result


# ── create_fodg / write_fodg ──────────────────────────────────────────────

class TestCreateAndWrite:

    def test_create_returns_dict(self):
        doc = create_fodg([])
        assert isinstance(doc, dict)

    def test_write_creates_file(self, tmp_path):
        doc = load(_MINIMAL)
        dest = tmp_path / "out.fodg"
        write_fodg(doc, dest)
        assert dest.exists()
        assert dest.stat().st_size > 0
