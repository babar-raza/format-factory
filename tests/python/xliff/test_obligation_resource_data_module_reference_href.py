"""XLIFF-TEXT-001 / XLIFF-PARSE-001 / XLIFF-MODULE-001 -- Resource Data
module reference href requirement.

MUST (SAL-XLIFF-OBL-7CED833579FE91A4 and its cross-capability duplicates):
"(XLIFF modules - resource data with external references) The Resource
Data module models resource items and references; source and target
resource payloads may use optional href attributes, while a reference
element requires href."

Grounded directly in the pinned XLIFF 2.1 Resource Data module schema
(inside .local/format-contracts/acquired/xliff/src-xlf-002.bin,
schemas/resource_data.xsd): res:source and res:target both declare their
href attribute use="optional", while res:reference declares its href
attribute use="required". res:reference can appear (0..unbounded) inside
any res:resourceItem nested inside the module's root res:resourceData
element, so the check walks the whole subtree rather than only direct
children.

Before this slice: the Resource Data module was preserved only as opaque
extension content, with zero structural inspection -- the same starting
point the Metadata module was in before an earlier tick this session.
"""

from __future__ import annotations

from format_factory.xliff import ExtensionNode, Segment, Unit, XliffDocument, XliffFile, validate

_RESOURCE_DATA_NS = "urn:oasis:names:tc:xliff:resourcedata:2.0"


def _document_with_resource_data_extension(resource_data_xml: bytes) -> XliffDocument:
    extension = ExtensionNode(tag=f"{{{_RESOURCE_DATA_NS}}}resourceData", xml=resource_data_xml)
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


def test_a_reference_with_href_validates_cleanly() -> None:
    document = _document_with_resource_data_extension(
        f'<res:resourceData xmlns:res="{_RESOURCE_DATA_NS}">'
        "<res:resourceItem>"
        '<res:reference href="http://example.com/image.png"/>'
        "</res:resourceItem>"
        "</res:resourceData>".encode()
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.resourcedata.reference.href.required" not in codes


def test_a_reference_with_no_href_is_a_violation() -> None:
    document = _document_with_resource_data_extension(
        f'<res:resourceData xmlns:res="{_RESOURCE_DATA_NS}">'
        "<res:resourceItem><res:reference/></res:resourceItem>"
        "</res:resourceData>".encode()
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.resourcedata.reference.href.required" in codes


def test_source_and_target_with_no_href_validate_cleanly_the_attribute_is_optional() -> None:
    document = _document_with_resource_data_extension(
        f'<res:resourceData xmlns:res="{_RESOURCE_DATA_NS}">'
        "<res:resourceItem><res:source/><res:target/></res:resourceItem>"
        "</res:resourceData>".encode()
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.resourcedata.reference.href.required" not in codes


def test_source_and_target_with_href_also_validate_cleanly() -> None:
    document = _document_with_resource_data_extension(
        f'<res:resourceData xmlns:res="{_RESOURCE_DATA_NS}">'
        '<res:resourceItem><res:source href="src.png"/><res:target href="tgt.png"/></res:resourceItem>'
        "</res:resourceData>".encode()
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.resourcedata.reference.href.required" not in codes


def test_one_reference_missing_href_among_several_resourceitems_is_still_flagged() -> None:
    document = _document_with_resource_data_extension(
        f'<res:resourceData xmlns:res="{_RESOURCE_DATA_NS}">'
        '<res:resourceItem><res:reference href="a.png"/></res:resourceItem>'
        "<res:resourceItem><res:reference/></res:resourceItem>"
        "</res:resourceData>".encode()
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.module.resourcedata.reference.href.required" in codes


def test_a_non_resourcedata_extension_is_untouched_by_this_check() -> None:
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

    assert not any(code.startswith("xliff.module.resourcedata") for code in codes)
