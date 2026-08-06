"""ORA-DOCUMENT-001 -- model construction without I/O.

MUST, quoted from the format contract:

  "The root image element requires positive integer w and h attributes and a
   version string identifying the OpenRaster specification profile."
  "Since profile 0.0.3, xres and yres are optional positive integer
   pixels-per-inch values that must be specified together and default to 72."

required_tests: "Root/canvas/profile boundary and overflow matrices; model
construction without I/O."

test_obligation_stack_and_document.py already proves the root/canvas/profile
boundary and overflow matrices, but exclusively through codec/stack_xml.py's
parse_stack() -- every fixture is bytes of XML. It never constructs an
`OraDocument` directly, so it cannot prove the domain invariants (positive
w/h, non-empty version, positive xres/yres) hold for "model construction
without I/O" the way model/stack.py's OraNode.__post_init__ already proves
for opacity/visibility/src. Before this slice, `OraDocument` had no
`__post_init__` at all: a caller building or editing one directly (not
through the XML parser) could construct `OraDocument(width=-5, height=10,
version="", root=stack)` with no refusal -- the model's own invariants were
enforced only accidentally, by the fact that every construction site
happened to be parse_stack.
"""

from __future__ import annotations

import dataclasses

import pytest

from format_factory.ora import OraDocument, OraStack, OraValidationError


def _stack() -> OraStack:
    return OraStack(children=())


def _document(**overrides: object) -> OraDocument:
    fields = {"width": 800, "height": 600, "version": "0.0.5", "root": _stack()}
    fields.update(overrides)
    return OraDocument(**fields)  # type: ignore[arg-type]


# ── Positive: constructing directly, with no XML in sight ──────────────────


def test_a_valid_document_constructs_directly_without_parsing_xml() -> None:
    document = _document()

    assert document.width == 800
    assert document.height == 600
    assert document.version == "0.0.5"
    assert document.xres == 72
    assert document.yres == 72


def test_explicit_resolution_is_retained_on_direct_construction() -> None:
    document = _document(xres=300, yres=300)

    assert document.xres == 300
    assert document.yres == 300


def test_pixel_count_is_available_immediately_after_direct_construction() -> None:
    document = _document(width=10, height=20)

    assert document.pixel_count == 200


# ── Negative: the same domain invariants hold without the XML parser ───────


@pytest.mark.parametrize("bad", [0, -1])
def test_non_positive_width_is_refused_on_direct_construction(bad: int) -> None:
    with pytest.raises(OraValidationError, match="width"):
        _document(width=bad)


@pytest.mark.parametrize("bad", [0, -1])
def test_non_positive_height_is_refused_on_direct_construction(bad: int) -> None:
    with pytest.raises(OraValidationError, match="height"):
        _document(height=bad)


def test_an_empty_version_is_refused_on_direct_construction() -> None:
    with pytest.raises(OraValidationError, match="version"):
        _document(version="")


@pytest.mark.parametrize("bad", [0, -1])
def test_non_positive_xres_is_refused_on_direct_construction(bad: int) -> None:
    with pytest.raises(OraValidationError, match="xres"):
        _document(xres=bad)


@pytest.mark.parametrize("bad", [0, -1])
def test_non_positive_yres_is_refused_on_direct_construction(bad: int) -> None:
    with pytest.raises(OraValidationError, match="yres"):
        _document(yres=bad)


# ── Editing (dataclasses.replace) re-runs the same invariants ──────────────


def test_replace_with_an_invalid_width_is_refused_not_silently_applied() -> None:
    """model/stack.py's OraNode docstring states this rule applies to editing,
    not only initial construction, for the identical reason: `replace()`
    calls `__init__` again, which runs `__post_init__`."""
    document = _document()

    with pytest.raises(OraValidationError, match="width"):
        dataclasses.replace(document, width=-1)


def test_replace_with_valid_values_produces_an_independent_document() -> None:
    document = _document()
    resized = dataclasses.replace(document, width=1920, height=1080)

    assert resized.width == 1920
    assert resized.height == 1080
    assert document.width == 800, "the original document must not be mutated"
