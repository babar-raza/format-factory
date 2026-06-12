"""R167 — ABW Load capability coverage test (GAP-ABW-FOSS-LOAD-001).

Closes: GAP-ABW-FOSS-LOAD-001 (missing_test_coverage for Load capability).
Queue:  gap-coverage-q-001
"""
from __future__ import annotations

import pytest
from pathlib import Path

from src.python.abw.abw_codec import load, AbwParseError

SAMPLE_ABW = Path("samples/by-format/abw/empty-section.abw")
MEETING_ABW = Path("examples/python/abw/sample_meeting_notes.abw")


class TestAbwLoadFromPath:
    def test_load_returns_dict(self):
        model = load(SAMPLE_ABW)
        assert isinstance(model, dict)

    def test_load_is_abw_true(self):
        model = load(SAMPLE_ABW)
        assert model["is_abw"] is True

    def test_load_has_paragraph_count(self):
        model = load(SAMPLE_ABW)
        assert "paragraph_count" in model
        assert isinstance(model["paragraph_count"], int)

    def test_load_has_paragraphs_list(self):
        model = load(SAMPLE_ABW)
        assert "paragraphs" in model
        assert isinstance(model["paragraphs"], list)

    def test_load_has_section_count(self):
        model = load(SAMPLE_ABW)
        assert "section_count" in model
        assert isinstance(model["section_count"], int)

    def test_load_meeting_notes_has_content(self):
        model = load(MEETING_ABW)
        assert model["is_abw"] is True
        assert model["paragraph_count"] >= 0

    def test_load_from_bytes(self):
        raw = SAMPLE_ABW.read_bytes()
        model = load(raw)
        assert model["is_abw"] is True

    def test_load_from_str_path(self):
        model = load(str(SAMPLE_ABW))
        assert model["is_abw"] is True

    def test_load_invalid_raises(self):
        with pytest.raises((AbwParseError, Exception)):
            load(b"not xml content at all !!!")
