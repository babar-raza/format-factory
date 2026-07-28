"""
test_tc_a9665f07_csv_probe.py -- Probe CSV test coverage for TC-A9665F07.

Taskcard: TC-A9665F07
Gap: GAP-CSV-FOSS-PROBE_CSV-001 (missing_test_coverage)
Sprint: product-probe-gap-closure-20260614-001
Required test types: file_based_input, string_input, empty_input,
                     return_type_check, error_handling
Minimum tests: 10
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import probe_csv

_SAMPLES = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = _SAMPLES / "minimal-2x2.csv"
_QUOTED = _SAMPLES / "quoted-fields.csv"
_SINGLE = _SAMPLES / "single-cell.csv"
_INVALID = _SAMPLES / "invalid-unterminated-quote.csv"


# ---------------------------------------------------------------------------
# file_based_input
# ---------------------------------------------------------------------------

class TestCsvProbeFileBasedInput:
    def test_probe_returns_dict_for_path_obj(self):
        result = probe_csv(_MINIMAL)
        assert isinstance(result, dict)

    def test_probe_exists_true_for_valid_file(self):
        result = probe_csv(_MINIMAL)
        assert result["exists"] is True

    def test_probe_has_size_bytes_positive(self):
        result = probe_csv(_MINIMAL)
        assert result["size_bytes"] > 0

    def test_probe_quoted_file_detected(self):
        result = probe_csv(_QUOTED)
        assert result["exists"] is True
        assert result["size_bytes"] > 0

    def test_probe_single_cell_file(self):
        result = probe_csv(_SINGLE)
        assert result["exists"] is True
        assert result["sample_line_count"] >= 1


# ---------------------------------------------------------------------------
# string_input (string file paths)
# ---------------------------------------------------------------------------

class TestCsvProbeStringInput:
    def test_probe_accepts_string_path(self):
        result = probe_csv(str(_MINIMAL))
        assert isinstance(result, dict)

    def test_probe_string_path_exists_true(self):
        result = probe_csv(str(_MINIMAL))
        assert result["exists"] is True

    def test_probe_first_line_populated(self):
        result = probe_csv(str(_MINIMAL))
        assert isinstance(result["first_line"], str)
        assert len(result["first_line"]) > 0


# ---------------------------------------------------------------------------
# empty_input (missing / nonexistent file)
# ---------------------------------------------------------------------------

class TestCsvProbeEmptyInput:
    def test_probe_nonexistent_returns_dict(self, tmp_path):
        result = probe_csv(tmp_path / "ghost.csv")
        assert isinstance(result, dict)

    def test_probe_nonexistent_exists_false(self, tmp_path):
        result = probe_csv(tmp_path / "ghost.csv")
        assert result["exists"] is False

    def test_probe_empty_file_exists_true(self, tmp_path):
        f = tmp_path / "empty.csv"
        f.write_bytes(b"")
        result = probe_csv(f)
        assert result["exists"] is True
        assert result["size_bytes"] == 0


# ---------------------------------------------------------------------------
# return_type_check
# ---------------------------------------------------------------------------

class TestCsvProbeReturnType:
    def test_return_is_dict(self):
        result = probe_csv(_MINIMAL)
        assert isinstance(result, dict)

    def test_return_has_exists_key(self):
        result = probe_csv(_MINIMAL)
        assert "exists" in result

    def test_return_has_path_key(self):
        result = probe_csv(_MINIMAL)
        assert "path" in result

    def test_return_delimiter_is_string(self):
        result = probe_csv(_MINIMAL)
        assert isinstance(result.get("delimiter", ""), str)


# ---------------------------------------------------------------------------
# error_handling
# ---------------------------------------------------------------------------

class TestCsvProbeErrorHandling:
    def test_probe_never_raises_on_missing_file(self, tmp_path):
        # Must not raise; must return dict
        result = probe_csv(tmp_path / "no-such-file.csv")
        assert isinstance(result, dict)

    def test_probe_never_raises_on_invalid_content(self):
        result = probe_csv(_INVALID)
        assert isinstance(result, dict)
        assert result["exists"] is True
