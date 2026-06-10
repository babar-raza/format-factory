"""
Tests for FODG write/export capabilities.

Sprint: FORMAT-FACTORY-CAPABILITY-FEATURE-UNDERSTANDING-LAYER-INVESTIGATIVE-HEALING-001
Run ID: capability-feature-understanding-layer-healing-20260608-e382e5f

Tests CAP-PROD-002 (write_fodg) and CAP-PROD-003 (export_to_txt).
"""
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src" / "python"))

from fodg.fodg_codec import (
    FodgError,
    FodgParseError,
    create_fodg,
    export_to_txt,
    load,
    probe_fodg,
    write_fodg,
)


# ---------------------------------------------------------------------------
# create_fodg tests
# ---------------------------------------------------------------------------


def test_create_fodg_empty():
    model = create_fodg([])
    assert model["is_fodg"] is True
    assert model["page_count"] == 0
    assert model["pages"] == []
    assert model["shapes_total"] == 0
    assert model["mime_type"] == "application/vnd.oasis.opendocument.graphics-flat-xml"


def test_create_fodg_single_page_no_texts():
    model = create_fodg([{"name": "Slide1"}])
    assert model["page_count"] == 1
    assert model["pages"][0]["name"] == "Slide1"
    assert model["pages"][0]["text_content"] == []
    assert model["shapes_total"] == 0


def test_create_fodg_single_page_with_texts():
    model = create_fodg([{"name": "Slide1", "texts": ["Hello", "World"]}])
    assert model["page_count"] == 1
    assert model["shapes_total"] == 2
    assert model["pages"][0]["text_content"] == ["Hello", "World"]


def test_create_fodg_multi_page():
    model = create_fodg([
        {"name": "Page1", "texts": ["A", "B"]},
        {"name": "Page2", "texts": ["C"]},
    ])
    assert model["page_count"] == 2
    assert model["shapes_total"] == 3


def test_create_fodg_default_page_name():
    model = create_fodg([{}])
    assert model["pages"][0]["name"] == "Page1"


def test_create_fodg_filters_empty_texts():
    model = create_fodg([{"texts": ["Hello", "", None, "World"]}])
    assert model["pages"][0]["text_content"] == ["Hello", "World"]


# ---------------------------------------------------------------------------
# write_fodg tests
# ---------------------------------------------------------------------------


def test_write_fodg_creates_file():
    model = create_fodg([{"name": "Slide1", "texts": ["Test"]}])
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        tmp = Path(f.name)
    try:
        write_fodg(model, tmp)
        assert tmp.exists()
        assert tmp.stat().st_size > 0
    finally:
        tmp.unlink(missing_ok=True)


def test_write_fodg_produces_valid_xml():
    model = create_fodg([{"name": "Slide1", "texts": ["Hello FODG"]}])
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        tmp = Path(f.name)
    try:
        write_fodg(model, tmp)
        content = tmp.read_text(encoding="utf-8")
        assert "<?xml" in content
        assert "office:document" in content
        assert "opendocument.graphics-flat-xml" in content
    finally:
        tmp.unlink(missing_ok=True)


def test_write_fodg_roundtrip_probe():
    model = create_fodg([{"name": "Test", "texts": ["foo"]}])
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        tmp = Path(f.name)
    try:
        write_fodg(model, tmp)
        assert probe_fodg(tmp) is True
    finally:
        tmp.unlink(missing_ok=True)


def test_write_fodg_roundtrip_load():
    model = create_fodg([
        {"name": "Slide1", "texts": ["Hello", "World"]},
        {"name": "Slide2", "texts": ["Foo"]},
    ])
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        tmp = Path(f.name)
    try:
        write_fodg(model, tmp)
        loaded = load(tmp)
        assert loaded["is_fodg"] is True
        assert loaded["page_count"] == 2
        # Text content should be preserved
        page0_texts = loaded["pages"][0]["text_content"]
        assert "Hello" in page0_texts
        assert "World" in page0_texts
    finally:
        tmp.unlink(missing_ok=True)


def test_write_fodg_multi_page_roundtrip():
    model = create_fodg([
        {"name": "Intro", "texts": ["Title"]},
        {"name": "Body", "texts": ["Content here", "More content"]},
        {"name": "Summary", "texts": []},
    ])
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        tmp = Path(f.name)
    try:
        write_fodg(model, tmp)
        loaded = load(tmp)
        assert loaded["page_count"] == 3
        assert loaded["pages"][0]["name"] == "Intro"
        assert loaded["pages"][1]["name"] == "Body"
        assert loaded["pages"][2]["name"] == "Summary"
    finally:
        tmp.unlink(missing_ok=True)


def test_write_fodg_empty_model():
    model = create_fodg([])
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        tmp = Path(f.name)
    try:
        write_fodg(model, tmp)
        loaded = load(tmp)
        assert loaded["page_count"] == 0
    finally:
        tmp.unlink(missing_ok=True)


def test_write_fodg_rejects_invalid_model():
    with pytest.raises(FodgError):
        write_fodg({"is_fodg": False}, "/tmp/test.fodg")


def test_write_fodg_rejects_non_dict():
    with pytest.raises(FodgError):
        write_fodg("not a dict", "/tmp/test.fodg")


def test_write_fodg_accepts_path_string():
    model = create_fodg([{"texts": ["test"]}])
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        tmp = f.name
    try:
        write_fodg(model, tmp)  # str path
        assert Path(tmp).exists()
    finally:
        Path(tmp).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# export_to_txt tests
# ---------------------------------------------------------------------------


def test_export_to_txt_basic():
    model = create_fodg([{"name": "Slide1", "texts": ["Hello", "World"]}])
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        tmp = Path(f.name)
    try:
        write_fodg(model, tmp)
        result = export_to_txt(tmp)
        assert "Hello" in result
        assert "World" in result
        assert "Slide1" in result
    finally:
        tmp.unlink(missing_ok=True)


def test_export_to_txt_returns_string():
    model = create_fodg([{"texts": ["foo"]}])
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        tmp = Path(f.name)
    try:
        write_fodg(model, tmp)
        result = export_to_txt(tmp)
        assert isinstance(result, str)
    finally:
        tmp.unlink(missing_ok=True)


def test_export_to_txt_empty_model():
    model = create_fodg([])
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        tmp = Path(f.name)
    try:
        write_fodg(model, tmp)
        result = export_to_txt(tmp)
        assert result == ""
    finally:
        tmp.unlink(missing_ok=True)


def test_export_to_txt_multi_page():
    model = create_fodg([
        {"name": "Page1", "texts": ["A"]},
        {"name": "Page2", "texts": ["B", "C"]},
    ])
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        tmp = Path(f.name)
    try:
        write_fodg(model, tmp)
        result = export_to_txt(tmp)
        assert "Page1" in result
        assert "Page2" in result
        assert "A" in result
        assert "B" in result
        assert "C" in result
    finally:
        tmp.unlink(missing_ok=True)


def test_export_to_txt_from_bytes():
    model = create_fodg([{"texts": ["bytes test"]}])
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        tmp = Path(f.name)
    try:
        write_fodg(model, tmp)
        raw_bytes = tmp.read_bytes()
        result = export_to_txt(raw_bytes)
        assert "bytes test" in result
    finally:
        tmp.unlink(missing_ok=True)


def test_export_to_txt_page_headers():
    model = create_fodg([{"name": "MySlide", "texts": ["content"]}])
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        tmp = Path(f.name)
    try:
        write_fodg(model, tmp)
        result = export_to_txt(tmp)
        assert "=== MySlide ===" in result
    finally:
        tmp.unlink(missing_ok=True)


def test_export_to_txt_fallback_page_number():
    # Page with no name → should get "Page N" header
    model = create_fodg([{"name": "", "texts": ["x"]}])
    with tempfile.NamedTemporaryFile(suffix=".fodg", delete=False) as f:
        tmp = Path(f.name)
    try:
        write_fodg(model, tmp)
        result = export_to_txt(tmp)
        assert "Page 1" in result
    finally:
        tmp.unlink(missing_ok=True)
