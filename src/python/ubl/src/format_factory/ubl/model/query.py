"""UBL-QUERY-001 -- domain and QName query with path-aware results.

"Find components by QName, type, ID, business role, and line/party/item
identifiers with path-aware results usable on large documents." A caller
should be able to find every line referencing an item identifier and get
paths plus typed nodes back, without walking the tree by hand each time.

`DocumentIndex` builds the index ONCE by walking the tree exactly once; every
query after that is a dict lookup, not a re-walk -- that is what "usable on
large documents" and "read-only indexed views" ask for. The index is built
from the immutable `XmlNode` tree, so it can never drift from the document it
was built against; there is no mutation path that could invalidate it silently.
"""

from __future__ import annotations

from dataclasses import dataclass

from .document import XmlNode
from .typed import local_name

Path = tuple[str, ...]

#: Local-name suffixes recognized as identifying a component's business role.
#: "party, item, line, document reference" are the four the contract names.
_PARTY_SUFFIX = "Party"
_LINE_SUFFIX = "Line"
_REFERENCE_SUFFIX = "Reference"
_ITEM_NAME = "Item"

#: Direct children whose text is treated as this node's own identifier, in
#: preference order. UBL uses cbc:ID almost universally; cbc:LineID and
#: cbc:UUID are the two other identifying fields that appear in place of, or
#: alongside, cbc:ID on some components.
_IDENTIFIER_CHILD_NAMES = ("ID", "LineID", "UUID")

#: cac:Item carries no cbc:ID of its own in the real UBL schema -- its
#: identifier lives one level deeper, inside one of these wrapper elements,
#: in preference order.
_ITEM_IDENTIFICATION_CHILDREN = (
    "StandardItemIdentification",
    "SellersItemIdentification",
    "BuyersItemIdentification",
)


@dataclass(frozen=True, slots=True)
class QueryMatch:
    """One node found by a query, with the path used to reach it."""

    path: Path
    node: XmlNode


def business_role(node: XmlNode) -> str | None:
    """Classify a node's business role by its local name, or None if it
    doesn't match one of the four the contract names.

    Suffix matching, not an exhaustive enum: UBL's real vocabulary has many
    role-specific element names (AccountingSupplierParty, InvoiceLine,
    OrderReference, ...) that share a common suffix rather than a fixed list
    this module would have to keep in sync with every UBL document type.

    "Reference" is narrower than the other three suffixes: cac:BillingReference
    is itself only a wrapper around a nested cac:InvoiceDocumentReference or
    cac:CreditNoteDocumentReference and carries no cbc:ID of its own, so
    suffix-matching alone would misclassify the wrapper as a reference in its
    own right. Requiring an own identifier excludes wrapper-only containers
    while still matching genuine references (cac:OrderReference,
    cac:InvoiceDocumentReference, ...), which all carry their own cbc:ID.
    """
    name = local_name(node.qname)
    if name == _ITEM_NAME:
        return "item"
    if name.endswith(_PARTY_SUFFIX):
        return "party"
    if name.endswith(_LINE_SUFFIX):
        return "line"
    if name.endswith(_REFERENCE_SUFFIX) and _own_identifier(node) is not None:
        return "document_reference"
    return None


def _own_identifier(node: XmlNode) -> str | None:
    """The text of this node's own cbc:ID/cbc:LineID/cbc:UUID child, if any."""
    for child in node.children:
        if local_name(child.qname) in _IDENTIFIER_CHILD_NAMES:
            return child.text
    return None


def _item_identifier(node: XmlNode) -> str | None:
    """An Item's identifier, resolved through whichever identification
    wrapper the document uses. cac:Item has no cbc:ID of its own in the real
    UBL schema, unlike every other role this module classifies."""
    for child in node.children:
        if local_name(child.qname) in _ITEM_IDENTIFICATION_CHILDREN:
            identifier = _own_identifier(child)
            if identifier is not None:
                return identifier
    return None


class DocumentIndex:
    """A read-only index over one document's tree, built once."""

    def __init__(self, root: XmlNode) -> None:
        self._by_qname: dict[str, list[QueryMatch]] = {}
        self._by_local_name: dict[str, list[QueryMatch]] = {}
        self._by_id: dict[str, list[QueryMatch]] = {}
        self._by_role: dict[str, list[QueryMatch]] = {}
        root_segment = f"{local_name(root.qname)}[0]"
        self._walk(root, (root_segment,))

    def _walk(self, node: XmlNode, path: Path) -> None:
        """`path` segments are always `name[index]`, index being this node's
        position among same-named siblings under its own parent -- two
        sibling cac:InvoiceLine elements need distinct paths to actually
        locate a SPECIFIC one, and a format that only bracketed the
        ambiguous case would make the path shape depend on the document's
        own content instead of being uniform."""
        match = QueryMatch(path=path, node=node)

        self._by_qname.setdefault(node.qname, []).append(match)
        self._by_local_name.setdefault(local_name(node.qname), []).append(match)

        identifier = _own_identifier(node)
        if identifier:
            self._by_id.setdefault(identifier, []).append(match)

        role = business_role(node)
        if role is not None:
            self._by_role.setdefault(role, []).append(match)

        sibling_counts: dict[str, int] = {}
        for child in node.children:
            name = local_name(child.qname)
            index = sibling_counts.get(name, 0)
            sibling_counts[name] = index + 1
            self._walk(child, path + (f"{name}[{index}]",))

    def by_qname(self, qname: str) -> tuple[QueryMatch, ...]:
        """Exact, namespace-qualified QName match."""
        return tuple(self._by_qname.get(qname, ()))

    def by_local_name(self, name: str) -> tuple[QueryMatch, ...]:
        """Match by local name alone -- "type" in the obligation's sense of
        "the kind of component", independent of which UBL document namespace
        it appears under."""
        return tuple(self._by_local_name.get(name, ()))

    def by_id(self, identifier: str) -> tuple[QueryMatch, ...]:
        """Every node whose own cbc:ID/cbc:LineID/cbc:UUID child equals
        `identifier`, anywhere in the document."""
        return tuple(self._by_id.get(identifier, ()))

    def by_business_role(self, role: str) -> tuple[QueryMatch, ...]:
        """`role` is one of "party", "item", "line", "document_reference"."""
        return tuple(self._by_role.get(role, ()))

    def lines_referencing_item_id(self, item_id: str) -> tuple[QueryMatch, ...]:
        """Every line-role component whose own cac:Item subtree contains an
        identifier matching `item_id`.

        The obligation's own example ("finds every line referencing an item
        identifier and gets paths plus typed nodes back") is not answered by
        `by_id` alone: the matching identifier lives on the Item nested
        inside the line, not on the line itself. This composes the line and
        identifier indexes to answer that exact question directly.
        """
        matches: list[QueryMatch] = []
        for line_match in self.by_business_role("line"):
            # A line's own local name never matches an "item" role (the two
            # suffixes -- "Line", "Item" -- are disjoint), so the line node
            # itself is safely included in this walk without a self-check.
            for descendant in line_match.node.iter():
                if business_role(descendant) == "item" and _item_identifier(descendant) == item_id:
                    matches.append(line_match)
                    break
        return tuple(matches)


__all__ = [
    "DocumentIndex",
    "Path",
    "QueryMatch",
    "business_role",
]
