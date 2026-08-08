"""Deterministic NRRD writer."""

from __future__ import annotations

import re
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


def _field_line(name: str, value: str) -> str:
    """One `name: value` header line -- refused, not silently emitted, if
    `value` is empty or whitespace-only: `_parse_header`'s own reader-side
    grammar already rejects such a line as malformed
    (`not value.strip()`), so writing one anyway would produce a file this
    same writer's own reader could never read back (NRRD-PRESERVE-001)."""
    if not value.strip():
        raise NrrdWriteError(
            f"cannot write header field {name!r} with an empty value -- the "
            "reader's own grammar requires a non-empty value after the "
            "colon and space, so writing one would produce output this "
            "library could not read back"
        )
    return f"{name}: {value}"


def _header_bytes(
    document: NrrdDocument, profile: str, *, detached_name: str | None = None
) -> bytes:
    lines = [profile]
    lines.extend(f"# {comment}" if comment else "#" for comment in document.comments)
    emitted: set[str] = set()
    for name in _FIELD_ORDER:
        if name in document.header:
            lines.append(_field_line(name, document.header[name]))
            emitted.add(name)
    for name in sorted(document.header):
        if name not in emitted and name != "data file":
            lines.append(_field_line(name, document.header[name]))
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
    header_destination: str | PathLike[str],
    payload_destination: str | PathLike[str],
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


def dump_multifile(
    document: NrrdDocument | Mapping[str, Any],
    header_destination: str | PathLike[str],
    payload_destinations: list[str | PathLike[str]],
    *,
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> None:
    """Write a multi-file detached NRRD: the header (with a `data file:
    LIST` declaration naming every entry in `payload_destinations`, in
    order) to `header_destination`, and the encoded payload split evenly
    across those files.

    Byte distribution: the reader's own `_safe_detached_payload` (codec/
    reader/reader.py) concatenates every listed file's raw bytes in
    declared order with no per-file splitting logic of its own -- `subdim`
    is parsed and range-validated but, per that function's own comment,
    "not otherwise used to alter which files are read or how their bytes
    are concatenated." Writing the exact mirror of that -- the full
    encoded payload split into `len(payload_destinations)` equal
    consecutive chunks, written in the same order the header lists them --
    is therefore both correct and the only byte distribution the reader's
    own contract requires. `payload_destinations` count must therefore
    evenly divide the encoded payload's own byte length; refused otherwise
    with a clear reason rather than guessing an uneven split.

    Multi-file `data file: LIST` declarations require NRRD0004 or newer
    (matching `_safe_detached_payload`'s own read-time version gate) --
    refused for an older explicit or auto-selected profile rather than
    silently writing a file the reader's own load() would then reject.
    """

    if not payload_destinations:
        raise NrrdWriteError("at least one payload destination is required")
    active_limits = effective_limits(limits)
    value = _coerce_document(document)
    header_path = Path(header_destination)
    selected = _select_profile(value, profile)
    if int(selected[-1]) < 4:
        raise NrrdWriteError(
            f"multi-file data file declarations require NRRD0004 or newer, "
            f"selected profile is {selected!r}"
        )
    payload = _encode_payload(value, active_limits)
    file_count = len(payload_destinations)
    if len(payload) % file_count != 0:
        raise NrrdWriteError(
            f"encoded payload of {len(payload)} bytes does not split evenly "
            f"across {file_count} files"
        )
    chunk_size = len(payload) // file_count
    header_parent = header_path.resolve().parent
    relative_names: list[str] = []
    for destination in payload_destinations:
        payload_path = Path(destination)
        try:
            relative_name = payload_path.resolve().relative_to(header_parent)
        except ValueError as exc:
            raise NrrdWriteError(
                "every multi-file payload destination must be inside the header "
                "destination's own directory, matching this reader's own "
                "confinement rules for reading it back"
            ) from exc
        relative_names.append(relative_name.as_posix())
    header_bytes = _header_bytes(
        value, selected, detached_name="LIST\n" + "\n".join(relative_names)
    )
    active_limits.enforce("max_output_bytes", len(header_bytes) + len(payload))
    try:
        header_path.write_bytes(header_bytes)
    except OSError as exc:
        raise NrrdWriteError(f"cannot write {header_path}: {exc}") from exc
    for index, destination in enumerate(payload_destinations):
        chunk = payload[index * chunk_size : (index + 1) * chunk_size]
        try:
            Path(destination).write_bytes(chunk)
        except OSError as exc:
            raise NrrdWriteError(f"cannot write {destination}: {exc}") from exc


#: Same grammar the reader's own _safe_detached_payload (codec/reader/
#: reader.py) validates a printf pattern's first token against -- reused
#: verbatim so a pattern this function accepts is guaranteed one the
#: reader would also accept back.
_PRINTF_PATTERN = re.compile(r"[^%]*%0?\d*d[^%]*")


def dump_multifile_printf(
    document: NrrdDocument | Mapping[str, Any],
    header_destination: str | PathLike[str],
    pattern: str,
    *,
    start: int = 0,
    step: int = 1,
    file_count: int,
    subdim: int | None = None,
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> None:
    """Write a multi-file detached NRRD using a printf numbered sequence
    (`data file: <pattern> <start> <stop> <step> [<subdim>]`) instead of
    an explicit LIST of paths -- the sibling form `dump_multifile()`
    (FF6-EVENT-000303) does not cover.

    `stop` is derived from `start`/`step`/`file_count` using the exact
    same arithmetic the reader's own `_safe_detached_payload` uses in
    reverse (`file_count = abs(stop - start) // abs(step) + 1`), and
    filenames are generated with the same `pattern % item` expression the
    reader itself evaluates when reading a printf sequence back -- so a
    file this function writes is named exactly what the reader would look
    for, not merely something "close enough". Byte distribution mirrors
    `dump_multifile()`: the full encoded payload split into `file_count`
    equal consecutive chunks, written in generated-name order (the
    reader's own contract for how printf sequence bytes are concatenated
    is identical to the LIST form's).

    `pattern` must contain exactly one printf integer conversion (the same
    grammar the reader's own read-time check enforces) and no path
    separators -- every generated file is written into the header
    destination's own directory, matching where the reader will look for
    a header-relative name.
    """

    if file_count < 1:
        raise NrrdWriteError("file_count must be at least 1")
    if not _PRINTF_PATTERN.fullmatch(pattern):
        raise NrrdWriteError(
            f"invalid printf pattern {pattern!r}: must contain exactly one "
            "%d-family conversion"
        )
    if "/" in pattern or "\\" in pattern:
        raise NrrdWriteError(
            "printf pattern must not contain a path separator -- every "
            "generated file is written into the header destination's own directory"
        )
    if step == 0:
        raise NrrdWriteError("step must not be zero")

    active_limits = effective_limits(limits)
    value = _coerce_document(document)
    header_path = Path(header_destination)
    selected = _select_profile(value, profile)
    if int(selected[-1]) < 4:
        raise NrrdWriteError(
            f"multi-file data file declarations require NRRD0004 or newer, "
            f"selected profile is {selected!r}"
        )
    if subdim is not None:
        dimension = value.dimension
        if not 1 <= subdim <= dimension:
            raise NrrdWriteError(
                f"subdim must be between 1 and {dimension}, got {subdim}"
            )

    stop = start + step * (file_count - 1)
    names = [pattern % item for item in range(start, stop + (1 if step > 0 else -1), step)]

    payload = _encode_payload(value, active_limits)
    if len(payload) % file_count != 0:
        raise NrrdWriteError(
            f"encoded payload of {len(payload)} bytes does not split evenly "
            f"across {file_count} files"
        )
    chunk_size = len(payload) // file_count

    header_value = f"{pattern} {start} {stop} {step}"
    if subdim is not None:
        header_value += f" {subdim}"
    header_bytes = _header_bytes(value, selected, detached_name=header_value)
    active_limits.enforce("max_output_bytes", len(header_bytes) + len(payload))
    try:
        header_path.write_bytes(header_bytes)
    except OSError as exc:
        raise NrrdWriteError(f"cannot write {header_path}: {exc}") from exc
    header_parent = header_path.resolve().parent
    for index, name in enumerate(names):
        chunk = payload[index * chunk_size : (index + 1) * chunk_size]
        try:
            (header_parent / name).write_bytes(chunk)
        except OSError as exc:
            raise NrrdWriteError(f"cannot write {header_parent / name}: {exc}") from exc
