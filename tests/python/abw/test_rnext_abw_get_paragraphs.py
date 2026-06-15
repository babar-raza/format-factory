"""Tests for ABW get_paragraphs() — returns all paragraph texts from a model."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import (
    get_paragraphs,
    load,
    create_abw,
    write_abw,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MINIMAL_ABW = """\
<?xml version="1.0" encoding="UTF-8"?>
<abiword>
<section>
<p>Hello world</p>
<p>Second paragraph</p>
<p>Third paragraph</p>
</section>
</abiword>
"""

_EMPTY_ABW = """\
<?xml version="1.0" encoding="UTF-8"?>
<abiword>
<section/>
</abiword>
"""


def _write_tmp(content: str, suffix: str = ".abw") -> Path:
    f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode="w", encoding="utf-8")
    f.write(content)
    f.close()
    return Path(f.name)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGetParagraphs:
    def test_returns_list(self):
        model = load(_write_tmp(_MINIMAL_ABW))
        result = get_paragraphs(model)
        assert isinstance(result, list)

    def test_correct_count(self):
        model = load(_write_tmp(_MINIMAL_ABW))
        assert len(get_paragraphs(model)) == 3

    def test_correct_content(self):
        model = load(_write_tmp(_MINIMAL_ABW))
        paras = get_paragraphs(model)
        assert paras[0] == "Hello world"
        assert paras[1] == "Second paragraph"
        assert paras[2] == "Third paragraph"

    def test_empty_document(self):
        model = load(_write_tmp(_EMPTY_ABW))
        assert get_paragraphs(model) == []

    def test_returns_copy(self):
        model = load(_write_tmp(_MINIMAL_ABW))
        paras1 = get_paragraphs(model)
        paras1.append("mutated")
        paras2 = get_paragraphs(model)
        assert len(paras2) == 3  # original unaffected

    def test_type_error_on_non_dict(self):
        with pytest.raises(TypeError):
            get_paragraphs("not a dict")

    def test_type_error_on_none(self):
        with pytest.raises(TypeError):
            get_paragraphs(None)

    def test_roundtrip_create_get(self):
        model = create_abw(["alpha", "beta", "gamma"])
        paras = get_paragraphs(model)
        assert paras == ["alpha", "beta", "gamma"]

    def test_single_paragraph(self):
        model = create_abw(["only one"])
        assert get_paragraphs(model) == ["only one"]

    def test_with_empty_paragraphs(self):
        model = create_abw(["first", "", "third"])
        paras = get_paragraphs(model)
        assert len(paras) == 3
        assert paras[1] == ""

    def test_write_reload_roundtrip(self, tmp_path):
        model = create_abw(["line A", "line B"])
        dest = tmp_path / "out.abw"
        write_abw(model, str(dest))
        reloaded = load(str(dest))
        assert get_paragraphs(reloaded) == ["line A", "line B"]

    def test_empty_model_dict(self):
        assert get_paragraphs({}) == []
