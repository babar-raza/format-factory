"""Strict, bounded NRRD0001-NRRD0005 reader."""

from __future__ import annotations

import re
from dataclasses import replace
from os import PathLike
from pathlib import Path

from format_factory.core import (
    BinarySource,
    ProbeResult,
    ResourceLimitError,
    ResourceLimits,
)

from ...errors import NrrdParseError
from ...model import NrrdDocument
from ...security import effective_limits
from ..payload import (
    SUPPORTED_ENCODINGS,
    TEXTUAL_ENCODINGS,
    decode_ascii,
    decode_binary,
    decode_encoding,
    encode_binary,
    expected_binary_size,
    is_block_type,
    parse_block_size,
)

_REQUIRED_FIELDS = frozenset({"type", "dimension", "sizes", "encoding"})

#: "Starting with NRRD0004, space, space dimension, space units, space
#: origin, and per-axis space directions describe array orientation in a
#: surrounding space" (SAL-NRRD-00019) -- these 5 fields, read-time gated
#: below the same way the LIST/printf multi-file form and the NRRD0005
#: "measurement frame" field already are.
_NRRD0004_SPACE_FIELDS = ("space", "space dimension", "space units", "space origin", "space directions")

#: "Field specifications with alternate equivalent forms are listed together
#: (for example, 'block size' is the same as 'blocksize')." Confirmed
#: programmatically against the pinned spec text (every "<spaced>: <...>
#: <unspaced>: <...>" adjacency where unspaced == spaced.replace(' ', '')):
#: block size/blocksize, old min/oldmin, old max/oldmax, data file/datafile,
#: line skip/lineskip, byte skip/byteskip, sample units/sampleunits. Five of
#: the seven were already handled by a scattered `header.get(canonical,
#: header.get(alias))` fallback at each consumer; "block size" and
#: "data file" were not -- the latter's list-mode detection is itself keyed
#: on the exact parsed field name, so both are normalized once, here, at the
#: earliest possible point, rather than patched at every consumer.
_UNSPACED_FIELD_ALIASES = {
    "blocksize": "block size",
    "datafile": "data file",
}


def _unescape_key_value(text: str) -> str:
    """Reverse the key/value escaping scheme: "\\n" -> newline, "\\\\" -> backslash."""
    result: list[str] = []
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char == "\\" and index + 1 < length and text[index + 1] in "n\\":
            result.append("\n" if text[index + 1] == "n" else "\\")
            index += 2
            continue
        result.append(char)
        index += 1
    return "".join(result)


def _read_source(source: BinarySource, limits: ResourceLimits) -> tuple[bytes, Path | None]:
    path: Path | None = None
    if isinstance(source, bytes):
        data = source
    elif isinstance(source, (bytearray, memoryview)):
        data = bytes(source)
    elif isinstance(source, (str, PathLike)):
        path = Path(source)
        try:
            limits.enforce("max_input_bytes", path.stat().st_size)
            data = path.read_bytes()
        except OSError as exc:
            raise NrrdParseError(f"cannot read {path}: {exc}") from exc
    elif hasattr(source, "read"):
        data = source.read(limits.max_input_bytes + 1)
        if not isinstance(data, bytes):
            raise TypeError("binary source read() must return bytes")
    else:
        raise TypeError("source must be bytes, a path, or a binary stream")
    limits.enforce("max_input_bytes", len(data))
    return data, path


def _split_header(data: bytes, limits: ResourceLimits) -> tuple[bytes, bytes, int]:
    candidates: list[tuple[int, int]] = []
    for terminator in (b"\n\n", b"\r\n\r\n"):
        index = data.find(terminator)
        if index >= 0:
            candidates.append((index, len(terminator)))
    if not candidates:
        raise NrrdParseError("NRRD header has no blank-line terminator")
    index, terminator_size = min(candidates, key=lambda item: item[0])
    end = index + terminator_size
    limits.enforce("max_header_bytes", end)
    return data[:index], data[end:], end


def _parse_header(
    raw_header: bytes,
) -> tuple[int, dict[str, str], list[str], dict[str, str]]:
    try:
        text = raw_header.decode("ascii")
    except UnicodeDecodeError as exc:
        raise NrrdParseError("NRRD header must be ASCII") from exc
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or len(lines[0]) != 8 or not lines[0].startswith("NRRD000"):
        raise NrrdParseError("invalid NRRD magic")
    try:
        version = int(lines[0][-1])
    except ValueError as exc:
        raise NrrdParseError("invalid NRRD version") from exc
    if not 1 <= version <= 5:
        raise NrrdParseError(f"unsupported NRRD version: {version}")

    header: dict[str, str] = {}
    comments: list[str] = []
    key_values: dict[str, str] = {}
    list_files: list[str] = []
    list_mode = False
    list_header_value = "LIST"
    for line_number, line in enumerate(lines[1:], start=2):
        if list_mode:
            if line:
                list_files.append(line)
            continue
        if not line:
            continue
        if line.startswith("#"):
            comments.append(line[1:].lstrip())
            continue
        if ":=" in line:
            if version < 2:
                raise NrrdParseError(
                    f"key/value pairs require NRRD0002 or newer, got NRRD000{version} "
                    f"at line {line_number}"
                )
            key, value = line.split(":=", 1)
            if not key:
                raise NrrdParseError(f"empty key/value key at line {line_number}")
            key_values[_unescape_key_value(key)] = _unescape_key_value(value)
            continue
        if ":" not in line:
            raise NrrdParseError(f"malformed header line {line_number}")
        if line[0].isspace():
            raise NrrdParseError(
                f"whitespace is not allowed before the field identifier at line {line_number}"
            )
        key, value = line.split(":", 1)
        if not value.startswith(" ") or value.startswith("  "):
            raise NrrdParseError(
                f"field identifier at line {line_number} must be followed by a colon "
                "and a single space"
            )
        normalized = key.strip().lower()
        normalized = _UNSPACED_FIELD_ALIASES.get(normalized, normalized)
        if not normalized or not value.strip():
            raise NrrdParseError(f"malformed header field at line {line_number}")
        if normalized in header:
            raise NrrdParseError(f"duplicate header field {normalized!r}")
        header[normalized] = value.strip()
        if normalized == "data file" and value.strip().upper().startswith("LIST"):
            list_mode = True
            list_header_value = value.strip()
    if list_files:
        # "data file: LIST [<subdim>]" -- the optional <subdim> token, if
        # present, is on the same line as the LIST keyword itself, not
        # among the filenames that follow. Preserve the original captured
        # first line verbatim instead of a hardcoded "LIST" so a subdim
        # token survives into the reconstructed value for the detached
        # payload parser to validate.
        header["data file"] = list_header_value + "\n" + "\n".join(list_files)
    missing = sorted(_REQUIRED_FIELDS.difference(header))
    if missing:
        raise NrrdParseError(f"missing required header fields: {', '.join(missing)}")
    return version, header, comments, key_values


def _parse_sizes(header: dict[str, str]) -> list[int]:
    try:
        sizes = [int(value) for value in header["sizes"].split()]
        dimension = int(header["dimension"])
    except ValueError as exc:
        raise NrrdParseError("dimension and sizes must be integers") from exc
    if dimension <= 0 or len(sizes) != dimension:
        raise NrrdParseError("dimension must be positive and equal the number of sizes")
    return sizes


def _read_relative_to(name: str, *, base: Path, what: str) -> bytes:
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise NrrdParseError("unsafe detached data path")
    resolved = (base / relative).resolve()
    try:
        resolved.relative_to(base)
    except ValueError as exc:
        raise NrrdParseError(f"detached data path escapes its {what}") from exc
    try:
        return resolved.read_bytes()
    except OSError as exc:
        raise NrrdParseError(f"cannot read detached payload {resolved}: {exc}") from exc


def _safe_detached_payload(
    value: str,
    *,
    source_path: Path | None,
    limits: ResourceLimits,
    version: int,
    dimension: int,
    cwd_relative_base: Path | None = None,
) -> bytes:
    if source_path is None:
        raise NrrdParseError("detached data requires a filesystem header source")
    def read_relative(name: str) -> bytes:
        if version < 4 and not name.startswith("./") and not name.startswith("/"):
            # "as of NRRD0004, the signifier of a header-relative file
            # changed from the presence (at the beginning of the filename)
            # of './', to the absence of '/'." Pre-NRRD0004, a name without
            # the explicit './' prefix is spec-defined as relative to the
            # reader's current working directory rather than the header's
            # directory -- an unconfined resolution base this reader
            # refuses by default. `cwd_relative_base` is the explicit,
            # caller-supplied opt-in: when given, it names the directory
            # "cwd-relative" means for this call, and the same
            # traversal-safety checks below apply relative to it instead of
            # refusing outright.
            if cwd_relative_base is None:
                raise NrrdParseError(
                    "pre-NRRD0004 detached data file names must start with "
                    "'./' to be resolved relative to the header; this reader "
                    "does not support cwd-relative resolution unless "
                    "cwd_relative_base is explicitly supplied"
                )
            return _read_relative_to(name, base=cwd_relative_base.resolve(), what="cwd_relative_base")
        if name.startswith("./"):
            name = name[2:]
        return _read_relative_to(name, base=base, what="header directory")

    base = source_path.resolve().parent
    is_multi_file = value.upper().startswith("LIST") or "%" in value
    if is_multi_file and version < 4:
        # "the data file field can identify multiple payload files ...
        # starting with NRRD0004" -- a LIST or printf-sequence declaration
        # under an older magic is refused at read time rather than silently
        # accepted and left for an optional, separately-invoked validate()
        # call to catch later (version_requirements()/validate() already
        # flag this as nrrd.version.insufficient, but a caller who only
        # calls load() never sees that diagnostic).
        raise NrrdParseError(
            f"multi-file data file declarations require NRRD0004 or newer, "
            f"got NRRD000{version}"
        )
    if value.upper().startswith("LIST"):
        first_line, *rest_lines = value.splitlines()
        names = [line.strip() for line in rest_lines if line.strip()]
        if not names:
            raise NrrdParseError("detached LIST has no payload paths")
        subdim_token = first_line.strip()[len("LIST") :].strip()
        if subdim_token:
            # "A different datafile dimension (besides D-1) can be
            # communicated with the optional <subdim> value. This value
            # can be between 1 and D," D being the declared `dimension:`.
            # Validated here, before any file is opened -- same
            # validate-only treatment as the printf form's own <subdim>:
            # not otherwise used to alter which files are read or how
            # their bytes are concatenated.
            try:
                subdim = int(subdim_token)
            except ValueError as exc:
                raise NrrdParseError("detached LIST subdim must be an integer") from exc
            if not 1 <= subdim <= dimension:
                raise NrrdParseError(
                    f"detached LIST subdim must be between 1 and {dimension}, got {subdim}"
                )
        if len(names) > limits.max_entries:
            raise ResourceLimitError(
                f"detached LIST declares {len(names)} files, over the limit of "
                f"{limits.max_entries}"
            )
    elif "%" in value:
        parts = value.split()
        if len(parts) not in (4, 5) or not re.fullmatch(r"[^%]*%0?\d*d[^%]*", parts[0]):
            raise NrrdParseError("invalid detached printf pattern")
        try:
            start, stop, step = (int(item) for item in parts[1:4])
        except ValueError as exc:
            raise NrrdParseError("invalid detached printf range") from exc
        if step == 0 or (stop - start) * step < 0:
            raise NrrdParseError("invalid detached printf range")
        if len(parts) == 5:
            # "A different datafile dimension (besides D-1) can be
            # communicated with the optional <subdim> value. This value
            # can be between 1 and D," D being the declared `dimension:`.
            # Validated here, before any file is opened; not otherwise
            # used to alter which files are read or how their bytes are
            # concatenated -- min/max/step alone already determine that,
            # and the declared array shape is independently checked
            # against the assembled payload's total byte count downstream.
            try:
                subdim = int(parts[4])
            except ValueError as exc:
                raise NrrdParseError("detached printf subdim must be an integer") from exc
            if not 1 <= subdim <= dimension:
                raise NrrdParseError(
                    f"detached printf subdim must be between 1 and {dimension}, got {subdim}"
                )
        file_count = abs(stop - start) // abs(step) + 1
        if file_count > limits.max_entries:
            raise ResourceLimitError(
                f"detached printf sequence declares {file_count} files, over the "
                f"limit of {limits.max_entries}"
            )
        names = [parts[0] % item for item in range(start, stop + (1 if step > 0 else -1), step)]
    else:
        names = [value]
    payload = b"".join(read_relative(name) for name in names)
    limits.enforce("max_input_bytes", len(payload))
    return payload


def _apply_skips(payload: bytes, header: dict[str, str]) -> bytes:
    try:
        line_skip = int(header.get("line skip", header.get("lineskip", "0")))
        byte_skip = int(header.get("byte skip", header.get("byteskip", "0")))
    except ValueError as exc:
        raise NrrdParseError("line skip and byte skip must be integers") from exc
    if line_skip < 0 or byte_skip < -1:
        raise NrrdParseError("invalid line skip or byte skip")
    for _ in range(line_skip):
        newline = payload.find(b"\n")
        if newline < 0:
            raise NrrdParseError("line skip exceeds payload")
        payload = payload[newline + 1 :]
    if byte_skip > 0:
        if byte_skip > len(payload):
            raise NrrdParseError("byte skip exceeds payload")
        payload = payload[byte_skip:]
    return payload


def probe(
    source: BinarySource, *, limits: ResourceLimits | None = None
) -> ProbeResult:
    """Inspect a bounded source without surfacing parse failures."""

    try:
        data, _ = _read_source(source, effective_limits(limits))
        line = data.splitlines()[0] if data else b""
        matched = (
            len(line) == 8
            and line.startswith(b"NRRD000")
            and line[-1:] in {b"1", b"2", b"3", b"4", b"5"}
        )
        return ProbeResult(
            matched=matched,
            confidence=1.0 if matched else 0.0,
            format_id="nrrd",
            profile=line.decode("ascii") if matched else None,
            reason="recognized NRRD magic" if matched else "NRRD magic not found",
        )
    except Exception:
        return ProbeResult(False, 0.0, "nrrd", reason="source is not readable")


def loads(
    data: bytes | bytearray | memoryview,
    *,
    mode: str = "strict",
    limits: ResourceLimits | None = None,
    cwd_relative_base: Path | None = None,
) -> NrrdDocument:
    if mode not in {"strict", "preservation", "recovery"}:
        raise ValueError("mode must be 'strict', 'preservation', or 'recovery'")
    return _load(data, limits=effective_limits(limits), cwd_relative_base=cwd_relative_base)


def load(
    source: BinarySource,
    *,
    mode: str = "strict",
    limits: ResourceLimits | None = None,
    cwd_relative_base: Path | None = None,
) -> NrrdDocument:
    if mode not in {"strict", "preservation", "recovery"}:
        raise ValueError("mode must be 'strict', 'preservation', or 'recovery'")
    return _load(source, limits=effective_limits(limits), cwd_relative_base=cwd_relative_base)


def _load(
    source: BinarySource,
    *,
    limits: ResourceLimits,
    recovery_actions: tuple[str, ...] = (),
    cwd_relative_base: Path | None = None,
) -> NrrdDocument:
    data, source_path = _read_source(source, limits)
    raw_header, attached, data_offset = _split_header(data, limits)
    version, header, comments, key_values = _parse_header(raw_header)
    declared_space_fields = [name for name in _NRRD0004_SPACE_FIELDS if name in header]
    if declared_space_fields and version < 4:
        # "Starting with NRRD0004, space, space dimension, space units,
        # space origin, and per-axis space directions describe array
        # orientation" -- a declaration under an older magic is refused
        # at read time rather than silently accepted, the same
        # read-time-vs-validate()-only distinction as the measurement
        # frame and LIST/printf gates in this same function.
        raise NrrdParseError(
            f"{declared_space_fields!r} require NRRD0004 or newer, got NRRD000{version}"
        )
    if "measurement frame" in header and version < 5:
        # "measurement frame... is not available until NRRD0005" -- a
        # declaration under an older magic is refused at read time rather
        # than silently accepted (same read-time-vs-validate()-only
        # distinction as the LIST/printf multi-file gate below:
        # version_requirements()/validate() already flag this as
        # nrrd.version.insufficient, but a caller who only calls load()
        # never sees that diagnostic).
        raise NrrdParseError(
            f"'measurement frame' requires NRRD0005 or newer, got NRRD000{version}"
        )
    sizes = _parse_sizes(header)
    encoding = header["encoding"].lower()
    if encoding not in SUPPORTED_ENCODINGS:
        raise NrrdParseError(f"unsupported NRRD encoding: {encoding!r}")
    block_size = (
        parse_block_size(header.get("block size"))
        if is_block_type(header["type"])
        else None
    )
    if block_size is not None and encoding in TEXTUAL_ENCODINGS:
        raise NrrdParseError("block type is not valid with ASCII encoding")
    payload = (
        _safe_detached_payload(
            header["data file"],
            source_path=source_path,
            limits=limits,
            version=version,
            dimension=len(sizes),
            cwd_relative_base=cwd_relative_base,
        )
        if "data file" in header
        else attached
    )
    payload = _apply_skips(payload, header)
    # SAL-NRRD-OBL-9C262130232DCD09 (NRRD-VALIDATE-001): "checked arithmetic
    # BEFORE any payload allocation... hostile headers must fail cheaply."
    # expected_binary_size() computes the declared shape's own exact byte
    # count via checked arithmetic and already enforces it against
    # limits.max_decompressed_bytes -- computing it once, upfront, for every
    # encoding (not only the byte-skip -1 case below) lets a compressed
    # payload's own decompression be capped at what the header's own
    # declared shape could ever need, not just the generic global ceiling.
    # A hostile file whose compressed bytes are small but whose header
    # claims a decompressed size near the generic 2GB default now fails at
    # the declared-shape arithmetic check, before a single byte is
    # decompressed, rather than only being caught partway through
    # decompression by the unrelated, much larger global limit.
    expected = expected_binary_size(header["type"], sizes, limits, block_size=block_size)
    if header.get("byte skip", header.get("byteskip")) == "-1":
        if encoding != "raw":
            raise NrrdParseError("byte skip -1 is valid only for raw encoding")
        if expected > len(payload):
            raise NrrdParseError("byte skip -1 payload is truncated")
        payload = payload[-expected:]

    if encoding in TEXTUAL_ENCODINGS:
        array = decode_ascii(header["type"], sizes, payload, limits=limits)
        # The values came from text, so the file exposes no byte order. This
        # re-encode only builds the document's derived binary buffer, so a
        # declared `endian` is honored when present but never demanded.
        binary = encode_binary(
            header["type"],
            sizes,
            array,
            endian=header.get("endian"),
            limits=limits,
            block_size=block_size,
            require_endian=False,
        )
    else:
        decode_limits = replace(
            limits, max_decompressed_bytes=min(limits.max_decompressed_bytes, expected)
        )
        binary = decode_encoding(payload, encoding, limits=decode_limits)
        array = decode_binary(
            header["type"],
            sizes,
            binary,
            endian=header.get("endian"),
            limits=limits,
            block_size=block_size,
        )
    return NrrdDocument(
        version=version,
        detected_version=version,
        header=header,
        comments=comments,
        key_value_pairs=key_values,
        raw_header=raw_header,
        payload=binary,
        array=array,
        source_path=str(source_path) if source_path else None,
        data_offset=data_offset,
        recovery_actions=recovery_actions,
        source_bytes=data if "data file" not in header else None,
        _original_header=dict(header),
        _original_comments=list(comments),
        _original_key_value_pairs=dict(key_values),
        _original_array=list(array),
    )
