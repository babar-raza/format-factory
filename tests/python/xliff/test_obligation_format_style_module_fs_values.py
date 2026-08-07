"""XLIFF-PARSE-001 / XLIFF-MODULE-001 -- Format Style module fs value
constraints.

MUST (SAL-XLIFF-OBL-D8C6CC9733716C74 and its cross-capability duplicate):
"(XLIFF 2.1 Format Style module) The Format Style module uses namespace
urn:oasis:names:tc:xliff:fs:2.0 and defines fs and subFs attributes; fs
values are constrained by the module schema."

Grounded directly in the pinned XLIFF 2.1 Format Style module schema
(inside .local/format-contracts/acquired/xliff/src-xlf-002.bin,
schemas/fs.xsd): fs:fs is restricted to a fixed 58-value enumeration of
HTML-tag-like tokens (cross-verified programmatically against the pinned
XSD's own <xs:enumeration> entries, not typed from memory); fs:subFs is
an unrestricted xs:string, so it has no value to check.

Unlike the Metadata/Resource Data/Matches modules (each a single
top-level extension element), fs and subFs "attach to existing core
elements rather than introducing their own" -- confirmed directly by this
package's own pre-existing fixture (test_format_style_attributes_round_
trip_on_a_unit), which attaches them to a <unit>. This slice therefore
checks every host this package generically preserves unknown attributes
on: the unit itself, each segment/ignorable and its own source/target
attribute dicts, and every inline code element (ph/pc/sc/ec/mrk) within
source/target content.
"""

from __future__ import annotations

from format_factory.xliff import InlineElement, Segment, Unit, XliffDocument, XliffFile, validate

_FS_NS = "urn:oasis:names:tc:xliff:fs:2.0"
_FS = f"{{{_FS_NS}}}fs"
_SUBFS = f"{{{_FS_NS}}}subFs"


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


def test_a_valid_fs_value_on_a_unit_validates_cleanly() -> None:
    document = _document(unit_attributes={_FS: "span", _SUBFS: "bold"})

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.fs.fs.invalid" not in codes


def test_an_invalid_fs_value_on_a_unit_is_a_violation() -> None:
    document = _document(unit_attributes={_FS: "not-a-real-html-tag"})

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.fs.fs.invalid" in codes


def test_a_valid_fs_value_on_an_inline_element_validates_cleanly() -> None:
    document = _document(source=[InlineElement("ph", {"id": "1", _FS: "b"})])

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.fs.fs.invalid" not in codes


def test_an_invalid_fs_value_on_an_inline_element_is_a_violation() -> None:
    document = _document(source=[InlineElement("ph", {"id": "1", _FS: "bogus"})])

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.fs.fs.invalid" in codes


def test_an_invalid_fs_value_on_source_attributes_is_a_violation() -> None:
    document = _document(source_attributes={_FS: "invalid-tag"})

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.fs.fs.invalid" in codes


def test_subfs_accepts_any_string_it_is_genuinely_unrestricted() -> None:
    document = _document(unit_attributes={_SUBFS: "anything-goes-here-123"})

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.fs.fs.invalid" not in codes


def test_no_fs_attributes_anywhere_validates_cleanly() -> None:
    document = _document()

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.fs.fs.invalid" not in codes


def test_every_enumerated_fs_value_is_individually_accepted() -> None:
    """A spot-check across a representative slice of the full 58-value
    enumeration, proving the set is not accidentally too narrow."""
    for value in ("a", "h1", "h6", "table", "tt", "ul", "div", "span"):
        document = _document(unit_attributes={_FS: value})

        codes = {item.code for item in validate(document).diagnostics}

        assert "xliff.module.fs.fs.invalid" not in codes, value
