"""ORA-CONTAINER-001 and ORA-MIMETYPE-001 — the archive wrapper.

Every other OpenRaster obligation reads through this layer, so it is the first
thing built and the first thing that has to be hostile to its input. An .ora
file is a ZIP supplied by a stranger; the container is where traversal,
duplicate members, zip bombs and unsupported compression have to die, before any
payload is touched.

The assertions come from the contract's normative rules, quoted where they bind:

  "The first archive member must be named mimetype, must be STORED without
   compression, and must contain exactly image/openraster without whitespace or
   a trailing newline."
  "Member names in an OpenRaster ZIP archive are case-sensitive and must be
   UTF-8 encoded..."
  "OpenRaster ZIP members may use only the DEFLATED and STORED compression
   methods."
  "The required stack.xml archive member is a UTF-8 encoded XML document..."
"""

from __future__ import annotations

import io
import zipfile

import pytest

from format_factory.core import ResourceLimits
from format_factory.ora import OraArchiveError, OraContainer, OraLimitError

MIMETYPE = b"image/openraster"
MINIMAL_STACK = (
    b'<?xml version="1.0" encoding="UTF-8"?>\n'
    b'<image w="1" h="1"><stack><layer name="l" src="data/l.png"/></stack></image>'
)


def build_archive(
    *,
    mimetype: bytes | None = MIMETYPE,
    mimetype_first: bool = True,
    mimetype_compressed: bool = False,
    members: dict[str, bytes] | None = None,
    stack: bytes | None = MINIMAL_STACK,
) -> bytes:
    """Compose an .ora archive, including deliberately malformed ones."""
    buffer = io.BytesIO()
    entries: dict[str, bytes] = {}
    if stack is not None:
        entries["stack.xml"] = stack
    if members:
        entries.update(members)

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        def write_mimetype() -> None:
            if mimetype is None:
                return
            info = zipfile.ZipInfo("mimetype")
            info.compress_type = (
                zipfile.ZIP_DEFLATED if mimetype_compressed else zipfile.ZIP_STORED
            )
            archive.writestr(info, mimetype)

        if mimetype_first:
            write_mimetype()
        for name, payload in entries.items():
            archive.writestr(name, payload)
        if not mimetype_first:
            write_mimetype()

    return buffer.getvalue()


# ── ORA-MIMETYPE-001: the sentinel ─────────────────────────────────────────


def test_a_well_formed_archive_opens() -> None:
    container = OraContainer.from_bytes(build_archive())

    assert container.mimetype == "image/openraster"
    assert "stack.xml" in container.names


def test_missing_mimetype_is_rejected() -> None:
    with pytest.raises(OraArchiveError) as raised:
        OraContainer.from_bytes(build_archive(mimetype=None))

    assert "mimetype" in str(raised.value)


def test_mimetype_must_be_the_first_member() -> None:
    """Position is normative: a reader must identify the format from the first
    bytes of the archive without scanning the central directory."""
    with pytest.raises(OraArchiveError) as raised:
        OraContainer.from_bytes(build_archive(mimetype_first=False))

    assert "first" in str(raised.value).lower()


def test_mimetype_must_be_stored_uncompressed() -> None:
    with pytest.raises(OraArchiveError) as raised:
        OraContainer.from_bytes(build_archive(mimetype_compressed=True))

    assert "stored" in str(raised.value).lower()


@pytest.mark.parametrize(
    "payload",
    [
        MIMETYPE + b"\n",
        MIMETYPE + b"\r\n",
        MIMETYPE + b" ",
        b" " + MIMETYPE,
        MIMETYPE + b"\t",
        b"image/openraster ",
    ],
    ids=["newline", "crlf", "trailing-space", "leading-space", "tab", "trailing-ws"],
)
def test_mimetype_rejects_any_surrounding_whitespace(payload: bytes) -> None:
    """"exactly image/openraster without whitespace or a trailing newline" --
    a reader that strips before comparing would accept all of these."""
    with pytest.raises(OraArchiveError):
        OraContainer.from_bytes(build_archive(mimetype=payload))


@pytest.mark.parametrize(
    "payload",
    [b"image/png", b"application/zip", b"", b"IMAGE/OPENRASTER", b"image/openraster2"],
)
def test_mimetype_rejects_wrong_values(payload: bytes) -> None:
    with pytest.raises(OraArchiveError):
        OraContainer.from_bytes(build_archive(mimetype=payload))


# ── ORA-CONTAINER-001: the wrapper and member directory ────────────────────


def test_a_non_zip_input_is_rejected() -> None:
    with pytest.raises(OraArchiveError):
        OraContainer.from_bytes(b"this is not a zip archive at all")


def test_a_truncated_archive_is_rejected() -> None:
    whole = build_archive()

    with pytest.raises(OraArchiveError):
        OraContainer.from_bytes(whole[: len(whole) // 2])


def test_stack_xml_is_required() -> None:
    with pytest.raises(OraArchiveError) as raised:
        OraContainer.from_bytes(build_archive(stack=None))

    assert "stack.xml" in str(raised.value)


@pytest.mark.parametrize(
    "hostile_name",
    [
        "../escape.png",
        "data/../../escape.png",
        "/absolute.png",
        "C:/windows/system32/evil.png",
        "data/./../../escape.png",
        "..",
    ],
    ids=["parent", "nested-parent", "absolute", "drive", "dot-parent", "bare-parent"],
)
def test_traversal_and_absolute_member_names_are_rejected(hostile_name: str) -> None:
    """Member names become file paths the moment anyone extracts. Rejecting at
    open means no caller can be the one who gets this wrong."""
    with pytest.raises(OraArchiveError) as raised:
        OraContainer.from_bytes(build_archive(members={hostile_name: b"x"}))

    assert "path" in str(raised.value).lower() or "name" in str(raised.value).lower()


def test_backslash_separators_are_rejected() -> None:
    """A backslash is a legal ZIP name character and a separator on Windows, so
    "data\\..\\..\\evil" escapes on one platform and not another."""
    with pytest.raises(OraArchiveError):
        OraContainer.from_bytes(build_archive(members={"data\\..\\..\\evil.png": b"x"}))


def test_duplicate_member_names_are_rejected() -> None:
    """Two members with one name: which one a reader sees depends on whether it
    walks the central directory or the local headers. Attackers rely on the
    disagreement, so the archive is refused instead of resolved."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        archive.writestr(info, MIMETYPE)
        archive.writestr("stack.xml", MINIMAL_STACK)
        archive.writestr("data/l.png", b"first")
        archive.writestr("data/l.png", b"second")

    with pytest.raises(OraArchiveError) as raised:
        OraContainer.from_bytes(buffer.getvalue())

    assert "duplicate" in str(raised.value).lower()


def test_unsupported_compression_method_is_rejected() -> None:
    """"OpenRaster ZIP members may use only the DEFLATED and STORED compression
    methods." BZIP2 is a valid ZIP method and an invalid OpenRaster one."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        archive.writestr(info, MIMETYPE)
        archive.writestr("stack.xml", MINIMAL_STACK)
        bzipped = zipfile.ZipInfo("data/l.png")
        bzipped.compress_type = zipfile.ZIP_BZIP2
        archive.writestr(bzipped, b"payload" * 100)

    with pytest.raises(OraArchiveError) as raised:
        OraContainer.from_bytes(buffer.getvalue())

    assert "compression" in str(raised.value).lower()


def test_deflated_and_stored_members_are_both_accepted() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        archive.writestr(info, MIMETYPE)
        archive.writestr("stack.xml", MINIMAL_STACK)
        stored = zipfile.ZipInfo("data/stored.png")
        stored.compress_type = zipfile.ZIP_STORED
        archive.writestr(stored, b"stored payload")
        deflated = zipfile.ZipInfo("data/deflated.png")
        deflated.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(deflated, b"deflated payload")

    container = OraContainer.from_bytes(buffer.getvalue())

    assert container.read("data/stored.png") == b"stored payload"
    assert container.read("data/deflated.png") == b"deflated payload"


def test_member_names_are_case_sensitive() -> None:
    """"Member names ... are case-sensitive." Data.png and data.png are two
    members, and a case-folding reader would silently collapse them."""
    container = OraContainer.from_bytes(
        build_archive(members={"data/Layer.png": b"upper", "data/layer.png": b"lower"})
    )

    assert container.read("data/Layer.png") == b"upper"
    assert container.read("data/layer.png") == b"lower"


def test_non_ascii_member_names_round_trip() -> None:
    container = OraContainer.from_bytes(build_archive(members={"data/ébène.png": b"x"}))

    assert "data/ébène.png" in container.names


def test_reading_an_absent_member_raises() -> None:
    container = OraContainer.from_bytes(build_archive())

    with pytest.raises(OraArchiveError):
        container.read("data/nothing.png")


def test_names_excludes_directory_entries() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        archive.writestr(info, MIMETYPE)
        archive.writestr("data/", b"")
        archive.writestr("stack.xml", MINIMAL_STACK)

    container = OraContainer.from_bytes(buffer.getvalue())

    assert "data/" not in container.names


# ── Resource bounds: the archive is untrusted and may be adversarial ───────


def test_too_many_members_is_a_limit_error() -> None:
    limits = ResourceLimits(max_entries=8)
    members = {f"data/l{index}.png": b"x" for index in range(20)}

    with pytest.raises(OraLimitError) as raised:
        OraContainer.from_bytes(build_archive(members=members), limits=limits)

    assert "entries" in str(raised.value).lower() or "members" in str(raised.value).lower()


def test_total_declared_size_over_the_limit_is_refused_before_reading() -> None:
    """The check reads the central directory, not the payload -- a bomb must be
    refused without being decompressed."""
    limits = ResourceLimits(max_decompressed_bytes=1024)
    members = {"data/big.png": b"A" * 100_000}

    with pytest.raises(OraLimitError):
        OraContainer.from_bytes(build_archive(members=members), limits=limits)


def test_an_extreme_compression_ratio_is_refused() -> None:
    """A classic zip bomb: tiny compressed, enormous declared."""
    limits = ResourceLimits(max_compression_ratio=10.0, max_decompressed_bytes=10**9)
    members = {"data/bomb.png": b"\0" * 5_000_000}

    with pytest.raises(OraLimitError) as raised:
        OraContainer.from_bytes(build_archive(members=members), limits=limits)

    assert "ratio" in str(raised.value).lower()


def test_a_benign_archive_passes_the_same_limits() -> None:
    """The control for the three tests above: if these limits rejected ordinary
    archives too, the rejections would prove nothing about hostility."""
    limits = ResourceLimits(
        max_entries=8, max_decompressed_bytes=1024, max_compression_ratio=10.0
    )

    container = OraContainer.from_bytes(
        build_archive(members={"data/l.png": b"small payload"}), limits=limits
    )

    assert container.mimetype == "image/openraster"


# ── The container is passive data ──────────────────────────────────────────


def test_opening_an_archive_never_executes_member_content() -> None:
    hostile = b"import os; os.system('echo pwned')"
    container = OraContainer.from_bytes(
        build_archive(members={"data/l.png": hostile, "evil.py": hostile})
    )

    assert container.read("evil.py") == hostile
