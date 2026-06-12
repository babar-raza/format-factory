"""Tests for FODG roundtrip capability (gap: GAP-FODG-FOSS-ROUNDTRIP-001).

Sprint: FORMAT-FACTORY-BROAD-CAPABILITY-LAYER-HEALING-RNEXT2
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

from src.python.fodg.fodg_codec import create_fodg, write_fodg, roundtrip


def test_roundtrip_preserves_page_count(tmp_path):
    """roundtrip preserves page count."""
    model = create_fodg([{"name": "P1"}, {"name": "P2"}])
    src = tmp_path / "src.fodg"
    write_fodg(model, src)
    dest = tmp_path / "dest.fodg"
    reloaded = roundtrip(src, dest)
    assert reloaded["page_count"] == 2


def test_roundtrip_preserves_text(tmp_path):
    """roundtrip preserves text content."""
    model = create_fodg([{"name": "Page1", "texts": ["Hello", "World"]}])
    src = tmp_path / "src.fodg"
    write_fodg(model, src)
    dest = tmp_path / "dest.fodg"
    reloaded = roundtrip(src, dest)
    texts = reloaded["pages"][0]["text_content"]
    assert "Hello" in texts
    assert "World" in texts


def test_roundtrip_creates_dest_file(tmp_path):
    """roundtrip writes to dest file."""
    model = create_fodg([{"name": "P1", "texts": ["content"]}])
    src = tmp_path / "src.fodg"
    write_fodg(model, src)
    dest = tmp_path / "dest.fodg"
    assert not dest.exists()
    roundtrip(src, dest)
    assert dest.exists()


def test_roundtrip_returns_valid_model(tmp_path):
    """roundtrip returns a model with is_fodg=True."""
    model = create_fodg([{"name": "P1"}])
    src = tmp_path / "src.fodg"
    write_fodg(model, src)
    dest = tmp_path / "rt.fodg"
    result = roundtrip(src, dest)
    assert result.get("is_fodg") is True
    assert "page_count" in result
    assert "pages" in result


def test_roundtrip_from_bytes(tmp_path):
    """roundtrip accepts raw bytes as source."""
    model = create_fodg([{"name": "B", "texts": ["byte_test"]}])
    src = tmp_path / "src.fodg"
    write_fodg(model, src)
    raw = src.read_bytes()
    dest = tmp_path / "dest.fodg"
    result = roundtrip(raw, dest)
    assert result["page_count"] == 1
    assert "byte_test" in result["pages"][0]["text_content"]


def test_roundtrip_empty_document(tmp_path):
    """roundtrip works for empty FODG document."""
    model = create_fodg([])
    src = tmp_path / "src.fodg"
    write_fodg(model, src)
    dest = tmp_path / "dest.fodg"
    result = roundtrip(src, dest)
    assert result["page_count"] == 0


def test_roundtrip_multiple_pages(tmp_path):
    """roundtrip preserves multiple pages."""
    pages = [{"name": f"P{i}", "texts": [f"text{i}"]} for i in range(4)]
    model = create_fodg(pages)
    src = tmp_path / "src.fodg"
    write_fodg(model, src)
    dest = tmp_path / "dest.fodg"
    result = roundtrip(src, dest)
    assert result["page_count"] == 4
    for i in range(4):
        assert f"text{i}" in result["pages"][i]["text_content"]
