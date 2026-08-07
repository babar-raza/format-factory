"""XLIFF-WRITE-001 against the shipped namespace.

MUST (SAL-XLIFF-OBL-1FE4640A3CD2FDAD, SAL-XLIFF-OBL-489B7755DF76C218):
"Preserve custom extensions and modules on write; deterministic
prefixing/formatting; report version-downgrade loss before writing" /
"Round-trip custom extensions byte-semantically in lossless mode and
report any version-downgrade loss before writing, so no tool in the chain
silently loses vendor data."

Before this slice: extension preservation and determinism were already
real and tested (test_semantic_roundtrip_preserves_unknown_namespace_and_order,
test_repeated_dumps_calls_on_one_unchanged_document_are_byte_identical), but
"report any version-downgrade loss before writing" had no implementation at
all -- dumps(profile="2.0") silently wrote a document containing 2.1-only
content under a "version=2.0" declaration, with nothing checking or
reporting the mismatch.

Per the XLIFF 2.1 specification's own Appendix C ("Specification Change
Tracking"), native ITS 2.0 support is one of exactly two content-level
features 2.1 adds over 2.0 (the other, Advanced Validation, is
Schematron-level and never appears in document content) -- the core
namespace and grammar are explicitly stated to be otherwise unchanged
between the two versions. This file proves dumps() now refuses to
downgrade a document carrying ITS content to profile="2.0", at every
level ITS content can appear (attributes on core elements, ExtensionNode
elements, and inline mixed content), while never blocking a downgrade
that carries no ITS content, and never blocking a native (non-downgrading)
write even when ITS content is present.
"""

from __future__ import annotations

import pytest

from format_factory.xliff import (
    ExtensionNode,
    InlineElement,
    PreservationMode,
    Segment,
    Unit,
    XliffDocument,
    XliffFile,
    XliffWriteError,
    dumps,
)

_ITSM_ATTR = "{urn:oasis:names:tc:xliff:itsm:2.1}mtConfidence"
_ITS_ELEMENT_TAG = "{http://www.w3.org/2005/11/its}locQualityIssues"
_ITS_ELEMENT_XML = (
    b'<its:locQualityIssues xmlns:its="http://www.w3.org/2005/11/its"/>'
)


def _document(*, units: list[Unit] | None = None, extra_children: list = None) -> XliffDocument:
    file_children: list = list(units) if units else [Unit(id="u1", children=[Segment(id="s1", source=["hi"])])]
    if extra_children:
        file_children.extend(extra_children)
    return XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[XliffFile(id="f1", children=file_children)],
    )


def test_a_document_with_no_its_content_downgrades_to_2_0_without_error() -> None:
    document = _document()

    output = dumps(document, profile="2.0")

    assert 'version="2.0"' in output


def test_an_itsm_attribute_on_a_segment_blocks_downgrade_to_2_0() -> None:
    document = _document(
        units=[
            Unit(
                id="u1",
                children=[
                    Segment(id="s1", source=["hi"], attributes={_ITSM_ATTR: "0.9"})
                ],
            )
        ]
    )

    with pytest.raises(XliffWriteError, match="ITS 2.0 content"):
        dumps(document, profile="2.0")


def test_an_its_extension_element_blocks_downgrade_to_2_0() -> None:
    document = _document(
        extra_children=[ExtensionNode(tag=_ITS_ELEMENT_TAG, xml=_ITS_ELEMENT_XML)]
    )

    with pytest.raises(XliffWriteError, match="ITS 2.0 content"):
        dumps(document, profile="2.0")


def test_its_content_inside_inline_mixed_content_blocks_downgrade_to_2_0() -> None:
    document = _document(
        units=[
            Unit(
                id="u1",
                children=[
                    Segment(
                        id="s1",
                        source=[
                            "hi ",
                            InlineElement(tag="{http://www.w3.org/2005/11/its}span", content=["x"]),
                        ],
                    )
                ],
            )
        ]
    )

    with pytest.raises(XliffWriteError, match="ITS 2.0 content"):
        dumps(document, profile="2.0")


def test_a_non_its_foreign_extension_does_not_block_downgrade() -> None:
    """Only ITS-namespaced content is a genuinely checkable content-level
    2.1-exclusive feature -- an ordinary vendor extension is preserved as
    opaque content at any profile and is not this obligation's concern."""
    document = _document(
        extra_children=[
            ExtensionNode(
                tag="{urn:example:vendor}metadata",
                xml=b'<vendor:metadata xmlns:vendor="urn:example:vendor"/>',
            )
        ]
    )

    output = dumps(document, profile="2.0")

    assert 'version="2.0"' in output


def test_its_content_never_blocks_a_native_2_1_write() -> None:
    """The refusal is specifically about downgrading, not about ITS content
    existing at all -- writing at the document's own (or an explicitly
    requested 2.1) profile must never be refused."""
    document = _document(
        extra_children=[ExtensionNode(tag=_ITS_ELEMENT_TAG, xml=_ITS_ELEMENT_XML)]
    )

    output_default = dumps(document)
    output_explicit = dumps(document, profile="2.1")

    assert 'version="2.1"' in output_default
    assert 'version="2.1"' in output_explicit


def test_canonical_mode_drops_its_extension_nodes_before_the_check_runs() -> None:
    """CANONICAL mode already drops every ExtensionNode as part of its own,
    separate contract -- once dropped, there is no longer any loss for this
    check to report, so a downgrade that would otherwise be blocked
    succeeds after canonicalization removes the ITS element."""
    document = _document(
        extra_children=[ExtensionNode(tag=_ITS_ELEMENT_TAG, xml=_ITS_ELEMENT_XML)]
    )

    output = dumps(document, profile="2.0", mode=PreservationMode.CANONICAL)

    assert 'version="2.0"' in output


def test_an_itsm_attribute_on_the_document_root_blocks_downgrade() -> None:
    document = XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[XliffFile(id="f1", children=[Unit(id="u1", children=[Segment(id="s1", source=["hi"])])])],
        attributes={_ITSM_ATTR: "0.9"},
    )

    with pytest.raises(XliffWriteError, match="ITS 2.0 content"):
        dumps(document, profile="2.0")
