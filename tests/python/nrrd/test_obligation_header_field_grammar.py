"""NRRD-HEADER-001 -- ordinary field-specification grammar is enforced.

MUST (SAL-NRRD-OBL-C13492B6879B6E90; SAL-NRRD-00008, "Teem NRRD Format
Specification -- Section 1.2"): "Every ordinary NRRD header field
specification uses a field identifier, a colon followed by one space, and a
field value; no whitespace may precede the field identifier."

The pinned spec source (src-nrrd-001.bin) states this precisely: "Whitespace
(that is not part of the previous line's termination) is not allowed before
a field identifier" and "a colon followed by a single space ... and then the
[field descriptor]". "Extra whitespace after the field descriptor and before
the line termination is ignored" -- so trailing value whitespace remains
correctly permissive; only the two explicit grammar rules are now enforced.

Before this slice, reader.py's ordinary-field branch stripped both the key
and the value unconditionally, silently accepting a leading-whitespace
field identifier, a missing space after the colon, or multiple spaces after
the colon -- all of which the spec forbids.
"""

from __future__ import annotations

import pytest

from format_factory.nrrd import loads
from format_factory.nrrd.errors import NrrdParseError


def _document(field_line: bytes) -> bytes:
    return (
        b"NRRD0005\n"
        + field_line
        + b"\ntype: uint8\ndimension: 1\nsizes: 2\nencoding: raw\n\n\x00\x00"
    )


def test_a_single_space_after_the_colon_parses() -> None:
    document = loads(_document(b"content: hello"))

    assert document.header["content"] == "hello"


def test_trailing_value_whitespace_is_still_ignored() -> None:
    """Spec: "Extra whitespace after the field descriptor and before the
    line termination is ignored" -- this permissive behavior must survive
    the new strict-grammar checks unchanged."""
    document = loads(_document(b"content: hello   "))

    assert document.header["content"] == "hello"


@pytest.mark.parametrize(
    "field_line",
    [
        pytest.param(b" content: hello", id="leading-whitespace"),
        pytest.param(b"\tcontent: hello", id="leading-tab"),
        pytest.param(b"content:hello", id="no-space-after-colon"),
        pytest.param(b"content:  hello", id="two-spaces-after-colon"),
    ],
)
def test_grammar_violations_are_rejected(field_line: bytes) -> None:
    with pytest.raises(NrrdParseError):
        loads(_document(field_line))
