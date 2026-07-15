"""FodtList — Compat facade for the FODT text:list element.

Spec authority: text:list (FACT-FODT-005, ODF 1.3 §5.3)
Canonical spec class: src/python/fodt/spec/text/list_.py::List
Qname registry: shared/qname-registry/fodt.yaml (facade_names: [FodtList])

TC-SP-005 (2026-06-25): facade created to satisfy Gate 11 P-ARCH-001 spec parity.
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.text.list_ import List as _SpecList


class FodtList(_SpecList):
    """ARCHITECTURE MARKER — spec_qname attribution for text:list (Gate 11 P-ARCH-001).

    Ordered or unordered list element within FODT document body.
    TC-SP-005 disposition: PATH B (architecture marker, 2026-06-25).
    """

    spec_qname: ClassVar[str] = "text:list"
    spec_fact_ref: ClassVar[str] = "FACT-FODT-005"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
