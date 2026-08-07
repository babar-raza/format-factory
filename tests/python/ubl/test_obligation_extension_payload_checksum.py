"""UBL-EXT-001 -- "Treat extension payloads and embedded binary
attachments as untrusted data; expose their media types and checksums
without decoding side effects, and gate any external attachment
retrieval behind allowlists, byte limits, and timeouts."

MUST (SAL-UBL-OBL-E98EB489DAC77A1A): before this slice, checksum exposure
for embedded binary attachments (BinaryObject.checksum) was already
proven, but extension payloads specifically had no dedicated
byte-serialization helper to hash at all -- extensions are preserved as
raw XmlNode subtrees, confirmed by direct code inspection.

This slice adds XmlNode.checksum: a SHA-256 hex digest of the subtree's
own canonical structural encoding (qname, attributes, text, children,
tail), never a real XML serialization and never anything decoded from the
extension's own content -- the same "expose checksums without decoding
side effects" guarantee BinaryObject.checksum already proves, extended to
arbitrary extension payload subtrees.
"""

from __future__ import annotations

from format_factory.ubl import loads

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
_EXT = "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
_INVOICE_NS = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"


def _invoice_with_extension(extension_body: str) -> bytes:
    return (
        f'<Invoice xmlns="{_INVOICE_NS}" xmlns:cbc="{_CBC}" xmlns:cac="{_CAC}" xmlns:ext="{_EXT}">'
        f"<ext:UBLExtensions><ext:UBLExtension><ext:ExtensionContent>"
        f"{extension_body}"
        f"</ext:ExtensionContent></ext:UBLExtension></ext:UBLExtensions>"
        f"<cbc:ID>INV-001</cbc:ID>"
        f"</Invoice>"
    ).encode()


def _extension_node(document):
    return document.root.children[0]


def test_an_extension_payload_exposes_a_checksum() -> None:
    document = loads(
        _invoice_with_extension('<vendor:Foo xmlns:vendor="urn:vendor:x">hello</vendor:Foo>')
    )

    checksum = _extension_node(document).checksum

    assert isinstance(checksum, str)
    assert len(checksum) == 64


def test_identical_extension_content_produces_the_same_checksum() -> None:
    body = '<vendor:Foo xmlns:vendor="urn:vendor:x">hello</vendor:Foo>'
    first = loads(_invoice_with_extension(body))
    second = loads(_invoice_with_extension(body))

    assert _extension_node(first).checksum == _extension_node(second).checksum


def test_different_extension_text_content_produces_a_different_checksum() -> None:
    first = loads(
        _invoice_with_extension('<vendor:Foo xmlns:vendor="urn:vendor:x">hello</vendor:Foo>')
    )
    second = loads(
        _invoice_with_extension('<vendor:Foo xmlns:vendor="urn:vendor:x">goodbye</vendor:Foo>')
    )

    assert _extension_node(first).checksum != _extension_node(second).checksum


def test_different_extension_attributes_produce_a_different_checksum() -> None:
    first = loads(
        _invoice_with_extension('<vendor:Foo xmlns:vendor="urn:vendor:x" id="1">hi</vendor:Foo>')
    )
    second = loads(
        _invoice_with_extension('<vendor:Foo xmlns:vendor="urn:vendor:x" id="2">hi</vendor:Foo>')
    )

    assert _extension_node(first).checksum != _extension_node(second).checksum


def test_checksum_is_deterministic_across_repeated_access() -> None:
    document = loads(
        _invoice_with_extension('<vendor:Foo xmlns:vendor="urn:vendor:x">hello</vendor:Foo>')
    )
    node = _extension_node(document)

    assert node.checksum == node.checksum
