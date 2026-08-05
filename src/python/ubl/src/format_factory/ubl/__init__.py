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
    UblDate,
    UblDateTime,
    UblTime,

    InvoiceLine,
    Item,
    LegalMonetaryTotal,
    TaxSubtotal,
    TaxTotal,
    invoice_line_of,
    item_of,
    legal_monetary_total_of,
    reconcile_invoice,
    tax_subtotal_of,
    tax_total_of,

    amount_of,
    binary_object_of,
    code_of,
    find,
    find_all,
    identifier_of,
    local_name,
    quantity_of,
    to_node,

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
    "UblTime",
    "UblDateTime",
    "UblDate",
    "tax_total_of",
    "tax_subtotal_of",
    "reconcile_invoice",
    "legal_monetary_total_of",
    "item_of",
    "invoice_line_of",
    "TaxTotal",
    "TaxSubtotal",
    "LegalMonetaryTotal",
    "Item",
    "InvoiceLine",
    "to_node",
    "quantity_of",
    "local_name",
    "identifier_of",
    "find_all",
    "find",
    "code_of",
    "binary_object_of",
    "amount_of",
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
