"""
tests/python/abw/test_r312_abw_iter_sections.py

Sprint: ff-sprint-s312-abw-section-iterator-20260626
Authority: AbiWord AWML 1.0 — section block element

Tests for abw_iter_sections() in abw_section_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_MINIMAL = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
_TWO = _REPO / "samples" / "by-format" / "abw" / "two-paragraphs.abw"


class TestAbwIterSectionsImport:
    def test_importable_from_abw_section_iterator(self):
        from abw.abw_section_iterator import abw_iter_sections
        assert callable(abw_iter_sections)

    def test_importable_from_package(self):
        import abw
        assert hasattr(abw, "abw_iter_sections")


class TestAbwIterSectionsOutput:
    def test_returns_iterator(self):
        from abw.abw_section_iterator import abw_iter_sections
        result = abw_iter_sections(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_sections(self):
        from abw.abw_section_iterator import abw_iter_sections
        sections = list(abw_iter_sections(str(_MINIMAL)))
        assert len(sections) >= 1

    def test_section_type_is_spec_section(self):
        from abw.abw_section_iterator import abw_iter_sections
        from abw.spec.document.section import Section
        sections = list(abw_iter_sections(str(_MINIMAL)))
        assert all(isinstance(s, Section) for s in sections)

    def test_section_has_spec_qname(self):
        from abw.abw_section_iterator import abw_iter_sections
        sections = list(abw_iter_sections(str(_MINIMAL)))
        assert all(hasattr(s, "spec_qname") for s in sections)

    def test_section_qname_value(self):
        from abw.abw_section_iterator import abw_iter_sections
        sections = list(abw_iter_sections(str(_MINIMAL)))
        assert all(s.spec_qname == "abiword:section" for s in sections)

    def test_section_has_index(self):
        from abw.abw_section_iterator import abw_iter_sections
        sections = list(abw_iter_sections(str(_MINIMAL)))
        for s in sections:
            assert isinstance(s.index, int) and s.index >= 0

    def test_section_has_paragraphs(self):
        from abw.abw_section_iterator import abw_iter_sections
        sections = list(abw_iter_sections(str(_MINIMAL)))
        for s in sections:
            assert isinstance(s.paragraphs, list)

    def test_section_has_paragraph_count(self):
        from abw.abw_section_iterator import abw_iter_sections
        sections = list(abw_iter_sections(str(_MINIMAL)))
        for s in sections:
            assert isinstance(s.paragraph_count, int) and s.paragraph_count >= 0

    def test_consistent(self):
        from abw.abw_section_iterator import abw_iter_sections
        r1 = [s.index for s in abw_iter_sections(str(_MINIMAL))]
        r2 = [s.index for s in abw_iter_sections(str(_MINIMAL))]
        assert r1 == r2
