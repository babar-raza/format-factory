"""Pluggable typed-adapter registry for extension content (UBL-EXT-001).

UBL-EXT-001 asks for two distinct things: "read and write extension
containers with arbitrary namespaces and payloads without loss" (built in
codec/preservation.py -- every foreign-namespace subtree, wrapped in the
formal ext:UBLExtensions container or not, round-trips generically as
XmlNode by default) and "expose registered typed adapters as opt-in" (not
previously built -- this module).

Mirrors :mod:`.codelist`'s already-proven pluggable-registry pattern
exactly: an in-memory registry a caller populates at runtime, keyed here by
QName rather than (list_id, agency_id, version), and a decode function with
the same known/unknown tri-state result shape as
:class:`~.codelist.CodeListValidation`. "Opt-in" is structural, not just
documented: a node with no registered adapter round-trips exactly as it
always has (a plain XmlNode) -- decode_extension() never raises and never
alters the node itself, it only optionally attaches a decoded value.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .document import XmlNode

ExtensionAdapter = Callable[[XmlNode], object]


@dataclass(frozen=True, slots=True)
class ExtensionDecodeResult:
    """The outcome of attempting to decode one extension payload node."""

    qname: str
    adapter_known: bool
    decoded: object | None
    node: XmlNode


class ExtensionAdapterRegistry:
    """A pluggable, in-memory registry of typed decoders, keyed by QName.

    Populated at runtime by the caller, exactly like
    :class:`~.codelist.CodeListRegistry` -- there is no built-in adapter for
    any namespace, since this package has no verified spec data describing
    the internal structure of any specific vendor/customization extension
    (digital signatures, PEPPOL extensions, and similar all differ).
    """

    def __init__(self) -> None:
        self._adapters: dict[str, ExtensionAdapter] = {}

    def register(self, qname: str, adapter: ExtensionAdapter) -> None:
        """Add or replace the decoder for `qname`.

        Registering a new adapter for an already-registered QName replaces
        it -- there is exactly one adapter per QName, matching
        CodeListRegistry's replace-on-register semantics.
        """

        self._adapters[qname] = adapter

    def get(self, qname: str) -> ExtensionAdapter | None:
        return self._adapters.get(qname)

    def __len__(self) -> int:
        return len(self._adapters)

    def __contains__(self, qname: str) -> bool:
        return qname in self._adapters


def decode_extension(registry: ExtensionAdapterRegistry, node: XmlNode) -> ExtensionDecodeResult:
    """Decode `node` through `registry`, deterministically and without
    touching the network or filesystem.

    A node whose QName has no registered adapter is reported as unknown,
    not as an error -- the node itself never claimed to be decodable, and
    it remains available, unchanged, as `.node` either way. This is what
    makes adapter use opt-in: calling this function on every extension node
    in a document is always safe, decoded or not.
    """

    adapter = registry.get(node.qname)
    if adapter is None:
        return ExtensionDecodeResult(qname=node.qname, adapter_known=False, decoded=None, node=node)
    return ExtensionDecodeResult(qname=node.qname, adapter_known=True, decoded=adapter(node), node=node)


__all__ = [
    "ExtensionAdapter",
    "ExtensionAdapterRegistry",
    "ExtensionDecodeResult",
    "decode_extension",
]
