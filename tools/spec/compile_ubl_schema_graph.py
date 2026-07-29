"""Compile a secure, deterministic UBL 2.3 package and root census.

This first UBL schema-graph stage establishes the authority package and
91-document-root denominator.  It intentionally does not claim that the
reachable type graph, obligation denominator, generated product source, or
production certification is complete.

generated_by: codex
visibility: internal
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import stat
import sys
import tempfile
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
from zipfile import (
    BadZipFile,
    ZIP_DEFLATED,
    ZIP_STORED,
    ZipFile,
    ZipInfo,
)

import yaml

from tools.spec.ubl_schema_graph import (
    GraphLimits,
    UblSchemaGraphError,
    compile_reachable_schema_graph,
)


XSD_NAMESPACE = "http://www.w3.org/2001/XMLSchema"
XSD = f"{{{XSD_NAMESPACE}}}"
DEFAULT_PACKAGE_SHA256 = (
    "623bef8310db4d979ff28000a96bcc56dbcdda4f6206cf094c0aa79b75817970"
)
DEFAULT_PACKAGE_PATH = Path(
    ".local/format-contracts/acquired/ubl/src-ubl-002.bin"
)
DEFAULT_OUTPUT_PATH = Path("reports/ff6/ubl-package-root-census.yaml")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_MAINDOC = re.compile(r"^xsd/maindoc/UBL-(?P<name>[A-Za-z0-9]+)-2\.3\.xsd$")
_FORBIDDEN_XML_DECLARATIONS = re.compile(br"<!\s*(?:DOCTYPE|ENTITY)\b", re.I)
_ALLOWED_COMPRESSION = frozenset({ZIP_STORED, ZIP_DEFLATED})


class UblCensusError(ValueError):
    """Raised when the authority package cannot support a safe exact census."""


class CensusLimits:
    """Resource limits for untrusted ZIP and XSD authority inputs."""

    __slots__ = (
        "max_archive_bytes",
        "max_members",
        "max_member_uncompressed_bytes",
        "max_total_uncompressed_bytes",
        "max_compression_ratio",
        "max_xml_depth",
        "max_xml_elements",
    )

    def __init__(
        self,
        *,
        max_archive_bytes: int = 268_435_456,
        max_members: int = 5_000,
        max_member_uncompressed_bytes: int = 134_217_728,
        max_total_uncompressed_bytes: int = 536_870_912,
        max_compression_ratio: float = 5_000.0,
        max_xml_depth: int = 128,
        max_xml_elements: int = 250_000,
    ) -> None:
        values = {
            "max_archive_bytes": max_archive_bytes,
            "max_members": max_members,
            "max_member_uncompressed_bytes": max_member_uncompressed_bytes,
            "max_total_uncompressed_bytes": max_total_uncompressed_bytes,
            "max_compression_ratio": max_compression_ratio,
            "max_xml_depth": max_xml_depth,
            "max_xml_elements": max_xml_elements,
        }
        for name, value in values.items():
            if not isinstance(value, (int, float)) or value <= 0:
                raise UblCensusError(f"{name} must be positive")
        self.max_archive_bytes = int(max_archive_bytes)
        self.max_members = int(max_members)
        self.max_member_uncompressed_bytes = int(max_member_uncompressed_bytes)
        self.max_total_uncompressed_bytes = int(max_total_uncompressed_bytes)
        self.max_compression_ratio = float(max_compression_ratio)
        self.max_xml_depth = int(max_xml_depth)
        self.max_xml_elements = int(max_xml_elements)

    def as_dict(self) -> dict[str, int | float]:
        """Return stable public limit values."""

        return {
            "max_archive_bytes": self.max_archive_bytes,
            "max_members": self.max_members,
            "max_member_uncompressed_bytes": self.max_member_uncompressed_bytes,
            "max_total_uncompressed_bytes": self.max_total_uncompressed_bytes,
            "max_compression_ratio": self.max_compression_ratio,
            "max_xml_depth": self.max_xml_depth,
            "max_xml_elements": self.max_xml_elements,
        }


def _canonical_json_sha256(value: object) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    # Keep proof-value digests byte-compatible with tools.spec.sal_proof.
    # The trailing newline is part of that repository-wide canonical form.
    payload = (serialized + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _package_bytes(
    source: str | os.PathLike[str] | bytes | bytearray,
    *,
    limits: CensusLimits,
) -> bytes:
    if isinstance(source, (bytes, bytearray)):
        data = bytes(source)
    else:
        path = Path(source)
        try:
            size = path.stat().st_size
        except OSError as exc:
            raise UblCensusError(f"cannot stat package: {path}") from exc
        if size > limits.max_archive_bytes:
            raise UblCensusError("archive byte limit exceeded")
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise UblCensusError(f"cannot read package: {path}") from exc
    if len(data) > limits.max_archive_bytes:
        raise UblCensusError("archive byte limit exceeded")
    return data


def _safe_member_name(name: str) -> str:
    if not name or "\x00" in name or "\\" in name:
        raise UblCensusError(f"unsafe ZIP member path: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise UblCensusError(f"unsafe ZIP member path: {name!r}")
    normalized = posixpath.normpath(name)
    if normalized != name.rstrip("/") or normalized.startswith("../"):
        raise UblCensusError(f"unsafe ZIP member path: {name!r}")
    return normalized


def _is_symlink(info: ZipInfo) -> bool:
    return info.create_system == 3 and stat.S_IFMT(info.external_attr >> 16) == (
        stat.S_IFLNK
    )


def _member_role(name: str) -> tuple[str, str]:
    if _MAINDOC.fullmatch(name):
        return "MAINDOC_XSD", "NORMATIVE_SCHEMA"
    if name.startswith("xsd/common/") and name.endswith(".xsd"):
        return "COMMON_XSD", "NORMATIVE_SCHEMA"
    if name.startswith("xsdrt/") and name.endswith(".xsd"):
        return "RUNTIME_XSD", "DERIVED_SCHEMA"
    if name.startswith("xml/"):
        return "OFFICIAL_EXAMPLE", "INFORMATIVE_EXAMPLE"
    if name.startswith("cl/"):
        return "CODE_LIST_RESOURCE", "NORMATIVE_SUPPORT"
    if name.startswith("val/"):
        return "VALIDATION_RESOURCE", "NORMATIVE_SUPPORT"
    if name.startswith("mod/"):
        return "MODEL_RESOURCE", "DERIVED_MODEL"
    if name.startswith("db/"):
        return "DATA_MODEL_RESOURCE", "DERIVED_MODEL"
    if name.startswith("art/"):
        return "ARTIFACT_DOCUMENTATION", "INFORMATIVE"
    if name.startswith("cva/"):
        return "CONTEXT_VALUE_ASSOCIATION", "NORMATIVE_SUPPORT"
    if name.startswith("UBL-2.3."):
        return "STANDARD_DOCUMENT", "NORMATIVE_OR_PUBLICATION"
    return "AUXILIARY", "AUXILIARY"


def _read_members(
    archive: ZipFile,
    *,
    limits: CensusLimits,
) -> tuple[list[dict[str, Any]], dict[str, bytes]]:
    infos = archive.infolist()
    if len(infos) > limits.max_members:
        raise UblCensusError("ZIP member count limit exceeded")
    names: set[str] = set()
    total = 0
    member_rows: list[dict[str, Any]] = []
    content: dict[str, bytes] = {}
    for info in infos:
        name = _safe_member_name(info.filename)
        if name in names:
            raise UblCensusError(f"duplicate ZIP member: {name}")
        names.add(name)
        if _is_symlink(info):
            raise UblCensusError(f"symlink ZIP member is prohibited: {name}")
        if info.flag_bits & 0x1:
            raise UblCensusError(f"encrypted ZIP member is prohibited: {name}")
        if info.compress_type not in _ALLOWED_COMPRESSION:
            raise UblCensusError(f"unsupported ZIP compression for member: {name}")
        if info.is_dir():
            continue
        if info.file_size > limits.max_member_uncompressed_bytes:
            raise UblCensusError(f"member byte limit exceeded: {name}")
        total += info.file_size
        if total > limits.max_total_uncompressed_bytes:
            raise UblCensusError("total uncompressed byte limit exceeded")
        compressed = max(info.compress_size, 1)
        ratio = info.file_size / compressed
        if ratio > limits.max_compression_ratio:
            raise UblCensusError(f"compression ratio limit exceeded: {name}")
        try:
            payload = archive.read(info)
        except (BadZipFile, RuntimeError, OSError) as exc:
            raise UblCensusError(f"cannot read ZIP member: {name}") from exc
        if len(payload) != info.file_size:
            raise UblCensusError(f"truncated ZIP member: {name}")
        role, normative_status = _member_role(name)
        row = {
            "member": name,
            "size": info.file_size,
            "compressed_size": info.compress_size,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "role": role,
            "normative_status": normative_status,
        }
        member_rows.append(row)
        content[name] = payload
    member_rows.sort(key=lambda row: row["member"])
    return member_rows, content


def _parse_xsd(
    payload: bytes,
    *,
    member: str,
    limits: CensusLimits,
) -> ET.Element:
    if _FORBIDDEN_XML_DECLARATIONS.search(payload):
        raise UblCensusError(f"DOCTYPE or entity declaration prohibited: {member}")
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise UblCensusError(f"invalid XSD XML: {member}") from exc
    if root.tag != f"{XSD}schema":
        raise UblCensusError(f"member is not an XML Schema document: {member}")
    count = 0
    stack: list[tuple[ET.Element, int]] = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        count += 1
        if count > limits.max_xml_elements:
            raise UblCensusError(f"XML element limit exceeded: {member}")
        if depth > limits.max_xml_depth:
            raise UblCensusError(f"XML depth limit exceeded: {member}")
        stack.extend((child, depth + 1) for child in list(node))
    return root


def _resolve_import(
    *,
    owner_member: str,
    schema_location: str,
    members: Mapping[str, bytes],
) -> str:
    parsed = urlsplit(schema_location)
    if parsed.scheme or parsed.netloc or schema_location.startswith("/"):
        raise UblCensusError(
            f"remote import is prohibited in {owner_member}: {schema_location}"
        )
    owner_dir = posixpath.dirname(owner_member)
    resolved = posixpath.normpath(posixpath.join(owner_dir, schema_location))
    if resolved.startswith("../") or resolved not in members:
        raise UblCensusError(
            f"unresolved import in {owner_member}: {schema_location}"
        )
    return resolved


def _root_row(
    *,
    member: str,
    payload: bytes,
    members: Mapping[str, bytes],
    limits: CensusLimits,
) -> dict[str, Any]:
    match = _MAINDOC.fullmatch(member)
    if match is None:
        raise UblCensusError(f"not a UBL 2.3 maindoc schema: {member}")
    document_name = match.group("name")
    schema = _parse_xsd(payload, member=member, limits=limits)
    target_namespace = schema.get("targetNamespace")
    if not target_namespace:
        raise UblCensusError(f"root schema lacks target namespace: {member}")
    elements = schema.findall(f"{XSD}element")
    if len(elements) != 1:
        raise UblCensusError(
            f"root schema must contain exactly one global element: {member}"
        )
    root_element = elements[0]
    root_name = root_element.get("name")
    content_type = root_element.get("type")
    if not root_name or not content_type:
        raise UblCensusError(f"root element lacks name or declared type: {member}")
    if root_name != document_name:
        raise UblCensusError(
            f"root element name contradicts maindoc member: {member}"
        )
    local_type = content_type.rsplit(":", 1)[-1]
    declared_types = {
        node.get("name")
        for node in schema.findall(f"{XSD}complexType")
        if node.get("name")
    }
    if local_type not in declared_types:
        raise UblCensusError(f"root declared type is missing in {member}")
    import_rows: list[dict[str, str]] = []
    for node in schema.findall(f"{XSD}import"):
        location = node.get("schemaLocation")
        namespace = node.get("namespace")
        if not location:
            raise UblCensusError(f"schema import lacks location: {member}")
        resolved = _resolve_import(
            owner_member=member,
            schema_location=location,
            members=members,
        )
        import_rows.append(
            {
                "namespace": namespace or "",
                "schema_location": location,
                "resolved_member": resolved,
                "resolved_member_sha256": hashlib.sha256(
                    members[resolved]
                ).hexdigest(),
            }
        )
    import_rows.sort(
        key=lambda row: (
            row["namespace"],
            row["schema_location"],
            row["resolved_member"],
        )
    )
    return {
        "schema_member": member,
        "schema_member_sha256": hashlib.sha256(payload).hexdigest(),
        "target_namespace": target_namespace,
        "root_name": root_name,
        "root_qname": f"{{{target_namespace}}}{root_name}",
        "content_type": content_type,
        "content_type_local_name": local_type,
        "content_type_declared_in": member,
        "imports": import_rows,
        "import_closure_sha256": _canonical_json_sha256(import_rows),
    }


def compile_ubl_package_census(
    source: str | os.PathLike[str] | bytes | bytearray,
    *,
    expected_package_sha256: str,
    expected_root_count: int = 91,
    limits: CensusLimits | None = None,
) -> dict[str, Any]:
    """Compile and validate the UBL authority package/root denominator."""

    active_limits = limits or CensusLimits()
    if _SHA256.fullmatch(expected_package_sha256) is None:
        raise UblCensusError("expected package digest is not a SHA-256 value")
    if expected_root_count <= 0:
        raise UblCensusError("expected root count must be positive")
    package = _package_bytes(source, limits=active_limits)
    observed_package_sha256 = hashlib.sha256(package).hexdigest()
    if observed_package_sha256 != expected_package_sha256:
        raise UblCensusError(
            "package digest mismatch: "
            f"expected {expected_package_sha256}, got {observed_package_sha256}"
        )
    try:
        from io import BytesIO

        with ZipFile(BytesIO(package)) as archive:
            member_rows, members = _read_members(archive, limits=active_limits)
    except BadZipFile as exc:
        raise UblCensusError("authority package is not a valid ZIP archive") from exc

    root_members = sorted(name for name in members if _MAINDOC.fullmatch(name))
    if len(root_members) != expected_root_count:
        raise UblCensusError(
            f"expected {expected_root_count} maindoc roots, found "
            f"{len(root_members)}"
        )
    roots = [
        _root_row(
            member=member,
            payload=members[member],
            members=members,
            limits=active_limits,
        )
        for member in root_members
    ]
    qname_counts = Counter(row["root_qname"] for row in roots)
    duplicate_qnames = sorted(
        qname for qname, count in qname_counts.items() if count != 1
    )
    if duplicate_qnames:
        raise UblCensusError(
            "duplicate root QName: " + ", ".join(duplicate_qnames)
        )
    role_counts = Counter(row["role"] for row in member_rows)
    signature_members = sorted(
        row["member"]
        for row in member_rows
        if re.search(r"(?:signature|xmldsig|xades)", row["member"], re.I)
    )
    category_counts = {
        "normative_xsd_files": sum(
            1 for name in members if name.startswith("xsd/") and name.endswith(".xsd")
        ),
        "all_xsd_files": sum(1 for name in members if name.endswith(".xsd")),
        "official_examples": role_counts["OFFICIAL_EXAMPLE"],
        "code_list_resources": role_counts["CODE_LIST_RESOURCE"],
        "signature_resources": len(signature_members),
        "auxiliary_resources": role_counts["AUXILIARY"],
    }
    result: dict[str, Any] = {
        "schema": "ff6/ubl-package-root-census@1",
        "format_id": "ubl",
        "profile": "ubl_2.3",
        "authority": {
            "source_id": "SRC-UBL-002",
            "authority_class": "UBL_STANDARD_PACKAGE",
            "package_sha256": observed_package_sha256,
            "legal_use_status": "APPROVED_FOR_LOCAL_USE",
            "redistribution": "ALLOWED_WITH_NOTICE",
        },
        "limits": active_limits.as_dict(),
        "member_count": len(member_rows),
        "member_uncompressed_bytes": sum(row["size"] for row in member_rows),
        "member_compressed_bytes": sum(
            row["compressed_size"] for row in member_rows
        ),
        "package_members_sha256": _canonical_json_sha256(member_rows),
        "role_counts": dict(sorted(role_counts.items())),
        "category_counts": category_counts,
        "signature_members": signature_members,
        "members": member_rows,
        "root_count": len(roots),
        "root_qname_count": len(qname_counts),
        "root_member_names_sha256": _canonical_json_sha256(root_members),
        "root_manifest_sha256": _canonical_json_sha256(roots),
        "roots": roots,
        "duplicate_member_count": 0,
        "unsafe_member_count": 0,
        "remote_import_count": 0,
        "unresolved_import_count": 0,
        "root_validation": {
            "missing_declared_type_count": 0,
            "duplicate_qname_count": 0,
            "root_name_mismatch_count": 0,
        },
        "completion": {
            "package_census_complete": True,
            "root_denominator_complete": True,
            "reachable_schema_graph_complete": False,
            "naming_contract_complete": False,
            "obligation_denominator_complete": False,
            "product_implementation_complete": False,
            "production_certification_complete": False,
        },
        "truth_boundary": (
            "This artifact proves the exact digest-bound UBL 2.3 package "
            "inventory, 91 unique maindoc roots, their declared local content "
            "types, and direct offline imports. It does not yet prove the "
            "complete reachable schema graph, generated Python typing, "
            "behavioral obligations, interoperability, or production readiness."
        ),
    }
    return result


def compile_ubl_reachable_schema_graph(
    source: str | os.PathLike[str] | bytes | bytearray,
    *,
    expected_package_sha256: str,
    expected_root_count: int = 91,
    limits: CensusLimits | None = None,
    graph_limits: GraphLimits | None = None,
) -> dict[str, Any]:
    """Compile the content-addressed XSD graph from the pinned UBL package."""

    active_limits = limits or CensusLimits()
    if _SHA256.fullmatch(expected_package_sha256) is None:
        raise UblCensusError("expected package digest is not a SHA-256 value")
    if expected_root_count <= 0:
        raise UblCensusError("expected root count must be positive")
    package = _package_bytes(source, limits=active_limits)
    observed_package_sha256 = hashlib.sha256(package).hexdigest()
    if observed_package_sha256 != expected_package_sha256:
        raise UblCensusError(
            "package digest mismatch: "
            f"expected {expected_package_sha256}, got {observed_package_sha256}"
        )
    try:
        from io import BytesIO

        with ZipFile(BytesIO(package)) as archive:
            _, members = _read_members(archive, limits=active_limits)
    except BadZipFile as exc:
        raise UblCensusError("authority package is not a valid ZIP archive") from exc
    root_members = sorted(name for name in members if _MAINDOC.fullmatch(name))
    if len(root_members) != expected_root_count:
        raise UblCensusError(
            f"expected {expected_root_count} maindoc roots, found "
            f"{len(root_members)}"
        )
    try:
        return compile_reachable_schema_graph(
            members,
            root_members=root_members,
            package_sha256=observed_package_sha256,
            limits=graph_limits,
        )
    except UblSchemaGraphError as exc:
        raise UblCensusError(f"schema graph invalid: {exc}") from exc


def canonical_yaml_bytes(value: Mapping[str, Any]) -> bytes:
    """Serialize canonical LF YAML for reproducible checked-in artifacts."""

    text = yaml.safe_dump(
        dict(value),
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=1_000_000,
    )
    return text.replace("\r\n", "\n").encode("utf-8")


def write_census_atomic(value: Mapping[str, Any], destination: Path) -> None:
    """Atomically replace a census with canonical bytes."""

    payload = canonical_yaml_bytes(value)
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="wb",
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
        delete=False,
    )
    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def check_census_file(value: Mapping[str, Any], destination: Path) -> None:
    """Fail when a tracked census differs from the current authority bytes."""

    try:
        observed = destination.read_bytes().replace(b"\r\n", b"\n")
    except OSError as exc:
        raise UblCensusError(f"cannot read census file: {destination}") from exc
    expected = canonical_yaml_bytes(value)
    if observed != expected:
        raise UblCensusError(f"census file is stale or differs: {destination}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE_PATH)
    parser.add_argument(
        "--expected-package-sha256",
        default=DEFAULT_PACKAGE_SHA256,
    )
    parser.add_argument("--expected-root-count", type=int, default=91)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        census = compile_ubl_package_census(
            args.package,
            expected_package_sha256=args.expected_package_sha256,
            expected_root_count=args.expected_root_count,
        )
        if args.check:
            check_census_file(census, args.output)
        else:
            write_census_atomic(census, args.output)
    except UblCensusError as exc:
        print(f"UBL census error: {exc}", file=sys.stderr)
        return 1
    summary = {
        "output": str(args.output),
        "package_sha256": census["authority"]["package_sha256"],
        "member_count": census["member_count"],
        "root_count": census["root_count"],
        "root_manifest_sha256": census["root_manifest_sha256"],
        "check": bool(args.check),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
