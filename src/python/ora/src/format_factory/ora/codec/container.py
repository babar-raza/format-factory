"""ORA-CONTAINER-001, ORA-MIMETYPE-001 — the OpenRaster archive wrapper.

An .ora file is a ZIP archive supplied by a stranger. Every other obligation in
this package reads through this module, so this is where hostile input has to
die: before a payload is decompressed, before a name becomes a path, and before
a caller can be the one who gets it wrong.

The normative rules this implements, quoted from the format contract:

  "The first archive member must be named mimetype, must be STORED without
   compression, and must contain exactly image/openraster without whitespace or
   a trailing newline."
  "Member names in an OpenRaster ZIP archive are case-sensitive and must be
   UTF-8 encoded with the ZIP UTF-8 flag used for non-ASCII names."
  "OpenRaster ZIP members may use only the DEFLATED and STORED compression
   methods."
  "The required stack.xml archive member is a UTF-8 encoded XML document
   conforming to the OpenRaster Layer Stack format."

Validation is eager and total: `from_bytes` either returns a container whose
every member has already been checked, or raises. There is deliberately no
general lazy or permissive mode -- a half-validated archive is the state in
which callers write the bugs this module exists to prevent.

`ReadMode.TOLERANT` (2026-08-11) is the one narrow, explicitly enumerated
exception: it does not weaken any check above, it changes exactly one thing
-- the mimetype sentinel is located by NAME rather than required to be the
ZIP's own first physical central-directory entry, because a real, widely
-used OpenRaster-producing application (MyPaint; see
tests/python/ora/fixtures/third-party-gpl-mypaint/PROVENANCE.md) emits
archives that do not honor that ordering. Existence, STORED compression, and
exact sentinel bytes are still mandatory in both modes; duplicate member
names, path traversal, disallowed compression, and every resource limit in
this module are unconditional in both modes. STRICT is unchanged: this
module's own docstring guarantee ("eager and total... or raises") still
holds for STRICT byte-for-byte.

ORA-STREAM-001 (FF6-EVENT-000487): `_check_limits`'s declared-size and
compression-ratio checks only ever inspect the ZIP central directory's own
metadata -- attacker-controlled fields, not independently verified against
the member's real compressed stream. Proven directly: a member whose
declared size (and matching crc32) describe only a small prefix of a much
larger real payload passes every check here, and `zipfile.ZipFile.read()`
decompresses the ENTIRE real payload internally before returning that small
prefix, so peak memory scales with the real payload's own size regardless
of what was declared. `read()` now decompresses through `_bounded_read`
instead, in fixed-size chunks via `ZipFile.open()`, decoupling peak memory
from the real payload's size.
"""

from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass, field
from pathlib import PurePosixPath

from format_factory.core import DEFAULT_LIMITS, ResourceLimits

from ..errors import OraArchiveError, OraLimitError
from ..modes import ReadMode

#: The sentinel's exact bytes. Compared without stripping, by design.
OPENRASTER_MEDIA_TYPE = b"image/openraster"

MIMETYPE_MEMBER = "mimetype"
STACK_MEMBER = "stack.xml"

#: "OpenRaster ZIP members may use only the DEFLATED and STORED compression
#: methods." Other methods are valid ZIP and invalid OpenRaster.
ALLOWED_COMPRESSION = frozenset({zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED})

_COMPRESSION_NAMES = {
    zipfile.ZIP_STORED: "STORED",
    zipfile.ZIP_DEFLATED: "DEFLATED",
    zipfile.ZIP_BZIP2: "BZIP2",
    zipfile.ZIP_LZMA: "LZMA",
}


def _describe_compression(method: int) -> str:
    return _COMPRESSION_NAMES.get(method, f"method {method}")


def _reject_unsafe_name(name: str) -> None:
    """Refuse any member name that could escape an extraction root.

    Member names become file paths the moment anyone extracts, and callers
    extract. Checking here means no caller has to remember to.

    Backslash is deliberately rejected rather than normalised: it is a legal
    ZIP name character and a path separator on Windows only, so a name like
    ``data\\..\\..\\evil`` escapes on one platform and is an odd filename on
    another. A container that behaved differently by platform would be worse
    than one that refuses.
    """
    if not name:
        raise OraArchiveError("archive contains a member with an empty name")

    if "\\" in name:
        raise OraArchiveError(
            f"member name {name!r} contains a backslash; OpenRaster member paths "
            "are archive-root-relative POSIX paths"
        )

    if name.startswith("/"):
        raise OraArchiveError(f"member name {name!r} is an absolute path")

    # "C:/..." is absolute on Windows even though it does not start with "/".
    if len(name) >= 2 and name[1] == ":":
        raise OraArchiveError(f"member name {name!r} is a drive-qualified absolute path")

    parts = PurePosixPath(name).parts
    if ".." in parts:
        raise OraArchiveError(
            f"member name {name!r} traverses outside the archive root"
        )


def _check_mimetype(
    archive: zipfile.ZipFile, infos: list[zipfile.ZipInfo], *, mode: ReadMode
) -> tuple[str, tuple[str, ...]]:
    """Enforce the sentinel's position (STRICT only), compression method and
    exact bytes (both modes, unconditionally). Returns (mimetype, recovery_notes)."""
    if not infos:
        raise OraArchiveError("archive is empty; the mimetype member is required")

    present = any(info.filename == MIMETYPE_MEMBER for info in infos)
    if not present:
        raise OraArchiveError("archive has no mimetype member")

    first = infos[0]
    recovery: list[str] = []
    if first.filename != MIMETYPE_MEMBER:
        if mode is ReadMode.STRICT:
            raise OraArchiveError(
                f"the mimetype member must be the first archive member, but "
                f"{first.filename!r} is first"
            )
        # TOLERANT: existence (checked above), compression, and exact content
        # are still mandatory below -- only physical position is excused, and
        # only because the member genuinely exists somewhere in the archive.
        recovery.append(
            f"mimetype member was not the first archive member (found after "
            f"{first.filename!r}); located by name instead of position "
            "(ReadMode.TOLERANT)"
        )

    mimetype_info = next(info for info in infos if info.filename == MIMETYPE_MEMBER)
    if mimetype_info.compress_type != zipfile.ZIP_STORED:
        raise OraArchiveError(
            "the mimetype member must be STORED without compression, but is "
            f"{_describe_compression(mimetype_info.compress_type)}"
        )

    payload = archive.read(MIMETYPE_MEMBER)
    if payload != OPENRASTER_MEDIA_TYPE:
        # Reported without stripping: whitespace is the failure, so showing the
        # stripped value would hide the reason.
        raise OraArchiveError(
            f"the mimetype member must contain exactly "
            f"{OPENRASTER_MEDIA_TYPE.decode()!r} with no whitespace or trailing "
            f"newline, but contains {payload!r}"
        )

    return OPENRASTER_MEDIA_TYPE.decode("ascii"), tuple(recovery)


def _bounded_read(archive: zipfile.ZipFile, name: str, *, limit: int) -> bytes:
    """Decompress one member, refusing before more than `limit` decompressed
    bytes accumulate.

    `zipfile.ZipFile.read()` decompresses however many bytes the member's
    real compressed stream actually produces, then checks the result's CRC-32
    against the central directory's own declared value -- a mismatch raises
    `BadZipFile`, but only AFTER the full content is already resident in
    memory. The central directory's declared uncompressed size (what
    `_check_limits` sums to reject an oversized archive up front) does not
    bound that decompression either: it is attacker-controlled metadata, not
    a cap `zipfile` itself enforces against the real stream. A member whose
    declared size is a small lie and whose real DEFLATE stream expands to
    gigabytes defeats every check in `_check_limits` and forces a full,
    unbounded expansion into memory before the lie is ever discovered.

    Reading through `ZipFile.open()` in fixed-size chunks, instead of the
    module's own eager `.read()`, decouples the memory bound from the
    declared metadata: decompression is refused mid-stream, the moment the
    real output exceeds `limit`, rather than after an arbitrary amount of it
    is already sitting in memory.
    """
    chunk_size = 1024 * 1024
    chunks: list[bytes] = []
    total = 0
    with archive.open(name) as member:
        while True:
            chunk = member.read(chunk_size)
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                raise OraLimitError(
                    f"member {name!r} decompressed to over {limit} bytes, "
                    "exceeding the configured limit before its declared size "
                    "could be trusted"
                )
            chunks.append(chunk)
    return b"".join(chunks)


def _check_limits(infos: list[zipfile.ZipInfo], limits: ResourceLimits) -> None:
    """Refuse oversized or bomb-shaped archives from the central directory alone.

    Every quantity here is read from the member directory, so an archive that
    declares gigabytes is refused without decompressing a single byte.
    """
    if len(infos) > limits.max_entries:
        raise OraLimitError(
            f"archive declares {len(infos)} members, over the limit of "
            f"{limits.max_entries} entries"
        )

    declared = sum(info.file_size for info in infos)
    if declared > limits.max_decompressed_bytes:
        raise OraLimitError(
            f"archive members declare {declared} bytes uncompressed, over the "
            f"limit of {limits.max_decompressed_bytes}"
        )

    compressed = sum(info.compress_size for info in infos)
    if compressed > 0 and declared / compressed > limits.max_compression_ratio:
        raise OraLimitError(
            f"archive expands {declared / compressed:.1f}x, over the maximum "
            f"compression ratio of {limits.max_compression_ratio}"
        )


@dataclass(frozen=True)
class OraContainer:
    """A validated OpenRaster archive.

    Construction guarantees the sentinel is correct, no member name can escape
    an extraction root, no member uses a forbidden compression method, no name
    is duplicated, stack.xml is present, and the declared sizes are within the
    supplied limits. Members are read on demand; nothing is decompressed during
    validation. `read()` itself enforces the same `max_decompressed_bytes`
    budget against each member's real decompressed output, not merely its
    declared (attacker-controlled) size -- see `_bounded_read`'s own
    docstring for why the declared-size check alone is not sufficient.
    """

    mimetype: str
    names: tuple[str, ...]
    _archive: zipfile.ZipFile = field(repr=False, compare=False)
    _limits: ResourceLimits = field(repr=False, compare=False)
    recovery_actions: tuple[str, ...] = ()

    @classmethod
    def from_bytes(
        cls,
        payload: bytes,
        *,
        limits: ResourceLimits = DEFAULT_LIMITS,
        mode: ReadMode = ReadMode.STRICT,
    ) -> "OraContainer":
        """Validate `payload` as an OpenRaster archive and return a
        `OraContainer` over it, enforcing this class's own guarantees (size,
        ZIP well-formedness, safe/unique member names, allowed compression,
        declared-size limits) before any member is decompressed. `mode`
        controls exactly one thing -- see this module's own docstring for the
        precise, narrow scope of what `ReadMode.TOLERANT` excuses."""
        if len(payload) > limits.max_input_bytes:
            raise OraLimitError(
                f"input is {len(payload)} bytes, over the limit of "
                f"{limits.max_input_bytes}"
            )

        try:
            archive = zipfile.ZipFile(io.BytesIO(payload))
        except zipfile.BadZipFile as exc:
            raise OraArchiveError(
                f"input is not a readable ZIP archive: {exc}"
            ) from exc
        except UnicodeDecodeError as exc:
            # A member declares the UTF-8 filename flag but its name bytes are
            # not valid UTF-8; zipfile decodes eagerly while reading the
            # central directory, so this surfaces here rather than per-member.
            raise OraArchiveError(
                f"archive contains a malformed Unicode member name: {exc}"
            ) from exc

        infos = archive.infolist()
        _check_limits(infos, limits)

        seen: set[str] = set()
        member_names: list[str] = []
        for info in infos:
            name = info.filename
            _reject_unsafe_name(name)

            if name in seen:
                # Two members with one name: which one a reader sees depends on
                # whether it walks the central directory or the local headers.
                # Attackers rely on that disagreement, so the archive is refused
                # rather than resolved one way or the other.
                raise OraArchiveError(f"archive contains duplicate member name {name!r}")
            seen.add(name)

            if info.is_dir():
                continue

            if info.compress_type not in ALLOWED_COMPRESSION:
                raise OraArchiveError(
                    f"member {name!r} uses compression "
                    f"{_describe_compression(info.compress_type)}; OpenRaster "
                    "permits only STORED and DEFLATED"
                )

            member_names.append(name)

        mimetype, recovery = _check_mimetype(archive, infos, mode=mode)

        if STACK_MEMBER not in seen:
            raise OraArchiveError(f"archive has no required {STACK_MEMBER} member")

        return cls(
            mimetype=mimetype,
            names=tuple(member_names),
            _archive=archive,
            _limits=limits,
            recovery_actions=recovery,
        )

    def read(self, name: str) -> bytes:
        """Return one member's bytes.

        Names are matched exactly: "Member names ... are case-sensitive", so
        `data/Layer.png` and `data/layer.png` are different members and a
        case-folding lookup would silently collapse them.

        Decompression itself is bounded by this container's own
        `max_decompressed_bytes` limit (the same one `from_bytes` validated
        declared sizes against), refusing a member whose real content
        exceeds it -- not only one whose declared metadata says so.
        """
        if name not in self.names:
            raise OraArchiveError(f"archive has no member named {name!r}")
        return _bounded_read(self._archive, name, limit=self._limits.max_decompressed_bytes)


__all__ = [
    "ALLOWED_COMPRESSION",
    "MIMETYPE_MEMBER",
    "OPENRASTER_MEDIA_TYPE",
    "STACK_MEMBER",
    "OraContainer",
]
