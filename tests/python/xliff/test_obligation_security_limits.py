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


def test_a_document_exceeding_a_configured_node_count_limit_is_rejected() -> None:
    tight = ResourceLimits(max_xml_nodes=10)

    with pytest.raises(ResourceLimitError, match="max_xml_nodes exceeded"):
        loads(_nested(50), limits=tight)


def test_default_limits_apply_without_caller_opt_in() -> None:
    assert effective_limits(None) is XLIFF_DEFAULT_LIMITS
    assert effective_limits(None).max_input_bytes > 0
    assert effective_limits(None).max_nesting_depth > 0


def test_loading_without_explicit_limits_still_enforces_the_safe_default_nesting_limit() -> None:
    with pytest.raises(ResourceLimitError, match="max_nesting_depth exceeded"):
        loads(_nested(XLIFF_DEFAULT_LIMITS.max_nesting_depth + 1))
