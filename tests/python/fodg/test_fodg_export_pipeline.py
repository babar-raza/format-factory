"""
test_fodg_export_pipeline.py -- FODG export pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-29
Tests export_to_json (returns JSON string), count_shapes (returns int),
get_text_shapes (returns list), get_all_text (returns list),
get_page_count on a created FODG model.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    export_to_json,
    count_shapes,
    get_text_shapes,
    get_all_text,
    get_page_count,
)

_MODEL = create_fodg([{"name": "Page1"}, {"name": "Page2"}])


def test_export_to_json_is_string():
    result = export_to_json(_MODEL)
    assert isinstance(result, str)


def test_export_to_json_parseable():
    result = export_to_json(_MODEL)
    data = json.loads(result)
    assert "pages" in data


def test_count_shapes_returns_int():
    n = count_shapes(_MODEL)
    assert isinstance(n, int)


def test_get_text_shapes_returns_list():
    shapes = get_text_shapes(_MODEL)
    assert isinstance(shapes, list)


def test_get_page_count():
    assert get_page_count(_MODEL) == 2
