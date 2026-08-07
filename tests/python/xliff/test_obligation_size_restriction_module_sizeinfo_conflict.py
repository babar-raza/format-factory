"""XLIFF-PARSE-001 / XLIFF-MODULE-001 -- Size and Length Restriction
module sizeInfo/sizeInfoRef mutual exclusivity.

MUST (SAL-XLIFF-OBL-05547046CBCB57F7 and its cross-capability duplicates
SAL-XLIFF-OBL-57668EDF714BE172, SAL-XLIFF-OBL-EEA9C58A385F7C96):
"Confirmed gap, not an audit backlog: no typed sizeRestriction/
storageRestriction attribute parsing exists to test -- the module is
preserved only as opaque extension content, not modeled." That framing
is correct for the module's typed attribute-value semantics (a full
sizeRestriction/storageRestriction typed model remains genuinely
unbuilt and out of scope here), but the pinned spec text also contains
one universally-true, profile-independent structural constraint this
package's own established Format Style module pattern
(_check_fs_value/_format_style_module_diagnostics) can directly enforce.

Grounded directly in the pinned XLIFF 2.1 specification text
(.local/format-contracts/acquired/xliff/src-xliff-003.bin, Section 5.7
"Size and Length Restriction Module"): sizeInfo's own prose Constraints
section -- "This attribute MUST NOT be specified if and only if
sizeInfoRef is used. They MUST NOT be specified at the same time" --
restated identically, from the other side, in sizeInfoRef's own
Constraints section.

Deliberately narrow: unlike the Glossary/Validation modules'
standalone-extension-element shape, slr:sizeInfo/slr:sizeInfoRef attach
directly to existing core elements (file/group/unit/pc/sc/ec/ph),
exactly like the Format Style module's fs:fs/fs:subFs -- this slice
mirrors that established pattern precisely rather than inventing new
architecture. It does NOT model sizeRestriction/storageRestriction's own
value format ("[minsize,]maxsize"), since that format is scoped to
specific named standard profiles (xliff:codepoints, xliff:utf8, ...)
selected via generalProfile/storageProfile, resolvable only through the
same whole-tree, parent-aware inheritance this package has deliberately
not built for xml:space/xml:lang either.
"""

from __future__ import annotations

from format_factory.xliff import InlineElement, Segment, Unit, XliffDocument, XliffFile, validate

_SLR_NS = "urn:oasis:names:tc:xliff:sizerestriction:2.0"
_SIZE_INFO = f"{{{_SLR_NS}}}sizeInfo"
_SIZE_INFO_REF = f"{{{_SLR_NS}}}sizeInfoRef"


def _document(
    *,
    unit_attributes: dict[str, str] | None = None,
    source: list[object] | None = None,
    source_attributes: dict[str, str] | None = None,
) -> XliffDocument:
    return XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f",
                children=[
                    Unit(
                        id="u",
                        attributes=unit_attributes or {},
                        children=[
                            Segment(
                                id="s",
                                source=source or ["x"],
                                source_attributes=source_attributes or {},
                            )
                        ],
                    )
                ],
            )
        ],
    )


def _codes(document: XliffDocument) -> set[str]:
    return {item.code for item in validate(document).diagnostics if "slr" in item.code}


def test_sizeinfo_alone_on_a_unit_validates_cleanly() -> None:
    document = _document(unit_attributes={_SIZE_INFO: "5"})

    assert _codes(document) == set()


def test_sizeinforef_alone_on_a_unit_validates_cleanly() -> None:
    document = _document(unit_attributes={_SIZE_INFO_REF: "#ref1"})

    assert _codes(document) == set()


def test_neither_attribute_present_validates_cleanly() -> None:
    document = _document()

    assert _codes(document) == set()


def test_both_attributes_on_a_unit_is_a_violation() -> None:
    document = _document(unit_attributes={_SIZE_INFO: "5", _SIZE_INFO_REF: "#ref1"})

    assert "xliff.module.slr.sizeinfo.conflict" in _codes(document)


def test_both_attributes_on_source_attributes_is_a_violation() -> None:
    document = _document(source_attributes={_SIZE_INFO: "5", _SIZE_INFO_REF: "#ref1"})

    assert "xliff.module.slr.sizeinfo.conflict" in _codes(document)


def test_both_attributes_on_an_inline_element_is_a_violation() -> None:
    document = _document(
        source=[InlineElement("ph", {"id": "1", _SIZE_INFO: "5", _SIZE_INFO_REF: "#ref1"})]
    )

    assert "xliff.module.slr.sizeinfo.conflict" in _codes(document)
