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
import struct
import tracemalloc
import zipfile
import zlib

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


@pytest.mark.parametrize(
    ("fixture_name", "expected_first_member"),
    [
        ("bigimage.ora", "data/"),
        ("fill_outlines.ora", "Thumbnails/"),
    ],
)
def test_mimetype_first_rule_correctly_rejects_a_real_independent_producers_archive(
    fixture_name: str, expected_first_member: str
) -> None:
    """`test_mimetype_must_be_the_first_member` above proves this rule against
    a hand-crafted malformed archive. This proves the same rule firing
    against a real one: these two files are unmodified vendored fixtures
    from MyPaint (github.com/mypaint/mypaint, tests/), a real, independent,
    widely-used OpenRaster-producing application -- not a synthetic
    violation this project invented to exercise its own check.

    Verified directly via `zipfile.ZipFile.namelist()` (the true central
    -directory order any real reader sees), not `unzip -l`'s display order,
    which does not necessarily match it -- see
    fixtures/third-party-gpl-mypaint/PROVENANCE.md for the full finding.
    Both files were acquired to serve as a render/composite comparison
    corpus (ORA-RENDER-001/ORA-COMPOSITE-001's own "independent producer"
    release gate); neither one is spec-conformant enough to reach rendering
    at all, which is itself the honest, disclosed result of that effort.
    """
    path = f"tests/python/ora/fixtures/third-party-gpl-mypaint/{fixture_name}"
    with open(path, "rb") as handle:
        payload = handle.read()

    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        assert archive.namelist()[0] == expected_first_member

    with pytest.raises(OraArchiveError) as raised:
        OraContainer.from_bytes(payload)

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


def _archive_with_raw_member_name(name_bytes: bytes, content: bytes) -> bytes:
    """Build a minimal ZIP by hand so the member name can be arbitrary bytes --
    zipfile's own writer API only ever accepts a valid Python str, so it can
    never produce a name that fails UTF-8 decoding."""
    flags = 0x800  # UTF-8 filename flag
    crc = zlib.crc32(content) & 0xFFFFFFFF
    local = (
        struct.pack(
            "<IHHHHHIIIHH",
            0x04034B50, 20, flags, 0, 0, 0, crc,
            len(content), len(content), len(name_bytes), 0,
        )
        + name_bytes
        + content
    )
    central = (
        struct.pack(
            "<IHHHHHHIIIHHHHHII",
            0x02014B50, 20, 20, flags, 0, 0, 0, crc,
            len(content), len(content), len(name_bytes), 0, 0, 0, 0, 0, 0,
        )
        + name_bytes
    )
    eocd = struct.pack("<IHHHHIIH", 0x06054B50, 0, 0, 1, 1, len(central), len(local), 0)
    return local + central + eocd


def test_malformed_unicode_member_names_are_rejected() -> None:
    """A member declaring the UTF-8 filename flag but carrying bytes that are
    not valid UTF-8 must be refused with a diagnostic, not leak a raw
    UnicodeDecodeError past the container boundary."""
    payload = _archive_with_raw_member_name(b"\xff\xfeinvalid.png", b"x")

    with pytest.raises(OraArchiveError) as raised:
        OraContainer.from_bytes(payload)

    assert "unicode" in str(raised.value).lower()


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


# ── read() bounds real decompressed output, not only declared metadata ─────


def _archive_with_a_lied_declared_size(
    *, real_payload: bytes, forged_size: int, forged_crc: int
) -> bytes:
    """A structurally valid, normally-written .ora archive whose one data
    member's declared uncompressed size AND crc32 (both the local file
    header and the central directory record carry each) are patched after
    the fact -- the real compressed bytes are left exactly as `zipfile`
    wrote them for `real_payload`, so this is not a corrupt or malformed
    archive, only one whose declared metadata lies. `_check_limits` only
    ever inspects that declared metadata, never the real content, so this
    reproduces exactly what an adversary controls: `file_size`/`CRC-32` are
    their own header fields to write however they like, independent of what
    the member's real compressed stream actually decompresses to. Forging
    the crc to match only the first `forged_size` bytes of the real payload
    (rather than leaving it correct for the full payload) means `read()`
    does not merely fail late with a CRC mismatch -- it succeeds, returning
    exactly the declared `forged_size` bytes, silently: the only outward
    difference between an honest small member and this one is how much
    memory decompressing it costs.
    """
    raw = bytearray(build_archive(members={"data/big.png": real_payload}))
    target = b"data/big.png"

    def _patch(
        signature: bytes, crc_offset: int, size_offset: int, namelen_offset: int, name_offset: int
    ) -> None:
        index = 0
        while True:
            index = raw.find(signature, index)
            if index == -1:
                raise AssertionError(f"{signature!r} record for {target!r} not found")
            name_len = struct.unpack(
                "<H", raw[index + namelen_offset : index + namelen_offset + 2]
            )[0]
            candidate = bytes(raw[index + name_offset : index + name_offset + name_len])
            if candidate == target:
                struct.pack_into("<I", raw, index + crc_offset, forged_crc)
                struct.pack_into("<I", raw, index + size_offset, forged_size)
                return
            index += 1

    # Local file header: sig(4) verneeded(2) flags(2) method(2) time(2)
    # date(2) crc(4) compsize(4) uncompsize(4) namelen(2) extralen(2) name.
    _patch(b"PK\x03\x04", crc_offset=14, size_offset=22, namelen_offset=26, name_offset=30)
    # Central directory record: sig(4) vermadeby(2) verneeded(2) flags(2)
    # method(2) time(2) date(2) crc(4) compsize(4) uncompsize(4) namelen(2)
    # extralen(2) commentlen(2) disknum(2) intattr(2) extattr(4) lhoffset(4) name.
    _patch(b"PK\x01\x02", crc_offset=16, size_offset=24, namelen_offset=28, name_offset=46)

    return bytes(raw)


def test_a_lied_declared_size_still_costs_flat_memory_not_the_real_payload_size() -> None:
    """FF6-EVENT-000487: this obligation's own required_tests wording
    ("flat-memory checks") taken literally, with a direct memory
    measurement rather than an architectural read-call-count proof.
    `_check_limits` (proven above) refuses an archive whose DECLARED sizes
    exceed the budget before decompressing anything -- but declared size is
    exactly the field an adversary controls. A member whose declared size
    (and matching crc) describe only a small prefix of a much larger real
    payload sails through `_check_limits` untouched and, both before and
    after this fix, `read()` returns that same small, correct-looking
    prefix -- but before this fix, producing it required decompressing the
    ENTIRE real payload internally first (proven directly: peak memory
    scaled with the real payload's own size, not the declared one). After
    this fix, `read()` decompresses in bounded chunks, so peak memory stays
    close to one chunk's worth regardless of how large the real payload
    actually is -- proven by using a real payload dramatically larger than
    any bound this test itself asserts."""
    real_payload = b"\0" * (10 * 1024 * 1024)  # 10MB: compresses to a few KB
    forged_size = 100
    forged_crc = zlib.crc32(real_payload[:forged_size]) & 0xFFFFFFFF
    payload = _archive_with_a_lied_declared_size(
        real_payload=real_payload, forged_size=forged_size, forged_crc=forged_crc
    )
    limits = ResourceLimits(max_decompressed_bytes=1024)

    container = OraContainer.from_bytes(payload, limits=limits)  # the lie sails through

    tracemalloc.start()
    try:
        result = container.read("data/big.png")
        current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    assert result == real_payload[:forged_size]
    # The real payload is 10MB; a naive full decompression peaks in the tens
    # of MB (proven directly against the unfixed code path: see this
    # obligation's own execution evidence). 5MB is comfortably above one
    # bounded chunk's own overhead and comfortably below "decompressed the
    # whole real payload" -- the only threshold this test needs to prove.
    assert peak < 5 * 1024 * 1024, f"peak traced memory was {peak} bytes, not flat"


def test_reading_a_member_within_its_declared_and_real_size_still_succeeds() -> None:
    """The control for the flat-memory test above: a member whose declared
    size is honest and within budget still reads correctly -- the bounded
    reader is not simply refusing or truncating every read."""
    payload = build_archive(members={"data/small.png": b"x" * 4096})
    limits = ResourceLimits(max_decompressed_bytes=1_000_000)

    container = OraContainer.from_bytes(payload, limits=limits)

    assert container.read("data/small.png") == b"x" * 4096
