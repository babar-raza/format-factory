"""XLIFF-PARSE-001 / XLIFF-MODULE-001 / XLIFF-MODEL-001 -- Metadata module
structural validation.

MUST (SAL-XLIFF-OBL-234A057EBC798099 and its cross-capability duplicates):
"(XLIFF 2.1 Metadata module) The Metadata module uses namespace
urn:oasis:names:tc:xliff:metadata:2.0; metadata contains one or more
metaGroup elements, and meta elements require a type attribute."

Grounded directly in the pinned XLIFF 2.1 Metadata module schema (inside
.local/format-contracts/acquired/xliff/src-xlf-002.bin,
schemas/metadata.xsd): mda:metadata's own sequence declares
minOccurs="1" maxOccurs="unbounded" for its mda:metaGroup children, and
mda:meta declares its type attribute use="required". mda:metaGroup can
also nest recursively (a choice of further metaGroup or meta elements,
each minOccurs="1" maxOccurs="unbounded"), so meta elements can appear at
any nesting depth, not only directly under the top-level metaGroup.

Before this slice: the Metadata module was preserved only as opaque
extension content (a generic ExtensionNode carrying raw, unparsed XML
bytes) -- _extension_well_formed() already re-parsed every extension to
check it is well-formed XML with a matching tag, but nothing inspected
Metadata-specific structure at all.
"""

from __future__ import annotations

from format_factory.xliff import ExtensionNode, Segment, Unit, XliffDocument, XliffFile, validate

_METADATA_NS = "urn:oasis:names:tc:xliff:metadata:2.0"


def _document_with_metadata_extension(metadata_xml: bytes) -> XliffDocument:
    extension = ExtensionNode(tag=f"{{{_METADATA_NS}}}metadata", xml=metadata_xml)
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


def test_a_metagroup_with_a_typed_meta_validates_cleanly() -> None:
    document = _document_with_metadata_extension(
        b'<mda:metadata xmlns:mda="urn:oasis:names:tc:xliff:metadata:2.0">'
        b'<mda:metaGroup><mda:meta type="project-id">PRJ-42</mda:meta></mda:metaGroup>'
        b"</mda:metadata>"
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.metadata.metagroup.required" not in codes
    assert "xliff.module.metadata.meta.type.required" not in codes


def test_metadata_with_no_metagroup_at_all_is_a_violation() -> None:
    document = _document_with_metadata_extension(
        b'<mda:metadata xmlns:mda="urn:oasis:names:tc:xliff:metadata:2.0"></mda:metadata>'
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.metadata.metagroup.required" in codes


def test_a_meta_element_with_no_type_attribute_is_a_violation() -> None:
    document = _document_with_metadata_extension(
        b'<mda:metadata xmlns:mda="urn:oasis:names:tc:xliff:metadata:2.0">'
        b"<mda:metaGroup><mda:meta>no type here</mda:meta></mda:metaGroup>"
        b"</mda:metadata>"
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.metadata.meta.type.required" in codes


def test_a_meta_nested_inside_a_nested_metagroup_still_requires_type() -> None:
    """metaGroup can nest recursively (a choice of further metaGroup or
    meta, per the pinned schema) -- meta's type requirement is checked at
    any nesting depth, not only directly under the top-level metaGroup."""
    document = _document_with_metadata_extension(
        b'<mda:metadata xmlns:mda="urn:oasis:names:tc:xliff:metadata:2.0">'
        b"<mda:metaGroup><mda:metaGroup>"
        b"<mda:meta>deeply nested, no type</mda:meta>"
        b"</mda:metaGroup></mda:metaGroup>"
        b"</mda:metadata>"
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.metadata.meta.type.required" in codes


def test_multiple_typed_meta_elements_across_multiple_metagroups_validate_cleanly() -> None:
    document = _document_with_metadata_extension(
        b'<mda:metadata xmlns:mda="urn:oasis:names:tc:xliff:metadata:2.0">'
        b'<mda:metaGroup><mda:meta type="a">1</mda:meta></mda:metaGroup>'
        b'<mda:metaGroup><mda:meta type="b">2</mda:meta><mda:meta type="c">3</mda:meta></mda:metaGroup>'
        b"</mda:metadata>"
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.metadata.metagroup.required" not in codes
    assert "xliff.module.metadata.meta.type.required" not in codes


def test_a_non_metadata_extension_is_untouched_by_this_check() -> None:
    """This check only applies to extensions carrying the Metadata
    module's own namespace -- any other extension, however malformed by
    Metadata's own rules it would be if reinterpreted, is not in scope."""
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

    assert not any(code.startswith("xliff.module.metadata") for code in codes)
