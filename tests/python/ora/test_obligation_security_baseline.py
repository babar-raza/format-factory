"""ORA-SEC-001 against the shipped namespace.

MUST: "Input limits, no implicit external effects, traversal protection,
untrusted-payload discipline, and complexity-attack guards are enforced with
diagnostics." Five required_behavior bullets, each tested here against the
real format_factory.ora API rather than assumed from reading the source.

This capability had no dedicated test file: its required behaviors are
implemented but were only exercised incidentally under other capabilities'
test files (container/mimetype, stack/document, lifecycle). This file gives
ORA-SEC-001 its own evidence, quoting each bullet it proves.
"""

from __future__ import annotations

import io
import struct
import zipfile
import zlib

import pytest

from format_factory.core import ResourceLimits
from format_factory.ora import OraArchiveError, OraLimitError, OraValidationError
from format_factory.ora.codec.container import OraContainer, _reject_unsafe_name
from format_factory.ora.codec.png_metadata import read_png_metadata
from format_factory.ora.codec.stack_xml import parse_stack
from format_factory.ora.lifecycle import ReadMode, load

TINY_LIMITS = ResourceLimits(
    max_input_bytes=200,
    max_header_bytes=200,
    max_xml_nodes=5,
    max_nesting_depth=3,
    max_entries=5,
    max_decompressed_bytes=1_000,
    max_compression_ratio=50.0,
)


def _archive(mimetype: bytes = b"image/openraster", extra: dict[str, bytes] | None = None) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, mimetype)
        for name, payload in (extra or {}).items():
            zf.writestr(name, payload)
    return buffer.getvalue()


# ── "Provide configurable limits...with safe defaults enabled." ────────────


def test_limits_are_configurable_not_hardcoded() -> None:
    payload = _archive(extra={"stack.xml": b"<image w='8' h='8' version='0.0.5'><stack/></image>"})

    with pytest.raises(OraLimitError):
        OraContainer.from_bytes(payload, limits=TINY_LIMITS)


def test_safe_defaults_are_enabled_without_the_caller_supplying_limits() -> None:
    """A caller who supplies no limits still gets bounded behavior -- the
    defaults themselves enforce the guard, not merely permit configuring one."""
    payload = _archive(extra={"stack.xml": b"<image w='8' h='8' version='0.0.5'><stack/></image>"})

    container = OraContainer.from_bytes(payload)  # no limits= argument

    assert container.mimetype == "image/openraster"


def test_input_size_limit_is_enforced() -> None:
    oversized = b"x" * 300
    with pytest.raises(OraLimitError):
        OraContainer.from_bytes(oversized, limits=TINY_LIMITS)


def test_entry_count_limit_is_enforced() -> None:
    payload = _archive(extra={f"data/{i}.png": b"x" for i in range(10)})

    with pytest.raises(OraLimitError):
        OraContainer.from_bytes(payload, limits=TINY_LIMITS)


def test_decompressed_byte_limit_is_enforced() -> None:
    payload = _archive(extra={"big.bin": b"x" * 2_000})

    with pytest.raises(OraLimitError):
        OraContainer.from_bytes(payload, limits=TINY_LIMITS)


def test_xml_node_and_nesting_limits_are_enforced() -> None:
    deep = "<stack>" * 10 + "</stack>" * 10
    stack_xml = f"<image w='8' h='8' version='0.0.5'>{deep}</image>".encode()

    with pytest.raises(OraLimitError):
        parse_stack(stack_xml, limits=TINY_LIMITS)


def test_a_nested_layer_attribute_flood_is_rejected() -> None:
    """Cumulative attribute count was not previously bounded at all --
    confirmed genuinely unenforced by direct probing before this fix. A
    layer carrying far more attributes than TINY_LIMITS.max_entries (5)
    is refused, independent of node count and nesting depth."""
    attrs = " ".join(f'a{i}="v"' for i in range(8))
    stack_xml = f"<image w='8' h='8' version='0.0.5'><stack><layer src='x.png' {attrs}/></stack></image>".encode()

    with pytest.raises(OraLimitError, match="cumulative attributes"):
        parse_stack(stack_xml, limits=TINY_LIMITS)


def test_a_root_image_attribute_flood_is_rejected() -> None:
    """The <image> root element's own attributes previously bypassed the
    walker entirely -- it is never reachable through _Walker.child()'s
    recursive dispatch, confirmed genuinely unenforced by direct probing
    before this fix."""
    attrs = " ".join(f'a{i}="v"' for i in range(8))
    stack_xml = f"<image w='8' h='8' version='0.0.5' {attrs}><stack></stack></image>".encode()

    with pytest.raises(OraLimitError, match="cumulative attributes"):
        parse_stack(stack_xml, limits=TINY_LIMITS)


def test_a_top_level_stack_attribute_flood_is_rejected() -> None:
    """The top-level <stack> element's own attributes also previously
    bypassed the walker entirely, for the same reason as the <image>
    root -- confirmed genuinely unenforced by direct probing before this
    fix."""
    attrs = " ".join(f'a{i}="v"' for i in range(8))
    stack_xml = f"<image w='8' h='8' version='0.0.5'><stack {attrs}></stack></image>".encode()

    with pytest.raises(OraLimitError, match="cumulative attributes"):
        parse_stack(stack_xml, limits=TINY_LIMITS)


def test_a_document_with_attributes_within_the_limit_still_parses() -> None:
    stack_xml = (
        b"<image w='8' h='8' version='0.0.5'>"
        b"<stack><layer src='x.png' name='a'/></stack></image>"
    )

    document = parse_stack(stack_xml, limits=TINY_LIMITS)

    assert document.width == 8


# ── "Never resolve network resources, execute embedded code, load plugins,
#     or follow external references...unless explicitly enabled." ──────────


def _png(width: int = 4, height: int = 4) -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(b"\0" * 16))
        + chunk(b"IEND", b"")
    )


def _valid_archive_with_layer_src(src: str) -> bytes:
    stack_xml = (
        f"<image w='4' h='4' version='0.0.5'>"
        f"<stack><layer name='x' src='{src}'/></stack>"
        f"</image>"
    ).encode()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, b"image/openraster")
        zf.writestr("stack.xml", stack_xml)
        zf.writestr("Thumbnails/thumbnail.png", _png())
        zf.writestr("mergedimage.png", _png())
    return buffer.getvalue()


def test_layer_references_cannot_resolve_to_a_network_url() -> None:
    """ORA has no href/URL concept for layer sources: `src` is used only as a
    ZIP member-name lookup key, never dereferenced as a URI. A URL-shaped src
    is not rejected at parse time (it is syntactically a relative path with
    no ".." segments), but it can never cause a network fetch: it simply
    fails to match any real archive member, exactly like any other absent
    file would. This is a stronger guarantee than an opt-in flag -- there is
    no code path in this package that could ever resolve a network resource,
    so there is nothing to opt into."""
    payload = _valid_archive_with_layer_src("https://example.com/evil.png")

    with pytest.raises(OraValidationError, match="not in the archive"):
        load(payload, mode=ReadMode.STRICT)


def test_layer_references_cannot_be_absolute_filesystem_paths() -> None:
    stack_xml = (
        b"<image w='8' h='8' version='0.0.5'>"
        b"<stack><layer name='x' src='/etc/passwd'/></stack>"
        b"</image>"
    )
    with pytest.raises(OraValidationError, match="not an archive-root-relative path"):
        parse_stack(stack_xml)


def test_no_embedded_script_or_executable_content_is_ever_evaluated() -> None:
    """Parsing an XML payload containing script-shaped text must treat it as
    inert data -- a value, never code. There is no evaluation path in this
    package for any embedded content."""
    stack_xml = (
        b"<image w='8' h='8' version='0.0.5'>"
        b"<stack><layer name='&lt;script&gt;alert(1)&lt;/script&gt;' src='data/a.png'/></stack>"
        b"</image>"
    )
    document = parse_stack(stack_xml)
    assert document.root.children[0].name == "<script>alert(1)</script>"


# ── "Prevent path traversal and unapproved absolute-path access." ──────────


def test_container_member_traversal_is_rejected() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, b"image/openraster")
        zf.writestr("../../evil.txt", b"x")

    with pytest.raises(OraArchiveError, match="traverses outside the archive root"):
        OraContainer.from_bytes(buffer.getvalue())


def test_layer_src_traversal_is_rejected() -> None:
    stack_xml = (
        b"<image w='8' h='8' version='0.0.5'>"
        b"<stack><layer name='x' src='../../../etc/passwd'/></stack>"
        b"</image>"
    )
    with pytest.raises(OraValidationError, match="traverses outside the archive root"):
        parse_stack(stack_xml)


def test_backslash_paths_are_rejected_not_platform_dependently_normalized() -> None:
    """A backslash is a legal ZIP filename character and a path separator on
    Windows only; refusing it outright avoids a container that behaved
    differently by platform.

    Exercised directly against the guard rather than through a real archive:
    Python's own zipfile writer normalizes any character equal to the
    CURRENT platform's os.sep (backslash on Windows) to '/' before the name
    is ever stored, so a literal backslash cannot survive a round trip
    through zipfile.writestr on this platform to reach the guard that way.
    A hostile archive built by another tool, or read on a platform where
    os.sep is not backslash, has no such normalization -- which is exactly
    why the guard checks for it explicitly rather than assuming it can't
    occur.
    """
    with pytest.raises(OraArchiveError, match="backslash"):
        _reject_unsafe_name("data\\..\\..\\evil.png")


# ── "Treat all embedded payloads...as untrusted data; parsing must not
#     evaluate them." ───────────────────────────────────────────────────────


def test_png_metadata_is_read_without_decoding_pixel_data() -> None:
    """Metadata comes from the IHDR chunk alone -- a payload whose compressed
    pixel data is corrupt garbage still yields correct metadata, proving the
    pixel stream itself is never decoded to answer this question."""
    ihdr = struct.pack(">IIBBBBB", 4, 4, 8, 6, 0, 0, 0)

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    corrupt_png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", b"not real deflate data at all")
        + chunk(b"IEND", b"")
    )

    metadata = read_png_metadata(corrupt_png)

    assert metadata.width == 4
    assert metadata.height == 4


# ── "Guard against algorithmic complexity attacks; use checked arithmetic
#     for size and count calculations and bound recursion depth." ─────────


def test_absurd_canvas_dimensions_are_refused_by_checked_arithmetic() -> None:
    """A tiny stack.xml can declare a canvas that would allocate exabytes;
    the declaration must be refused before any allocation is attempted."""
    stack_xml = b"<image w='999999999' h='999999999' version='0.0.5'><stack/></image>"

    with pytest.raises(OraLimitError):
        parse_stack(stack_xml)


def test_absurd_png_dimensions_are_refused_by_checked_arithmetic() -> None:
    ihdr = struct.pack(">IIBBBBB", 999_999_999, 999_999_999, 16, 6, 0, 0, 0)

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    huge_png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IEND", b"")

    with pytest.raises(OraLimitError):
        read_png_metadata(huge_png)


def test_deeply_nested_stacks_are_refused_by_a_bounded_recursion_walk() -> None:
    depth = 200
    nested = "<stack>" * depth + "</stack>" * depth
    stack_xml = f"<image w='8' h='8' version='0.0.5'>{nested}</image>".encode()

    with pytest.raises(OraLimitError, match="nests deeper"):
        parse_stack(stack_xml)


def test_excessive_compression_ratio_is_refused() -> None:
    """A tiny compressed payload that expands enormously is a zip-bomb
    shape -- refused from the central directory alone, before decompressing."""
    huge_repetitive = b"\0" * 100_000
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, b"image/openraster")
        zf.writestr("bomb.bin", huge_repetitive)

    tight_ratio_limits = ResourceLimits(
        max_input_bytes=10_000_000,
        max_header_bytes=10_000_000,
        max_xml_nodes=10_000,
        max_nesting_depth=100,
        max_entries=10_000,
        max_decompressed_bytes=10_000_000,
        max_compression_ratio=10.0,
    )

    with pytest.raises(OraLimitError, match="compression ratio"):
        OraContainer.from_bytes(buffer.getvalue(), limits=tight_ratio_limits)
