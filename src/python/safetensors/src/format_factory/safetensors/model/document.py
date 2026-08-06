"""Pure SafeTensors model objects; this module performs no I/O."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any

from format_factory.core import CheckedArithmeticError, checked_product

from ..errors import SafeTensorsError

_MAX_U64 = (1 << 64) - 1


class DType(StrEnum):
    BOOL = "BOOL"
    F4 = "F4"
    F6_E2M3 = "F6_E2M3"
    F6_E3M2 = "F6_E3M2"
    U8 = "U8"
    I8 = "I8"
    F8_E5M2 = "F8_E5M2"
    F8_E4M3 = "F8_E4M3"
    F8_E8M0 = "F8_E8M0"
    F8_E4M3FNUZ = "F8_E4M3FNUZ"
    F8_E5M2FNUZ = "F8_E5M2FNUZ"
    I16 = "I16"
    U16 = "U16"
    F16 = "F16"
    BF16 = "BF16"
    I32 = "I32"
    U32 = "U32"
    F32 = "F32"
    C64 = "C64"
    F64 = "F64"
    I64 = "I64"
    U64 = "U64"

    @property
    def bits(self) -> int:
        return {
            DType.F4: 4,
            DType.F6_E2M3: 6,
            DType.F6_E3M2: 6,
            DType.BOOL: 8,
            DType.U8: 8,
            DType.I8: 8,
            DType.F8_E5M2: 8,
            DType.F8_E4M3: 8,
            DType.F8_E8M0: 8,
            DType.F8_E4M3FNUZ: 8,
            DType.F8_E5M2FNUZ: 8,
            DType.I16: 16,
            DType.U16: 16,
            DType.F16: 16,
            DType.BF16: 16,
            DType.I32: 32,
            DType.U32: 32,
            DType.F32: 32,
            DType.C64: 64,
            DType.F64: 64,
            DType.I64: 64,
            DType.U64: 64,
        }[self]


@dataclass(frozen=True, slots=True)
class TensorDescriptor:
    name: str
    dtype: DType
    shape: tuple[int, ...]
    data_offsets: tuple[int, int]
    unknown_fields: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name or self.name == "__metadata__":
            raise ValueError("tensor name must be non-empty and not reserved")
        if any(isinstance(dim, bool) or not isinstance(dim, int) or dim < 0 for dim in self.shape):
            raise ValueError("shape dimensions must be non-negative integers")
        start, end = self.data_offsets
        if isinstance(start, bool) or isinstance(end, bool) or start < 0 or end < start:
            raise ValueError("data offsets must be an ordered non-negative pair")
        element_count = self._checked_element_count()
        if element_count > _MAX_U64 // self.dtype.bits:
            raise ValueError("tensor element-bit count overflows unsigned 64-bit size")
        object.__setattr__(self, "unknown_fields", MappingProxyType(dict(self.unknown_fields)))

    def _checked_element_count(self) -> int:
        try:
            return checked_product(
                self.shape, ceiling=_MAX_U64, label="shape element count"
            )
        except CheckedArithmeticError as exc:
            # Preserve this package's published error type AND its exact
            # messages: shape validation surfaces as ValueError from
            # __post_init__, and callers/tests match on these strings.
            if exc.context.get("reason") == "factor_exceeds_ceiling":
                raise ValueError(
                    "shape dimension exceeds unsigned 64-bit size"
                ) from exc
            raise ValueError(
                "shape element count overflows unsigned 64-bit size"
            ) from exc

    @property
    def element_count(self) -> int:
        return self._checked_element_count()

    @property
    def byte_length(self) -> int:
        bits = self.element_count * self.dtype.bits
        if bits % 8:
            raise ValueError("sub-byte tensor does not end on a byte boundary")
        return bits // 8


class PayloadAccessMode(StrEnum):
    """How a document or header reaches its tensor payload."""

    HEADER_ONLY = "header_only"
    MEMORY_MAPPED = "memory_mapped"
    BORROWED_BUFFER = "borrowed_buffer"
    BUFFERED_STREAM = "buffered_stream"


@dataclass(frozen=True, slots=True)
class PayloadAccess:
    """Machine-readable disclosure of I/O and decoding behavior."""

    mode: PayloadAccessMode
    zero_copy: bool
    region_reads: bool
    full_payload_read_required: bool
    full_decode_required: bool
    detail: str


@dataclass(frozen=True, slots=True)
class SafeTensorsHeader:
    """Validated metadata and descriptors without an opened tensor payload."""

    tensors: Mapping[str, TensorDescriptor]
    metadata: Mapping[str, str] = field(default_factory=dict)
    metadata_declared: bool | None = None
    payload_size: int = 0
    header_size: int = 0
    profile: str = "v0.8.0"
    access: PayloadAccess = field(
        default_factory=lambda: PayloadAccess(
            mode=PayloadAccessMode.HEADER_ONLY,
            zero_copy=False,
            region_reads=False,
            full_payload_read_required=False,
            full_decode_required=False,
            detail="only the prefix and JSON header were read",
        )
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "tensors", MappingProxyType(dict(self.tensors)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        if self.metadata_declared is None:
            # A caller who never says whether __metadata__ was present is
            # assumed to mean "as declared as this metadata implies" --
            # correct for the common case, but the reader always passes this
            # explicitly rather than relying on the guess (SAFETENSORS-PRESERVE-001:
            # absence and explicit emptiness are not the same thing).
            object.__setattr__(self, "metadata_declared", bool(self.metadata))
        if self.payload_size < 0 or self.header_size < 0:
            raise ValueError("header and payload sizes must be non-negative")

    @property
    def tensor_names(self) -> tuple[str, ...]:
        return tuple(sorted(self.tensors))


class SafeTensorsDocument:
    """Immutable descriptors plus a zero-copy view of the tensor data buffer."""

    __slots__ = (
        "_closed",
        "_metadata",
        "_metadata_declared",
        "_owner",
        "_payload",
        "_tensors",
        "access",
        "header_size",
        "profile",
    )

    def __init__(
        self,
        *,
        tensors: Mapping[str, TensorDescriptor],
        metadata: Mapping[str, str] | None = None,
        metadata_declared: bool | None = None,
        payload: bytes | bytearray | memoryview = b"",
        header_size: int = 0,
        profile: str = "v0.8.0",
        owner: Any = None,
        access: PayloadAccess | None = None,
    ) -> None:
        self._tensors = MappingProxyType(dict(tensors))
        self._metadata = MappingProxyType(dict(metadata or {}))
        # SAFETENSORS-PRESERVE-001: "no __metadata__ key" and "__metadata__: {}"
        # are not the same document. A caller who passes `metadata=None`
        # (the default -- no metadata section at all) is declared=False;
        # passing `metadata={}` explicitly (a present-but-empty section) is
        # declared=True. `metadata_declared` overrides both when given.
        self._metadata_declared = (
            (metadata is not None) if metadata_declared is None else metadata_declared
        )
        self._payload = memoryview(payload).toreadonly()
        self._owner = owner
        self._closed = False
        self.header_size = header_size
        self.profile = profile
        self.access = access or PayloadAccess(
            mode=PayloadAccessMode.BORROWED_BUFFER,
            zero_copy=True,
            region_reads=True,
            full_payload_read_required=False,
            full_decode_required=False,
            detail="tensor regions are borrowed from the caller-provided buffer",
        )

    @property
    def tensors(self) -> Mapping[str, TensorDescriptor]:
        return self._tensors

    @property
    def metadata(self) -> Mapping[str, str]:
        return self._metadata

    @property
    def metadata_declared(self) -> bool:
        """Whether a `__metadata__` section was present, even if empty.

        SAFETENSORS-PRESERVE-001: preserving "optional metadata absence"
        means this must be distinguishable from `not self.metadata`, which
        is also true for a present-but-empty section.
        """
        return self._metadata_declared

    @property
    def tensor_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._tensors))

    @property
    def payload_size(self) -> int:
        self._require_open()
        return len(self._payload)

    @property
    def closed(self) -> bool:
        """Whether tensor payload access has been closed."""

        return self._closed

    def _require_open(self) -> None:
        if self._closed:
            raise SafeTensorsError(
                "the SafeTensors document is closed",
                code="SAFETENSORS_DOCUMENT_CLOSED",
            )

    def tensor_bytes(self, name: str) -> memoryview:
        return self.tensor_region(name)

    def tensor_region(
        self,
        name: str,
        start: int = 0,
        stop: int | None = None,
    ) -> memoryview:
        """Return a zero-copy byte region relative to one tensor."""

        self._require_open()
        descriptor = self._tensors[name]
        tensor_start, tensor_end = descriptor.data_offsets
        tensor_size = tensor_end - tensor_start
        selected_stop = tensor_size if stop is None else stop
        if (
            isinstance(start, bool)
            or isinstance(selected_stop, bool)
            or not isinstance(start, int)
            or not isinstance(selected_stop, int)
            or start < 0
            or selected_stop < start
            or selected_stop > tensor_size
        ):
            raise ValueError(f"tensor region must satisfy 0 <= start <= stop <= {tensor_size}")
        return self._payload[tensor_start + start : tensor_start + selected_stop]

    def items(self) -> Iterator[tuple[str, memoryview]]:
        for name in self.tensor_names:
            yield name, self.tensor_bytes(name)

    def close(self) -> None:
        if not self._closed:
            self._payload.release()
            self._closed = True
        owner = self._owner
        if owner is not None and hasattr(owner, "close"):
            try:
                owner.close()
            except BufferError as exc:
                # Retain the owner so callers can release exported regions and
                # retry. Dropping it here would leak a live memory mapping.
                raise SafeTensorsError(
                    "cannot close the SafeTensors payload while borrowed views are active",
                    code="SAFETENSORS_BORROWED_VIEW_ACTIVE",
                ) from exc
            self._owner = None

    def __enter__(self) -> "SafeTensorsDocument":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
