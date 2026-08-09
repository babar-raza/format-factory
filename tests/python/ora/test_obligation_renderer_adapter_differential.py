"""ORA-COMPOSITE-001 -- adapter differential tests against a genuinely
independent second renderer.

MUST (SAL-ORA-OBL-2CC875865800D528): "Expose the selected profile's
complete compositing-operation inventory, default operation, validation,
and pixel semantics through a replaceable rendering adapter." required_tests
names "adapter differential tests" explicitly. Before this file, the
`Renderer` protocol's own substitutability was proven only against test
doubles (a minimal class, a stateful class -- neither doing real pixel
arithmetic) -- confirmed by direct grep before writing this file: no
second real compositing implementation existed anywhere in this package.

`render_straight_alpha_reference()` (render.py) is that second,
independent implementation: it re-derives Porter-Duff "source over"
directly from the textbook straight-alpha definition
(out_a = a_s + a_d*(1-a_s); out_c = (a_s*c_s + a_d*(1-a_s)*c_d) / out_a)
and walks the layer tree with its own recursive function, sharing no
compositing code with `render()`'s own premultiplied-canvas
implementation -- only the separately-tested `decode_png`/
`composite_op_info` primitives. It is deliberately, honestly bounded to
Normal blend + Source Over (the default, and the only combination every
real sample in this package's own corpus uses), refusing
(`OraValidationError`) any other composite-op rather than silently
producing an unverified result. Building a second independent
implementation of the full 15-blend-mode/6-operator matrix is a
substantially larger undertaking, not attempted here.
"""

from __future__ import annotations

import io
import struct
import zipfile
import zlib

from format_factory.ora import (
    OraDocument,
    OraValidationError,
    load,
    render_document,
    render_straight_alpha_reference,
)

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _png(width: int = 8, height: int = 8, *, r: int = 255, g: int = 0, b: int = 0, a: int = 200) -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    row = bytes([0]) + bytes([r, g, b, a]) * width
    raw = row * height
    return PNG_SIGNATURE + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


def _archive(stack_xml: bytes, layers: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, b"image/openraster")
        zf.writestr("stack.xml", stack_xml)
        zf.writestr("Thumbnails/thumbnail.png", _png(16, 16))
        zf.writestr("mergedimage.png", _png())
        for name, data in layers.items():
            zf.writestr(name, data)
    return buffer.getvalue()


def _assert_pixel_identical(document: OraDocument, members: dict[str, bytes]) -> None:
    a = render_document(document, members)
    b = render_straight_alpha_reference(
        document.root, members, width=document.width, height=document.height
    )
    assert (a.width, a.height) == (b.width, b.height)
    assert a.pixels == b.pixels, "the two independent implementations disagree on at least one pixel"


class TestRealCorpusSamplesAgree:
    def test_minimal_sample(self) -> None:
        image = load("samples/by-format/ora/valid/minimal.ora")
        _assert_pixel_identical(image.document, image.members)

    def test_multi_layer_sample(self) -> None:
        image = load("samples/by-format/ora/valid/multi-layer.ora")
        _assert_pixel_identical(image.document, image.members)

    def test_with_groups_sample(self) -> None:
        image = load("samples/by-format/ora/valid/with-groups.ora")
        _assert_pixel_identical(image.document, image.members)


class TestSyntheticEdgeCasesAgree:
    def test_isolated_group_with_opacity_offset_and_clipping(self) -> None:
        stack_xml = (
            b'<?xml version="1.0" encoding="UTF-8"?>\n'
            b'<image w="10" h="10" version="0.0.5">'
            b"<stack>"
            b'<stack name="iso" isolation="isolate" opacity="0.6">'
            b'<layer name="a" src="data/a.png" x="2" y="2"/>'
            b'<layer name="b" src="data/b.png" opacity="0.5"/>'
            b"</stack>"
            b'<layer name="c" src="data/c.png" x="6" y="6"/>'
            b"</stack></image>"
        )
        layers = {
            "data/a.png": _png(8, 8, r=255, g=0, b=0, a=200),
            "data/b.png": _png(8, 8, r=0, g=255, b=0, a=150),
            "data/c.png": _png(8, 8, r=0, g=0, b=255, a=100),
        }
        image = load(_archive(stack_xml, layers))
        _assert_pixel_identical(image.document, image.members)

    def test_fully_transparent_layer(self) -> None:
        stack_xml = (
            b'<?xml version="1.0" encoding="UTF-8"?>\n'
            b'<image w="8" h="8" version="0.0.5">'
            b'<stack><layer name="a" src="data/a.png"/></stack></image>'
        )
        layers = {"data/a.png": _png(8, 8, a=0)}
        image = load(_archive(stack_xml, layers))
        _assert_pixel_identical(image.document, image.members)

    def test_fully_opaque_overlapping_layers(self) -> None:
        stack_xml = (
            b'<?xml version="1.0" encoding="UTF-8"?>\n'
            b'<image w="8" h="8" version="0.0.5">'
            b'<stack><layer name="top" src="data/top.png"/>'
            b'<layer name="bottom" src="data/bottom.png"/></stack></image>'
        )
        layers = {
            "data/top.png": _png(8, 8, r=10, g=20, b=30, a=255),
            "data/bottom.png": _png(8, 8, r=200, g=200, b=200, a=255),
        }
        image = load(_archive(stack_xml, layers))
        _assert_pixel_identical(image.document, image.members)


def test_refuses_a_non_normal_source_over_composite_op_rather_than_silently_producing_an_unverified_result() -> None:
    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.5">'
        b'<stack><layer name="a" src="data/a.png" composite-op="svg:multiply"/></stack></image>'
    )
    image = load(_archive(stack_xml, {"data/a.png": _png()}))

    try:
        render_straight_alpha_reference(
            image.document.root,
            image.members,
            width=image.document.width,
            height=image.document.height,
        )
        raise AssertionError("expected OraValidationError")
    except OraValidationError as exc:
        assert "svg:multiply" in str(exc)
