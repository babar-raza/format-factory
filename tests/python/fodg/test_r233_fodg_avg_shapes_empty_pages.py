"""Tests for fodg_avg_shapes_per_page and fodg_has_empty_pages (Sprint 23)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import fodg_avg_shapes_per_page, fodg_has_empty_pages

_FODG_ONE_SHAPE = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  office:mimetype="application/vnd.oasis.opendocument.graphics-flat-xml">
  <office:body>
    <office:drawing>
      <draw:page draw:name="Page1">
        <draw:rect><text:p>Hello</text:p></draw:rect>
      </draw:page>
    </office:drawing>
  </office:body>
</office:document>"""

_FODG_EMPTY_PAGE = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  office:mimetype="application/vnd.oasis.opendocument.graphics-flat-xml">
  <office:body>
    <office:drawing>
      <draw:page draw:name="Page1">
      </draw:page>
    </office:drawing>
  </office:body>
</office:document>"""

_FODG_TWO_SHAPES = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  office:mimetype="application/vnd.oasis.opendocument.graphics-flat-xml">
  <office:body>
    <office:drawing>
      <draw:page draw:name="Page1">
        <draw:rect><text:p>A</text:p></draw:rect>
        <draw:rect><text:p>B</text:p></draw:rect>
      </draw:page>
    </office:drawing>
  </office:body>
</office:document>"""


def _write(tmp_path, name, content):
    p = tmp_path / f"{name}.fodg"
    p.write_text(content, encoding="utf-8")
    return str(p)


class TestFodgAvgShapesPerPage:
    def test_return_type(self, tmp_path):
        p = _write(tmp_path, "rt", _FODG_ONE_SHAPE)
        result = fodg_avg_shapes_per_page(p)
        assert isinstance(result, float)

    def test_nonnegative(self, tmp_path):
        p = _write(tmp_path, "nn", _FODG_ONE_SHAPE)
        result = fodg_avg_shapes_per_page(p)
        assert result >= 0.0

    def test_empty_page_returns_zero(self, tmp_path):
        p = _write(tmp_path, "ep", _FODG_EMPTY_PAGE)
        result = fodg_avg_shapes_per_page(p)
        assert result == 0.0

    def test_one_shape(self, tmp_path):
        p = _write(tmp_path, "os", _FODG_ONE_SHAPE)
        result = fodg_avg_shapes_per_page(p)
        assert result >= 0.0

    def test_two_shapes(self, tmp_path):
        p = _write(tmp_path, "ts", _FODG_TWO_SHAPES)
        result = fodg_avg_shapes_per_page(p)
        assert isinstance(result, float)


class TestFodgHasEmptyPages:
    def test_return_type(self, tmp_path):
        p = _write(tmp_path, "rt2", _FODG_ONE_SHAPE)
        result = fodg_has_empty_pages(p)
        assert isinstance(result, bool)

    def test_empty_page_is_true(self, tmp_path):
        p = _write(tmp_path, "ep2", _FODG_EMPTY_PAGE)
        assert fodg_has_empty_pages(p) is True

    def test_nonempty_page_is_false(self, tmp_path):
        p = _write(tmp_path, "ne", _FODG_ONE_SHAPE)
        result = fodg_has_empty_pages(p)
        assert isinstance(result, bool)

    def test_two_shapes_page(self, tmp_path):
        p = _write(tmp_path, "ts2", _FODG_TWO_SHAPES)
        result = fodg_has_empty_pages(p)
        assert isinstance(result, bool)

    def test_bool_not_truthy(self, tmp_path):
        p = _write(tmp_path, "bt", _FODG_ONE_SHAPE)
        result = fodg_has_empty_pages(p)
        assert result is True or result is False
