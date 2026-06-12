"""
Tests for export_to_txt.

Sprint: FORMAT-FACTORY-AUTONOMOUS-FILE-FORMAT-ACQUISITION-MEGA-TRAIN-001
Task: h9-abw-txt-export-001

Run from repo root (with PYTHONPATH set):
    python -m pytest tests/python/abw/test_r119_abw_export_to_txt.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from abw.abw_codec import (
    export_to_txt,
    create_abw,
    write_abw,
)
import abw as abw_pkg


# ---------------------------------------------------------------------------
# 1. export_to_txt — importable and exported
# ---------------------------------------------------------------------------

def test_export_to_txt_importable():
    from abw.abw_codec import export_to_txt as e
    assert callable(e)


def test_export_to_txt_in_init():
    assert hasattr(abw_pkg, "export_to_txt")


def test_export_to_txt_in_all():
    assert "export_to_txt" in abw_pkg.__all__


# ---------------------------------------------------------------------------
# 2. export_to_txt — basic usage
# ---------------------------------------------------------------------------

def test_export_to_txt_from_file(tmp_path):
    model = create_abw(["Hello world", "Second line"])
    out = tmp_path / "doc.abw"
    write_abw(model, out)
    result = export_to_txt(out)
    assert "Hello world" in result
    assert "Second line" in result


def test_export_to_txt_from_path_str(tmp_path):
    model = create_abw(["Hello world"])
    out = tmp_path / "doc.abw"
    write_abw(model, out)
    result = export_to_txt(str(out))
    assert "Hello world" in result


def test_export_to_txt_from_bytes(tmp_path):
    model = create_abw(["Paragraph text"])
    out = tmp_path / "doc.abw"
    write_abw(model, out)
    result = export_to_txt(out.read_bytes())
    assert "Paragraph text" in result


def test_export_to_txt_from_xml_string():
    xml = '<?xml version="1.0"?><abiword template="false" styles="unlocked" version="1.0" fileformat="1.0"><section><p>My text</p></section></abiword>'
    result = export_to_txt(xml)
    assert "My text" in result


# ---------------------------------------------------------------------------
# 3. export_to_txt — content correctness
# ---------------------------------------------------------------------------

def test_export_to_txt_newline_separated(tmp_path):
    model = create_abw(["Line one", "Line two", "Line three"])
    out = tmp_path / "doc.abw"
    write_abw(model, out)
    result = export_to_txt(out)
    assert "\n" in result
    lines = result.split("\n")
    non_empty = [l for l in lines if l.strip()]
    assert len(non_empty) == 3


def test_export_to_txt_returns_string(tmp_path):
    model = create_abw(["text"])
    out = tmp_path / "doc.abw"
    write_abw(model, out)
    result = export_to_txt(out)
    assert isinstance(result, str)


def test_export_to_txt_empty_doc(tmp_path):
    model = create_abw([])
    out = tmp_path / "empty.abw"
    write_abw(model, out)
    result = export_to_txt(out)
    assert isinstance(result, str)
    assert result == ""


def test_export_to_txt_single_paragraph(tmp_path):
    model = create_abw(["Only one paragraph"])
    out = tmp_path / "single.abw"
    write_abw(model, out)
    result = export_to_txt(out)
    assert result == "Only one paragraph"


def test_export_to_txt_preserves_unicode(tmp_path):
    model = create_abw(["Héllo wörld", "日本語テスト"])
    out = tmp_path / "unicode.abw"
    write_abw(model, out)
    result = export_to_txt(out)
    assert "Héllo wörld" in result
    assert "日本語テスト" in result


def test_export_to_txt_does_not_include_xml_tags(tmp_path):
    model = create_abw(["Clean text"])
    out = tmp_path / "clean.abw"
    write_abw(model, out)
    result = export_to_txt(out)
    assert "<" not in result
    assert ">" not in result


# ---------------------------------------------------------------------------
# 4. Roundtrip: create → write → export_to_txt
# ---------------------------------------------------------------------------

def test_roundtrip_paragraphs_preserved(tmp_path):
    paragraphs = ["First", "Second", "Third"]
    model = create_abw(paragraphs)
    out = tmp_path / "rt.abw"
    write_abw(model, out)
    result = export_to_txt(out)
    for p in paragraphs:
        assert p in result


def test_roundtrip_order_preserved(tmp_path):
    paragraphs = ["Alpha", "Beta", "Gamma"]
    model = create_abw(paragraphs)
    out = tmp_path / "order.abw"
    write_abw(model, out)
    result = export_to_txt(out)
    alpha_pos = result.index("Alpha")
    beta_pos = result.index("Beta")
    gamma_pos = result.index("Gamma")
    assert alpha_pos < beta_pos < gamma_pos
