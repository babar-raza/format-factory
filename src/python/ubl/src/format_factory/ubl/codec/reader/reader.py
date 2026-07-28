"""Bounded, namespace-aware UBL 2.3 structural reader."""

from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from os import PathLike
from pathlib import Path

from format_factory.core import BinarySource, ProbeResult, ResourceLimits

from ..._generated import ROOT_NAMESPACES, ROOT_NAME_SET
from ...errors import UblParseError
from ...model import UblDocument, XmlNode, document_from_root
from ...security import effective_limits

SUPPORTED_PROFILE = "UBL-2.3"
_FORBIDDEN_DECLARATIONS = (b"<!doctype", b"<!entity")
_SIGNATURE_NAMESPACES = frozenset(
    {
        "http://www.w3.org/2000/09/xmldsig#",
        "urn:oasis:names:specification:ubl:schema:xsd:CommonSignatureComponents-2",
    }
)


def _read_source(source: BinarySource, limits: ResourceLimits) -> bytes:
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
            raise UblParseError(f"cannot read {path}: {exc}") from exc
    elif hasattr(source, "read"):
        data = source.read(limits.max_input_bytes + 1)
        if not isinstance(data, bytes):
            raise TypeError("binary source read() must return bytes")
    else:
        raise TypeError("source must be bytes, a path, or a binary stream")
    limits.enforce("max_input_bytes", len(data))
    return data


def _split_qname(qname: str) -> tuple[str, str]:
    if not qname.startswith("{") or "}" not in qname:
        return "", qname
    namespace, local = qname[1:].split("}", 1)
    return namespace, local


def _reject_unsafe_declarations(data: bytes) -> None:
    lowered = data.lower()
    if any(marker in lowered for marker in _FORBIDDEN_DECLARATIONS):
        raise UblParseError("DTD and entity declarations are not permitted")


def _enforce_tree_limits(root: ET.Element, limits: ResourceLimits) -> None:
    count = 0
    text_bytes = 0
    attribute_count = 0
    stack: list[tuple[ET.Element, int]] = [(root, 1)]
    while stack:
        element, depth = stack.pop()
        count += 1
        if count > limits.max_xml_nodes:
            raise UblParseError(f"XML node limit exceeded: {count}")
        if depth > limits.max_nesting_depth:
            raise UblParseError(f"XML nesting limit exceeded: {depth}")
        attribute_count += len(element.attrib)
        if attribute_count > limits.max_entries:
            raise UblParseError(f"XML attribute limit exceeded: {attribute_count}")
        text_bytes += len((element.text or "").encode("utf-8"))
        text_bytes += len((element.tail or "").encode("utf-8"))
        if text_bytes > limits.max_decompressed_bytes:
            raise UblParseError(f"XML text limit exceeded: {text_bytes}")
        stack.extend((child, depth + 1) for child in reversed(element))


def _to_node(element: ET.Element) -> XmlNode:
    return XmlNode.create(
        element.tag,
        attributes=element.attrib,
        text=element.text or "",
        children=tuple(_to_node(child) for child in element),
        tail=element.tail or "",
    )


def _has_signature(root: ET.Element) -> bool:
    for element in root.iter():
        namespace, local = _split_qname(element.tag)
        if local in {"Signature", "UBLDocumentSignatures"} and (
            namespace in _SIGNATURE_NAMESPACES or "Signature" in namespace
        ):
            return True
    return False


def _parse(data: bytes, *, limits: ResourceLimits) -> UblDocument:
    _reject_unsafe_declarations(data)
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise UblParseError(f"malformed XML: {exc}") from exc
    _enforce_tree_limits(root, limits)
    namespace, root_name = _split_qname(root.tag)
    if root_name not in ROOT_NAME_SET:
        raise UblParseError(f"unsupported UBL document root: {root_name!r}")
    expected_namespace = ROOT_NAMESPACES[root_name]
    if namespace != expected_namespace:
        raise UblParseError(
            f"root namespace mismatch for {root_name}: expected "
            f"{expected_namespace!r}, got {namespace!r}"
        )
    source_sha256 = hashlib.sha256(data).hexdigest()
    return document_from_root(
        _to_node(root),
        source_sha256=source_sha256,
        signed_content_sha256=source_sha256 if _has_signature(root) else None,
    )


def loads(
    data: bytes | bytearray | memoryview | str,
    *,
    mode: str = "strict",
    limits: ResourceLimits | None = None,
) -> UblDocument:
    """Load a UBL document from bytes or Unicode XML."""

    if mode not in {"strict", "preservation"}:
        raise ValueError("mode must be 'strict' or 'preservation'")
    raw = data.encode("utf-8") if isinstance(data, str) else bytes(data)
    selected_limits = effective_limits(limits)
    selected_limits.enforce("max_input_bytes", len(raw))
    return _parse(raw, limits=selected_limits)


def load(
    source: BinarySource,
    *,
    mode: str = "strict",
    limits: ResourceLimits | None = None,
) -> UblDocument:
    """Load a UBL document from a path, bytes, or binary stream."""

    if mode not in {"strict", "preservation"}:
        raise ValueError("mode must be 'strict' or 'preservation'")
    selected_limits = effective_limits(limits)
    return _parse(_read_source(source, selected_limits), limits=selected_limits)


def probe(
    source: BinarySource, *, limits: ResourceLimits | None = None
) -> ProbeResult:
    """Probe a source without raising."""

    try:
        document = load(source, mode="preservation", limits=limits)
    except (Exception, KeyboardInterrupt):
        return ProbeResult(False, 0.0, "ubl", reason="not bounded UBL 2.3 XML")
    return ProbeResult(
        True,
        1.0,
        "ubl",
        profile=SUPPORTED_PROFILE,
        reason=f"recognized {document.root_name} document root",
    )
