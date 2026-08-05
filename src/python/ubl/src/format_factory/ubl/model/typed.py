"""Project between the lossless XML tree and the typed business values.

The value types in `values.py` were correct but unreachable: a parsed Invoice
yielded untyped `XmlNode` text, so a caller wanting a line total still had to
pull a string out and build a number themselves — which is precisely where the
binary float the specification forbids gets introduced.

This layer closes that gap in both directions and carries the supplementary
attributes across, because the obligation requires them to survive edits.

Two refusals matter here as much as the conversions:

* **A missing `currencyID` is an error, never a default.** Inventing a currency
  the document never stated is the most dangerous thing this layer could do.
* **An unmodelled value is refused rather than stringified**, so unvalidated
  text cannot reach a business document through the back door.
"""

from __future__ import annotations

from typing import Union

from ..errors import UblValidationError
from .document import XmlNode
from .values import Amount, BinaryObject, Code, Identifier, Quantity

#: Attribute names are unprefixed in UBL instances, so they are read directly.
CURRENCY_ID = "currencyID"
UNIT_CODE = "unitCode"
SCHEME_ID = "schemeID"
SCHEME_AGENCY_ID = "schemeAgencyID"
LIST_ID = "listID"
LIST_AGENCY_ID = "listAgencyID"
LIST_VERSION_ID = "listVersionID"
MIME_CODE = "mimeCode"
FILENAME = "filename"

TypedValue = Union[Amount, Quantity, Code, Identifier, BinaryObject]


def local_name(qname: str) -> str:
    """Strip Clark notation, so callers navigate by `ID` rather than
    `{urn:...:CommonBasicComponents-2}ID`."""
    if qname.startswith("{"):
        return qname.partition("}")[2]
    return qname


def find(node: XmlNode, name: str) -> XmlNode | None:
    """The first child with this local name, or None."""
    for child in node.children:
        if local_name(child.qname) == name:
            return child
    return None


def find_all(node: XmlNode, name: str) -> tuple[XmlNode, ...]:
    """Every child with this local name, in document order.

    Order is preserved because UBL line ordering is meaningful — an invoice's
    lines are numbered by position as often as by `cbc:ID`.
    """
    return tuple(child for child in node.children if local_name(child.qname) == name)


def _require_node(node: XmlNode | None, expected: str) -> XmlNode:
    if node is None:
        raise UblValidationError(
            f"cannot project a missing element into {expected}; `find` returned "
            "None, which usually means the element is absent from the document"
        )
    return node


def _attribute(node: XmlNode, name: str) -> str | None:
    for key, value in node.attributes:
        if key == name:
            return value
    return None


def amount_of(node: XmlNode | None) -> Amount:
    """Project an amount-typed element. `currencyID` is required."""
    element = _require_node(node, "an Amount")
    currency = _attribute(element, CURRENCY_ID)
    if currency is None:
        raise UblValidationError(
            f"<{local_name(element.qname)}> is amount-typed but carries no "
            f"{CURRENCY_ID}; the UBL unqualified data type requires it, and "
            "defaulting one would invent a currency the document never stated"
        )
    return Amount(element.text.strip(), currency)


def quantity_of(node: XmlNode | None) -> Quantity:
    """Project a quantity-typed element. `unitCode` is optional."""
    element = _require_node(node, "a Quantity")
    return Quantity(element.text.strip(), _attribute(element, UNIT_CODE))


def identifier_of(node: XmlNode | None) -> Identifier:
    element = _require_node(node, "an Identifier")
    return Identifier(
        element.text,
        scheme_id=_attribute(element, SCHEME_ID),
        scheme_agency_id=_attribute(element, SCHEME_AGENCY_ID),
    )


def code_of(node: XmlNode | None) -> Code:
    element = _require_node(node, "a Code")
    return Code(
        element.text,
        list_id=_attribute(element, LIST_ID),
        list_agency_id=_attribute(element, LIST_AGENCY_ID),
        list_version_id=_attribute(element, LIST_VERSION_ID),
    )


def binary_object_of(node: XmlNode | None) -> BinaryObject:
    element = _require_node(node, "a BinaryObject")
    mime_code = _attribute(element, MIME_CODE)
    if mime_code is None:
        raise UblValidationError(
            f"<{local_name(element.qname)}> carries no {MIME_CODE}; it is "
            "mandatory in the UBL unqualified data type"
        )
    return BinaryObject.from_base64(
        element.text.strip(), mime_code, _attribute(element, FILENAME)
    )


def to_node(qname: str, value: TypedValue) -> XmlNode:
    """Project a typed value back to an element, carrying its attributes.

    Optional attributes that are absent emit nothing rather than an empty
    string: an empty `unitCode` would assert a unit of measure the value never
    had.
    """
    attributes: dict[str, str] = {}

    if isinstance(value, Amount):
        text = str(value.value)
        attributes[CURRENCY_ID] = value.currency_id
    elif isinstance(value, Quantity):
        text = str(value.value)
        if value.unit_code is not None:
            attributes[UNIT_CODE] = value.unit_code
    elif isinstance(value, Identifier):
        text = value.value
        if value.scheme_id is not None:
            attributes[SCHEME_ID] = value.scheme_id
        if value.scheme_agency_id is not None:
            attributes[SCHEME_AGENCY_ID] = value.scheme_agency_id
    elif isinstance(value, Code):
        text = value.value
        if value.list_id is not None:
            attributes[LIST_ID] = value.list_id
        if value.list_agency_id is not None:
            attributes[LIST_AGENCY_ID] = value.list_agency_id
        if value.list_version_id is not None:
            attributes[LIST_VERSION_ID] = value.list_version_id
    elif isinstance(value, BinaryObject):
        text = value.to_base64()
        attributes[MIME_CODE] = value.mime_code
        if value.filename is not None:
            attributes[FILENAME] = value.filename
    else:
        raise UblValidationError(
            f"cannot project {type(value).__name__} into a UBL element; "
            "stringifying an unmodelled value would put unvalidated text into a "
            "business document"
        )

    return XmlNode.create(qname, attributes=attributes, text=text)


__all__ = [
    "TypedValue",
    "amount_of",
    "binary_object_of",
    "code_of",
    "find",
    "find_all",
    "identifier_of",
    "local_name",
    "quantity_of",
    "to_node",
]
