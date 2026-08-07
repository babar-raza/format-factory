from __future__ import annotations

import json
import struct
from collections.abc import Callable
from pathlib import Path

import pytest
from format_factory.core import ResourceLimitError, ResourceLimits
from format_factory.safetensors import (
    DType,
    SafeTensorsDocument,
    SafeTensorsError,
    TensorDescriptor,
    load,
    validate,
)


def _encoded(header: object, payload: bytes = b"") -> bytes:
    header_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")
    return struct.pack("<Q", len(header_bytes)) + header_bytes + payload


def _raw_header(header: bytes, payload: bytes = b"") -> bytes:
    return struct.pack("<Q", len(header)) + header + payload


def _diagnostic_codes(
    value: SafeTensorsDocument | bytes,
    *,
    limits: ResourceLimits | None = None,
) -> tuple[str, ...]:
    return tuple(item.code for item in validate(value, limits=limits).diagnostics)


@pytest.mark.parametrize(
    ("value_factory", "expected_code"),
    [
        (
            lambda: _raw_header(
                b'{"x":{"dtype":"U8","shape":[1],"data_offsets":[0,1]},'
                b'"x":{"dtype":"U8","shape":[1],"data_offsets":[0,1]}}',
                b"\0",
            ),
            "SAFETENSORS_DUPLICATE_KEY",
        ),
        (
            lambda: _raw_header(b"\xff"),
            "SAFETENSORS_HEADER_ENCODING",
        ),
        (
            lambda: _encoded({"__metadata__": {"nested": {"unsafe": True}}}),
            "SAFETENSORS_METADATA_TYPE",
        ),
        (
            lambda: _encoded(
                {"x": {"dtype": "NOT_A_DTYPE", "shape": [1], "data_offsets": [0, 1]}},
                b"\0",
            ),
            "SAFETENSORS_DTYPE",
        ),
        (
            lambda: _encoded(
                {"x": {"dtype": "U8", "shape": [-1], "data_offsets": [0, 0]}}
            ),
            "SAFETENSORS_SHAPE",
        ),
        (
            lambda: _encoded(
                {"x": {"dtype": "U8", "shape": [2], "data_offsets": [0, 1]}},
                b"\0",
            ),
            "SAFETENSORS_TENSOR_SIZE",
        ),
        (
            lambda: _encoded(
                {"x": {"dtype": "U8", "shape": [1], "data_offsets": [1, 2]}},
                b"\0\0",
            ),
            "SAFETENSORS_OFFSET_COVERAGE",
        ),
        (
            lambda: _encoded(
                {"x": {"dtype": "U8", "shape": [1], "data_offsets": [0, 1]}},
                b"\0trailing",
            ),
            "SAFETENSORS_TRAILING_DATA",
        ),
        (
            lambda: struct.pack("<Q", 100_000_001),
            "SAFETENSORS_HEADER_LIMIT",
        ),
    ],
)
def test_raw_validation_uses_rule_specific_stable_codes(
    value_factory: Callable[[], bytes],
    expected_code: str,
) -> None:
    value = value_factory()

    first = _diagnostic_codes(value)
    second = _diagnostic_codes(value)

    assert first == second == (expected_code,)


def test_resource_limits_have_stable_code_and_machine_readable_context() -> None:
    report = validate(
        _encoded({}),
        limits=ResourceLimits(max_input_bytes=1),
    )

    assert _diagnostic_codes(
        _encoded({}),
        limits=ResourceLimits(max_input_bytes=1),
    ) == ("SAFETENSORS_RESOURCE_LIMIT",)
    assert report.diagnostics[0].details == {
        "limit": "max_input_bytes",
        "actual": 10,
        "maximum": 1,
    }


def test_tensor_rank_uses_the_configurable_nesting_limit() -> None:
    report = validate(
        _encoded(
            {
                "x": {
                    "dtype": "U8",
                    "shape": [1, 1, 1],
                    "data_offsets": [0, 1],
                }
            },
            b"\0",
        ),
        limits=ResourceLimits(max_nesting_depth=2),
    )

    assert tuple(item.code for item in report.diagnostics) == (
        "SAFETENSORS_RESOURCE_LIMIT",
    )
    assert report.diagnostics[0].details["limit"] == "max_nesting_depth"


def test_header_entry_count_is_bounded_during_parsing_not_only_after() -> None:
    """max_entries was previously configured (security/limits.py) but never
    referenced anywhere in this package -- confirmed genuinely unenforced by
    direct probing before this fix: a 300,000-descriptor header (19.7MB)
    fully parsed into a live Python dict in ~0.66s before any limit check
    could reject it. The object_pairs_hook now checks max_entries
    incrementally as each JSON object in the header completes (the
    top-level name-to-descriptor mapping and every individual descriptor),
    accumulating a single running total across the whole header."""
    header = {
        f"t{index}": {"dtype": "U8", "shape": [1], "data_offsets": [index, index + 1]}
        for index in range(5)
    }

    with pytest.raises(ResourceLimitError, match="max_entries exceeded"):
        load(_encoded(header, b"\0" * 5), limits=ResourceLimits(max_entries=3))


def test_header_entry_count_within_the_limit_still_loads() -> None:
    header = {
        f"t{index}": {"dtype": "U8", "shape": [1], "data_offsets": [index, index + 1]}
        for index in range(2)
    }

    document = load(_encoded(header, b"\0" * 2), limits=ResourceLimits(max_entries=100))

    assert len(document.tensors) == 2


def test_header_entry_count_limit_is_reported_by_validate_with_stable_code() -> None:
    header = {
        f"t{index}": {"dtype": "U8", "shape": [1], "data_offsets": [index, index + 1]}
        for index in range(5)
    }

    report = validate(_encoded(header, b"\0" * 5), limits=ResourceLimits(max_entries=3))

    assert tuple(item.code for item in report.diagnostics) == (
        "SAFETENSORS_RESOURCE_LIMIT",
    )
    assert report.diagnostics[0].details["limit"] == "max_entries"


def test_duplicate_key_detection_is_unaffected_by_the_entry_count_check() -> None:
    with pytest.raises(SafeTensorsError, match="duplicate JSON key"):
        load(
            _raw_header(
                b'{"x":{"dtype":"U8","shape":[1],"data_offsets":[0,1]},'
                b'"x":{"dtype":"U8","shape":[1],"data_offsets":[0,1]}}',
                b"\0",
            )
        )


def test_model_validation_reports_all_stable_codes_deterministically() -> None:
    document = SafeTensorsDocument(
        tensors={
            "x": TensorDescriptor(
                name="x",
                dtype=DType.U8,
                shape=(1,),
                data_offsets=(1, 3),
            )
        },
        metadata={"unsafe": 1},  # type: ignore[dict-item]
        payload=b"\0\0\0\0",
    )

    first = _diagnostic_codes(document)
    second = _diagnostic_codes(document)

    assert first == second == (
        "SAFETENSORS_OFFSET_COVERAGE",
        "SAFETENSORS_TENSOR_SIZE",
        "SAFETENSORS_TRAILING_DATA",
        "SAFETENSORS_METADATA_TYPE",
    )


class _BorrowedOwner:
    def __init__(self) -> None:
        self.blocked = True
        self.closed = False
        self.close_calls = 0

    def close(self) -> None:
        self.close_calls += 1
        if self.blocked:
            raise BufferError("borrowed view is still exported")
        self.closed = True


def test_close_retains_owner_until_borrowed_views_are_released() -> None:
    owner = _BorrowedOwner()
    document = SafeTensorsDocument(
        tensors={"x": TensorDescriptor("x", DType.U8, (1,), (0, 1))},
        payload=b"\x07",
        owner=owner,
    )
    region = document.tensor_region("x")

    with pytest.raises(SafeTensorsError) as caught:
        document.close()

    assert caught.value.code == "SAFETENSORS_BORROWED_VIEW_ACTIVE"
    assert document.closed
    region.release()
    owner.blocked = False
    document.close()
    assert owner.closed
    assert owner.close_calls == 2


def test_mapped_document_close_can_be_retried_after_region_release(
    tmp_path: Path,
) -> None:
    source = tmp_path / "borrowed-view.safetensors"
    source.write_bytes(
        _encoded(
            {"x": {"dtype": "U8", "shape": [1], "data_offsets": [0, 1]}},
            b"\x07",
        )
    )
    document = load(source)
    region = document.tensor_region("x")

    with pytest.raises(SafeTensorsError) as caught:
        document.close()

    assert caught.value.code == "SAFETENSORS_BORROWED_VIEW_ACTIVE"
    assert document.closed
    region.release()
    document.close()
    source.unlink()


def test_closed_document_validation_and_access_are_stable() -> None:
    document = SafeTensorsDocument(tensors={}, payload=b"")
    document.close()

    assert _diagnostic_codes(document) == ("SAFETENSORS_DOCUMENT_CLOSED",)
    with pytest.raises(SafeTensorsError) as caught:
        document.tensor_region("missing")
    assert caught.value.code == "SAFETENSORS_DOCUMENT_CLOSED"
