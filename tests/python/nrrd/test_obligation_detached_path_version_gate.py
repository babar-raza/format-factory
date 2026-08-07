"""NRRD-PAYLOAD-001 -- pre-NRRD0004 vs NRRD0004+ detached-path resolution
rules.

MUST (SAL-NRRD-OBL-4CAFF21A47F62F19; Teem NRRD Format Specification
Section 3): "Detached-path interpretation changes at NRRD0004: older
headers use a leading ./ to mark header-relative files, while NRRD0004 and
newer treat any path without a leading slash as relative to the detached
header."

The pinned spec source (src-nrrd-001.bin) states this precisely: "as of
NRRD0004, the signifier of a header-relative file changed from the
presence (at the beginning of the filename) of './', to the absence of
'/'... With this change, it becomes impossible for a header to refer to
the data file relative to the current working directory of the reader."

Before this slice: reader.py's _safe_detached_payload (and lazy.py's
_resolve_detached_path, its lazy-access counterpart) applied the
NRRD0004+ rule unconditionally regardless of declared version -- a
pre-NRRD0004 header without the explicit './' prefix was silently
resolved as header-relative, when the spec defines that case as
cwd-relative (a different, unconfined resolution base this reader does
not implement, since no caller-supplied resolver policy exists to opt
into it -- see SAL-NRRD-OBL-09CDF5A28C011CD7, which stays honestly
partial for that specific remaining gap).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from format_factory.nrrd import load
from format_factory.nrrd.errors import NrrdParseError


def _header(version: int, data_file: str) -> bytes:
    return (
        f"NRRD000{version}\n"
        "type: uint8\ndimension: 1\nsizes: 2\nencoding: raw\n"
        f"data file: {data_file}\n\n"
    ).encode()


@pytest.mark.parametrize("version", [1, 2, 3])
def test_pre_nrrd0004_resolves_a_leading_dot_slash_name_as_header_relative(
    version: int, tmp_path: Path
) -> None:
    (tmp_path / "data.raw").write_bytes(b"\x01\x02")
    header_path = tmp_path / "h.nhdr"
    header_path.write_bytes(_header(version, "./data.raw"))

    assert load(header_path).array == [1, 2]


@pytest.mark.parametrize("version", [1, 2, 3])
def test_pre_nrrd0004_refuses_a_bare_relative_name_without_dot_slash(
    version: int, tmp_path: Path
) -> None:
    """Strict spec semantics say this is cwd-relative; this reader
    deliberately does not support unconfined cwd-relative resolution
    without an explicit caller opt-in, so it refuses rather than silently
    resolving it against the header's directory (the NRRD0004+ rule)."""
    (tmp_path / "data.raw").write_bytes(b"\x01\x02")
    header_path = tmp_path / "h.nhdr"
    header_path.write_bytes(_header(version, "data.raw"))

    with pytest.raises(NrrdParseError, match="pre-NRRD0004"):
        load(header_path)


@pytest.mark.parametrize("version", [4, 5])
def test_nrrd0004_and_newer_resolve_a_bare_relative_name_as_header_relative(
    version: int, tmp_path: Path
) -> None:
    (tmp_path / "data.raw").write_bytes(b"\x01\x02")
    header_path = tmp_path / "h.nhdr"
    header_path.write_bytes(_header(version, "data.raw"))

    assert load(header_path).array == [1, 2]


@pytest.mark.parametrize("version", [4, 5])
def test_nrrd0004_and_newer_still_accept_a_leading_dot_slash_name(
    version: int, tmp_path: Path
) -> None:
    """The explicit './' prefix is no longer required at NRRD0004+, but it
    is still a valid relative path component and must not be rejected."""
    (tmp_path / "data.raw").write_bytes(b"\x01\x02")
    header_path = tmp_path / "h.nhdr"
    header_path.write_bytes(_header(version, "./data.raw"))

    assert load(header_path).array == [1, 2]


def test_the_version_gate_still_enforces_directory_confinement(tmp_path: Path) -> None:
    """The version-gated './' handling is a naming-convention distinction
    only -- it must not weaken the existing escape-the-header-directory
    protection for either era."""
    header_path = tmp_path / "h.nhdr"
    header_path.write_bytes(_header(3, "./../escape.raw"))

    with pytest.raises(NrrdParseError):
        load(header_path)
