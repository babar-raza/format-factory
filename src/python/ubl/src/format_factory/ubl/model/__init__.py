"""Public UBL model types."""

from .document import UblDocument, XmlNode
from .root_types import ROOT_CLASSES
from .aggregates import (
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
)
from .typed import (
    amount_of,
    binary_object_of,
    code_of,
    find,
    find_all,
    identifier_of,
    local_name,
    quantity_of,
    to_node,
)
from .values import (
    Amount,
    BinaryObject,
    Code,
    Identifier,
    Quantity,
    Rounding,
)


def document_from_root(
    root: XmlNode,
    *,
    source_sha256: str | None = None,
    signed_content_sha256: str | None = None,
) -> UblDocument:
    root_name = root.qname.rsplit("}", 1)[-1]
    document_type = ROOT_CLASSES.get(root_name)
    if document_type is None:
        raise ValueError(f"unsupported UBL document root: {root_name}")
    return document_type(
        root,
        source_sha256=source_sha256,
        signed_content_sha256=signed_content_sha256,
    )

__all__ = [
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
    "Amount","ROOT_CLASSES", "UblDocument", "XmlNode", "document_from_root"]
