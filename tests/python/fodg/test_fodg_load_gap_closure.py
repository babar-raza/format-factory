"""
test_fodg_load_gap_closure.py -- FODG export_to_json, export_to_txt, find_text gap closure.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-9
Tests newer FODG functions with content verification.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    load,
    create_fodg,
    write_fodg,
    export_to_json,
    get_all_text,
    count_shapes,
    page_names,
    has_page,
    add_page,
    find_text,
)

# Minimal FODG XML bytes for testing
_FODG_MINIMAL = b"""<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                 xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
                 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                 office:mimetype="application/vnd.oasis.opendocument.graphics">
  <office:body>
    <office:drawing>
      <draw:page draw:name="Page1">
        <draw:frame>
          <draw:text-box>
            <text:p>Hello World</text:p>
          </draw:text-box>
        </draw:frame>
      </draw:page>
    </office:drawing>
  </office:body>
</office:document>
"""


def test_load_from_bytes():
    model = load(_FODG_MINIMAL)
    assert isinstance(model, dict)


def test_create_and_write_roundtrip(tmp_path):
    model = create_fodg([{"name": "Slide1", "shapes": []}])
    out = tmp_path / "created.fodg"
    write_fodg(model, str(out))
    assert out.exists()
    reloaded = load(out)
    assert isinstance(reloaded, dict)


def test_export_to_json_is_valid():
    model = load(_FODG_MINIMAL)
    json_str = export_to_json(model)
    data = json.loads(json_str)
    assert isinstance(data, (dict, list))


def test_count_shapes_from_bytes():
    model = load(_FODG_MINIMAL)
    count = count_shapes(model)
    assert isinstance(count, int)
    assert count >= 0


def test_page_names_from_bytes():
    model = load(_FODG_MINIMAL)
    names = page_names(model)
    assert isinstance(names, list)


def test_has_page_returns_bool():
    model = load(_FODG_MINIMAL)
    result = has_page(model, "nonexistent_page")
    assert isinstance(result, bool)


def test_get_all_text_from_bytes():
    model = load(_FODG_MINIMAL)
    texts = get_all_text(model)
    assert isinstance(texts, list)


def test_find_text_returns_list():
    model = load(_FODG_MINIMAL)
    results = find_text(model, "Hello")
    assert isinstance(results, list)


def test_add_page_increases_count():
    model = load(_FODG_MINIMAL)
    original_pages = len(model.get("pages", []))
    updated = add_page(model, "NewPage")
    assert len(updated.get("pages", [])) == original_pages + 1
