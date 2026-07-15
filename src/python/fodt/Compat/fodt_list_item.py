"""FodtListItem — Compat facade for the FODT text:list-item element.

Spec authority: text:list-item (FACT-FODT-005, ODF 1.3 §5.3)
Canonical spec class: src/python/fodt/spec/text/list_item.py::ListItem
Qname registry: shared/qname-registry/fodt.yaml (facade_names: [FodtListItem])

TC-SP-005 (2026-06-25): facade created to satisfy Gate 11 P-ARCH-001 spec parity.
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.text.list_item import ListItem as _SpecListItem


class FodtListItem(_SpecListItem):
    """ARCHITECTURE MARKER — spec_qname attribution for text:list-item (Gate 11 P-ARCH-001).

    Individual item within a text:list container.
    TC-SP-005 disposition: PATH B (architecture marker, 2026-06-25).
    """

    spec_qname: ClassVar[str] = "text:list-item"
    spec_fact_ref: ClassVar[str] = "FACT-FODT-005"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
