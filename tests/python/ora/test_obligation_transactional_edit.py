"""ORA-EDIT-001 against the shipped namespace (partial scope: rollback only).

MUST: "Provide transactional add, replace, move, rename, and remove
operations for groups, layers, assets, and metadata; maintain references
and invalidate stale derived views."

required_tests: "Transaction rollback, reference repair, stale-view
invalidation, and independent application reopen tests."

Scope of this file: `apply_transaction`'s rollback guarantee only. See
transaction.py's module docstring for exactly what "reference repair",
"invalidate stale derived views", and "independent application reopen"
are NOT attempted and why (no reference type exists yet to repair against,
no rendering engine exists to make a stale view fresh again, and reopen
round-tripping is already covered by test_obligation_lifecycle_and_write.py).
"""

from __future__ import annotations

import dataclasses
import io
import zipfile

import pytest
from format_factory.ora import EditStep, OraImage, OraLayer, TransactionResult, apply_transaction, load

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _png(width: int = 8, height: int = 8) -> bytes:
    import struct
    import zlib

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


def _archive(stack_xml: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, b"image/openraster")
        zf.writestr("stack.xml", stack_xml)
        zf.writestr("Thumbnails/thumbnail.png", _png(16, 16))
        zf.writestr("mergedimage.png", _png())
        zf.writestr("data/only.png", _png())
    return buffer.getvalue()


def _image() -> OraImage:
    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.5">'
        b'<stack><layer name="only" src="data/only.png"/></stack></image>'
    )
    return load(_archive(stack_xml))


def _rename_root(new_name: str) -> EditStep:
    def step(image: OraImage) -> OraImage:
        renamed_root = dataclasses.replace(image.document.root, name=new_name)
        renamed_document = dataclasses.replace(image.document, root=renamed_root)
        return dataclasses.replace(image, document=renamed_document)

    return step


def _add_layer(name: str, src: str) -> EditStep:
    def step(image: OraImage) -> OraImage:
        new_layer = OraLayer(name=name, src=src)
        root = image.document.root
        new_root = dataclasses.replace(root, children=root.children + (new_layer,))
        new_document = dataclasses.replace(image.document, root=new_root)
        return dataclasses.replace(image, document=new_document)

    return step


def _add_member(name: str, payload: bytes) -> EditStep:
    def step(image: OraImage) -> OraImage:
        members = dict(image.members)
        members[name] = payload
        return dataclasses.replace(image, members=members)

    return step


def _failing_step(image: OraImage) -> OraImage:
    raise ValueError("simulated failure mid-transaction")


def _non_image_step(image: OraImage) -> OraImage:
    return "not an image"  # type: ignore[return-value]


# ── All steps succeed: committed, every edit present ────────────────────────


def test_all_steps_succeeding_commits_the_final_result() -> None:
    image = _image()

    result = apply_transaction(
        image,
        [_rename_root("renamed"), _add_layer("second", "data/only.png")],
    )

    assert isinstance(result, TransactionResult)
    assert result.committed is True
    assert result.steps_applied == 2
    assert result.failure is None
    assert result.image.document.root.name == "renamed"
    assert len(result.image.document.root.children) == 2


def test_empty_step_sequence_commits_trivially() -> None:
    image = _image()

    result = apply_transaction(image, [])

    assert result.committed is True
    assert result.steps_applied == 0
    assert result.image is image


# ── A failing step rolls the whole sequence back ────────────────────────────


def test_a_failing_step_rolls_back_to_the_original_image() -> None:
    image = _image()

    result = apply_transaction(
        image,
        [_rename_root("renamed"), _failing_step, _add_layer("never", "data/only.png")],
    )

    assert result.committed is False
    assert result.image is image  # the exact original object, not a copy
    assert result.image.document.root.name is None  # untouched
    assert len(result.image.document.root.children) == 1  # untouched


def test_rollback_reports_how_many_steps_succeeded_before_the_failure() -> None:
    image = _image()

    result = apply_transaction(
        image, [_rename_root("a"), _rename_root("b"), _failing_step]
    )

    assert result.committed is False
    assert result.steps_applied == 2


def test_rollback_preserves_the_original_failure_for_diagnosis() -> None:
    image = _image()

    result = apply_transaction(image, [_failing_step])

    assert isinstance(result.failure, ValueError)
    assert "simulated failure" in str(result.failure)


def test_a_validation_error_from_an_invalid_edit_also_rolls_back() -> None:
    """The same __post_init__ domain validation ORA-LAYER-001/ORA-GROUP-001
    established (model/stack.py) fires inside a transaction step exactly as
    it would standalone, and still triggers a full rollback."""

    def invalid_step(image: OraImage) -> OraImage:
        root = image.document.root
        # opacity out of range -- OraStack.__post_init__ raises OraValidationError
        new_root = dataclasses.replace(root, opacity=2.0)
        return dataclasses.replace(image, document=dataclasses.replace(image.document, root=new_root))

    image = _image()

    result = apply_transaction(image, [_rename_root("renamed"), invalid_step])

    assert result.committed is False
    assert result.image is image
    assert result.image.document.root.name is None


def test_a_step_returning_a_non_image_rolls_back_with_a_type_error() -> None:
    image = _image()

    result = apply_transaction(image, [_non_image_step])

    assert result.committed is False
    assert isinstance(result.failure, TypeError)
    assert result.image is image


# ── Asset (archive member) edits participate in the same transaction ───────


def test_asset_and_layer_edits_commit_together() -> None:
    image = _image()

    result = apply_transaction(
        image,
        [
            _add_member("data/second.png", _png()),
            _add_layer("second", "data/second.png"),
        ],
    )

    assert result.committed is True
    assert "data/second.png" in result.image.members
    assert len(result.image.document.root.children) == 2


def test_asset_edit_rolls_back_together_with_a_later_failing_layer_edit() -> None:
    image = _image()

    result = apply_transaction(
        image,
        [_add_member("data/second.png", _png()), _failing_step],
    )

    assert result.committed is False
    assert "data/second.png" not in result.image.members  # asset add rolled back too


# ── Sanity: apply_transaction rejects a non-OraImage input outright ────────


def test_apply_transaction_requires_an_ora_image() -> None:
    with pytest.raises(TypeError):
        apply_transaction("not an image", [])  # type: ignore[arg-type]
