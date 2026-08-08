"""ORA-PRESERVE-001 -- distinguish an absent optional value from an
explicitly written default or empty value.

MUST, quoted from the format contract:

  "Preserve the distinction between an absent optional value and an
   explicitly written default or empty value."

model/stack.py's own OraNode applies attribute defaults (x, y, opacity,
visibility, composite-op, and -- on OraStack -- isolation) at construction
time by deliberate design, so every existing compositing consumer can keep
reading `node.opacity` etc. directly without change. This obligation's own
gap was that nothing recorded WHICH of those values the source XML
actually wrote versus which were supplied because the attribute was
absent -- confirmed unbuilt by a prior tick, which framed a fix as needing
"nullable defaults threaded through OraNode/OraStack/OraLayer and every
consumer of them," a genuinely large, invasive type change.

That framing was investigated fresh and found larger than necessary: a
parallel, additive `explicit_attributes: frozenset[str]` field records
presence without changing any existing field's own type or default value,
so no existing consumer (is_isolated_group, is_visible,
composite_op_details, and any external caller) is affected at all --
proven by the fact that the entire pre-existing ora suite (337 tests)
passes unchanged.
"""

from __future__ import annotations

from format_factory.core import ResourceLimits
from format_factory.ora import OraLayer, OraStack, OraText, parse_stack

HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'


def image(body: str = "", **attributes: object) -> bytes:
    merged = {"w": 800, "h": 600, "version": "0.0.5"}
    merged.update(attributes)
    rendered = " ".join(f'{key}="{value}"' for key, value in merged.items())
    return (HEADER + f"<image {rendered}>{body}</image>").encode("utf-8")


class TestLayerAttributes:
    def test_an_explicitly_written_opacity_is_recorded_as_explicit(self) -> None:
        body = '<stack><layer name="a" src="data/1.png" opacity="0.5"/></stack>'
        document = parse_stack(image(body))
        layer = document.root.children[0]

        assert layer.was_explicit("opacity") is True
        assert layer.opacity == 0.5

    def test_an_omitted_opacity_is_not_recorded_as_explicit_even_though_the_default_matches(
        self,
    ) -> None:
        body = '<stack><layer name="a" src="data/1.png" opacity="1.0"/></stack>'
        omitted_body = '<stack><layer name="a" src="data/1.png"/></stack>'
        written = parse_stack(image(body)).root.children[0]
        omitted = parse_stack(image(omitted_body)).root.children[0]

        # Same resulting value, different provenance -- the whole point of
        # this obligation.
        assert written.opacity == omitted.opacity == 1.0
        assert written.was_explicit("opacity") is True
        assert omitted.was_explicit("opacity") is False

    def test_every_tracked_attribute_is_independently_recorded(self) -> None:
        body = (
            '<stack><layer name="a" src="data/1.png" x="5" y="-3" '
            'opacity="0.25" visibility="hidden" composite-op="svg:multiply"/></stack>'
        )
        layer = parse_stack(image(body)).root.children[0]

        for attribute in ("x", "y", "opacity", "visibility", "composite-op"):
            assert layer.was_explicit(attribute) is True

    def test_no_attributes_written_means_none_are_explicit(self) -> None:
        body = '<stack><layer name="a" src="data/1.png"/></stack>'
        layer = parse_stack(image(body)).root.children[0]

        assert layer.explicit_attributes == frozenset()
        for attribute in ("x", "y", "opacity", "visibility", "composite-op"):
            assert layer.was_explicit(attribute) is False

    def test_a_partially_written_set_records_only_what_was_written(self) -> None:
        body = '<stack><layer name="a" src="data/1.png" visibility="hidden"/></stack>'
        layer = parse_stack(image(body)).root.children[0]

        assert layer.explicit_attributes == frozenset({"visibility"})
        assert layer.was_explicit("visibility") is True
        assert layer.was_explicit("opacity") is False


class TestStackIsolationAttribute:
    def test_an_explicitly_written_isolation_is_recorded(self) -> None:
        body = '<stack isolation="isolate"><layer name="a" src="data/1.png"/></stack>'
        stack = parse_stack(image(body)).root

        assert stack.was_explicit("isolation") is True
        assert stack.isolation == "isolate"

    def test_an_omitted_isolation_is_not_recorded_even_though_it_defaults_to_auto(
        self,
    ) -> None:
        body = '<stack><layer name="a" src="data/1.png"/></stack>'
        stack = parse_stack(image(body)).root

        assert stack.isolation == "auto"
        assert stack.was_explicit("isolation") is False

    def test_isolation_does_not_leak_into_a_sibling_layers_own_tracking(self) -> None:
        body = (
            '<stack isolation="isolate">'
            '<layer name="a" src="data/1.png"/>'
            "</stack>"
        )
        stack = parse_stack(image(body)).root
        layer = stack.children[0]

        assert stack.was_explicit("isolation") is True
        assert layer.was_explicit("isolation") is False


class TestTextNode:
    def test_text_nodes_track_explicitness_the_same_way_as_layers(self) -> None:
        body = '<stack><text name="a" opacity="0.75"/></stack>'
        text = parse_stack(image(body)).root.children[0]

        assert isinstance(text, OraText)
        assert text.was_explicit("opacity") is True


class TestConstructedDirectlyInMemory:
    def test_a_node_built_directly_has_no_explicit_attributes(self) -> None:
        stack = OraStack(children=())
        assert stack.explicit_attributes == frozenset()
        assert stack.was_explicit("opacity") is False

    def test_a_layer_built_directly_has_no_explicit_attributes(self) -> None:
        layer = OraLayer(src="data/1.png")
        assert layer.explicit_attributes == frozenset()
        assert layer.was_explicit("composite-op") is False


class TestNestedStacksTrackIndependently:
    def test_a_nested_group_and_its_parent_track_their_own_attributes_separately(
        self,
    ) -> None:
        body = (
            '<stack opacity="0.9">'
            '<stack isolation="isolate">'
            '<layer name="a" src="data/1.png"/>'
            "</stack>"
            "</stack>"
        )
        outer = parse_stack(image(body)).root
        inner = outer.children[0]

        assert outer.was_explicit("opacity") is True
        assert outer.was_explicit("isolation") is False
        assert inner.was_explicit("isolation") is True
        assert inner.was_explicit("opacity") is False
