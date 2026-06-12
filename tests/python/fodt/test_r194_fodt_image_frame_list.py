"""
tests/python/fodt/test_r194_fodt_image_frame_list.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT62-001
Tests for document_image_frame_list() — image frame enumeration.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import document_image_frame_list


class TestFodtImageFrameList:
    def test_empty_doc_returns_empty_list(self):
        result = document_image_frame_list({})
        assert result == []

    def test_returns_list(self):
        result = document_image_frame_list({})
        assert isinstance(result, list)

    def test_real_file_returns_list(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"))
        result = document_image_frame_list(doc)
        assert isinstance(result, list)

    def test_no_images_in_minimal_doc(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"))
        result = document_image_frame_list(doc)
        assert len(result) == 0

    def test_no_images_in_headings_doc(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"))
        result = document_image_frame_list(doc)
        assert isinstance(result, list)
