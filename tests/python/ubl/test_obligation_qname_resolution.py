"""UBL-PARSE-001 -- QName resolution independent of prefix/default-namespace form.

MUST (SAL-UBL-OBL-55B90386831BAA06): "Resolve every element and attribute by
QName; default and prefixed namespace forms with identical expanded names
behave identically."

The parser (`xml.etree.ElementTree`) always normalizes an element's tag to
Clark notation (`{namespace}local`) at parse time regardless of whether the
source document declared that namespace as the default (`xmlns=`) or bound
it to a prefix (`xmlns:p=`) -- so this fact was already true by construction,
just never directly asserted. This test proves it rather than assuming it.
"""

from __future__ import annotations

from format_factory.ubl import loads

_NS = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"


def _default_namespace_form() -> bytes:
    return f"""<Invoice xmlns="{_NS}" xmlns:cbc="{_CBC}">
<cbc:ID>INV-1</cbc:ID>
</Invoice>""".encode()


def _prefixed_form() -> bytes:
    return f"""<inv:Invoice xmlns:inv="{_NS}" xmlns:cbc="{_CBC}">
<cbc:ID>INV-1</cbc:ID>
</inv:Invoice>""".encode()


def test_default_and_prefixed_root_namespace_forms_produce_identical_qnames() -> None:
    default_ns = loads(_default_namespace_form())
    prefixed = loads(_prefixed_form())

    assert default_ns.root.qname == prefixed.root.qname == f"{{{_NS}}}Invoice"


def test_default_and_prefixed_forms_project_the_same_child_value() -> None:
    default_ns = loads(_default_namespace_form())
    prefixed = loads(_prefixed_form())

    assert default_ns.root.children[0].qname == prefixed.root.children[0].qname
    assert default_ns.root.children[0].text == prefixed.root.children[0].text == "INV-1"
