"""XLIFF-SEC-001 -- security baseline: limits, DTD/entity rejection, no
implicit execution or resolution of embedded/untrusted content.

MUST (SAL-XLIFF-OBL-130340BC212989D5): "Guard against algorithmic complexity
attacks; use checked arithmetic for size and count calculations and bound
recursion depth."

MUST (SAL-XLIFF-OBL-FE51662AAD65CDB3): "Provide configurable limits for
input size, nesting depth, element/record count, and total decoded payload
bytes, with safe defaults enabled."

Before this slice, `_enforce_tree_limits` (reader.py) already enforced
max_nesting_depth and max_xml_nodes on every parse, and XLIFF_DEFAULT_LIMITS
already supplied safe defaults without caller opt-in -- but nothing in the
suite exercised the nesting-depth rejection path directly (only DTD/entity
rejection and a bare input-size limit were tested).
"""

from __future__ import annotations

import pytest

from format_factory.core import ResourceLimitError, ResourceLimits
from format_factory.xliff import loads
from format_factory.xliff.security import XLIFF_DEFAULT_LIMITS, effective_limits

_NS = "urn:oasis:names:tc:xliff:document:2.0"


def _nested(depth: int) -> bytes:
    open_tags = b"<a>" * depth
    close_tags = b"</a>" * depth
    return (
        f'<xliff xmlns="{_NS}" version="2.1" srcLang="en">'
        '<file id="f">'
    ).encode() + open_tags + close_tags + b"</file></xliff>"


def test_a_document_within_the_default_nesting_limit_loads() -> None:
    document = loads(_nested(5))

    assert document.version == "2.1"


def test_a_document_exceeding_a_configured_nesting_limit_is_rejected() -> None:
    tight = ResourceLimits(max_nesting_depth=5)

    with pytest.raises(ResourceLimitError, match="max_nesting_depth exceeded"):
        loads(_nested(50), limits=tight)


def _wide(width: int) -> bytes:
    siblings = b"<a/>" * width
    return (
        f'<xliff xmlns="{_NS}" version="2.1" srcLang="en">'
        '<file id="f">'
    ).encode() + siblings + b"</file></xliff>"


def test_a_wide_shallow_document_is_bounded_by_node_count_not_depth() -> None:
    """A quadratic-blowup-style complexity attack (many siblings, shallow
    nesting) is a distinct vector from the deep-nesting case above --
    _enforce_tree_limits checks max_xml_nodes on every node visited, so a
    wide-but-shallow document is refused even though its depth stays low."""
    tight = ResourceLimits(max_xml_nodes=100)

    with pytest.raises(ResourceLimitError, match="max_xml_nodes exceeded"):
        loads(_wide(10000), limits=tight)


def test_a_wide_document_within_the_node_count_limit_loads() -> None:
    document = loads(_wide(50), limits=ResourceLimits(max_xml_nodes=1000))

    assert document.version == "2.1"


def test_a_document_exceeding_a_configured_node_count_limit_is_rejected() -> None:
    tight = ResourceLimits(max_xml_nodes=10)

    with pytest.raises(ResourceLimitError, match="max_xml_nodes exceeded"):
        loads(_nested(50), limits=tight)


def _many_attributes(count: int) -> bytes:
    attrs = " ".join(f'a{i}="v"' for i in range(count))
    return (
        f'<xliff xmlns="{_NS}" version="2.1" srcLang="en" {attrs}>'
        '<file id="f"><unit id="u"><segment id="s"><source>hi</source></segment></unit></file>'
        "</xliff>"
    ).encode()


def test_an_attribute_flood_on_one_element_is_rejected() -> None:
    """Attribute-count accumulation was not previously bounded at all --
    confirmed genuinely unenforced by direct probing before this fix,
    unlike the equivalent ubl reader's own _enforce_tree_limits, which
    already checks this vector. A single element carrying far more
    attributes than the configured max_entries limit is refused,
    independent of node count and nesting depth (both stay trivially
    small here)."""
    tight = ResourceLimits(max_entries=100)

    with pytest.raises(ResourceLimitError, match="max_entries exceeded"):
        loads(_many_attributes(2000), limits=tight)


def test_a_document_with_attributes_within_the_limit_loads() -> None:
    document = loads(_many_attributes(10), limits=ResourceLimits(max_entries=1000))

    assert document.version == "2.1"


def _huge_text(byte_count: int) -> bytes:
    text = "x" * byte_count
    return (
        f'<xliff xmlns="{_NS}" version="2.1" srcLang="en">'
        f'<file id="f"><unit id="u"><segment id="s"><source>{text}</source></segment></unit></file>'
        "</xliff>"
    ).encode()


def test_a_text_flood_exceeding_the_decoded_byte_limit_is_rejected() -> None:
    """Cumulative text-byte accumulation across the whole tree was not
    previously bounded at all -- confirmed genuinely unenforced by direct
    probing before this fix. A single large text node is refused via the
    same limit UBL's equivalent check already uses for this vector."""
    tight = ResourceLimits(max_decompressed_bytes=100)

    with pytest.raises(ResourceLimitError, match="max_decompressed_bytes exceeded"):
        loads(_huge_text(5000), limits=tight)


def test_a_document_with_text_within_the_byte_limit_loads() -> None:
    document = loads(_huge_text(10), limits=ResourceLimits(max_decompressed_bytes=1000))

    assert document.version == "2.1"


def test_default_limits_apply_without_caller_opt_in() -> None:
    assert effective_limits(None) is XLIFF_DEFAULT_LIMITS
    assert effective_limits(None).max_input_bytes > 0
    assert effective_limits(None).max_nesting_depth > 0


def test_loading_without_explicit_limits_still_enforces_the_safe_default_nesting_limit() -> None:
    with pytest.raises(ResourceLimitError, match="max_nesting_depth exceeded"):
        loads(_nested(XLIFF_DEFAULT_LIMITS.max_nesting_depth + 1))
