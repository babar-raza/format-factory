"""Tests for ndjson_deepest_nesting (Sprint 40 batch 3).

Closes:
  GAP-NDJSON-FOSS-NDJSON_DEEPE-001  (Ndjson Deepest Nesting)
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_deepest_nesting


@pytest.fixture
def nested_file(tmp_path):
    """File with deeply nested record (depth=3)."""
    path = tmp_path / "nested.ndjson"
    records = [{"a": {"b": {"c": 1}}}, {"x": 2}]
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return str(path)


@pytest.fixture
def flat_file(tmp_path):
    """File with flat records (depth=1)."""
    path = tmp_path / "flat.ndjson"
    records = [{"a": 1}, {"b": 2}]
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return str(path)


class TestNdjsonDeepestNesting:
    def test_return_type(self, flat_file):
        assert isinstance(ndjson_deepest_nesting(flat_file), int)

    def test_exact_1_for_flat_file(self, flat_file):
        assert ndjson_deepest_nesting(flat_file) == 1

    def test_exact_3_for_nested_file(self, nested_file):
        # a.b.c = depth 3
        assert ndjson_deepest_nesting(nested_file) == 3

    def test_positive(self, flat_file):
        assert ndjson_deepest_nesting(flat_file) >= 1

    def test_consistent_across_calls(self, nested_file):
        assert ndjson_deepest_nesting(nested_file) == ndjson_deepest_nesting(nested_file)
