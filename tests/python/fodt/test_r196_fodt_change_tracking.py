"""
tests/python/fodt/test_r196_fodt_change_tracking.py

Sprint: FORMAT-FACTORY-FODT-FODS-DEEPENING-001
Tests for document_change_tracking_summary() and document_text_field_warnings().
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import document_change_tracking_summary, document_text_field_warnings


class TestFodtChangeTrackingSummary:
    def test_empty_doc_returns_zero_changes(self):
        result = document_change_tracking_summary({})
        assert result["tracked_change_count"] == 0

    def test_returns_required_keys(self):
        result = document_change_tracking_summary({})
        assert "tracked_change_count" in result
        assert "author_names" in result

    def test_author_names_is_list(self):
        result = document_change_tracking_summary({})
        assert isinstance(result["author_names"], list)

    def test_tracked_change_count_non_negative(self):
        result = document_change_tracking_summary({})
        assert result["tracked_change_count"] >= 0

    def test_real_file_valid_structure(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"))
        result = document_change_tracking_summary(doc)
        assert isinstance(result["tracked_change_count"], int)


class TestFodtTextFieldWarnings:
    def test_empty_doc_returns_empty_list(self):
        result = document_text_field_warnings({})
        assert result == []

    def test_returns_list(self):
        result = document_text_field_warnings({})
        assert isinstance(result, list)

    def test_real_file_returns_list(self):
        from src.python.fodt.parser import parse_fodt
        doc = parse_fodt(str(_REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"))
        result = document_text_field_warnings(doc)
        assert isinstance(result, list)
