"""XLIFF-SEG-001 -- unit/segment structure and source/target language
compatibility.

MUST (SAL-XLIFF-OBL-D16EDB479826DAB5): "A unit contains at least one segment
or ignorable child; each segment and ignorable contains exactly one source
followed by at most one target."

MUST (SAL-XLIFF-OBL-6808B6BB958F8A9B / SAL-XLIFF-OBL-90EFD3BBDD9D1EC7): "An
explicit xml:lang value on a source/target child of segment or ignorable must
satisfy the enclosing xliff srcLang/trgLang. XLIFF 2.0 requires exact
equality; XLIFF 2.1 accepts exact and more-specific language tags and reports
incompatible values."

Before this slice: a Unit with zero segments passed validate() silently, and
no diagnostic existed anywhere for a segment's xml:lang conflicting with the
document's declared srcLang/trgLang. "Exactly one source, at most one
target" is a structural guarantee of the Segment dataclass shape itself
(one `source` field, one optional `target` field) rather than a runtime
check -- there is no way to construct a Segment with more than one of
either.
"""

from __future__ import annotations

import pytest

from format_factory.xliff import Segment, Unit, XliffDocument, XliffFile, validate

_XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


def _document(
    unit: Unit, *, version: str = "2.1", target_language: str | None = "fr"
) -> XliffDocument:
    return XliffDocument(
        version=version,
        source_language="en",
        target_language=target_language,
        children=[XliffFile(id="f", children=[unit])],
    )


def test_a_unit_with_no_segments_is_refused() -> None:
    report = validate(_document(Unit(id="u")))

    assert not report.is_valid
    assert "xliff.unit.segment.required" in {item.code for item in report.diagnostics}


def test_a_unit_with_a_segment_or_ignorable_is_accepted() -> None:
    segment = Segment(id="s", source=["hello"])
    ignorable = Segment(id="i", source=[" "], kind="ignorable")

    assert validate(_document(Unit(id="u", children=[segment]))).is_valid
    assert validate(_document(Unit(id="u", children=[ignorable]))).is_valid


@pytest.mark.parametrize("declared", ["en", "en-US", "EN-us"])
def test_xliff_21_accepts_exact_and_more_specific_source_language(
    declared: str,
) -> None:
    segment = Segment(
        id="s", source=["hello"], source_attributes={_XML_LANG: declared}
    )

    report = validate(_document(Unit(id="u", children=[segment]), version="2.1"))

    assert report.is_valid


def test_xliff_21_rejects_an_unrelated_source_language() -> None:
    segment = Segment(
        id="s", source=["bonjour"], source_attributes={_XML_LANG: "fr"}
    )

    report = validate(_document(Unit(id="u", children=[segment]), version="2.1"))

    assert not report.is_valid
    codes = {item.code for item in report.diagnostics}
    assert "xliff.segment.source.lang.incompatible" in codes


def test_xliff_20_requires_exact_source_language_equality() -> None:
    segment = Segment(
        id="s", source=["hello"], source_attributes={_XML_LANG: "en-US"}
    )

    report = validate(_document(Unit(id="u", children=[segment]), version="2.0"))

    assert not report.is_valid
    codes = {item.code for item in report.diagnostics}
    assert "xliff.segment.source.lang.incompatible" in codes


def test_target_language_compatibility_mirrors_source() -> None:
    compatible = Segment(
        id="s1",
        source=["hello"],
        target=["bonjour"],
        target_attributes={_XML_LANG: "fr-CA"},
    )
    incompatible = Segment(
        id="s2",
        source=["hi"],
        target=["salut"],
        target_attributes={_XML_LANG: "de"},
    )

    assert validate(
        _document(Unit(id="u", children=[compatible]), version="2.1")
    ).is_valid

    report = validate(_document(Unit(id="u", children=[incompatible]), version="2.1"))
    assert not report.is_valid
    assert "xliff.segment.target.lang.incompatible" in {
        item.code for item in report.diagnostics
    }


def test_no_declared_target_language_skips_the_target_check() -> None:
    segment = Segment(
        id="s",
        source=["hi"],
        target=["salut"],
        target_attributes={_XML_LANG: "de"},
    )

    report = validate(
        _document(Unit(id="u", children=[segment]), target_language=None)
    )

    assert "xliff.segment.target.lang.incompatible" not in {
        item.code for item in report.diagnostics
    }
