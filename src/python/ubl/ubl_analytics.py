"""UBL document analytics — statistics derived from parsed UBL documents.

Each function operates on a freshly re-parsed model dict obtained via
load_ubl(source); no pre-built domain model object is required. No I/O
beyond the load_ubl() call itself.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Union

from .ubl_codec import load_ubl

SourceType = Union[str, Path, bytes]

spec_qname = "ubl:invoice"
spec_fact_ref = "FACT-UBL-002"


def ubl_total_line_count(source: SourceType) -> int:
    """Return the count of line items in the document.

    Works for both Invoice (cac:InvoiceLine) and Order (cac:OrderLine)
    document types, since load_ubl() normalizes both to a "lines" list.

    Spec: Invoice/Order mandatory line items (FACT-UBL-002)
    """
    model = load_ubl(source)
    return len(model.get("lines", []))


def ubl_supplier_name(source: SourceType) -> str | None:
    """Return the supplier party name if present, else None.

    Only Invoice documents carry a "supplier" key (cac:AccountingSupplierParty).
    Order documents and Invoices missing the supplier element return None.

    Spec: cac:AccountingSupplierParty / cac:PartyName / cbc:Name (FACT-UBL-002)
    """
    model = load_ubl(source)
    supplier = model.get("supplier")
    if not supplier:
        return None
    name = supplier.get("name", "")
    return name if name else None


def ubl_document_type_summary(source: SourceType) -> dict[str, Any]:
    """Return a summary dict describing the document's type and line count.

    Return shape: {"document_type": str, "line_count": int}.

    Spec: UBL document type is determined by the root element's namespace
    (Invoice-2, Order-2, ...) (FACT-UBL-001)
    """
    model = load_ubl(source)
    return {
        "document_type": model.get("document_type", ""),
        "line_count": len(model.get("lines", [])),
    }
