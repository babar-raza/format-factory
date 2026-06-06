"""
Tests for probe_abw() format-detection function.
Sprint: FORMAT-FACTORY-H6-QUEUE-DRIVEN-PRODUCT-SOURCE-PILOT-001
Task: h8-probe-abw-001
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root / "src" / "python"))


def test_probe_abw_importable():
    from abw.abw_codec import probe_abw
    assert callable(probe_abw)


def test_probe_abw_in_init():
    import abw
    assert hasattr(abw, "probe_abw")
    assert callable(abw.probe_abw)


def test_probe_abw_in_all():
    import abw
    assert "probe_abw" in abw.__all__


def test_probe_abw_valid_file(tmp_path):
    from abw.abw_codec import create_abw, write_abw, probe_abw
    model = create_abw(["Hello probe_abw"])
    p = tmp_path / "test.abw"
    write_abw(model, p)
    assert probe_abw(p) is True


def test_probe_abw_valid_bytes():
    from abw.abw_codec import probe_abw
    abw_bytes = b'<?xml version="1.0"?><abiword version="1.0"><section><p>test</p></section></abiword>'
    assert probe_abw(abw_bytes) is True


def test_probe_abw_valid_xml_string():
    from abw.abw_codec import probe_abw
    xml_str = '<abiword version="1.0"><section><p>probe test</p></section></abiword>'
    assert probe_abw(xml_str) is True


def test_probe_abw_rejects_html_bytes():
    from abw.abw_codec import probe_abw
    assert probe_abw(b"<html><body></body></html>") is False


def test_probe_abw_rejects_json_bytes():
    from abw.abw_codec import probe_abw
    assert probe_abw(b'{"key": "value"}') is False


def test_probe_abw_rejects_empty_bytes():
    from abw.abw_codec import probe_abw
    assert probe_abw(b"") is False


def test_probe_abw_rejects_nonexistent_path():
    from abw.abw_codec import probe_abw
    assert probe_abw("/nonexistent/does/not/exist.abw") is False


def test_probe_abw_returns_bool():
    from abw.abw_codec import probe_abw
    result = probe_abw(b"<abiword/>")
    assert isinstance(result, bool)


def test_probe_abw_roundtrip_matches_load(tmp_path):
    """File that loads successfully should also probe True."""
    from abw.abw_codec import create_abw, write_abw, probe_abw, load
    model = create_abw(["paragraph one", "paragraph two"])
    p = tmp_path / "roundtrip.abw"
    write_abw(model, p)
    assert probe_abw(p) is True
    loaded = load(p)
    assert loaded["is_abw"] is True


def test_probe_abw_does_not_mutate_file(tmp_path):
    """probe_abw must not modify the file on disk."""
    from abw.abw_codec import create_abw, write_abw, probe_abw
    model = create_abw(["unchanged"])
    p = tmp_path / "unchanged.abw"
    write_abw(model, p)
    before = p.read_bytes()
    probe_abw(p)
    after = p.read_bytes()
    assert before == after
