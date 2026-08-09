"""cac:OrderLine, cac:CreditNoteLine, cac:DespatchLine, and
cac:DocumentResponse -- the maindoc-specific line/response aggregates.

The contract names each of these document types explicitly, describing
their line items as typed aggregate carriers analogous to `cac:InvoiceLine`
(model/aggregates.py). Every field modeled here is grounded directly in the
pinned OASIS UBL 2.3 release package's own vendored XSD
(xsd/common/UBL-CommonAggregateComponents-2.3.xsd, read from the ZIP
itself, not a SAL-fact paraphrase or memory) -- the same technique already
used for `charges.FinancialAccount` and `party.Party`/`party.PostalAddress`
earlier this session.

Scope is deliberately bounded, mirroring `InvoiceLine`'s own precedent: the
fields modeled are each type's identifying, quantity, and amount fields
plus its required nested aggregate, not the full XSD type (OrderLineType,
CreditNoteLineType, and DespatchLineType each declare 8-30 optional fields
covering delivery, warranty, pricing-reference, and sub-line detail this
package does not separately model). `cac:LineItem` (OrderLineType's
required child, itself carrying the identifying/quantity/amount/item
fields InvoiceLine has) is modeled as its own type, matching the XSD's own
structure rather than flattening it into OrderLine.

UBL-PARSE-001 (FF6-EVENT-000484): every lookup here is namespace-precise
via `find_qname`/`find_all_qname`, not `find`/`find_all`'s own
local-name-only matching -- wave 3 of the ~79 disclosed call sites (wave
1: reference.py; wave 2: charges.py). Every field's own namespace was
confirmed directly against the pinned OASIS UBL 2.3 schema
(LineItemType/OrderLineType/CreditNoteLineType/DespatchLineType/
DocumentReferenceType/ResponseType/DocumentResponseType, via a live
xmlschema introspection) before migrating, not assumed: this file mixes
both namespaces genuinely (ID/Quantity/LineExtensionAmount/
CreditedQuantity/DeliveredQuantity/DocumentTypeCode/ResponseCode/
Description are CommonBasicComponents; Item/LineItem/Response/
DocumentReference are CommonAggregateComponents aggregates).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..errors import UblValidationError
from .aggregates import Item, _require, item_of
from .document import XmlNode
from .typed import amount_of, code_of, find_all_qname, find_qname, identifier_of, local_name, quantity_of
from .values import Amount, Code, Identifier, Quantity

_CBC_NAMESPACE = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC_NAMESPACE = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"


def _cbc(node: XmlNode, name: str) -> XmlNode | None:
    return find_qname(node, _CBC_NAMESPACE, name)


def _cac(node: XmlNode, name: str) -> XmlNode | None:
    return find_qname(node, _CAC_NAMESPACE, name)


def _cac_all(node: XmlNode, name: str) -> tuple[XmlNode, ...]:
    return find_all_qname(node, _CAC_NAMESPACE, name)


@dataclass(frozen=True)
class LineItem:
    """`cac:LineItem` -- OrderLineType's required line detail."""

    id: Identifier
    item: Item
    quantity: Quantity | None = None
    line_extension_amount: Amount | None = None

    def __post_init__(self) -> None:
        _require(self.id, "cbc:ID", "cac:LineItem")
        _require(self.item, "a cac:Item", "cac:LineItem")


@dataclass(frozen=True)
class OrderLine:
    """`cac:OrderLine` -- carries a required `cac:LineItem`."""

    line_item: LineItem

    def __post_init__(self) -> None:
        _require(self.line_item, "a cac:LineItem", "cac:OrderLine")


@dataclass(frozen=True)
class CreditNoteLine:
    """`cac:CreditNoteLine` -- cbc:ID, an optional credited quantity and
    line extension amount, and an optional item."""

    id: Identifier
    credited_quantity: Quantity | None = None
    line_extension_amount: Amount | None = None
    item: Item | None = None

    def __post_init__(self) -> None:
        _require(self.id, "cbc:ID", "cac:CreditNoteLine")


@dataclass(frozen=True)
class DespatchLine:
    """`cac:DespatchLine` -- cbc:ID, an optional delivered quantity, and a
    required item."""

    id: Identifier
    item: Item
    delivered_quantity: Quantity | None = None

    def __post_init__(self) -> None:
        _require(self.id, "cbc:ID", "cac:DespatchLine")
        _require(self.item, "a cac:Item", "cac:DespatchLine")


@dataclass(frozen=True)
class DocumentReference:
    """`cac:DocumentReference` -- a required cbc:ID plus an optional
    document type code."""

    id: Identifier
    document_type_code: Code | None = None

    def __post_init__(self) -> None:
        _require(self.id, "cbc:ID", "cac:DocumentReference")


@dataclass(frozen=True)
class Response:
    """`cac:Response` -- an acknowledgement's response code and
    description."""

    response_code: Code | None = None
    description: str | None = None


@dataclass(frozen=True)
class DocumentResponse:
    """`cac:DocumentResponse` -- a required `cac:Response` plus the
    document(s) it responds to."""

    response: Response
    document_references: tuple[DocumentReference, ...] = ()

    def __post_init__(self) -> None:
        _require(self.response, "a cac:Response", "cac:DocumentResponse")


def line_item_of(node: XmlNode | None) -> LineItem:
    if node is None:
        raise UblValidationError("cannot project a missing element into a cac:LineItem")
    item = _cac(node, "Item")
    if item is None:
        raise UblValidationError("cac:LineItem has no cac:Item")
    quantity = _cbc(node, "Quantity")
    amount = _cbc(node, "LineExtensionAmount")
    return LineItem(
        id=identifier_of(_cbc(node, "ID")),
        item=item_of(item),
        quantity=quantity_of(quantity) if quantity is not None else None,
        line_extension_amount=amount_of(amount) if amount is not None else None,
    )


def order_line_of(node: XmlNode | None) -> OrderLine:
    if node is None:
        raise UblValidationError("cannot project a missing element into a cac:OrderLine")
    line_item = _cac(node, "LineItem")
    if line_item is None:
        raise UblValidationError(
            f"<{local_name(node.qname)}> has no cac:LineItem"
        )
    return OrderLine(line_item=line_item_of(line_item))


def credit_note_line_of(node: XmlNode | None) -> CreditNoteLine:
    if node is None:
        raise UblValidationError(
            "cannot project a missing element into a cac:CreditNoteLine"
        )
    quantity = _cbc(node, "CreditedQuantity")
    amount = _cbc(node, "LineExtensionAmount")
    item = _cac(node, "Item")
    return CreditNoteLine(
        id=identifier_of(_cbc(node, "ID")),
        credited_quantity=quantity_of(quantity) if quantity is not None else None,
        line_extension_amount=amount_of(amount) if amount is not None else None,
        item=item_of(item) if item is not None else None,
    )


def despatch_line_of(node: XmlNode | None) -> DespatchLine:
    if node is None:
        raise UblValidationError("cannot project a missing element into a cac:DespatchLine")
    item = _cac(node, "Item")
    if item is None:
        raise UblValidationError(
            f"<{local_name(node.qname)}> has no cac:Item"
        )
    quantity = _cbc(node, "DeliveredQuantity")
    return DespatchLine(
        id=identifier_of(_cbc(node, "ID")),
        item=item_of(item),
        delivered_quantity=quantity_of(quantity) if quantity is not None else None,
    )


def document_reference_of(node: XmlNode) -> DocumentReference:
    code = _cbc(node, "DocumentTypeCode")
    return DocumentReference(
        id=identifier_of(_cbc(node, "ID")),
        document_type_code=code_of(code) if code is not None else None,
    )


def response_of(node: XmlNode | None) -> Response | None:
    if node is None:
        return None
    code = _cbc(node, "ResponseCode")
    description = _cbc(node, "Description")
    return Response(
        response_code=code_of(code) if code is not None else None,
        description=description.text.strip() if description is not None else None,
    )


def document_response_of(node: XmlNode | None) -> DocumentResponse:
    if node is None:
        raise UblValidationError(
            "cannot project a missing element into a cac:DocumentResponse"
        )
    response = response_of(_cac(node, "Response"))
    if response is None:
        raise UblValidationError(
            f"<{local_name(node.qname)}> has no cac:Response"
        )
    return DocumentResponse(
        response=response,
        document_references=tuple(
            document_reference_of(child) for child in _cac_all(node, "DocumentReference")
        ),
    )


__all__ = [
    "CreditNoteLine",
    "DespatchLine",
    "DocumentReference",
    "DocumentResponse",
    "LineItem",
    "OrderLine",
    "Response",
    "credit_note_line_of",
    "despatch_line_of",
    "document_reference_of",
    "document_response_of",
    "line_item_of",
    "order_line_of",
    "response_of",
]
