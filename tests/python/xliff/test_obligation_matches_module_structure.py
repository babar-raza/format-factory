"""XLIFF-TEXT-001 / XLIFF-PARSE-001 / XLIFF-MODULE-001 -- Translation
Candidates (Matches) module structural validation.

MUST (SAL-XLIFF-OBL-73868B0E3F5A4C22 and its cross-capability duplicates):
"(XLIFF 2.1 Translation Candidates module) The Translation Candidates
module uses namespace urn:oasis:names:tc:xliff:matches:2.0; matches
contains one or more match elements, and each match requires ref plus one
source and one target."

Grounded directly in the pinned XLIFF 2.1 Translation Candidates module
schema (inside .local/format-contracts/acquired/xliff/src-xlf-002.bin,
schemas/matches.xsd): mtc:matches declares minOccurs="1"
maxOccurs="unbounded" for its mtc:match children; mtc:match itself
declares its own ref attribute use="required" and requires EXACTLY one
xlf:source and EXACTLY one xlf:target direct child -- both use the XLIFF
core namespace (imported from xliff_core_2.0.xsd), not the Matches
module's own namespace.

Before this slice: the Matches module was preserved only as opaque
extension content, the same starting point Metadata and Resource Data
were in before the two immediately preceding ticks this session. While
verifying this slice against the full pre-existing suite before writing
any new test, a genuinely pre-existing, non-conformant fixture was found
and fixed: test_obligation_module_coverage.py's
test_translation_candidates_module_round_trips had an mtc:match with a
ref attribute but no source or target children at all (raw text content
directly inside match, which the schema also does not permit --
mtc:match's complexType is mixed="false"). Fixed by adding proper
source/target children carrying the same "candidate" text the test
already asserted on, preserving the test's own round-trip-preservation
purpose.
"""

from __future__ import annotations

from format_factory.xliff import ExtensionNode, Segment, Unit, XliffDocument, XliffFile, validate

_MATCHES_NS = "urn:oasis:names:tc:xliff:matches:2.0"
_CORE_NS = "urn:oasis:names:tc:xliff:document:2.0"


def _document_with_matches_extension(matches_xml: bytes) -> XliffDocument:
    extension = ExtensionNode(tag=f"{{{_MATCHES_NS}}}matches", xml=matches_xml)
    return XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f",
                children=[
                    Unit(id="u", children=[Segment(id="s", source=["x"])]),
                    extension,
                ],
            )
        ],
    )


def test_a_well_formed_match_validates_cleanly() -> None:
    document = _document_with_matches_extension(
        f'<mtc:matches xmlns:mtc="{_MATCHES_NS}" xmlns="{_CORE_NS}">'
        '<mtc:match ref="#u1/source-text"><source>s</source><target>t</target></mtc:match>'
        "</mtc:matches>".encode()
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert not any(code.startswith("xliff.module.matches") for code in codes)


def test_matches_with_no_match_at_all_is_a_violation() -> None:
    document = _document_with_matches_extension(
        f'<mtc:matches xmlns:mtc="{_MATCHES_NS}"></mtc:matches>'.encode()
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.matches.match.required" in codes


def test_a_match_with_no_ref_attribute_is_a_violation() -> None:
    document = _document_with_matches_extension(
        f'<mtc:matches xmlns:mtc="{_MATCHES_NS}" xmlns="{_CORE_NS}">'
        "<mtc:match><source>s</source><target>t</target></mtc:match>"
        "</mtc:matches>".encode()
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.matches.match.ref.required" in codes


def test_a_match_with_neither_source_nor_target_is_flagged_for_both() -> None:
    document = _document_with_matches_extension(
        f'<mtc:matches xmlns:mtc="{_MATCHES_NS}">'
        '<mtc:match ref="#x"/>'
        "</mtc:matches>".encode()
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.matches.match.source.required" in codes
    assert "xliff.module.matches.match.target.required" in codes


def test_a_match_with_two_sources_is_a_violation() -> None:
    document = _document_with_matches_extension(
        f'<mtc:matches xmlns:mtc="{_MATCHES_NS}" xmlns="{_CORE_NS}">'
        '<mtc:match ref="#x"><source>a</source><source>b</source><target>t</target></mtc:match>'
        "</mtc:matches>".encode()
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.matches.match.source.required" in codes
    assert "xliff.module.matches.match.target.required" not in codes


def test_multiple_well_formed_matches_all_validate_cleanly() -> None:
    document = _document_with_matches_extension(
        f'<mtc:matches xmlns:mtc="{_MATCHES_NS}" xmlns="{_CORE_NS}">'
        '<mtc:match ref="#a"><source>a1</source><target>a2</target></mtc:match>'
        '<mtc:match ref="#b"><source>b1</source><target>b2</target></mtc:match>'
        "</mtc:matches>".encode()
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert not any(code.startswith("xliff.module.matches") for code in codes)


def test_a_non_matches_extension_is_untouched_by_this_check() -> None:
    extension = ExtensionNode(
        tag="{urn:vendor:test}other", xml=b'<v:other xmlns:v="urn:vendor:test"/>'
    )
    document = XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f",
                children=[Unit(id="u", children=[Segment(id="s", source=["x"])]), extension],
            )
        ],
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert not any(code.startswith("xliff.module.matches") for code in codes)
