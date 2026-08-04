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
lazy or permissive mode -- a half-validated archive is the state in which
callers write the bugs this module exists to prevent.
"""

from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass, field
from pathlib import PurePosixPath

from format_factory.core import DEFAULT_LIMITS, ResourceLimits

from ..errors import OraArchiveError, OraLimitError

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


def _check_mimetype(archive: zipfile.ZipFile, infos: list[zipfile.ZipInfo]) -> str:
    """Enforce the sentinel's position, compression method and exact bytes."""
    if not infos:
        raise OraArchiveError("archive is empty; the mimetype member is required")

    first = infos[0]
    if first.filename != MIMETYPE_MEMBER:
        present = any(info.filename == MIMETYPE_MEMBER for info in infos)
        if present:
            raise OraArchiveError(
                f"the mimetype member must be the first archive member, but "
                f"{first.filename!r} is first"
            )
        raise OraArchiveError("archive has no mimetype member")

    if first.compress_type != zipfile.ZIP_STORED:
        raise OraArchiveError(
            "the mimetype member must be STORED without compression, but is "
            f"{_describe_compression(first.compress_type)}"
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

    return OPENRASTER_MEDIA_TYPE.decode("ascii")


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
    validation.
    """

    mimetype: str
    names: tuple[str, ...]
    _archive: zipfile.ZipFile = field(repr=False, compare=False)

    @classmethod
    def from_bytes(
        cls, payload: bytes, *, limits: ResourceLimits = DEFAULT_LIMITS
    ) -> "OraContainer":
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

        mimetype = _check_mimetype(archive, infos)

        if STACK_MEMBER not in seen:
            raise OraArchiveError(f"archive has no required {STACK_MEMBER} member")

        return cls(mimetype=mimetype, names=tuple(member_names), _archive=archive)

    def read(self, name: str) -> bytes:
        """Return one member's bytes.

        Names are matched exactly: "Member names ... are case-sensitive", so
        `data/Layer.png` and `data/layer.png` are different members and a
        case-folding lookup would silently collapse them.
        """
        if name not in self.names:
            raise OraArchiveError(f"archive has no member named {name!r}")
        return self._archive.read(name)


__all__ = [
    "ALLOWED_COMPRESSION",
    "MIMETYPE_MEMBER",
    "OPENRASTER_MEDIA_TYPE",
    "STACK_MEMBER",
    "OraContainer",
]
