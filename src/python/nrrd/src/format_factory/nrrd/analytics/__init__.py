"""Pure NRRD inspection helpers."""

from __future__ import annotations

from ..model import NrrdDocument


def axis_sizes(document: NrrdDocument) -> tuple[int, ...]:
    return tuple(document.sizes)


def element_count(document: NrrdDocument) -> int:
    return document.element_count


def is_compressed(document: NrrdDocument) -> bool:
    return document.encoding in {"gzip", "gz", "bzip2", "bz2"}


__all__ = ["axis_sizes", "element_count", "is_compressed"]
