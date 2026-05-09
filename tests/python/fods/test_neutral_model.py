"""
test_neutral_model.py -- Unit tests for neutral_model module.

Covers: make_warning, build_workbook, validate_workbook (IR-FODS-018).
"""
from pathlib import Path

import pytest

from fods import parse_fods
from fods.constants import FORMAT_ID, SPEC_VERSION
from fods.neutral_model import build_workbook, make_warning, validate_workbook

SAMPLES = Path(__file__).resolve().parent.parent.parent.parent / "samples" / "by-format" / "fods"


def _sample(name):
    return str(SAMPLES / name)


# ---------------------------------------------------------------------------
# make_warning
# ---------------------------------------------------------------------------

def test_make_warning_required_fields():
    w = make_warning("TEST_CODE", "test message")
    assert w["code"] == "TEST_CODE"
    assert w["message"] == "test message"


def test_make_warning_no_source_by_default():
    w = make_warning("X", "y")
    assert "source" not in w


def test_make_warning_with_source():
    w = make_warning("X", "y", source="row:3 col:5")
    assert w["source"] == "row:3 col:5"


# ---------------------------------------------------------------------------
# build_workbook
# ---------------------------------------------------------------------------

def test_build_workbook_format_id():
    wb = build_workbook("1.3", None, [], [], [], [])
    assert wb["format_id"] == FORMAT_ID


def test_build_workbook_spec_version():
    wb = build_workbook("1.3", None, [], [], [], [])
    assert wb["spec_version"] == SPEC_VERSION


def test_build_workbook_sheet_count():
    sheets = [{"name": "A", "index": 0, "row_count": 0, "rows": []}]
    wb = build_workbook("1.3", None, sheets, [], [], [])
    assert wb["sheet_count"] == 1


def test_build_workbook_unsupported_sorted():
    wb = build_workbook("1.3", None, [], [], ["chart", "macros", "animation"], [])
    assert wb["unsupported_features"] == sorted(["chart", "macros", "animation"])


# ---------------------------------------------------------------------------
# validate_workbook violations
# ---------------------------------------------------------------------------

def test_validate_workbook_valid_minimal():
    wb = build_workbook("1.3", None, [], [], [], [])
    violations = validate_workbook(wb)
    assert violations == []


def test_validate_workbook_missing_format_id():
    wb = build_workbook("1.3", None, [], [], [], [])
    del wb["format_id"]
    violations = validate_workbook(wb)
    assert any("format_id" in v for v in violations)


def test_validate_workbook_wrong_format_id():
    wb = build_workbook("1.3", None, [], [], [], [])
    wb["format_id"] = "xlsx"
    violations = validate_workbook(wb)
    assert any("format_id" in v for v in violations)


def test_validate_workbook_sheet_count_mismatch():
    sheets = [{"name": "A", "index": 0, "row_count": 0, "rows": []}]
    wb = build_workbook("1.3", None, sheets, [], [], [])
    wb["sheet_count"] = 99
    violations = validate_workbook(wb)
    assert any("sheet_count" in v for v in violations)


def test_validate_workbook_sheet_missing_name():
    sheets = [{"index": 0, "row_count": 0, "rows": []}]  # no "name"
    wb = build_workbook("1.3", None, sheets, [], [], [])
    wb["sheet_count"] = 1
    violations = validate_workbook(wb)
    assert any("name" in v for v in violations)


def test_validate_workbook_sheet_wrong_index():
    sheets = [{"name": "X", "index": 5, "row_count": 0, "rows": []}]
    wb = build_workbook("1.3", None, sheets, [], [], [])
    violations = validate_workbook(wb)
    assert any("index" in v for v in violations)


def test_validate_workbook_row_wrong_index():
    rows = [{"index": 99, "cells": []}]
    sheets = [{"name": "A", "index": 0, "row_count": 1, "rows": rows}]
    wb = build_workbook("1.3", None, sheets, [], [], [])
    violations = validate_workbook(wb)
    assert any("index" in v for v in violations)


# ---------------------------------------------------------------------------
# Integration: parse_fods output passes validate_workbook
# ---------------------------------------------------------------------------

def test_parse_result_passes_neutral_model_validation():
    result = parse_fods(_sample("minimal-spreadsheet.fods"))
    assert "error" not in result
    violations = validate_workbook(result)
    # Violations become warnings in the result, but validate should find none
    # on a well-formed parse result (they would have been added as warnings already)
    neutral_violations = [v for v in violations if "NEUTRAL_MODEL_VIOLATION" not in str(v)]
    assert neutral_violations == [], f"Unexpected violations: {neutral_violations}"


def test_multi_sheet_passes_validation():
    result = parse_fods(_sample("multi-sheet-basic.fods"))
    assert "error" not in result
    violations = validate_workbook(result)
    neutral_violations = [v for v in violations if "NEUTRAL_MODEL_VIOLATION" not in str(v)]
    assert neutral_violations == []
