"""R67 Train H: FODT minimal product readiness tests.

Low-risk readiness improvements: section/change-tracking coverage,
and helper function smoke tests.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt import parse_fodt, document_section_summary, document_change_tracking_summary


def _minimal_document():
    from src.python.fodt.neutral_model import build_document
    return build_document(
        odf_version_attr="1.3",
        mimetype="application/vnd.oasis.opendocument.text-flat-xml",
        blocks=[{"type": "paragraph", "text": "Hello world", "style": None}],
        lists=[],
        tables=[],
        warnings=[],
        unsupported_features=[],
        parse_errors=[],
    )


class TestDocumentSectionSummary:
    def test_returns_dict(self):
        doc = _minimal_document()
        result = document_section_summary(doc)
        assert isinstance(result, dict)

    def test_has_section_count_key(self):
        doc = _minimal_document()
        result = document_section_summary(doc)
        assert any(k in result for k in ("count", "section_count")), \
            f"Expected a count key, got: {list(result.keys())}"

    def test_no_crash_on_real_fodt_file(self):
        sample = PROJECT_ROOT / "samples" / "by-format" / "fodt" / "test_document.fodt"
        if not sample.exists():
            pytest.skip("Sample FODT not available")
        doc = parse_fodt(str(sample))
        result = document_section_summary(doc)
        assert isinstance(result, dict)


class TestDocumentChangeTrackingSummary:
    def test_returns_dict(self):
        doc = _minimal_document()
        result = document_change_tracking_summary(doc)
        assert isinstance(result, dict)

    def test_has_tracking_count_key(self):
        doc = _minimal_document()
        result = document_change_tracking_summary(doc)
        assert any(k in result for k in ("count", "tracked_change_count")), \
            f"Expected a count key, got: {list(result.keys())}"

    def test_no_crash_on_real_fodt_file(self):
        sample = PROJECT_ROOT / "samples" / "by-format" / "fodt" / "test_document.fodt"
        if not sample.exists():
            pytest.skip("Sample FODT not available")
        doc = parse_fodt(str(sample))
        result = document_change_tracking_summary(doc)
        assert isinstance(result, dict)
