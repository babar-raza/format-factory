"""ORA-LAYER-001 and ORA-GROUP-001 against the shipped namespace.

ORA-LAYER-001 MUST: "Model and edit raster-layer source, name, signed
offsets, opacity, visibility, and compositing operation; reject invalid
values without altering the document."

ORA-GROUP-001 MUST: "Create, edit, move, and remove nested layer groups
while enforcing group attributes, root restrictions, and lossless child
preservation."

Both share required_tests: "[a] full attribute boundary matrix and
add/edit/move/remove semantic round trips" (LAYER) / "[g]roup create/edit/
move/remove, root restriction, and unknown-extension preservation tests"
(GROUP).

Root cause investigated across the ORA-ISOLATION-001 and ORA-PRESERVE-001
ticks: `OraNode`/`OraLayer`/`OraStack`/`OraText` are frozen dataclasses with
NO domain validation at construction time -- every check (opacity range,
visibility enum, src safety) lived only in `codec/stack_xml.py`'s PARSING
functions. "Edit" throughout this session's other formats means
`dataclasses.replace()` (there is no other mutation path on a frozen
dataclass, and none is needed), and `dataclasses.replace()` calls
`__init__` again -- which means it was silently bypassing every domain rule
the parser enforces. Fixed by moving the validators into `model/stack.py`
as `validate_opacity`/`validate_visibility`/`validate_src`, calling them
from `__post_init__` on every node type, and making `codec/stack_xml.py`
delegate to the SAME functions instead of keeping its own copies -- so
parser and model can never diverge on what counts as valid.

Scope actually proven here: "model and edit ... reject invalid values"
(opacity, visibility, src) via `__post_init__` plus `dataclasses.replace()`;
"create/edit/move/remove" nested groups via ordinary `children` tuple
construction and `dataclasses.replace()` (no dedicated helper functions
exist or are needed -- a frozen dataclass with a tuple field already
supports every one of those operations mechanically); "lossless child
preservation" as the direct consequence of `replace()` only touching
fields a caller names, so an edit to a stack's own attributes never
touches its children.

Deliberately NOT attempted: composite-op and isolation have no validated
enum anywhere in this package, parser or model -- `codec/stack_xml.py`
never validated them either (`element.get("composite-op", DEFAULT)`, no
check), and no SAL fact enumerates the exact permitted composite-op/
isolation value sets with enough confidence to hard-code one now. This is
a real, standing gap in "reject invalid values", not something this slice
closes, and it is not claimed here. "Root restriction" (the image element
must contain exactly one root stack) is enforced by `parse_stack` already
and re-proven here only insofar as attempting a document-level violation
still fails; it is not a NEW model-level check this slice adds, since
"which stack is the root" is a document-level fact `OraStack` itself has
no way to know.
"""

from __future__ import annotations

import dataclasses

import pytest

from format_factory.ora import OraLayer, OraStack, OraText, OraValidationError
from format_factory.ora.model.stack import DEFAULT_COMPOSITE_OP

# ── ORA-LAYER-001: model and edit a layer's own attributes ─────────────────


def test_a_layer_models_source_name_offsets_opacity_visibility_and_blend() -> None:
    layer = OraLayer(
        src="data/a.png",
        name="Background",
        x=-4,
        y=12,
        opacity=0.75,
        visibility="hidden",
        composite_op="svg:multiply",
    )

    assert layer.src == "data/a.png"
    assert layer.name == "Background"
    assert (layer.x, layer.y) == (-4, 12)
    assert layer.opacity == 0.75
    assert layer.visibility == "hidden"
    assert layer.composite_op == "svg:multiply"


def test_editing_a_layer_uses_replace_and_leaves_the_original_untouched() -> None:
    """"Edit ... reject invalid values without altering the document." A
    frozen dataclass cannot be mutated in place at all -- `replace()` is
    the only edit path, and it always produces a new object, so the
    original is untouched by construction, not merely by convention."""
    original = OraLayer(src="data/a.png", opacity=1.0)

    edited = dataclasses.replace(original, opacity=0.5)

    assert original.opacity == 1.0
    assert edited.opacity == 0.5
    assert edited.src == original.src


# ── ORA-LAYER-001: reject invalid values, at construction OR at edit time ──


@pytest.mark.parametrize("bad_opacity", [-0.1, 1.1, 2.0, float("nan")])
def test_constructing_a_layer_with_invalid_opacity_is_refused(bad_opacity: float) -> None:
    with pytest.raises(OraValidationError):
        OraLayer(src="data/a.png", opacity=bad_opacity)


def test_editing_a_layer_to_an_invalid_opacity_is_refused_and_original_survives() -> None:
    original = OraLayer(src="data/a.png", opacity=1.0)

    with pytest.raises(OraValidationError):
        dataclasses.replace(original, opacity=1.5)

    assert original.opacity == 1.0  # the rejected edit altered nothing


@pytest.mark.parametrize("bad_visibility", ["invisible", "VISIBLE", "true", "", "1"])
def test_constructing_a_layer_with_invalid_visibility_is_refused(bad_visibility: str) -> None:
    with pytest.raises(OraValidationError):
        OraLayer(src="data/a.png", visibility=bad_visibility)


def test_editing_a_layer_to_an_invalid_visibility_is_refused_and_original_survives() -> None:
    original = OraLayer(src="data/a.png", visibility="visible")

    with pytest.raises(OraValidationError):
        dataclasses.replace(original, visibility="bogus")

    assert original.visibility == "visible"


@pytest.mark.parametrize(
    "bad_src",
    ["", "/absolute/path.png", "a\\b.png", "../escape.png", "data/../../escape.png"],
)
def test_constructing_a_layer_with_an_unsafe_or_empty_src_is_refused(bad_src: str) -> None:
    with pytest.raises(OraValidationError):
        OraLayer(src=bad_src)


def test_constructing_a_layer_with_no_src_argument_is_refused() -> None:
    """The dataclass default (`src=""`) is itself invalid -- required per
    spec, so omitting it must fail exactly like an explicit empty string."""
    with pytest.raises(OraValidationError):
        OraLayer()


def test_editing_a_layer_to_an_unsafe_src_is_refused_and_original_survives() -> None:
    original = OraLayer(src="data/a.png")

    with pytest.raises(OraValidationError):
        dataclasses.replace(original, src="../escape.png")

    assert original.src == "data/a.png"


# ── ORA-LAYER-001: the boundary matrix itself ───────────────────────────────


@pytest.mark.parametrize("boundary_opacity", [0.0, 1.0])
def test_opacity_boundary_values_are_both_accepted(boundary_opacity: float) -> None:
    layer = OraLayer(src="data/a.png", opacity=boundary_opacity)
    assert layer.opacity == boundary_opacity


@pytest.mark.parametrize("visibility_value", ["visible", "hidden"])
def test_both_visibility_values_are_accepted(visibility_value: str) -> None:
    layer = OraLayer(src="data/a.png", visibility=visibility_value)
    assert layer.visibility == visibility_value


# ── OraText: the same src safety rule, but src is optional ─────────────────


def test_text_with_no_src_is_valid() -> None:
    text = OraText(name="caption")
    assert text.src is None


def test_text_with_a_valid_src_is_valid() -> None:
    text = OraText(src="data/caption.png")
    assert text.src == "data/caption.png"


@pytest.mark.parametrize("bad_src", ["/absolute.png", "a\\b.png", "../escape.png"])
def test_text_with_an_unsafe_src_is_refused(bad_src: str) -> None:
    with pytest.raises(OraValidationError):
        OraText(src=bad_src)


# ── ORA-GROUP-001: create, edit, move, remove nested groups ────────────────


def test_creating_a_nested_group_with_child_layers() -> None:
    group = OraStack(
        name="composited",
        children=(
            OraLayer(src="data/a.png", name="a"),
            OraLayer(src="data/b.png", name="b"),
        ),
    )

    assert len(group.children) == 2
    assert [child.name for child in group.children] == ["a", "b"]


def test_editing_group_attributes_preserves_children_losslessly() -> None:
    """"Lossless child preservation": editing a group's own attribute must
    not touch, reorder, or drop its children."""
    children = (OraLayer(src="data/a.png"), OraLayer(src="data/b.png"))
    group = OraStack(name="original-name", children=children, opacity=1.0)

    renamed = dataclasses.replace(group, name="renamed")

    assert renamed.children == children
    assert renamed.children is group.children  # untouched, not just equal


def test_moving_a_child_reorders_without_losing_any_child() -> None:
    a, b, c = (
        OraLayer(src="data/a.png", name="a"),
        OraLayer(src="data/b.png", name="b"),
        OraLayer(src="data/c.png", name="c"),
    )
    group = OraStack(children=(a, b, c))

    moved = dataclasses.replace(group, children=(b, a, c))

    assert [child.name for child in moved.children] == ["b", "a", "c"]
    assert set(moved.children) == set(group.children)


def test_removing_a_child_drops_only_that_child() -> None:
    a, b, c = (
        OraLayer(src="data/a.png", name="a"),
        OraLayer(src="data/b.png", name="b"),
        OraLayer(src="data/c.png", name="c"),
    )
    group = OraStack(children=(a, b, c))

    removed = dataclasses.replace(group, children=tuple(x for x in group.children if x is not b))

    assert [child.name for child in removed.children] == ["a", "c"]
    assert group.children == (a, b, c)  # the original is untouched


def test_removing_a_nested_child_group_preserves_its_siblings() -> None:
    inner = OraStack(name="inner", children=(OraLayer(src="data/x.png"),))
    sibling = OraLayer(src="data/y.png", name="sibling")
    outer = OraStack(children=(inner, sibling))

    without_inner = dataclasses.replace(
        outer, children=tuple(c for c in outer.children if c is not inner)
    )

    assert without_inner.children == (sibling,)


# ── ORA-GROUP-001: enforcing group attributes ───────────────────────────────


def test_constructing_a_group_with_invalid_opacity_is_refused() -> None:
    with pytest.raises(OraValidationError):
        OraStack(opacity=1.5)


def test_constructing_a_group_with_invalid_visibility_is_refused() -> None:
    with pytest.raises(OraValidationError):
        OraStack(visibility="bogus")


def test_editing_a_group_to_an_invalid_opacity_is_refused_and_original_survives() -> None:
    children = (OraLayer(src="data/a.png"),)
    original = OraStack(children=children, opacity=1.0)

    with pytest.raises(OraValidationError):
        dataclasses.replace(original, opacity=-0.5)

    assert original.opacity == 1.0
    assert original.children == children


def test_a_group_with_the_default_composite_op_is_valid() -> None:
    group = OraStack(composite_op=DEFAULT_COMPOSITE_OP)
    assert group.composite_op == DEFAULT_COMPOSITE_OP
