"""UBL-QUERY-001 -- indexed and linear scans agree.

MUST (RF-UBL-00006): "Find components by QName, type, ID, and business
identifiers with path-aware results; offer read-only indexed views for
large documents." / "...including read-only indexed views for large
documents."

required_tests: "Query result paths verified against fixtures; indexed and
linear scans agree."

test_obligation_document_query.py already proves query result paths against
fixtures, the four business roles, the worked "lines referencing an item"
example, and that one index answers multiple queries without rebuilding.
It does not prove the second, narrower clause: that `DocumentIndex`'s
pre-built dict lookups return exactly what an independent, freshly-written
linear scan over the same tree would find. That is the property this file
adds -- it is what actually justifies trusting the index instead of always
walking the tree, and it is the one thing a caching bug (stale entry, wrong
grouping key, an off-by-one in sibling numbering) would break silently
without ever raising an exception.

The linear-scan implementations below deliberately do not import or reuse
`DocumentIndex`'s internals (`_walk`, `_by_qname`, etc.) -- they are a
second, independently written pass over `XmlNode.iter()`, so agreement
between the two is evidence of correctness rather than two call sites for
the same code.
"""

from __future__ import annotations

import pytest

from format_factory.ubl import DocumentIndex, XmlNode, business_role, loads

CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"

INVOICE = f"""<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cbc="{CBC}" xmlns:cac="{CAC}">
<cbc:ID>INV-001</cbc:ID>
<cac:OrderReference>
  <cbc:ID>ORD-77</cbc:ID>
</cac:OrderReference>
<cac:BillingReference>
  <cac:InvoiceDocumentReference>
    <cbc:ID>PRIOR-INV-9</cbc:ID>
  </cac:InvoiceDocumentReference>
</cac:BillingReference>
<cac:AccountingSupplierParty>
  <cac:Party>
    <cbc:ID>SUPPLIER-1</cbc:ID>
  </cac:Party>
</cac:AccountingSupplierParty>
<cac:AccountingCustomerParty>
  <cac:Party>
    <cbc:ID>CUSTOMER-1</cbc:ID>
  </cac:Party>
</cac:AccountingCustomerParty>
<cac:InvoiceLine>
  <cbc:ID>1</cbc:ID>
  <cac:Item>
    <cbc:Name>Coffee beans</cbc:Name>
    <cac:StandardItemIdentification>
      <cbc:ID>ITEM-COFFEE</cbc:ID>
    </cac:StandardItemIdentification>
  </cac:Item>
</cac:InvoiceLine>
<cac:InvoiceLine>
  <cbc:ID>2</cbc:ID>
  <cac:Item>
    <cbc:Name>Milk</cbc:Name>
    <cac:StandardItemIdentification>
      <cbc:ID>ITEM-MILK</cbc:ID>
    </cac:StandardItemIdentification>
  </cac:Item>
</cac:InvoiceLine>
</Invoice>"""

#: A second, more adversarial fixture: deeper nesting, three same-named
#: siblings at one level (to stress sibling-index numbering beyond a simple
#: pair), and a party nested two levels below another party-shaped wrapper.
NESTED_ORDER = f"""<Order xmlns="urn:oasis:names:specification:ubl:schema:xsd:Order-2"
 xmlns:cbc="{CBC}" xmlns:cac="{CAC}">
<cbc:ID>ORD-900</cbc:ID>
<cac:BuyerCustomerParty>
  <cac:Party>
    <cbc:ID>BUYER-1</cbc:ID>
    <cac:Contact>
      <cbc:ID>CONTACT-1</cbc:ID>
    </cac:Contact>
  </cac:Party>
</cac:BuyerCustomerParty>
<cac:OrderLine>
  <cac:LineItem>
    <cbc:ID>1</cbc:ID>
    <cac:Item>
      <cbc:Name>Widget</cbc:Name>
      <cac:BuyersItemIdentification>
        <cbc:ID>W-1</cbc:ID>
      </cac:BuyersItemIdentification>
    </cac:Item>
  </cac:LineItem>
</cac:OrderLine>
<cac:OrderLine>
  <cac:LineItem>
    <cbc:ID>2</cbc:ID>
    <cac:Item>
      <cbc:Name>Gadget</cbc:Name>
      <cac:BuyersItemIdentification>
        <cbc:ID>W-2</cbc:ID>
      </cac:BuyersItemIdentification>
    </cac:Item>
  </cac:LineItem>
</cac:OrderLine>
<cac:OrderLine>
  <cac:LineItem>
    <cbc:ID>3</cbc:ID>
    <cac:Item>
      <cbc:Name>Gizmo</cbc:Name>
      <cac:BuyersItemIdentification>
        <cbc:ID>W-3</cbc:ID>
      </cac:BuyersItemIdentification>
    </cac:Item>
  </cac:LineItem>
</cac:OrderLine>
</Order>"""


def _local_name(qname: str) -> str:
    return qname.rsplit("}", 1)[-1] if "}" in qname else qname


def _linear_scan_paths(root: XmlNode) -> list[tuple[tuple[str, ...], XmlNode]]:
    """A from-scratch, top-down recursive walk computing the same
    `name[index-among-same-named-siblings]` path convention `DocumentIndex`
    uses, but via separate recursion (not the module's iterative
    stack-plus-counts-dict shape) so a numbering bug in one would not
    automatically reproduce in the other."""

    results: list[tuple[tuple[str, ...], XmlNode]] = []

    def recurse(node: XmlNode, path: tuple[str, ...]) -> None:
        results.append((path, node))
        counts: dict[str, int] = {}
        for child in node.children:
            name = _local_name(child.qname)
            index = counts.get(name, 0)
            counts[name] = index + 1
            recurse(child, path + (f"{name}[{index}]",))

    recurse(root, (f"{_local_name(root.qname)}[0]",))
    return results


def _linear_own_identifier(node: XmlNode) -> str | None:
    for child in node.children:
        if _local_name(child.qname) in ("ID", "LineID", "UUID"):
            return child.text
    return None


def _as_comparable(matches) -> set[tuple[tuple[str, ...], str]]:
    """(path, qname) is enough to identify a match uniquely in these
    fixtures (no two distinct nodes share both), and is trivially
    hashable/comparable, unlike the frozen dataclass instances themselves
    where identity of the underlying tuple matters less than what was found."""
    return {(match.path, match.node.qname) for match in matches}


def _linear_by_qname(root: XmlNode, qname: str) -> set[tuple[tuple[str, ...], str]]:
    return {
        (path, node.qname)
        for path, node in _linear_scan_paths(root)
        if node.qname == qname
    }


def _linear_by_local_name(root: XmlNode, name: str) -> set[tuple[tuple[str, ...], str]]:
    return {
        (path, node.qname)
        for path, node in _linear_scan_paths(root)
        if _local_name(node.qname) == name
    }


def _linear_by_id(root: XmlNode, identifier: str) -> set[tuple[tuple[str, ...], str]]:
    return {
        (path, node.qname)
        for path, node in _linear_scan_paths(root)
        if _linear_own_identifier(node) == identifier
    }


def _linear_by_business_role(root: XmlNode, role: str) -> set[tuple[tuple[str, ...], str]]:
    return {
        (path, node.qname)
        for path, node in _linear_scan_paths(root)
        if business_role(node) == role
    }


_FIXTURES = [INVOICE, NESTED_ORDER]
_FIXTURE_IDS = ["invoice", "nested_order"]


@pytest.mark.parametrize("xml", _FIXTURES, ids=_FIXTURE_IDS)
def test_by_qname_agrees_with_a_linear_scan(xml: str) -> None:
    root = loads(xml).root
    index = DocumentIndex(root)

    for qname in {node.qname for _, node in _linear_scan_paths(root)}:
        assert _as_comparable(index.by_qname(qname)) == _linear_by_qname(root, qname)


@pytest.mark.parametrize("xml", _FIXTURES, ids=_FIXTURE_IDS)
def test_by_local_name_agrees_with_a_linear_scan(xml: str) -> None:
    root = loads(xml).root
    index = DocumentIndex(root)

    for name in {_local_name(node.qname) for _, node in _linear_scan_paths(root)}:
        assert _as_comparable(index.by_local_name(name)) == _linear_by_local_name(root, name)


@pytest.mark.parametrize("xml", _FIXTURES, ids=_FIXTURE_IDS)
def test_by_id_agrees_with_a_linear_scan(xml: str) -> None:
    root = loads(xml).root
    index = DocumentIndex(root)

    identifiers = {
        _linear_own_identifier(node)
        for _, node in _linear_scan_paths(root)
        if _linear_own_identifier(node) is not None
    }
    assert identifiers, "fixture must contain at least one identified component"
    for identifier in identifiers:
        assert _as_comparable(index.by_id(identifier)) == _linear_by_id(root, identifier)


@pytest.mark.parametrize("xml", _FIXTURES, ids=_FIXTURE_IDS)
def test_by_business_role_agrees_with_a_linear_scan(xml: str) -> None:
    root = loads(xml).root
    index = DocumentIndex(root)

    for role in ("party", "item", "line", "document_reference"):
        assert _as_comparable(index.by_business_role(role)) == _linear_by_business_role(root, role)


def test_a_query_for_an_absent_identifier_agrees_on_emptiness() -> None:
    root = loads(INVOICE).root
    index = DocumentIndex(root)

    assert index.by_id("NO-SUCH-ID") == ()
    assert _linear_by_id(root, "NO-SUCH-ID") == set()


def test_the_linear_scan_itself_visits_every_node_exactly_once() -> None:
    """A sanity check on the comparator: if the linear scan under- or
    over-counted nodes, every agreement assertion above would be vacuous."""
    root = loads(NESTED_ORDER).root

    paths = _linear_scan_paths(root)

    assert len(paths) == len(list(root.iter()))
    assert len({path for path, _ in paths}) == len(paths)
