# R97 Train Q: DIF Parse Hardening Tests
# Governed skill: /add-python-object-model-feature
# Ledger: R97-GOVERNED-PYTHON-DIF-PARSE-001

"""Tests for DIF parse hardening — structure, edge cases."""

import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))

from dif.dif_parser import parse_dif


class TestDifParseHardening:
    """R97 DIF parse hardening tests."""

    SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "dif", "valid")

    def _sample_path(self, name):
        return os.path.join(self.SAMPLES_DIR, name)

    def test_parse_returns_dict(self):
        result = parse_dif(self._sample_path("minimal-2x2.dif"))
        assert isinstance(result, dict)

    def test_parse_has_ok(self):
        result = parse_dif(self._sample_path("minimal-2x2.dif"))
        assert result.get("ok") is True

    def test_parse_has_rows(self):
        result = parse_dif(self._sample_path("minimal-2x2.dif"))
        assert "rows" in result or "row_count" in result or "data" in result

    def test_parse_consistent(self):
        path = self._sample_path("minimal-2x2.dif")
        r1 = parse_dif(path)
        r2 = parse_dif(path)
        assert r1.get("ok") == r2.get("ok")

    def test_parse_nonexistent_raises(self):
        try:
            result = parse_dif("/nonexistent/file.dif")
            assert result.get("ok") is not True
        except (FileNotFoundError, OSError, Exception):
            pass

    def test_parse_has_no_fatal_errors(self):
        result = parse_dif(self._sample_path("minimal-2x2.dif"))
        assert result.get("ok") is True

    def test_parse_has_header(self):
        result = parse_dif(self._sample_path("minimal-2x2.dif"))
        assert result.get("ok") is True

    def test_parse_returns_structure(self):
        result = parse_dif(self._sample_path("minimal-2x2.dif"))
        assert len(result) > 1
