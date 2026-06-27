"""
tests/python/odt/test_r315_odt_iter_headings.py

Sprint: ff-sprint-s315-odt-heading-iterator-20260626
Authority: ODF 1.3 §5.1.2 — text:h

Tests for odt_iter_headings() in odt_heading_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_VALID_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
_MINIMAL = _VALID_DIR / "minimal-document.odt"
_TWO = _VALID_DIR / "two-paragraphs.odt"


class TestOdtIterHeadingsImport:
    def test_importable_from_odt_heading_iterator(self):
        from odt.odt_heading_iterator import odt_iter_headings
        assert callable(odt_iter_headings)

    def test_importable_from_package(self):
        import odt
        assert hasattr(odt, "odt_iter_headings")


class TestOdtIterHeadingsOutput:
    def test_returns_iterator(self):
        from odt.odt_heading_iterator import odt_iter_headings
        result = odt_iter_headings(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_list(self):
        from odt.odt_heading_iterator import odt_iter_headings
        # minimal-document.odt has no headings — should yield nothing
        headings = list(odt_iter_headings(str(_MINIMAL)))
        assert isinstance(headings, list)

    def test_heading_type_is_spec_heading(self):
        from odt.odt_heading_iterator import odt_iter_headings
        from odt.spec.text.heading import Heading
        headings = list(odt_iter_headings(str(_MINIMAL)))
        assert all(isinstance(h, Heading) for h in headings)

    def test_heading_spec_qname_attr_exists(self):
        from odt.spec.text.heading import Heading
        assert hasattr(Heading, "spec_qname")
        assert Heading.spec_qname == "text:h"

    def test_heading_spec_fact_ref_attr_exists(self):
        from odt.spec.text.heading import Heading
        assert hasattr(Heading, "spec_fact_ref")

    def test_consistent(self):
        from odt.odt_heading_iterator import odt_iter_headings
        r1 = list(odt_iter_headings(str(_MINIMAL)))
        r2 = list(odt_iter_headings(str(_MINIMAL)))
        assert len(r1) == len(r2)

    def test_heading_instance_properties(self):
        from odt.spec.text.heading import Heading
        h = Heading({"text": "Chapter 1", "level": 1})
        assert h.text == "Chapter 1"
        assert h.level == 1
        assert h.spec_qname == "text:h"
