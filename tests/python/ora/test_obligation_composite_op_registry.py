"""ORA-COMPOSITE-001 / ORA-STACK-001 / ORA-LAYER-001 / ORA-GROUP-001 /
ORA-EDIT-001 / ORA-RENDER-001.

MUST: "(Layer Stack — Common attributes — composite-op) The composite-op
attribute defaults to svg:src-over and selects a documented blend function
combined with a Porter-Duff compositing operator."

Before this slice: composite-op was stored and round-tripped as an opaque
string with no lookup exposing what a value like svg:src-over actually
means in blend-function/Porter-Duff terms -- confirmed gap, shared across
6 obligations under 6 different capability IDs. Not attempted until now
because building an honest registry needed the OpenRaster specification's
actual composite-op inventory as a verified source, not invented from
memory; that inventory has now been read directly from the pinned,
authority-locked Layer Stack Specification
(.local/format-contracts/acquired/ora/src-ora-003.bin, "composite-op
attribute" section).

That same spec section also states composite-op is a deliberately open,
forward-compatible vocabulary ("In the future other compositing modes
might be added..."), so this registry's lookup returns None for an
unrecognized value rather than raising -- and a document using one keeps
loading and round-tripping unchanged, proven below.
"""

from __future__ import annotations

from format_factory.ora import CompositeOpInfo, OraLayer, OraStack, composite_op_info
from format_factory.ora.model import COMPOSITE_OP_REGISTRY, DEFAULT_COMPOSITE_OP


def test_the_registry_covers_every_value_in_the_pinned_spec_table() -> None:
    """20 values, transcribed directly from the Layer Stack Specification's
    own composite-op table."""
    assert len(COMPOSITE_OP_REGISTRY) == 20
    assert "svg:src-over" in COMPOSITE_OP_REGISTRY
    assert "svg:dst-atop" in COMPOSITE_OP_REGISTRY


def test_the_default_value_maps_to_normal_blending_and_source_over() -> None:
    info = composite_op_info(DEFAULT_COMPOSITE_OP)

    assert info == CompositeOpInfo("Normal", "Source Over")


def test_a_non_default_blend_only_value_maps_correctly() -> None:
    """svg:multiply changes only the blending function; the compositing
    operator stays Source Over, exactly as the spec table lists it."""
    info = composite_op_info("svg:multiply")

    assert info == CompositeOpInfo("Multiply", "Source Over")


def test_a_non_default_porter_duff_operator_value_maps_correctly() -> None:
    """svg:dst-atop changes the compositing operator, not the blending
    function -- the spec table lists its blending function as Normal."""
    info = composite_op_info("svg:dst-atop")

    assert info == CompositeOpInfo("Normal", "Destination Atop")


def test_svg_plus_is_the_one_value_with_a_non_source_over_operator_named_lighter() -> None:
    info = composite_op_info("svg:plus")

    assert info == CompositeOpInfo("Normal", "Lighter")


def test_an_unrecognized_value_returns_none_rather_than_raising() -> None:
    """composite-op is a deliberately open vocabulary -- the spec's own text
    reserves it for future compositing modes. A value outside today's table
    is forward-compatible content, not a defect."""
    assert composite_op_info("future:some-new-mode") is None


def test_a_layer_exposes_its_composite_op_details_via_the_default() -> None:
    layer = OraLayer(src="data/only.png")

    assert layer.composite_op == DEFAULT_COMPOSITE_OP
    assert layer.composite_op_details == CompositeOpInfo("Normal", "Source Over")


def test_a_layer_exposes_its_composite_op_details_for_a_non_default_value() -> None:
    layer = OraLayer(src="data/only.png", composite_op="svg:screen")

    assert layer.composite_op_details == CompositeOpInfo("Screen", "Source Over")


def test_a_stack_exposes_its_composite_op_details_the_same_way_as_a_layer() -> None:
    stack = OraStack(composite_op="svg:color-burn")

    assert stack.composite_op_details == CompositeOpInfo("Color Burn", "Source Over")


def test_an_unrecognized_composite_op_on_a_layer_is_preserved_not_rejected() -> None:
    """Forward compatibility, proven behaviorally: constructing a node with a
    value outside today's table does not raise, and the raw string survives
    unchanged -- only the documented-meaning lookup returns None."""
    layer = OraLayer(src="data/only.png", composite_op="future:some-new-mode")

    assert layer.composite_op == "future:some-new-mode"
    assert layer.composite_op_details is None


def test_every_registry_value_round_trips_through_a_layer_construction() -> None:
    """No value in the spec's own table is silently rejected or altered."""
    for value, expected in COMPOSITE_OP_REGISTRY.items():
        layer = OraLayer(src="data/only.png", composite_op=value)

        assert layer.composite_op == value
        assert layer.composite_op_details == expected
