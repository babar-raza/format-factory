"""Typed NRRD document model with no eager I/O dependencies."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


DOMAIN_KINDS = frozenset({"domain", "space", "time"})


@dataclass(frozen=True, slots=True)
class PreservationIssue:
    """A construct that prevents an exact source-preserving write."""

    code: str
    message: str


@dataclass(frozen=True, slots=True)
class PreservationReport:
    """Explicit result of evaluating whether a document can be written losslessly."""

    issues: tuple[PreservationIssue, ...] = ()

    @property
    def is_lossless(self) -> bool:
        return not self.issues


@dataclass(slots=True)
class NrrdDocument:
    """A decoded NRRD document with preserved headers and comments."""

    version: int
    header: dict[str, str]
    payload: bytes
    array: list[Any]
    comments: list[str] = field(default_factory=list)
    key_value_pairs: dict[str, str] = field(default_factory=dict)
    raw_header: bytes = b""
    source_path: str | None = None
    data_offset: int = 0
    source_bytes: bytes | None = field(default=None, repr=False, compare=False)
    _original_header: dict[str, str] | None = field(default=None, repr=False, compare=False)
    _original_comments: list[str] | None = field(default=None, repr=False, compare=False)
    _original_key_value_pairs: dict[str, str] | None = field(
        default=None, repr=False, compare=False
    )
    _original_array: list[Any] | None = field(default=None, repr=False, compare=False)

    @property
    def dimension(self) -> int:
        return int(self.header["dimension"])

    @property
    def sizes(self) -> list[int]:
        return [int(value) for value in self.header["sizes"].split()]

    @property
    def encoding(self) -> str:
        return self.header.get("encoding", "raw").lower()

    @property
    def nrrd_type(self) -> str:
        return self.header["type"].lower()

    @property
    def data_size(self) -> int:
        return len(self.payload)

    @property
    def element_count(self) -> int:
        result = 1
        for size in self.sizes:
            result *= size
        return result

    @property
    def array_shape(self) -> list[int]:
        return self.sizes

    @property
    def kinds(self) -> list[str]:
        value = self.header.get("kinds", "")
        return value.split() if value else []

    @property
    def domain_axes(self) -> list[int]:
        return [
            index
            for index, value in enumerate(self.kinds)
            if value.lower() in DOMAIN_KINDS
        ]

    @property
    def range_axes(self) -> list[int]:
        return [
            index
            for index, value in enumerate(self.kinds)
            if value.lower() not in DOMAIN_KINDS
        ]

    @property
    def space(self) -> str:
        return self.header.get("space", "")

    def preservation_report(self) -> PreservationReport:
        """Report whether the original byte representation can be replayed safely.

        Canonical output preserves represented NRRD semantics. Exact preservation
        is available only for an attached source document whose semantic state has
        not been modified after load.
        """

        issues: list[PreservationIssue] = []
        if self.source_bytes is None:
            issues.append(PreservationIssue(
                "nrrd.lossless.source_unavailable",
                "no attached source bytes are available for lossless output",
            ))
        if "data file" in self.header:
            issues.append(PreservationIssue(
                "nrrd.lossless.detached_payload",
                "detached payloads require an explicit detached writer",
            ))
        if self._original_header is None:
            issues.append(PreservationIssue(
                "nrrd.lossless.snapshot_unavailable",
                "the document was not loaded from a preservable source",
            ))
        elif (
            self.header != self._original_header
            or self.comments != self._original_comments
            or self.key_value_pairs != self._original_key_value_pairs
            or self.array != self._original_array
        ):
            issues.append(PreservationIssue(
                "nrrd.lossless.document_modified",
                "header, metadata, comments, or array values changed after load",
            ))
        return PreservationReport(tuple(issues))

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> NrrdDocument:
        """Migrate a legacy model mapping without performing I/O."""

        header_value = value.get("header", {})
        if not isinstance(header_value, Mapping):
            raise TypeError("header must be a mapping")
        key_values = value.get("key_value_pairs", {})
        if not isinstance(key_values, Mapping):
            raise TypeError("key_value_pairs must be a mapping")
        payload_value = value.get("payload", b"")
        if not isinstance(payload_value, bytes):
            raise TypeError("payload must be bytes")
        return cls(
            version=int(value.get("version", 5)),
            header={str(key).lower(): str(item) for key, item in header_value.items()},
            payload=payload_value,
            array=list(value.get("array") or []),
            comments=[str(item) for item in value.get("comments", [])],
            key_value_pairs={
                str(key): str(item) for key, item in key_values.items()
            },
            raw_header=bytes(value.get("raw_header", b"")),
            source_path=(
                str(value["source_path"])
                if value.get("source_path") is not None
                else None
            ),
            data_offset=int(value.get("data_offset", 0)),
            source_bytes=(
                bytes(value["source_bytes"])
                if isinstance(value.get("source_bytes"), bytes)
                else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a compatibility mapping without exposing internal dicts."""

        return {
            "version": self.version,
            "header": dict(self.header),
            "key_value_pairs": dict(self.key_value_pairs),
            "comments": list(self.comments),
            "raw_header": self.raw_header,
            "payload": self.payload,
            "data_size": self.data_size,
            "element_count": self.element_count,
            "data_offset": self.data_offset,
            "kinds": self.kinds,
            "space": self.space,
            "array": list(self.array),
            "array_shape": self.array_shape,
            "source_path": self.source_path,
        }

    def to_array(self) -> Any:
        return reshape_nrrd_array(self.array, self.sizes)


def reshape_nrrd_array(flat: list[Any], sizes: list[int]) -> Any:
    """Reshape flat values using NRRD's fastest-first axis convention."""

    if not sizes or len(sizes) == 1:
        return list(flat)
    strides = [1] * len(sizes)
    for axis in range(1, len(sizes)):
        strides[axis] = strides[axis - 1] * sizes[axis - 1]

    def build(axis: int, base: int) -> Any:
        if axis < 0:
            return flat[base]
        return [
            build(axis - 1, base + index * strides[axis])
            for index in range(sizes[axis])
        ]

    return build(len(sizes) - 1, 0)
