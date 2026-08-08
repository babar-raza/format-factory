"""NRRD-PAYLOAD-001 -- explicit, caller-supplied cwd-relative resolver policy.

MUST (SAL-NRRD-OBL-09CDF5A28C011CD7): "Support attached and single-file
detached payloads in every profile; apply profile-correct header-relative
path semantics, skip fields, payload bounds, and a secure resolver
policy."

The pinned spec source (src-nrrd-001.bin) confirms word-for-word: "as of
NRRD0004, the signifier of a header-relative file changed from the
presence (at the beginning of the filename) of './', to the absence of
'/'." Before this slice, a pre-NRRD0004 bare-relative detached data file
name (no leading './') was unconditionally refused -- correct as a safe
default (the spec-defined resolution base, the reader's own current
working directory, has no natural confinement boundary), but the
obligation's own missing_behavior named the gap precisely: "an explicit
opt-in policy parameter would be needed to support it safely, and does
not exist yet."

This module proves that parameter now exists (`cwd_relative_base=` on
`load()`/`loads()`/`open_lazy_payload()`), is opt-in only (the refusal
remains the default), and does not weaken the existing traversal-safety
guarantees -- the same absolute-path and directory-escape checks that
already apply to header-relative resolution apply, unchanged, relative to
the caller-supplied base instead.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from format_factory.nrrd import PayloadAccessMode, load, loads, open_lazy_payload
from format_factory.nrrd.errors import NrrdParseError


def _header(data_file: str, *, version: int = 2, encoding: str = "raw") -> bytes:
    return (
        f"NRRD000{version}\n"
        f"type: uint8\ndimension: 1\nsizes: 4\nencoding: {encoding}\n"
        f"data file: {data_file}\n\n"
    ).encode()


def test_bare_relative_pre_nrrd0004_still_refuses_without_the_opt_in(tmp_path: Path) -> None:
    (tmp_path / "data.raw").write_bytes(b"\x01\x02\x03\x04")
    header_path = tmp_path / "h.nhdr"
    header_path.write_bytes(_header("data.raw"))

    with pytest.raises(NrrdParseError, match="cwd_relative_base"):
        load(header_path)


def test_load_resolves_against_an_explicit_cwd_relative_base(tmp_path: Path) -> None:
    header_dir = tmp_path / "headers"
    header_dir.mkdir()
    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    (cwd_dir / "data.raw").write_bytes(b"\x05\x06\x07\x08")
    header_path = header_dir / "h.nhdr"
    header_path.write_bytes(_header("data.raw"))

    document = load(header_path, cwd_relative_base=cwd_dir)

    assert document.array == [5, 6, 7, 8]


def test_loads_exposes_the_same_parameter_though_bytes_input_has_no_detached_payload(
    tmp_path: Path,
) -> None:
    """`loads()` reads bytes with no filesystem source, so a detached
    payload can never resolve regardless of `cwd_relative_base` -- this is
    pre-existing, unrelated behavior ("detached data requires a filesystem
    header source"), confirmed here so the parameter's presence on
    `loads()` is not mistaken for a claim it changes that."""
    (tmp_path / "data.raw").write_bytes(b"\x09\x0a\x0b\x0c")
    header_bytes = _header("data.raw")

    with pytest.raises(NrrdParseError, match="filesystem header source"):
        loads(header_bytes, cwd_relative_base=tmp_path)


def test_open_lazy_payload_resolves_against_the_opt_in_for_memory_mapped_access(
    tmp_path: Path,
) -> None:
    header_dir = tmp_path / "headers"
    header_dir.mkdir()
    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    (cwd_dir / "data.raw").write_bytes(b"\x01\x02\x03\x04")
    header_path = header_dir / "h.nhdr"
    header_path.write_bytes(_header("data.raw"))

    header, payload = open_lazy_payload(header_path, cwd_relative_base=cwd_dir)
    try:
        assert header.access.mode is PayloadAccessMode.MEMORY_MAPPED
        region = payload.region(0, 4)
        try:
            assert bytes(region) == b"\x01\x02\x03\x04"
        finally:
            region.release()
    finally:
        payload.close()


def test_open_lazy_payload_resolves_against_the_opt_in_for_streaming_decode(
    tmp_path: Path,
) -> None:
    import gzip

    header_dir = tmp_path / "headers"
    header_dir.mkdir()
    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    with gzip.open(cwd_dir / "data.raw.gz", "wb") as fh:
        fh.write(b"\x0d\x0e\x0f\x10")
    header_path = header_dir / "h.nhdr"
    header_path.write_bytes(_header("data.raw.gz", encoding="gzip"))

    header, payload = open_lazy_payload(header_path, cwd_relative_base=cwd_dir)
    try:
        assert header.access.mode is PayloadAccessMode.STREAMING_DECODE
        assert payload.read_stream(4) == b"\x0d\x0e\x0f\x10"
    finally:
        payload.close()


def test_the_opt_in_still_refuses_a_path_that_escapes_the_supplied_base(
    tmp_path: Path,
) -> None:
    header_dir = tmp_path / "headers"
    header_dir.mkdir()
    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    (outside_dir / "secret.raw").write_bytes(b"\x01\x02\x03\x04")
    header_path = header_dir / "h.nhdr"
    header_path.write_bytes(_header("../outside/secret.raw"))

    with pytest.raises(NrrdParseError, match="unsafe detached data path"):
        load(header_path, cwd_relative_base=cwd_dir)


def test_the_opt_in_still_refuses_an_absolute_path(tmp_path: Path) -> None:
    header_dir = tmp_path / "headers"
    header_dir.mkdir()
    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    absolute = (tmp_path / "elsewhere.raw").resolve()
    absolute.write_bytes(b"\x01\x02\x03\x04")
    header_path = header_dir / "h.nhdr"
    header_path.write_bytes(_header(str(absolute)))

    with pytest.raises(NrrdParseError, match="unsafe detached data path"):
        load(header_path, cwd_relative_base=cwd_dir)


def test_the_opt_in_does_not_affect_header_relative_dot_slash_names(tmp_path: Path) -> None:
    """`cwd_relative_base` only changes resolution for the bare-relative
    case; an explicit './' name still resolves against the header's own
    directory, exactly as it does with no opt-in supplied at all."""
    header_dir = tmp_path / "headers"
    header_dir.mkdir()
    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    (header_dir / "data.raw").write_bytes(b"\xaa\xbb\xcc\xdd")
    (cwd_dir / "data.raw").write_bytes(b"\x01\x01\x01\x01")
    header_path = header_dir / "h.nhdr"
    header_path.write_bytes(_header("./data.raw"))

    document = load(header_path, cwd_relative_base=cwd_dir)

    assert document.array == [0xAA, 0xBB, 0xCC, 0xDD]


def test_the_opt_in_is_unused_at_nrrd0004_and_newer(tmp_path: Path) -> None:
    """NRRD0004+ has no cwd-relative case at all -- a bare relative name is
    already header-relative -- so supplying cwd_relative_base changes
    nothing; the header's own directory is still used."""
    header_dir = tmp_path / "headers"
    header_dir.mkdir()
    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    (header_dir / "data.raw").write_bytes(b"\x01\x02\x03\x04")
    (cwd_dir / "data.raw").write_bytes(b"\x09\x09\x09\x09")
    header_path = header_dir / "h.nhdr"
    header_path.write_bytes(_header("data.raw", version=4))

    document = load(header_path, cwd_relative_base=cwd_dir)

    assert document.array == [1, 2, 3, 4]
