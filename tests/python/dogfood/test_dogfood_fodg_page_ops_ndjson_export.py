"""
Dogfood pipeline: FODG page ops → NDJSON export.
Covers: create_fodg, write_fodg, add_page, remove_page, rename_page, get_page_by_name
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    load,
    create_fodg,
    write_fodg,
    add_page,
    remove_page,
    rename_page,
    get_page_by_name,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _valid_fodg_files():
    return sorted(_FODG_DIR.glob("*.fodg"))


def test_create_fodg_returns_dict(tmp_path):
    model = create_fodg([{"name": "Page1", "shapes": []}])
    assert isinstance(model, dict)
    assert "pages" in model
    assert len(model["pages"]) == 1

    record = {"format": "fodg", "function": "create_fodg", "page_count": len(model["pages"])}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["page_count"] == 1
    assert json.dumps(loaded[0]) is not None


def test_write_fodg_creates_file(tmp_path):
    model = create_fodg([{"name": "TestPage", "shapes": []}])
    dest = tmp_path / "out.fodg"
    write_fodg(model, str(dest))
    assert dest.exists()
    assert dest.stat().st_size > 0

    record = {"format": "fodg", "function": "write_fodg", "file_size": dest.stat().st_size}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["file_size"] > 0
    assert json.dumps(loaded[0]) is not None


def test_add_page_increases_count(tmp_path):
    path = str(_valid_fodg_files()[0])
    model = load(path)
    original_count = len(model.get("pages", []))
    updated = add_page(model, "NewPage")
    assert isinstance(updated, dict)
    assert len(updated["pages"]) == original_count + 1

    record = {"format": "fodg", "function": "add_page", "pages_before": original_count, "pages_after": len(updated["pages"])}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["pages_after"] == loaded[0]["pages_before"] + 1
    assert json.dumps(loaded[0]) is not None


def test_remove_page_decreases_count(tmp_path):
    path = str(_valid_fodg_files()[0])
    model = load(path)
    # Add a page first so we can remove it
    with_extra = add_page(model, "ToRemove")
    count_before = len(with_extra["pages"])
    removed = remove_page(with_extra, count_before - 1)
    assert isinstance(removed, dict)
    assert len(removed["pages"]) == count_before - 1

    record = {"format": "fodg", "function": "remove_page", "pages_before": count_before, "pages_after": len(removed["pages"])}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["pages_after"] == loaded[0]["pages_before"] - 1
    assert json.dumps(loaded[0]) is not None


def test_rename_page_changes_name(tmp_path):
    path = str(_valid_fodg_files()[0])
    model = load(path)
    updated = rename_page(model, 0, "RenamedPage")
    assert isinstance(updated, dict)
    assert updated["pages"][0]["name"] == "RenamedPage"

    record = {"format": "fodg", "function": "rename_page", "new_name": updated["pages"][0]["name"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["new_name"] == "RenamedPage"
    assert json.dumps(loaded[0]) is not None


def test_get_page_by_name(tmp_path):
    path = str(_valid_fodg_files()[0])
    model = load(path)
    page_name = model["pages"][0]["name"]
    page = get_page_by_name(model, page_name)
    assert page is not None
    assert page["name"] == page_name
    # Nonexistent name returns None
    missing = get_page_by_name(model, "__nonexistent__")
    assert missing is None

    record = {"format": "fodg", "function": "get_page_by_name", "found": page is not None}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["found"] is True
    assert json.dumps(loaded[0]) is not None
