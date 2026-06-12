"""
Tests for ABW export_to_json capability.

Sprint: FORMAT-FACTORY-ABW-GNUMERIC-CAPABILITY-MATRIX-ADVANCE-001
Track: Python FOSS — ABW codec
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3] / "src" / "python"))

from abw.abw_codec import create_abw, export_to_json, load, write_abw


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_abw_bytes(paragraphs: list[str]) -> bytes:
    model = create_abw(paragraphs)
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".abw", delete=False) as f:
        tmp = Path(f.name)
    write_abw(model, tmp)
    data = tmp.read_bytes()
    tmp.unlink(missing_ok=True)
    return data


# ---------------------------------------------------------------------------
# Basic structure tests
# ---------------------------------------------------------------------------

def test_json_export_returns_string():
    abw = _make_abw_bytes(["Hello world"])
    result = export_to_json(abw)
    assert isinstance(result, str)


def test_json_export_is_valid_json():
    abw = _make_abw_bytes(["Para 1", "Para 2"])
    result = export_to_json(abw)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_json_export_has_required_keys():
    abw = _make_abw_bytes(["Hello"])
    parsed = json.loads(export_to_json(abw))
    assert "section_count" in parsed
    assert "paragraph_count" in parsed
    assert "paragraphs" in parsed


# ---------------------------------------------------------------------------
# Content correctness tests
# ---------------------------------------------------------------------------

def test_json_export_single_paragraph():
    abw = _make_abw_bytes(["Hello world"])
    parsed = json.loads(export_to_json(abw))
    assert parsed["paragraph_count"] == 1
    assert parsed["paragraphs"] == ["Hello world"]


def test_json_export_two_paragraphs():
    abw = _make_abw_bytes(["First", "Second"])
    parsed = json.loads(export_to_json(abw))
    assert parsed["paragraph_count"] == 2
    assert parsed["paragraphs"] == ["First", "Second"]


def test_json_export_empty_paragraphs():
    abw = _make_abw_bytes([])
    parsed = json.loads(export_to_json(abw))
    assert parsed["paragraph_count"] == 0
    assert parsed["paragraphs"] == []


def test_json_export_section_count():
    abw = _make_abw_bytes(["A", "B", "C"])
    parsed = json.loads(export_to_json(abw))
    assert parsed["section_count"] >= 1


def test_json_export_preserves_text_content():
    texts = ["Line one", "Line two", "Line three"]
    abw = _make_abw_bytes(texts)
    parsed = json.loads(export_to_json(abw))
    assert parsed["paragraphs"] == texts


def test_json_export_special_characters():
    abw = _make_abw_bytes(["Hello & World", "Price: 10 < 20"])
    parsed = json.loads(export_to_json(abw))
    assert "Hello & World" in parsed["paragraphs"]
    assert "Price: 10 < 20" in parsed["paragraphs"]


def test_json_export_unicode_content():
    abw = _make_abw_bytes(["Café au lait", "日本語テキスト"])
    parsed = json.loads(export_to_json(abw))
    assert "Café au lait" in parsed["paragraphs"]
    assert "日本語テキスト" in parsed["paragraphs"]


# ---------------------------------------------------------------------------
# Input type tests
# ---------------------------------------------------------------------------

def test_json_export_from_bytes():
    abw = _make_abw_bytes(["From bytes"])
    parsed = json.loads(export_to_json(abw))
    assert parsed["paragraphs"] == ["From bytes"]


def test_json_export_from_xml_string():
    xml = '<?xml version="1.0" encoding="UTF-8"?><abiword version="1.0" fileformat="1.0"><section><p>From string</p></section></abiword>'
    parsed = json.loads(export_to_json(xml))
    assert "From string" in parsed["paragraphs"]


def test_json_export_from_path(tmp_path):
    abw_path = tmp_path / "test.abw"
    model = create_abw(["From file"])
    write_abw(model, abw_path)
    parsed = json.loads(export_to_json(abw_path))
    assert parsed["paragraphs"] == ["From file"]


# ---------------------------------------------------------------------------
# Roundtrip consistency
# ---------------------------------------------------------------------------

def test_json_export_matches_load_model():
    texts = ["Alpha", "Beta", "Gamma"]
    abw = _make_abw_bytes(texts)
    model = load(abw)
    parsed = json.loads(export_to_json(abw))
    assert parsed["section_count"] == model["section_count"]
    assert parsed["paragraph_count"] == model["paragraph_count"]
    assert parsed["paragraphs"] == model["paragraphs"]


def test_json_export_large_document():
    texts = [f"Paragraph {i}" for i in range(50)]
    abw = _make_abw_bytes(texts)
    parsed = json.loads(export_to_json(abw))
    assert parsed["paragraph_count"] == 50
    assert len(parsed["paragraphs"]) == 50
    assert parsed["paragraphs"][0] == "Paragraph 0"
    assert parsed["paragraphs"][49] == "Paragraph 49"
