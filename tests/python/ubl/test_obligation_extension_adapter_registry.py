"""UBL-EXT-001 -- pluggable typed-adapter registry for extension content.

MUST, quoted from the format contract (SAL-UBL-OBL-B36305DA0BCEE0F6):

  "Read and write extension containers with arbitrary namespaces and
   payloads without loss; expose registered typed adapters as opt-in."

The "read and write... without loss" half is proven elsewhere
(test_production_namespace.py::test_unknown_extension_is_preserved_semantically).
This file proves the other half: a caller can register a typed decoder for
a specific extension QName and get a decoded value back, while a node with
no registered adapter remains available unchanged -- decoding is always
opt-in, never required, and never mutates the node itself.

Mirrors test_obligation_codelist_registry.py's already-proven
pluggable-registry test pattern, since extension_adapters.py mirrors
codelist.py's registry shape exactly.
"""

from __future__ import annotations

from format_factory.ubl import (
    ExtensionAdapterRegistry,
    ExtensionDecodeResult,
    XmlNode,
    decode_extension,
)

_VENDOR_NS = "urn:example:vendor"
_AUDIT_QNAME = f"{{{_VENDOR_NS}}}Audit"
_OTHER_QNAME = f"{{{_VENDOR_NS}}}Other"


def _audit_node(flag: str = "yes", value: str = "42") -> XmlNode:
    return XmlNode.create(
        _AUDIT_QNAME,
        attributes={f"{{{_VENDOR_NS}}}flag": flag},
        children=(XmlNode.create(f"{{{_VENDOR_NS}}}Value", text=value),),
    )


def _audit_decoder(node: XmlNode) -> dict[str, str | None]:
    return {
        "flag": dict(node.attributes).get(f"{{{_VENDOR_NS}}}flag"),
        "value": node.children[0].text if node.children else None,
    }


class TestRegistryPopulation:
    def test_empty_registry_has_length_zero(self) -> None:
        assert len(ExtensionAdapterRegistry()) == 0

    def test_register_then_get_round_trips(self) -> None:
        registry = ExtensionAdapterRegistry()
        registry.register(_AUDIT_QNAME, _audit_decoder)
        assert registry.get(_AUDIT_QNAME) is _audit_decoder

    def test_get_on_unregistered_qname_returns_none(self) -> None:
        assert ExtensionAdapterRegistry().get(_OTHER_QNAME) is None

    def test_contains_reflects_registration(self) -> None:
        registry = ExtensionAdapterRegistry()
        assert _AUDIT_QNAME not in registry
        registry.register(_AUDIT_QNAME, _audit_decoder)
        assert _AUDIT_QNAME in registry

    def test_registering_a_second_adapter_for_the_same_qname_replaces_it(self) -> None:
        registry = ExtensionAdapterRegistry()
        registry.register(_AUDIT_QNAME, lambda node: "first")
        registry.register(_AUDIT_QNAME, lambda node: "second")
        assert len(registry) == 1
        assert registry.get(_AUDIT_QNAME)(_audit_node()) == "second"


class TestDecodeExtension:
    def test_a_node_with_a_registered_adapter_is_decoded(self) -> None:
        registry = ExtensionAdapterRegistry()
        registry.register(_AUDIT_QNAME, _audit_decoder)
        node = _audit_node(flag="yes", value="42")

        result = decode_extension(registry, node)

        assert isinstance(result, ExtensionDecodeResult)
        assert result.adapter_known is True
        assert result.decoded == {"flag": "yes", "value": "42"}
        assert result.node is node

    def test_a_node_with_no_registered_adapter_is_unknown_not_an_error(self) -> None:
        registry = ExtensionAdapterRegistry()
        node = XmlNode.create(_OTHER_QNAME)

        result = decode_extension(registry, node)

        assert result.adapter_known is False
        assert result.decoded is None
        assert result.node is node

    def test_an_unregistered_node_round_trips_unchanged_through_decode(self) -> None:
        """Opt-in is structural: calling decode_extension on a node with no
        adapter never raises and never alters the node -- proven by
        identity, not just equality."""
        registry = ExtensionAdapterRegistry()
        node = _audit_node()

        result = decode_extension(registry, node)

        assert result.node is node
        assert result.adapter_known is False

    def test_decoding_is_deterministic_and_repeatable(self) -> None:
        registry = ExtensionAdapterRegistry()
        registry.register(_AUDIT_QNAME, _audit_decoder)
        node = _audit_node()

        first = decode_extension(registry, node)
        second = decode_extension(registry, node)

        assert first == second

    def test_two_different_extension_qnames_use_their_own_adapters_independently(self) -> None:
        registry = ExtensionAdapterRegistry()
        registry.register(_AUDIT_QNAME, _audit_decoder)
        registry.register(_OTHER_QNAME, lambda node: "other-decoded")

        audit_result = decode_extension(registry, _audit_node())
        other_result = decode_extension(registry, XmlNode.create(_OTHER_QNAME))

        assert audit_result.decoded == {"flag": "yes", "value": "42"}
        assert other_result.decoded == "other-decoded"
