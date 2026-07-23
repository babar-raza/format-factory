"""Shared path/stream protocols and probe result.

visibility: generated
generated_by: codex
"""

from __future__ import annotations

from dataclasses import dataclass
from os import PathLike
from typing import BinaryIO, Protocol, TextIO, TypeAlias, runtime_checkable


@runtime_checkable
class ReadableBinary(Protocol):
    def read(self, size: int = -1, /) -> bytes: ...


@runtime_checkable
class SeekableBinary(ReadableBinary, Protocol):
    def seek(self, offset: int, whence: int = 0, /) -> int: ...

    def tell(self) -> int: ...


@runtime_checkable
class WritableBinary(Protocol):
    def write(self, data: bytes, /) -> int: ...


@runtime_checkable
class ReadableText(Protocol):
    def read(self, size: int = -1, /) -> str: ...


@runtime_checkable
class WritableText(Protocol):
    def write(self, data: str, /) -> int: ...


BinarySource: TypeAlias = str | PathLike[str] | bytes | bytearray | memoryview | BinaryIO
TextSource: TypeAlias = str | PathLike[str] | TextIO
BinaryDestination: TypeAlias = str | PathLike[str] | BinaryIO
TextDestination: TypeAlias = str | PathLike[str] | TextIO


@dataclass(frozen=True, slots=True)
class ProbeResult:
    matched: bool
    confidence: float
    format_id: str
    profile: str | None = None
    reason: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not self.format_id:
            raise ValueError("format_id must not be empty")

    def __bool__(self) -> bool:
        return self.matched
