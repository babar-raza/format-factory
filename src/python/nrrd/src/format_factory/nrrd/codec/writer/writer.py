"""Deterministic NRRD writer."""

from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import Any, Mapping

from format_factory.core import BinaryDestination, ResourceLimits

from ...errors import NrrdWriteError
from ...model import NrrdDocument
from ...security import effective_limits
from ..payload import SUPPORTED_ENCODINGS, encode_binary, encode_encoding

_FIELD_ORDER = (
    "type", "dimension", "space", "sizes", "space directions", "kinds",
    "endian", "encoding", "space origin", "measurement frame",
)


def _coerce_document(value: NrrdDocument | Mapping[str, Any]) -> NrrdDocument:
    return value if isinstance(value, NrrdDocument) else NrrdDocument.from_mapping(value)


def _header_bytes(document: NrrdDocument, profile: str) -> bytes:
    lines = [profile]
    lines.extend(f"# {comment}" if comment else "#" for comment in document.comments)
    emitted: set[str] = set()
    for name in _FIELD_ORDER:
        if name in document.header:
            lines.append(f"{name}: {document.header[name]}")
            emitted.add(name)
    for name in sorted(document.header):
        if name not in emitted and name != "data file":
            lines.append(f"{name}: {document.header[name]}")
    for key in sorted(document.key_value_pairs):
        lines.append(f"{key}:={document.key_value_pairs[key]}")
    try:
        return ("\n".join(lines) + "\n\n").encode("ascii")
    except UnicodeEncodeError as exc:
        raise NrrdWriteError("NRRD headers must be ASCII") from exc


def dumps(
    document: NrrdDocument | Mapping[str, Any],
    *,
    profile: str | None = None,
    mode: str = "canonical",
    limits: ResourceLimits | None = None,
) -> bytes:
    """Serialize an attached document in canonical or exact-preservation mode."""

    active_limits = effective_limits(limits)
    value = _coerce_document(document)
    if mode not in {"canonical", "lossless"}:
        raise NrrdWriteError("mode must be 'canonical' or 'lossless'")
    if mode == "lossless":
        if profile is not None:
            raise NrrdWriteError(
                "lossless output cannot convert the declared NRRD profile"
            )
        report = value.preservation_report()
        if not report.is_lossless:
            detail = "; ".join(issue.message for issue in report.issues)
            raise NrrdWriteError(f"lossless output unavailable: {detail}")
        assert value.source_bytes is not None
        active_limits.enforce("max_output_bytes", len(value.source_bytes))
        return value.source_bytes
    # Default serialization preserves the version declared by the document.
    # Callers may deliberately request an explicit target profile to convert it.
    selected = profile or f"NRRD000{value.version}"
    if selected not in {f"NRRD000{version}" for version in range(1, 6)}:
        raise NrrdWriteError(f"unsupported NRRD profile: {selected!r}")
    if value.encoding not in SUPPORTED_ENCODINGS:
        raise NrrdWriteError(f"unsupported NRRD encoding: {value.encoding!r}")
    binary = encode_binary(
        value.nrrd_type,
        value.sizes,
        value.array,
        endian=value.header.get("endian"),
        limits=active_limits,
    )
    payload = encode_encoding(
        binary, value.array, value.encoding, limits=active_limits
    )
    result = _header_bytes(value, selected) + payload
    active_limits.enforce("max_output_bytes", len(result))
    return result


def dump(
    document: NrrdDocument | Mapping[str, Any],
    destination: BinaryDestination,
    *,
    profile: str | None = None,
    mode: str = "canonical",
    limits: ResourceLimits | None = None,
) -> None:
    """Write an attached NRRD to a path or binary stream."""

    data = dumps(document, profile=profile, mode=mode, limits=limits)
    if isinstance(destination, (str, PathLike)):
        try:
            Path(destination).write_bytes(data)
        except OSError as exc:
            raise NrrdWriteError(f"cannot write {destination}: {exc}") from exc
        return
    written = destination.write(data)
    if written != len(data):
        raise NrrdWriteError(
            f"short write: expected {len(data)} bytes, wrote {written}"
        )
