"""
test_dif_export_colcount_w113_pipeline.py -- DIF export_to_html + get_column_count pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-113
Tests get_column_count returns int, correct count=3, export_to_html returns str,
exported HTML contains table tag, HTML has td tags.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"
_DIF_FILE = _SAMPLES / "numeric-row.dif"

from dif.dif_parser import (
    get_column_count,
    export_to_html,
)


def test_get_column_count_returns_int():
    result = get_column_count(_DIF_FILE)
    assert isinstance(result, int)


def test_get_column_count_correct():
    result = get_column_count(_DIF_FILE)
    assert result == 3


def test_export_to_html_returns_str():
    result = export_to_html(_DIF_FILE)
    assert isinstance(result, str)


def test_export_to_html_has_table_tag():
    result = export_to_html(_DIF_FILE)
    assert "<table>" in result


def test_export_to_html_has_td_tags():
    result = export_to_html(_DIF_FILE)
    assert "<td>" in result
