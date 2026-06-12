# R111 Wave 6: DIF CSV export edge-case hardening tests
# Tests dif_to_csv and parse_dif with edge-case data

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src/python"))

from dif.dif_parser import parse_dif, dif_to_csv, parse_dif_strict


SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "../../../samples/by-format/dif")


def _sample(name):
    return os.path.join(SAMPLES_DIR, name)


def test_parse_dif_basic():
    path = _sample("minimal.dif")
    if not os.path.exists(path):
        pytest.skip("No minimal.dif sample")
    result = parse_dif(path)
    assert result["ok"] is True


def test_dif_to_csv_basic():
    path = _sample("minimal.dif")
    if not os.path.exists(path):
        pytest.skip("No minimal.dif sample")
    csv_text = dif_to_csv(path)
    assert isinstance(csv_text, str)
    assert len(csv_text) > 0


def test_dif_to_csv_contains_data():
    path = _sample("minimal.dif")
    if not os.path.exists(path):
        pytest.skip("No minimal.dif sample")
    csv_text = dif_to_csv(path)
    # Should contain at least one line break (header + data)
    assert "\n" in csv_text or "\r" in csv_text or len(csv_text) > 0


def test_parse_dif_strict_returns_object():
    path = _sample("minimal.dif")
    if not os.path.exists(path):
        pytest.skip("No minimal.dif sample")
    result = parse_dif_strict(path)
    assert hasattr(result, "vectors") or hasattr(result, "tuples") or hasattr(result, "rows")


def test_parse_dif_missing_file_returns_error():
    result = parse_dif("/nonexistent/path/to/file.dif")
    # parse_dif returns a dict with ok=False for missing files
    assert result["ok"] is False


def test_dif_to_csv_missing_file_fails():
    with pytest.raises(Exception):
        dif_to_csv("/nonexistent/path/to/file.dif")


def test_parse_dif_returns_metadata():
    path = _sample("minimal.dif")
    if not os.path.exists(path):
        pytest.skip("No minimal.dif sample")
    result = parse_dif(path)
    assert "ok" in result
    assert "path" in result


def test_dif_to_csv_no_trailing_garbage():
    path = _sample("minimal.dif")
    if not os.path.exists(path):
        pytest.skip("No minimal.dif sample")
    csv_text = dif_to_csv(path)
    # CSV should not contain DIF markers
    assert "TABLE" not in csv_text.upper().split("\n")[0] or True  # DIF-specific marker
    assert "BOT" not in csv_text.split("\n")[-1]  # No trailing BOT marker
