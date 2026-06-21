"""Tests for NDJSON Sprint 65 gap closure.

Closes:
  GAP-NDJSON-FOSS-NDJSON_HAS_U-001   (Ndjson Has Uniform Types)
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_has_uniform_types


class TestNdjsonHasUniformTypes:
    def test_return_type(self, tmp_path):
        f = tmp_path / "u.ndjson"
        f.write_text(json.dumps({"a": 1}) + "\n" + json.dumps({"b": 2}) + "\n")
        assert isinstance(ndjson_has_uniform_types(str(f)), bool)

    def test_true_for_uniform_dicts(self, tmp_path):
        f = tmp_path / "dicts.ndjson"
        f.write_text(json.dumps({"a": 1}) + "\n" + json.dumps({"b": 2}) + "\n")
        assert ndjson_has_uniform_types(str(f)) is True

    def test_false_for_mixed_types(self, tmp_path):
        f = tmp_path / "mixed.ndjson"
        f.write_text(json.dumps({"a": 1}) + "\n" + json.dumps([1, 2]) + "\n")
        assert ndjson_has_uniform_types(str(f)) is False

    def test_false_for_empty_file(self, tmp_path):
        f = tmp_path / "empty.ndjson"
        f.write_text("")
        assert ndjson_has_uniform_types(str(f)) is False

    def test_true_for_single_record(self, tmp_path):
        f = tmp_path / "single.ndjson"
        f.write_text(json.dumps({"x": 42}) + "\n")
        assert ndjson_has_uniform_types(str(f)) is True

    def test_consistent_across_calls(self, tmp_path):
        f = tmp_path / "consistent.ndjson"
        f.write_text(json.dumps({"a": 1}) + "\n")
        assert ndjson_has_uniform_types(str(f)) == ndjson_has_uniform_types(str(f))
