"""Deterministic semantic UBL XML writer."""

from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from os import PathLike
from pathlib import Path
from typing import cast

from format_factory.core import BinaryDestination, ResourceLimits

from ..._generated import ROOT_NAMESPACES
from ...errors import UblWriteError
from ...model import UblDocument, XmlNode
from ...security import effective_limits
from ...validation import validate
from ..preservation import PreservationMode, canonicalize


def _to_element(node: XmlNode) -> ET.Element:
    element = ET.Element(node.qname, dict(node.attributes))
    element.text = node.text or None
    element.tail = node.tail or None
    for child in node.children:
        element.append(_to_element(child))
    return element


def dumps(
    document: UblDocument,
    *,
    mode: PreservationMode = PreservationMode.LOSSLESS,
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> bytes:
    """Serialize a document with stable attribute and child ordering.

    ``mode`` selects LOSSLESS (default; unchanged from this function's
    historical behavior) or CANONICAL (a root-level ``ext:UBLExtensions``
    container is dropped before validating and serializing -- see
    ``codec.preservation`` for what is and is not eligible to drop).
    """

    if mode == PreservationMode.CANONICAL:
        document, _dropped = canonicalize(document)
    elif mode != PreservationMode.LOSSLESS:
        raise UblWriteError(f"unknown preservation mode: {mode!r}")

    selected_profile = profile or "UBL-2.3"
    report = validate(document, profile=selected_profile, limits=limits)
    if not report.is_valid:
        message = "; ".join(item.message for item in report.errors)
        raise UblWriteError(f"cannot serialize invalid UBL document: {message}")
    selected_limits = effective_limits(limits)
    root_namespace = ROOT_NAMESPACES[document.root_name]
    ET.register_namespace("", root_namespace)
    ET.register_namespace(
        "cbc", "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    )
    ET.register_namespace(
        "cac",
        "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    )
    ET.register_namespace(
        "ext",
        "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    )
    data = cast(
        bytes,
        ET.tostring(
            _to_element(document.root),
            encoding="utf-8",
            xml_declaration=True,
            short_empty_elements=True,
        ),
    )
    selected_limits.enforce("max_output_bytes", len(data))
    return data


def dump(
    document: UblDocument,
    destination: BinaryDestination,
    *,
    mode: PreservationMode = PreservationMode.LOSSLESS,
    profile: str | None = None,
    limits: ResourceLimits | None = None,
) -> None:
    """Serialize to a path or binary stream."""

    data = dumps(document, mode=mode, profile=profile, limits=limits)
    if isinstance(destination, (str, PathLike)):
        path = Path(destination)
        try:
            path.write_bytes(data)
        except OSError as exc:
            raise UblWriteError(f"cannot write {path}: {exc}") from exc
        return
    written = destination.write(data)
    if written != len(data):
        raise UblWriteError(f"short write: wrote {written} of {len(data)} bytes")


def semantic_sha256(document: UblDocument) -> str:
    """Return the deterministic serialized digest used for edit tracking."""

    return hashlib.sha256(dumps(document)).hexdigest()
