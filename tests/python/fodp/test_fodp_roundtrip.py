"""FODP export-roundtrip tests.

FODP is a read-only format (no writer), so "roundtrip" means:
  load → export_to_json → json.loads → verify structural consistency

TC-CERT-H-RT certification hardening.
"""
import json
from pathlib import Path

import pytest

from fodp import load, export_to_json, export_to_txt, export_to_csv

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodp"


def _sample(name: str) -> Path:
    p = SAMPLES / name
    if not p.exists():
        pytest.skip(f"Sample file not found: {p}")
    return p


def test_json_export_roundtrip_minimal():
    """Load → export_to_json → json.loads preserves page count."""
    path = _sample("minimal-presentation.fodp")
    model = load(path)
    json_str = export_to_json(path)
    reloaded = json.loads(json_str)

    assert model["page_count"] == reloaded["page_count"]
    assert model["is_fodp"] == reloaded["is_fodp"]
    assert len(model["pages"]) == len(reloaded["pages"])


def test_json_export_roundtrip_two_slides():
    """Load → export_to_json → json.loads preserves multi-slide structure."""
    path = _sample("two-slides-basic.fodp")
    model = load(path)
    json_str = export_to_json(path)
    reloaded = json.loads(json_str)

    assert model["page_count"] == reloaded["page_count"]
    assert model["page_count"] >= 2
    for i, page in enumerate(model["pages"]):
        assert page["name"] == reloaded["pages"][i]["name"]
        assert page["shape_count"] == reloaded["pages"][i]["shape_count"]


def test_json_export_roundtrip_title_only():
    """Title-only presentation load → export_to_json roundtrip."""
    path = _sample("title-only.fodp")
    model = load(path)
    json_str = export_to_json(path)
    reloaded = json.loads(json_str)

    assert model["page_count"] == reloaded["page_count"]
    assert isinstance(reloaded["pages"], list)


def test_txt_export_preserves_text():
    """export_to_txt returns non-empty text for slides with content."""
    path = _sample("minimal-presentation.fodp")
    model = load(path)
    txt = export_to_txt(path)

    assert isinstance(txt, str)
    # If model has text content, export should contain it
    for page in model["pages"]:
        for text_item in page.get("text_content", []):
            if text_item.strip():
                assert text_item.strip() in txt


def test_csv_export_has_headers():
    """export_to_csv returns CSV with header row."""
    path = _sample("two-slides-basic.fodp")
    csv_str = export_to_csv(path)

    assert isinstance(csv_str, str)
    lines = csv_str.strip().split("\n")
    assert len(lines) >= 2  # header + at least 1 data row


def test_double_load_consistency():
    """Loading the same file twice produces identical results."""
    path = _sample("minimal-presentation.fodp")
    model1 = load(path)
    model2 = load(path)

    assert model1["page_count"] == model2["page_count"]
    assert model1["is_fodp"] == model2["is_fodp"]
    assert len(model1["pages"]) == len(model2["pages"])
    for i in range(len(model1["pages"])):
        assert model1["pages"][i]["name"] == model2["pages"][i]["name"]
        assert model1["pages"][i]["shape_count"] == model2["pages"][i]["shape_count"]
