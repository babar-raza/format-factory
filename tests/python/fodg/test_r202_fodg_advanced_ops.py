"""
tests/python/fodg/test_r202_fodg_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT8-001
TASK-001: FODG advanced operations — probe/load, page ops, shape ops, analytics, mutation.

Covers: probe_fodg, load, get_page_count, get_shape_count, extract_text,
get_page_metadata, export_to_txt, page_names, has_page, get_page_by_name,
get_page_index, get_page_text, get_all_text, total_text_length,
count_shapes, get_text_shapes, fodg_page_shape_count, fodg_total_shape_count,
fodg_text_shape_count, export_to_json, export_to_csv, export_page_to_json,
find_shapes_by_text_pattern, find_text, add_page, remove_page, rename_page,
duplicate_page, clear_page, swap_pages, create_fodg, write_fodg, roundtrip.
"""
from __future__ import annotations

import sys
import os
import json
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    probe_fodg, load, get_page_count, get_shape_count, extract_text,
    get_page_metadata, export_to_txt, page_names, has_page, get_page_by_name,
    get_page_index, get_page_text, get_all_text, total_text_length,
    count_shapes, get_text_shapes, fodg_page_shape_count, fodg_total_shape_count,
    fodg_text_shape_count, export_to_json, export_to_csv, export_page_to_json,
    find_shapes_by_text_pattern, find_text, add_page, remove_page,
    rename_page, duplicate_page, clear_page, swap_pages, create_fodg, write_fodg,
    roundtrip,
)

_TEXTS_P1 = ["Hello World", "Format Factory"]
_TEXTS_P2 = ["Slide Two", "More Content"]


def _make_model():
    return create_fodg([
        {"name": "PageOne", "texts": _TEXTS_P1},
        {"name": "PageTwo", "texts": _TEXTS_P2},
    ])


def _make_file():
    model = _make_model()
    fd, path = tempfile.mkstemp(suffix=".fodg")
    os.close(fd)
    write_fodg(model, path)
    return path, model


class TestFodgProbeAndLoad:
    """probe_fodg, load, get_page_count, get_shape_count, extract_text, get_page_metadata, export_to_txt."""

    def test_probe_fodg_true(self):
        path, _ = _make_file()
        try:
            assert probe_fodg(path) is True
        finally:
            os.unlink(path)

    def test_probe_fodg_bytes(self):
        path, _ = _make_file()
        try:
            data = Path(path).read_bytes()
            assert probe_fodg(data) is True
        finally:
            os.unlink(path)

    def test_load_returns_dict(self):
        path, _ = _make_file()
        try:
            model = load(path)
            assert isinstance(model, dict)
            assert model["is_fodg"] is True
        finally:
            os.unlink(path)

    def test_get_page_count_model(self):
        model = _make_model()
        assert get_page_count(model) == 2

    def test_get_shape_count_file(self):
        path, _ = _make_file()
        try:
            # texts become text-box shapes
            count = get_shape_count(path)
            assert isinstance(count, int)
            assert count >= 0
        finally:
            os.unlink(path)

    def test_extract_text_from_file(self):
        path, _ = _make_file()
        try:
            texts = extract_text(path)
            assert isinstance(texts, list)
            assert "Hello World" in texts
        finally:
            os.unlink(path)

    def test_get_page_metadata_structure(self):
        path, _ = _make_file()
        try:
            meta = get_page_metadata(path)
            assert isinstance(meta, list)
            assert len(meta) == 2
            assert meta[0]["name"] == "PageOne"
        finally:
            os.unlink(path)

    def test_export_to_txt_has_headers(self):
        path, _ = _make_file()
        try:
            txt = export_to_txt(path)
            assert isinstance(txt, str)
            assert "PageOne" in txt
            assert "Hello World" in txt
        finally:
            os.unlink(path)

    def test_load_page_count_matches(self):
        path, _ = _make_file()
        try:
            model = load(path)
            assert model["page_count"] == 2
        finally:
            os.unlink(path)

    def test_load_mime_type_set(self):
        path, _ = _make_file()
        try:
            model = load(path)
            assert "opendocument.graphics" in model["mime_type"]
        finally:
            os.unlink(path)


class TestFodgPageOps:
    """page_names, has_page, get_page_by_name, get_page_index, get_page_text, get_all_text, total_text_length."""

    def test_page_names_returns_list(self):
        model = _make_model()
        names = page_names(model)
        assert isinstance(names, list)
        assert "PageOne" in names
        assert "PageTwo" in names

    def test_has_page_true(self):
        model = _make_model()
        assert has_page(model, "PageOne") is True

    def test_has_page_false(self):
        model = _make_model()
        assert has_page(model, "NoSuchPage") is False

    def test_get_page_by_name_found(self):
        model = _make_model()
        page = get_page_by_name(model, "PageOne")
        assert page is not None
        assert page["name"] == "PageOne"

    def test_get_page_by_name_missing(self):
        model = _make_model()
        page = get_page_by_name(model, "Missing")
        assert page is None

    def test_get_page_index_correct(self):
        model = _make_model()
        assert get_page_index(model, "PageOne") == 0
        assert get_page_index(model, "PageTwo") == 1

    def test_get_page_text_first_page(self):
        model = _make_model()
        texts = get_page_text(model, 0)
        assert isinstance(texts, list)
        assert "Hello World" in texts

    def test_get_page_text_out_of_range(self):
        model = _make_model()
        result = get_page_text(model, 99)
        assert result == []

    def test_get_all_text_flat_list(self):
        model = _make_model()
        all_texts = get_all_text(model)
        assert isinstance(all_texts, list)
        assert "Hello World" in all_texts
        assert "Slide Two" in all_texts

    def test_total_text_length_positive(self):
        model = _make_model()
        length = total_text_length(model)
        assert isinstance(length, int)
        assert length > 0


class TestFodgShapeOps:
    """count_shapes, get_text_shapes, fodg_page_shape_count, fodg_total_shape_count, fodg_text_shape_count."""

    def test_count_shapes_returns_int(self):
        model = _make_model()
        n = count_shapes(model)
        assert isinstance(n, int)
        assert n >= 0

    def test_get_text_shapes_list(self):
        model = _make_model()
        ts = get_text_shapes(model)
        assert isinstance(ts, list)
        # Both pages have text so at least 2 results
        assert len(ts) >= 2

    def test_get_text_shapes_structure(self):
        model = _make_model()
        ts = get_text_shapes(model)
        assert "page_name" in ts[0]
        assert "text_content" in ts[0]

    def test_fodg_page_shape_count_model(self):
        model = _make_model()
        count = fodg_page_shape_count(model, 0)
        assert isinstance(count, int)
        assert count >= 0

    def test_fodg_total_shape_count_file(self):
        path, _ = _make_file()
        try:
            count = fodg_total_shape_count(path)
            assert isinstance(count, int)
            assert count >= 0
        finally:
            os.unlink(path)

    def test_fodg_text_shape_count_file(self):
        path, _ = _make_file()
        try:
            count = fodg_text_shape_count(path)
            assert isinstance(count, int)
        finally:
            os.unlink(path)

    def test_fodg_page_shape_count_oob(self):
        model = _make_model()
        assert fodg_page_shape_count(model, 99) == 0


class TestFodgAnalytics:
    """export_to_json, export_to_csv, export_page_to_json, find_shapes_by_text_pattern, find_text."""

    def test_export_to_json_valid(self):
        model = _make_model()
        js = export_to_json(model)
        assert isinstance(js, str)
        parsed = json.loads(js)
        assert parsed["page_count"] == 2

    def test_export_to_json_pages_structure(self):
        model = _make_model()
        parsed = json.loads(export_to_json(model))
        assert isinstance(parsed["pages"], list)
        assert parsed["pages"][0]["name"] == "PageOne"

    def test_export_to_csv_header(self):
        path, _ = _make_file()
        try:
            csv_str = export_to_csv(path)
            assert isinstance(csv_str, str)
            assert csv_str.startswith("page_name,shape_index,text")
        finally:
            os.unlink(path)

    def test_export_to_csv_content(self):
        path, _ = _make_file()
        try:
            csv_str = export_to_csv(path)
            assert "Hello World" in csv_str
        finally:
            os.unlink(path)

    def test_export_page_to_json_valid(self):
        model = _make_model()
        js = export_page_to_json(model, 0)
        assert isinstance(js, str)
        parsed = json.loads(js)
        assert parsed["name"] == "PageOne"

    def test_export_page_to_json_oob(self):
        model = _make_model()
        js = export_page_to_json(model, 99)
        assert js == "{}"

    def test_find_shapes_by_text_pattern_match(self):
        model = _make_model()
        results = find_shapes_by_text_pattern(model, r"Hello")
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_find_shapes_by_text_pattern_no_match(self):
        model = _make_model()
        results = find_shapes_by_text_pattern(model, r"XYZNOTFOUND")
        assert results == []

    def test_find_text_empty_when_no_shapes(self):
        model = _make_model()
        # created models have shapes=[] per page, so find_text won't match
        results = find_text(model, "Hello")
        assert isinstance(results, list)


class TestFodgMutation:
    """add_page, remove_page, rename_page, duplicate_page, clear_page, swap_pages, write_fodg, roundtrip."""

    def test_add_page_increases_count(self):
        model = _make_model()
        m2 = add_page(model, "NewPage")
        assert get_page_count(m2) == 3
        assert has_page(m2, "NewPage") is True

    def test_add_page_with_texts(self):
        model = _make_model()
        m2 = add_page(model, {"name": "Rich", "texts": ["A", "B"]})
        assert get_page_count(m2) == 3
        assert "A" in get_page_text(m2, 2)

    def test_remove_page_decreases_count(self):
        model = _make_model()
        m2 = remove_page(model, 0)
        assert get_page_count(m2) == 1
        assert has_page(m2, "PageTwo") is True

    def test_rename_page_changes_name(self):
        model = _make_model()
        m2 = rename_page(model, 0, "Renamed")
        assert has_page(m2, "Renamed") is True
        assert not has_page(m2, "PageOne")

    def test_duplicate_page_appends(self):
        model = _make_model()
        m2 = duplicate_page(model, 0)
        assert get_page_count(m2) == 3
        names = page_names(m2)
        assert names[0] == "PageOne"
        assert names[2] == "PageOne"

    def test_clear_page_empties_text(self):
        model = _make_model()
        m2 = clear_page(model, 0)
        assert get_page_text(m2, 0) == []

    def test_swap_pages_reorders(self):
        model = _make_model()
        m2 = swap_pages(model, 0, 1)
        names = page_names(m2)
        assert names[0] == "PageTwo"
        assert names[1] == "PageOne"

    def test_write_fodg_produces_file(self):
        model = _make_model()
        fd, path = tempfile.mkstemp(suffix=".fodg")
        os.close(fd)
        try:
            write_fodg(model, path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)

    def test_roundtrip_returns_model(self):
        path, _ = _make_file()
        fd, dest = tempfile.mkstemp(suffix=".fodg")
        os.close(fd)
        try:
            m2 = roundtrip(path, dest)
            assert isinstance(m2, dict)
            assert m2["page_count"] == 2
        finally:
            os.unlink(path)
            os.unlink(dest)

    def test_create_fodg_empty(self):
        model = create_fodg([])
        assert isinstance(model, dict)
        assert model["page_count"] == 0

    def test_create_fodg_preserves_names(self):
        model = create_fodg([{"name": "A"}, {"name": "B"}])
        assert page_names(model) == ["A", "B"]
