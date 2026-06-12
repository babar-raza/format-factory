"""
test_abw_metadata_section_pipeline.py -- ABW metadata + section pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-54
Tests get_metadata returns dict, get_section_count int, get_paragraph_count int,
extract_text list, get_section_count after write.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    write_abw,
    get_metadata,
    get_section_count,
    get_paragraph_count,
    extract_text,
)

_PARAGRAPHS = ["Introduction", "Main body text here.", "Conclusion"]
_MODEL = create_abw(_PARAGRAPHS)


def _write_abw(tmp_path):
    dest = tmp_path / "doc.abw"
    write_abw(_MODEL, str(dest))
    return dest


def test_get_metadata_returns_dict(tmp_path):
    dest = _write_abw(tmp_path)
    result = get_metadata(str(dest))
    assert isinstance(result, dict)


def test_get_section_count_int(tmp_path):
    dest = _write_abw(tmp_path)
    count = get_section_count(str(dest))
    assert isinstance(count, int)
    assert count >= 1


def test_get_paragraph_count(tmp_path):
    dest = _write_abw(tmp_path)
    count = get_paragraph_count(str(dest))
    assert count == 3


def test_extract_text_list(tmp_path):
    dest = _write_abw(tmp_path)
    texts = extract_text(str(dest))
    assert isinstance(texts, list)
    assert "Introduction" in texts


def test_extract_text_all_paragraphs(tmp_path):
    dest = _write_abw(tmp_path)
    texts = extract_text(str(dest))
    assert len(texts) == 3
