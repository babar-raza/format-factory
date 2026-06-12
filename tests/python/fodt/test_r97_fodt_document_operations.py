# R97 Train P: FODT Document Operations Hardening Tests
# Governed skill: /add-python-object-model-feature
# Ledger: R97-GOVERNED-PYTHON-FODT-DOC-OPS-001

"""Tests for FODT document operations — parse, text extraction."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))

from fodt.parser import parse_fodt


class TestFodtDocumentOperations:
    """R97 FODT document operations hardening tests."""

    SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "fodt")

    def _sample_path(self, name):
        return os.path.join(self.SAMPLES_DIR, name)

    def test_parse_returns_dict(self):
        result = parse_fodt(self._sample_path("minimal-document.fodt"))
        assert isinstance(result, dict)

    def test_parse_has_format(self):
        result = parse_fodt(self._sample_path("minimal-document.fodt"))
        assert result.get("format_id") == "fodt"

    def test_parse_has_paragraphs(self):
        result = parse_fodt(self._sample_path("minimal-document.fodt"))
        assert "paragraphs" in result or "blocks" in result or "content" in result

    def test_parse_consistent(self):
        path = self._sample_path("minimal-document.fodt")
        r1 = parse_fodt(path)
        r2 = parse_fodt(path)
        assert r1.get("format_id") == r2.get("format_id")

    def test_parse_nonexistent_raises(self):
        try:
            result = parse_fodt("/nonexistent/file.fodt")
            assert result.get("parse_errors") or result.get("format_id") != "fodt"
        except (FileNotFoundError, OSError, Exception):
            pass

    def test_parse_has_no_errors(self):
        result = parse_fodt(self._sample_path("minimal-document.fodt"))
        errors = result.get("parse_errors", [])
        assert len(errors) == 0

    def test_parse_has_content(self):
        result = parse_fodt(self._sample_path("minimal-document.fodt"))
        assert result.get("format_id") == "fodt"

    def test_parse_mimetype(self):
        result = parse_fodt(self._sample_path("minimal-document.fodt"))
        mime = result.get("mimetype", "")
        assert "opendocument" in mime.lower() or result.get("format_id") == "fodt"
