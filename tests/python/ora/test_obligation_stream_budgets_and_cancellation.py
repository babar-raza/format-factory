"""ORA-STREAM-001 (SAL-ORA-OBL-F8A3777A56AA6121) against the shipped
namespace.

MUST: "Stream archive and XML inspection in bounded memory, expose lazy
asset access, and fail before exceeding configured compressed, expanded,
raster, nesting, or render budgets."

Before this slice: this specific obligation ID had zero cross-referenced
evidence -- status=missing, source_symbols=[] -- despite five of its own six
named requirements already being implemented and extensively tested across
sibling modules built for other obligations this session: bounded-memory
archive inspection and the compressed/expanded budgets
(codec/container.py, test_obligation_container_and_mimetype.py -- limits
checked from the ZIP central directory alone, before decompressing a
single byte), lazy asset access and the raster budget
(codec/assets.py, codec/png_metadata.py, test_obligation_raster_assets.py --
metadata read from a PNG's IHDR chunk only, proven available even when the
pixel data itself is corrupt), and the nesting budget
(codec/stack_xml.py, test_obligation_stack_and_document.py /
test_obligation_security_baseline.py -- a bounded recursion walk refusing
depth beyond the configured limit).

This file closes the two remaining, genuinely unproven pieces with fresh,
dedicated tests:

"Lazy-read instrumentation" (this obligation's own required_tests wording,
taken literally): proven by spying on the underlying archive's own read
calls, not inferred from the absence of an observed side effect --
resolving one layer's asset never reads a sibling layer's own archive
member.

"Cancellation": this library is synchronous with no async/threading
primitives anywhere, so cancellation cannot mean interrupting a read
mid-flight. It means the API's own shape lets a caller stop calling the
resolver after any layer without cost -- proven by contrasting
resolve_all_assets() (eager, all-or-nothing: fails outright on an
unresolvable layer without yielding anything) with the granular
iter_layers()/resolve_asset() combination (yields each result as it goes,
so a caller can stop -- "cancel" -- the moment they have what they need or
before reaching a layer they no longer want).

"Render budget" is NOT addressed here and remains this obligation's own
sole genuine gap: this package has no rendering engine at all, the same
scope already correctly deferred for ORA-RENDER-001 and ORA-COMPOSITE-001's
own "pixel semantics" clause.
"""

from __future__ import annotations

import io
import struct
import zipfile
import zlib
from unittest.mock import patch

import pytest

from format_factory.ora import OraContainer, OraValidationError, parse_stack, resolve_all_assets, resolve_asset
from format_factory.ora.codec.assets import iter_layers

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def _png(width: int = 4, height: int = 4) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    body = zlib.compress(b"\0" * 16)
    return PNG_SIGNATURE + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", body) + _chunk(b"IEND", b"")


def _archive_with(members: dict[str, bytes], stack_xml: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        archive.writestr(info, b"image/openraster")
        archive.writestr("stack.xml", stack_xml)
        for name, payload in members.items():
            archive.writestr(name, payload)
    return buffer.getvalue()


_TWO_LAYER_STACK = (
    b'<?xml version="1.0" encoding="UTF-8"?>'
    b'<image w="8" h="8" version="0.0.5"><stack>'
    b'<layer name="ok" src="data/ok.png"/>'
    b'<layer name="bad" src="data/bad.png"/>'
    b"</stack></image>"
)


# -- Lazy-read instrumentation -----------------------------------------


def test_resolving_one_asset_never_reads_a_sibling_layers_own_archive_member() -> None:
    """FF6-EVENT-000487: OraContainer.read() now decompresses through
    ZipFile.open() in bounded chunks rather than ZipFile.read()'s own eager,
    unbounded call (see container._bounded_read's own docstring -- the
    declared central-directory size does not itself bound a member's real
    decompressed output), so the spy point moves from `.read` to `.open`,
    the new place a member's content actually gets touched."""
    payload = _archive_with(
        {"data/ok.png": _png(), "data/bad.png": _png(width=8, height=8)},
        _TWO_LAYER_STACK,
    )
    container = OraContainer.from_bytes(payload)
    document = parse_stack(container.read("stack.xml"))

    open_calls: list[str] = []
    original_open = zipfile.ZipFile.open

    def spy(self: zipfile.ZipFile, name: object, *args: object, **kwargs: object) -> object:
        open_calls.append(name if isinstance(name, str) else name.filename)  # type: ignore[attr-defined]
        return original_open(self, name, *args, **kwargs)  # type: ignore[arg-type]

    with patch.object(zipfile.ZipFile, "open", spy):
        resolve_asset(container, document.root.children[0])  # layer "ok" only

    assert "data/ok.png" in open_calls
    assert "data/bad.png" not in open_calls


# -- Cancellation: the granular API lets a caller stop early ------------


def test_the_granular_api_lets_a_caller_stop_before_an_unresolvable_layer_resolve_all_does_not() -> None:
    """resolve_all_assets() is eager and all-or-nothing (fails outright,
    yielding nothing); iter_layers()/resolve_asset() composed by hand lets
    a caller take what they have and stop -- "cancel" -- before reaching a
    layer they no longer want or that would fail."""
    payload = _archive_with({"data/ok.png": _png()}, _TWO_LAYER_STACK)  # "bad" has no member at all
    container = OraContainer.from_bytes(payload)
    document = parse_stack(container.read("stack.xml"))

    with pytest.raises(OraValidationError):
        resolve_all_assets(container, document.root)

    partial = []
    for layer in iter_layers(document.root):
        if layer.name == "bad":
            break  # the caller cancels before reaching the unresolvable layer
        partial.append(resolve_asset(container, layer))

    assert len(partial) == 1
    assert partial[0].src == "data/ok.png"
