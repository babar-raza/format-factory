"""
test_dogfood_abw_gnumeric_pipeline.py -- ABW→Gnumeric cross-format pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-19
Tests that text data extracted from ABW documents can be fed into Gnumeric
to build a spreadsheet, and that the resulting sheet has correct cell content.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_ABW_SAMPLES = _REPO / "samples" / "by-format" / "abw"

from abw.abw_codec import load as load_abw, extract_text, get_word_count
from gnumeric.gnumeric_codec import (
    create_gnumeric,
    get_cell_value,
    get_row_count,
    get_column_count,
    write_gnumeric,
    load as load_gnumeric,
)


def _abw_paragraphs_to_gnumeric():
    """Load ABW sample and build a Gnumeric model from its paragraphs."""
    m = load_abw(str(_ABW_SAMPLES / "two-paragraphs.abw"))
    paragraphs = m["paragraphs"]
    rows = [[p] for p in paragraphs]
    return create_gnumeric([{"name": "Sheet1", "rows": rows}])


def test_abw_paragraphs_populate_gnumeric_rows():
    gm = _abw_paragraphs_to_gnumeric()
    assert get_row_count(gm, 0) == 2


def test_abw_first_paragraph_in_gnumeric_cell():
    gm = _abw_paragraphs_to_gnumeric()
    cell_val = get_cell_value(gm, 0, 0, 0)
    assert cell_val == "First paragraph."


def test_abw_second_paragraph_in_gnumeric_cell():
    gm = _abw_paragraphs_to_gnumeric()
    cell_val = get_cell_value(gm, 0, 1, 0)
    assert cell_val == "Second paragraph."


def test_abw_gnumeric_pipeline_write_reload(tmp_path):
    gm = _abw_paragraphs_to_gnumeric()
    dest = tmp_path / "abw_to_gnumeric.gnumeric"
    write_gnumeric(gm, str(dest))
    gm2 = load_gnumeric(str(dest))
    assert get_cell_value(gm2, 0, 0, 0) == "First paragraph."
    assert get_row_count(gm2, 0) == 2
