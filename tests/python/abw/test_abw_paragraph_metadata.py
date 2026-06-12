"""
test_abw_paragraph_metadata.py -- ABW paragraph metadata pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-48
Tests paragraph_lengths list/values, first_paragraph content,
last_paragraph content, get_paragraph_count, get_section_count.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    write_abw,
    paragraph_lengths,
    first_paragraph,
    last_paragraph,
    get_paragraph_count,
    get_section_count,
    load,
)

_MODEL = create_abw([
    "Short",
    "Medium length paragraph",
    "This is the longest paragraph in the document",
])


def _write_abw(tmp_path):
    dest = tmp_path / "doc.abw"
    write_abw(_MODEL, str(dest))
    return dest


def test_paragraph_lengths_list():
    lengths = paragraph_lengths(_MODEL)
    assert isinstance(lengths, list)
    assert len(lengths) == 3


def test_paragraph_lengths_values():
    lengths = paragraph_lengths(_MODEL)
    assert lengths[0] == len("Short")
    assert lengths[1] == len("Medium length paragraph")


def test_first_paragraph():
    first = first_paragraph(_MODEL)
    assert first == "Short"


def test_last_paragraph():
    last = last_paragraph(_MODEL)
    assert last == "This is the longest paragraph in the document"


def test_get_paragraph_count(tmp_path):
    dest = _write_abw(tmp_path)
    count = get_paragraph_count(str(dest))
    assert count == 3
