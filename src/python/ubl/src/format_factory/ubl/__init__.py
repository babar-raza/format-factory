"""Production OASIS UBL 2.3 lifecycle API."""

from __future__ import annotations

from pathlib import Path

from format_factory.core import BinarySource

from ._generated import (
    ARCHIVE_MEMBER_NAMES_SHA256,
    AUTHORITY_SHA256,
    ROOT_NAMES,
    ROOT_NAMESPACES,
    ROOT_NAMES_SHA256,
)
from .analytics import element_count, qname_histogram
from .codec import (
    SUPPORTED_PROFILE,
    dump,
    dumps,
    load,
    loads,
    probe,
    semantic_sha256,
)
from .errors import UblError, UblParseError, UblValidationError, UblWriteError
from .model import (
    ROOT_CLASSES,
    Amount,
    BinaryObject,
    Code,
    Identifier,
    Quantity,
    Rounding,
    UblDocument,
    XmlNode,
)
from .security import UBL_DEFAULT_LIMITS
from .validation import validate

__all__ = [
    "Rounding",
    "Quantity",
    "Identifier",
    "Code",
    "BinaryObject",
    "Amount",
    "ARCHIVE_MEMBER_NAMES_SHA256",
    "AUTHORITY_SHA256",
    "ROOT_CLASSES",
    "ROOT_NAMES",
    "ROOT_NAMESPACES",
    "ROOT_NAMES_SHA256",
    "SUPPORTED_PROFILE",
    "UBL_DEFAULT_LIMITS",
    "UblDocument",
    "UblError",
    "UblParseError",
    "UblValidationError",
    "UblWriteError",
    "XmlNode",
    "dump",
    "dumps",
    "element_count",
    "load",
    "loads",
    "probe",
    "qname_histogram",
    "roundtrip",
    "semantic_sha256",
    "ubl_installed_workflow",
    "validate",
]

__version__ = "0.2.0.dev0"


def roundtrip(source: BinarySource, destination: str | Path) -> UblDocument:
    document = load(source)
    dump(document, destination)
    return load(destination)


def ubl_installed_workflow(source: BinarySource) -> dict[str, object]:
    document = load(source)
    return {
        "element_count": element_count(document),
        "format": "ubl",
        "loaded": True,
        "profile": SUPPORTED_PROFILE,
        "root": document.root_name,
    }
