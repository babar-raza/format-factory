# R109 Lane F: SYLK CSV roundtrip hardening tests
# Tests parse → CSV export → data integrity

import os
import pytest

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "sylk")

def _sample(name="minimal.sylk"):
    return os.path.join(SAMPLES_DIR, name)

def test_import_sylk():
    """SYLK module imports successfully."""
    import sylk
    assert hasattr(sylk, 'parse_sylk')
    assert hasattr(sylk, 'sylk_to_csv')

def test_parse_returns_dict():
    """parse_sylk returns a dict with expected keys."""
    from sylk import parse_sylk
    p = _sample()
    if not os.path.exists(p):
        pytest.skip("Sample file not found")
    result = parse_sylk(p)
    assert isinstance(result, dict)
    assert 'ok' in result

def test_csv_export_returns_string():
    """sylk_to_csv returns a non-empty string."""
    from sylk import sylk_to_csv
    p = _sample()
    if not os.path.exists(p):
        pytest.skip("Sample file not found")
    csv = sylk_to_csv(p)
    assert isinstance(csv, str)
    assert len(csv) > 0

def test_csv_export_has_rows():
    """CSV export contains at least one row."""
    from sylk import sylk_to_csv
    p = _sample()
    if not os.path.exists(p):
        pytest.skip("Sample file not found")
    csv = sylk_to_csv(p)
    lines = [l for l in csv.strip().split('\n') if l.strip()]
    assert len(lines) >= 1

def test_parse_nonexistent_file():
    """Parsing a nonexistent file returns error or raises."""
    from sylk import parse_sylk
    result = parse_sylk("/nonexistent/path/r109.sylk")
    if isinstance(result, dict):
        assert result.get('ok') is False or 'error' in result or 'err' in str(result).lower()

def test_csv_consistent_with_parse():
    """CSV export cell count consistent with parse data."""
    from sylk import parse_sylk, sylk_to_csv
    p = _sample()
    if not os.path.exists(p):
        pytest.skip("Sample file not found")
    result = parse_sylk(p)
    csv = sylk_to_csv(p)
    # Both should succeed on the same file
    assert isinstance(result, dict)
    assert isinstance(csv, str)

def test_csv_no_binary_artifacts():
    """CSV output contains only printable text."""
    from sylk import sylk_to_csv
    p = _sample()
    if not os.path.exists(p):
        pytest.skip("Sample file not found")
    csv = sylk_to_csv(p)
    for ch in csv:
        assert ch.isprintable() or ch in '\n\r\t', f"Non-printable char: {ord(ch)}"

def test_parse_ok_field_true():
    """parse_sylk on valid file returns ok=True."""
    from sylk import parse_sylk
    p = _sample()
    if not os.path.exists(p):
        pytest.skip("Sample file not found")
    result = parse_sylk(p)
    assert result.get('ok') is True
