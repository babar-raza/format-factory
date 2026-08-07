"""Deterministic NRRD writer."""

from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import Any, Mapping

from format_factory.core import BinaryDestination, ResourceLimits

from ...errors import NrrdParseError, NrrdWriteError
from ...model import NrrdDocument
from ...security import effective_limits
from ..payload import (
    SUPPORTED_ENCODINGS,
    TEXTUAL_ENCODINGS,
    encode_binary,
    encode_encoding,
    is_block_type,
    parse_block_size,
)

_FIELD_ORDER = (
    "type", "dimension", "space", "sizes", "space directions", "kinds",
    "endian", "encoding", "space origin", "measurement frame",
)


def _escape_key_value(text: str) -> str:
    """Apply the key/value escaping scheme: backslash -> "\\\\", newline -> "\\n"."""
    return text.replace("\\", "\\\\").replace("\n", "\\n")


def _coerce_document(value: NrrdDocument | Mapping[str, Any]) -> NrrdDocument:
    return value if isinstance(value, NrrdDocument) else NrrdDocument.from_mapping(value)


def _header_bytes(
    document: NrrdDocument, profile: str, *, detached_name: str | None = None
) -> bytes:
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
    if detached_name is not None:
        # The "data file: LIST" form must be the last field specification
        # in the header (NRRD-HEADER-001) -- a single detached name has no
        # such constraint, but emitting it last keeps both forms uniform.
        lines.append(f"data file: {detached_name}")
    for key in sorted(document.key_value_pairs):
        escaped_key = _escape_key_value(key)
        escaped_value = _escape_key_value(document.key_value_pairs[key])
        lines.append(f"{escaped_key}:={escaped_value}")
    try:
        return ("\n".join(lines) + "\n\n").encode("ascii")
    except UnicodeEncodeError as exc:
        raise NrrdWriteError("NRRD headers must be ASCII") from exc


def _select_profile(value: NrrdDocument, profile: str | None) -> str:
    # Default serialization preserves the version declared by the document.
    # Callers may deliberately request an explicit target profile to convert
    # it, or "auto" to select the oldest profile able to represent it
    # (NRRD-VERSION-001, NRRD-WRITE-001; feature gates per SAL-NRRD-00020).
    if profile == "auto":
        selected = f"NRRD000{value.minimal_version_for()}"
    else:
        selected = profile or f"NRRD000{value.version}"
    if selected not in {f"NRRD000{version}" for version in range(1, 6)}:
        raise NrrdWriteError(f"unsupported NRRD profile: {selected!r}")
    selected_version = int(selected[-1])
    minimal_version = value.minimal_version_for()
    if selected_version < minimal_version:
        # NRRD-LIFECYCLE-001: never silently rewrite a declared version --
        # refuse loudly instead of writing a profile too old for the fields
        # actually present.
        blocking = ", ".join(
            sorted(
                {
                    name
                    for gate, name in value.version_requirements()
                    if gate > selected_version
                }
            )
        )
        raise NrrdWriteError(
            f"{selected} cannot represent this document: {blocking} requires "
            f"NRRD000{minimal_version} or newer (declared version is never "
            'silently rewritten -- pass profile="auto" to select the oldest '
            "sufficient profile explicitly)"
        )
    return selected


def _encode_payload(value: NrrdDocument, active_limits: ResourceLimits) -> bytes:
    if value.encoding not in SUPPORTED_ENCODINGS:
        raise NrrdWriteError(f"unsupported NRRD encoding: {value.encoding!r}")
    try:
        block_size = (
            parse_block_size(value.header.get("block size"))
            if is_block_type(value.nrrd_type)
            else None
        )
    except NrrdParseError as exc:
        raise NrrdWriteError(str(exc)) from exc
    if block_size is not None and value.encoding in TEXTUAL_ENCODINGS:
        raise NrrdWriteError("block type is not valid with ASCII encoding")
    try:
        binary = encode_binary(
            value.nrrd_type,
            value.sizes,
            value.array,
            endian=value.header.get("endian"),
            limits=active_limits,
            block_size=block_size,
            # A textual payload exposes no byte order, so writing one must not
            # demand a declared `endian` (TC-FF6-NRRD-ASCII-ENDIAN-001).
            require_endian=value.encoding not in TEXTUAL_ENCODINGS,
        )
    except NrrdParseError as exc:
        # Reached via header-derived checks such as the endian guard. Failing to
        # produce output is a write failure, whichever helper detected it.
        raise NrrdWriteError(str(exc)) from exc
    return encode_encoding(binary, value.array, value.encoding, limits=active_limits)


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
    selected = _select_profile(value, profile)
    payload = _encode_payload(value, active_limits)
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


def dump_detached(
    document: NrrdDocument | Mapping[str, Any],
    header_destination: str | PathLike,
    payload_destination: str | PathLike,
    *,
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> None:
    """Write a detached NRRD: the header (with a `data file:` field naming
    ``payload_destination``) to ``header_destination``, and the encoded
    payload to ``payload_destination`` separately.

    ``payload_destination`` must resolve to a path this reader's own
    detached-path confinement rules can read back (NRRD-PAYLOAD-001,
    NRRD-SEC-001): a bare name relative to ``header_destination``'s own
    directory, never escaping it. Lossless/exact-preservation mode is not
    supported here -- it returns the document's original source bytes
    verbatim as a single buffer, which has no detached-form counterpart.
    """

    active_limits = effective_limits(limits)
    value = _coerce_document(document)
    header_path = Path(header_destination)
    payload_path = Path(payload_destination)
    try:
        relative_name = payload_path.resolve().relative_to(
            header_path.resolve().parent
        )
    except ValueError as exc:
        raise NrrdWriteError(
            "detached payload destination must be inside the header "
            "destination's own directory, matching this reader's own "
            "confinement rules for reading it back"
        ) from exc
    relative_str = relative_name.as_posix()
    selected = _select_profile(value, profile)
    payload = _encode_payload(value, active_limits)
    header_bytes = _header_bytes(value, selected, detached_name=relative_str)
    active_limits.enforce("max_output_bytes", len(header_bytes) + len(payload))
    try:
        header_path.write_bytes(header_bytes)
    except OSError as exc:
        raise NrrdWriteError(f"cannot write {header_path}: {exc}") from exc
    try:
        payload_path.write_bytes(payload)
    except OSError as exc:
        raise NrrdWriteError(f"cannot write {payload_path}: {exc}") from exc
