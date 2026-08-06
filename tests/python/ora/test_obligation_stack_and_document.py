"""ORA-STACK-001 and ORA-DOCUMENT-001 — the layer tree and its document root.

`stack.xml` is the only place OpenRaster records what a document *is*: canvas
size, profile version, resolution, and the ordered nested tree of stacks and
layers. It is also untrusted XML from inside an untrusted archive, so the parser
has to be bounded and refuse doctypes before it models anything.

Assertions come from the contract's normative rules, quoted where they bind:

  "The root image element requires positive integer w and h attributes and a
   version string identifying the OpenRaster specification profile."
  "Since profile 0.0.3, xres and yres are optional positive integer
   pixels-per-inch values that must be specified together and default to 72."
  "A stack element contains nested stack, layer, or text elements, and its first
   child is the uppermost item in visual layer order."
  "Every layer element requires a src attribute identifying the separate archive
   member that stores the graphical layer."
  "Non-root stacks and layers use signed integer x and y positions whose default
   values are zero."
  "Stack and layer opacity is a floating-point value in the inclusive range zero
   through one."
  "Stack and layer visibility accepts only visible or hidden and defaults to
   visible when omitted."
  "The composite-op attribute defaults to svg:src-over..."
"""

from __future__ import annotations

import pytest

from format_factory.core import ResourceLimits
from format_factory.ora import OraLayer, OraStack, OraText, OraValidationError, parse_stack

HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'


def image(body: str = "", **attributes: object) -> bytes:
    merged = {"w": 800, "h": 600, "version": "0.0.5"}
    merged.update(attributes)
    rendered = " ".join(f'{key}="{value}"' for key, value in merged.items())
    return (HEADER + f"<image {rendered}>{body}</image>").encode("utf-8")


SIMPLE_BODY = '<stack><layer name="top" src="data/1.png"/><layer name="bottom" src="data/2.png"/></stack>'


# ── ORA-DOCUMENT-001: the root image element ───────────────────────────────


def test_a_minimal_document_parses() -> None:
    document = parse_stack(image(SIMPLE_BODY))

    assert (document.width, document.height) == (800, 600)
    assert document.version == "0.0.5"


@pytest.mark.parametrize("missing", ["w", "h", "version"])
def test_required_root_attributes_are_required(missing: str) -> None:
    attributes = {"w": 8, "h": 6, "version": "0.0.5"}
    del attributes[missing]
    rendered = " ".join(f'{k}="{v}"' for k, v in attributes.items())
    payload = (HEADER + f"<image {rendered}>{SIMPLE_BODY}</image>").encode("utf-8")

    with pytest.raises(OraValidationError) as raised:
        parse_stack(payload)

    assert missing in str(raised.value)


@pytest.mark.parametrize("bad", ["0", "-1", "1.5", "", "eight", "0x10", " 8"])
def test_canvas_dimensions_must_be_positive_integers(bad: str) -> None:
    with pytest.raises(OraValidationError):
        parse_stack(image(SIMPLE_BODY, w=bad))


def test_the_root_element_must_be_image() -> None:
    payload = (HEADER + f"<stack>{SIMPLE_BODY}</stack>").encode("utf-8")

    with pytest.raises(OraValidationError) as raised:
        parse_stack(payload)

    assert "image" in str(raised.value)


# ── Resolution: optional, paired, positive, defaulting to 72 ───────────────


def test_resolution_defaults_to_72_when_absent() -> None:
    document = parse_stack(image(SIMPLE_BODY))

    assert (document.xres, document.yres) == (72, 72)


def test_resolution_is_read_when_present() -> None:
    document = parse_stack(image(SIMPLE_BODY, xres=300, yres=600))

    assert (document.xres, document.yres) == (300, 600)


@pytest.mark.parametrize("present,absent", [("xres", "yres"), ("yres", "xres")])
def test_resolution_attributes_must_be_specified_together(present: str, absent: str) -> None:
    """"must be specified together" -- one alone is an error, not a half-default.
    A parser that defaulted the missing one would silently invent a resolution."""
    with pytest.raises(OraValidationError) as raised:
        parse_stack(image(SIMPLE_BODY, **{present: 300}))

    assert absent in str(raised.value)


@pytest.mark.parametrize("bad", ["0", "-300", "1.5", "abc"])
def test_resolution_must_be_positive_integers(bad: str) -> None:
    with pytest.raises(OraValidationError):
        parse_stack(image(SIMPLE_BODY, xres=bad, yres=300))


def test_an_absurd_canvas_is_refused_by_checked_arithmetic() -> None:
    """"validate dimensions with checked arithmetic" -- w*h is a pixel count that
    a caller will allocate against, so it is bounded before it is believed."""
    limits = ResourceLimits(max_decompressed_bytes=1_000_000)

    with pytest.raises(Exception) as raised:
        parse_stack(image(SIMPLE_BODY, w=10**9, h=10**9), limits=limits)

    assert "canvas" in str(raised.value).lower() or "pixel" in str(raised.value).lower()


def test_an_ordinary_canvas_passes_the_same_limits() -> None:
    """Control: the rejection above must be about the absurd canvas, not the limits."""
    limits = ResourceLimits(max_decompressed_bytes=1_000_000)

    document = parse_stack(image(SIMPLE_BODY, w=640, h=480), limits=limits)

    assert document.width == 640


# ── ORA-STACK-001: the ordered nested tree ─────────────────────────────────


def test_the_root_stack_is_exposed() -> None:
    document = parse_stack(image(SIMPLE_BODY))

    assert isinstance(document.root, OraStack)
    assert len(document.root.children) == 2


def test_document_order_is_visual_order_topmost_first() -> None:
    """"its first child is the uppermost item in visual layer order" -- the one
    rule a reader cannot get wrong without inverting every rendered image."""
    document = parse_stack(image(SIMPLE_BODY))

    assert [child.name for child in document.root.children] == ["top", "bottom"]
    assert document.root.children[0].name == "top"


def test_nested_stacks_are_modelled_as_a_tree() -> None:
    body = (
        '<stack>'
        '<stack name="group"><layer name="inner" src="data/i.png"/></stack>'
        '<layer name="outer" src="data/o.png"/>'
        "</stack>"
    )
    document = parse_stack(image(body))

    group = document.root.children[0]
    assert isinstance(group, OraStack)
    assert group.name == "group"
    assert [child.name for child in group.children] == ["inner"]
    assert document.root.children[1].name == "outer"


def test_a_text_element_parses_as_a_stack_child() -> None:
    """"A stack element contains nested stack, layer, or text elements" --
    the third permitted child kind, unlike stack/layer, is never exercised
    through the actual XML parser elsewhere in this file."""
    body = '<stack><text name="caption" src="data/caption.png"/><layer name="art" src="data/art.png"/></stack>'
    document = parse_stack(image(body))

    caption = document.root.children[0]
    assert isinstance(caption, OraText)
    assert caption.name == "caption"
    assert caption.src == "data/caption.png"
    assert document.root.children[1].name == "art"


def test_a_text_element_without_src_parses_with_src_none() -> None:
    """Text is optional-src, unlike layer -- captured content can be inline."""
    body = '<stack><text name="caption"/></stack>'
    document = parse_stack(image(body))

    caption = document.root.children[0]
    assert isinstance(caption, OraText)
    assert caption.src is None


def test_every_layer_requires_a_src() -> None:
    body = '<stack><layer name="no-src"/></stack>'

    with pytest.raises(OraValidationError) as raised:
        parse_stack(image(body))

    assert "src" in str(raised.value)


def test_layer_src_is_archive_root_relative() -> None:
    document = parse_stack(image(SIMPLE_BODY))
    layer = document.root.children[0]

    assert isinstance(layer, OraLayer)
    assert layer.src == "data/1.png"


def test_a_layer_src_that_escapes_the_archive_is_refused() -> None:
    """The container refuses traversing member names; a src attribute is the
    other way the same escape arrives, and it is validated here for the same
    reason -- it becomes a path the moment a caller resolves it."""
    body = '<stack><layer name="evil" src="../../etc/passwd"/></stack>'

    with pytest.raises(OraValidationError):
        parse_stack(image(body))


def test_unknown_child_elements_are_refused() -> None:
    body = '<stack><sneaky src="data/1.png"/></stack>'

    with pytest.raises(OraValidationError):
        parse_stack(image(body))


# ── Common attributes ──────────────────────────────────────────────────────


def test_positions_default_to_zero_and_accept_negative_values() -> None:
    body = (
        '<stack>'
        '<layer name="a" src="data/a.png"/>'
        '<layer name="b" src="data/b.png" x="-40" y="17"/>'
        "</stack>"
    )
    document = parse_stack(image(body))

    assert (document.root.children[0].x, document.root.children[0].y) == (0, 0)
    assert (document.root.children[1].x, document.root.children[1].y) == (-40, 17)


def test_opacity_defaults_to_one_and_accepts_the_inclusive_range() -> None:
    body = (
        '<stack>'
        '<layer name="a" src="data/a.png"/>'
        '<layer name="b" src="data/b.png" opacity="0"/>'
        '<layer name="c" src="data/c.png" opacity="1"/>'
        '<layer name="d" src="data/d.png" opacity="0.25"/>'
        "</stack>"
    )
    document = parse_stack(image(body))

    assert [child.opacity for child in document.root.children] == [1.0, 0.0, 1.0, 0.25]


@pytest.mark.parametrize("bad", ["-0.1", "1.1", "2", "abc", ""])
def test_opacity_outside_zero_through_one_is_refused(bad: str) -> None:
    body = f'<stack><layer name="a" src="data/a.png" opacity="{bad}"/></stack>'

    with pytest.raises(OraValidationError):
        parse_stack(image(body))


def test_visibility_defaults_to_visible_and_accepts_only_two_values() -> None:
    body = (
        '<stack>'
        '<layer name="a" src="data/a.png"/>'
        '<layer name="b" src="data/b.png" visibility="hidden"/>'
        "</stack>"
    )
    document = parse_stack(image(body))

    assert document.root.children[0].visibility == "visible"
    assert document.root.children[1].visibility == "hidden"


@pytest.mark.parametrize("bad", ["invisible", "VISIBLE", "true", "1", ""])
def test_unknown_visibility_values_are_refused(bad: str) -> None:
    body = f'<stack><layer name="a" src="data/a.png" visibility="{bad}"/></stack>'

    with pytest.raises(OraValidationError):
        parse_stack(image(body))


def test_composite_op_defaults_to_src_over() -> None:
    document = parse_stack(image(SIMPLE_BODY))

    assert document.root.children[0].composite_op == "svg:src-over"


def test_composite_op_is_preserved_verbatim() -> None:
    """Blend modes are an open vocabulary; an unknown one is preserved rather
    than rejected, because discarding it would silently change the image."""
    body = '<stack><layer name="a" src="data/a.png" composite-op="svg:multiply"/></stack>'
    document = parse_stack(image(body))

    assert document.root.children[0].composite_op == "svg:multiply"


# ── The XML is untrusted ───────────────────────────────────────────────────


def test_a_doctype_is_refused() -> None:
    """Entity expansion is the classic XML denial-of-service and file-disclosure
    vector. Refusing the doctype outright is simpler to prove than bounding it."""
    payload = (
        HEADER
        + '<!DOCTYPE image [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>\n'
        + f"<image w=\"8\" h=\"6\" version=\"0.0.5\">{SIMPLE_BODY}</image>"
    ).encode("utf-8")

    with pytest.raises(OraValidationError) as raised:
        parse_stack(payload)

    assert "dtd" in str(raised.value).lower()


def test_malformed_xml_is_refused() -> None:
    with pytest.raises(OraValidationError):
        parse_stack(b"<image w='8' h='6' version='0.0.5'><stack></image>")


def test_nesting_deeper_than_the_limit_is_refused() -> None:
    depth = 40
    body = "<stack>" * depth + "</stack>" * depth
    limits = ResourceLimits(max_nesting_depth=8)

    with pytest.raises(Exception) as raised:
        parse_stack(image(body), limits=limits)

    assert "depth" in str(raised.value).lower() or "nest" in str(raised.value).lower()


def test_more_nodes_than_the_limit_is_refused() -> None:
    body = "<stack>" + "".join(
        f'<layer name="l{index}" src="data/{index}.png"/>' for index in range(200)
    ) + "</stack>"
    limits = ResourceLimits(max_xml_nodes=20)

    with pytest.raises(Exception) as raised:
        parse_stack(image(body), limits=limits)

    assert "node" in str(raised.value).lower()


def test_an_ordinary_document_passes_the_same_node_and_depth_limits() -> None:
    """Control for the two limit tests above."""
    limits = ResourceLimits(max_nesting_depth=8, max_xml_nodes=20)

    document = parse_stack(image(SIMPLE_BODY), limits=limits)

    assert len(document.root.children) == 2
