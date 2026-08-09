"""ORA-EDIT-001 -- "maintain references" is genuinely proven, not merely
asserted.

MUST: "Provide transactional add, replace, move, rename, and remove
operations for groups, layers, assets, and metadata; maintain references
and invalidate stale derived views."

FF6-EVENT-000318's own evidence found that `src` (the archive-member path
a layer's own raster data lives at) is the ONLY reference-shaped concept
OpenRaster defines (full-text search of all 3 pinned spec sources for
"reference": 4 hits, all describing `src` pointing to an archive member;
zero hits describing a cross-element identifier-based reference within
the model tree). That same evidence asserted "renaming, moving, or
removing a layer does not change what its own src value means" -- a real,
testable, PROSE-ONLY claim until this file: no prior test directly proved
that an UNTOUCHED sibling's own `src` value survives a transaction
targeting a DIFFERENT node byte-for-byte, across every named operation
type (add, replace, move, remove -- rename only ever targets the root,
which carries no `src` at all, so it is checked trivially).

"Metadata" as a CRUD target remains genuinely, separately unmet (no
metadata concept exists anywhere in the pinned OpenRaster spec -- 0 hits
for "metadata" across all 3 sources, per FF6-EVENT-000318) and is NOT
addressed by this file. ORA-EDIT-001 stays partial after this file closes
the "maintain references" clause specifically -- a real narrowing, not a
close, matching this session's own established discipline of never
overclaiming past what a specific proof actually covers.
"""

from __future__ import annotations

import dataclasses
import io
import struct
import zipfile
import zlib

from format_factory.ora import (
    EditStep,
    OraImage,
    OraLayer,
    OraStack,
    apply_transaction,
    load,
)

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _png(width: int = 8, height: int = 8) -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        PNG_SIGNATURE
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(b"\0" * 16))
        + chunk(b"IEND", b"")
    )


def _image_with_three_layers() -> OraImage:
    """A root stack with a nested group (holding one layer) and two
    root-level layers, so every operation type can target one node while
    leaving multiple genuinely untouched `src`-bearing siblings to check."""
    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.5">'
        b'<stack>'
        b'<stack name="group1"><layer name="a" src="data/a.png"/></stack>'
        b'<layer name="b" src="data/b.png"/>'
        b'<layer name="c" src="data/c.png"/>'
        b'</stack></image>'
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, b"image/openraster")
        zf.writestr("stack.xml", stack_xml)
        zf.writestr("Thumbnails/thumbnail.png", _png(16, 16))
        zf.writestr("mergedimage.png", _png())
        zf.writestr("data/a.png", _png())
        zf.writestr("data/b.png", _png())
        zf.writestr("data/c.png", _png())
    return load(buffer.getvalue())


def _src_map(image: OraImage) -> dict[str, str]:
    """name -> src for every layer in the tree, recursively."""
    result: dict[str, str] = {}

    def walk(node: object) -> None:
        if isinstance(node, OraLayer):
            result[node.name] = node.src
        elif isinstance(node, OraStack):
            for child in node.children:
                walk(child)

    walk(image.document.root)
    return result


def _add_layer(name: str, src: str) -> EditStep:
    def step(image: OraImage) -> OraImage:
        root = image.document.root
        new_root = dataclasses.replace(
            root, children=root.children + (OraLayer(name=name, src=src),)
        )
        return dataclasses.replace(image, document=dataclasses.replace(image.document, root=new_root))

    return step


def _replace_layer(target_name: str, replacement: OraLayer) -> EditStep:
    def step(image: OraImage) -> OraImage:
        root = image.document.root
        new_children = tuple(
            replacement if child.name == target_name else child for child in root.children
        )
        new_root = dataclasses.replace(root, children=new_children)
        return dataclasses.replace(image, document=dataclasses.replace(image.document, root=new_root))

    return step


def _move_layer_into_group(layer_name: str, group_name: str) -> EditStep:
    def step(image: OraImage) -> OraImage:
        root = image.document.root
        moved = next(child for child in root.children if child.name == layer_name)
        remaining = tuple(child for child in root.children if child.name != layer_name)
        group_index = next(i for i, c in enumerate(remaining) if c.name == group_name)
        group = remaining[group_index]
        new_group = dataclasses.replace(group, children=group.children + (moved,))
        new_children = remaining[:group_index] + (new_group,) + remaining[group_index + 1 :]
        new_root = dataclasses.replace(root, children=new_children)
        return dataclasses.replace(image, document=dataclasses.replace(image.document, root=new_root))

    return step


def _remove_layer(target_name: str) -> EditStep:
    def step(image: OraImage) -> OraImage:
        root = image.document.root
        new_children = tuple(child for child in root.children if child.name != target_name)
        new_root = dataclasses.replace(root, children=new_children)
        return dataclasses.replace(image, document=dataclasses.replace(image.document, root=new_root))

    return step


def _rename_root(new_name: str) -> EditStep:
    def step(image: OraImage) -> OraImage:
        renamed_root = dataclasses.replace(image.document.root, name=new_name)
        return dataclasses.replace(
            image, document=dataclasses.replace(image.document, root=renamed_root)
        )

    return step


def test_add_leaves_every_pre_existing_src_untouched() -> None:
    image = _image_with_three_layers()
    before = _src_map(image)

    result = apply_transaction(image, [_add_layer("d", "data/d.png")])

    assert result.committed is True
    after = _src_map(result.image)
    for name, src in before.items():
        assert after[name] == src, f"{name}'s own src changed: {src!r} -> {after[name]!r}"


def test_replace_leaves_every_other_layers_own_src_untouched() -> None:
    image = _image_with_three_layers()
    before = _src_map(image)

    result = apply_transaction(
        image, [_replace_layer("b", OraLayer(name="b-replaced", src="data/b-new.png"))]
    )

    assert result.committed is True
    after = _src_map(result.image)
    untouched = {name: src for name, src in before.items() if name != "b"}
    for name, src in untouched.items():
        assert after[name] == src, f"{name}'s own src changed: {src!r} -> {after[name]!r}"
    assert after["b-replaced"] == "data/b-new.png"


def test_move_does_not_change_the_moved_layers_own_src_or_any_siblings() -> None:
    image = _image_with_three_layers()
    before = _src_map(image)

    result = apply_transaction(image, [_move_layer_into_group("b", "group1")])

    assert result.committed is True
    after = _src_map(result.image)
    assert after == before, "moving a layer must not change any src value, its own or a sibling's"


def test_remove_leaves_every_remaining_layers_own_src_untouched() -> None:
    image = _image_with_three_layers()
    before = _src_map(image)

    result = apply_transaction(image, [_remove_layer("b")])

    assert result.committed is True
    after = _src_map(result.image)
    remaining = {name: src for name, src in before.items() if name != "b"}
    assert after == remaining


def test_rename_the_root_leaves_every_layers_own_src_untouched() -> None:
    """The root stack itself carries no `src` at all (only layers do), so
    renaming it can structurally never affect a reference -- checked
    directly rather than assumed."""
    image = _image_with_three_layers()
    before = _src_map(image)

    result = apply_transaction(image, [_rename_root("renamed-root")])

    assert result.committed is True
    assert _src_map(result.image) == before
    assert result.image.document.root.name == "renamed-root"


def test_a_multi_step_transaction_still_leaves_genuinely_unrelated_srcs_untouched() -> None:
    """Composing several operations in one transaction -- add, move, and
    remove targeting three DIFFERENT layers -- must still leave the one
    remaining, entirely uninvolved layer's own src untouched."""
    image = _image_with_three_layers()
    before = _src_map(image)

    result = apply_transaction(
        image,
        [
            _add_layer("d", "data/d.png"),
            _move_layer_into_group("b", "group1"),
            _remove_layer("c"),
        ],
    )

    assert result.committed is True
    after = _src_map(result.image)
    assert after["a"] == before["a"]
    assert "c" not in after
    assert after["b"] == before["b"]
    assert after["d"] == "data/d.png"
