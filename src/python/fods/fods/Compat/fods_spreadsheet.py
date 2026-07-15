"""FodsSpreadsheet — Compat facade for the FODS office:spreadsheet element.

Spec authority: office:spreadsheet (FACT-FODS-003, ODF 1.3 §9.1)
Canonical spec class: src/python/fods/spec/office/spreadsheet.py::Spreadsheet
Qname registry: shared/qname-registry/fods.yaml (facade_names: [FodsSpreadsheet])

TC-SP-002 (2026-06-25): facade created to satisfy Gate 11 P-ARCH-001 spec parity.
"""
from __future__ import annotations
from typing import ClassVar

from src.python.fods.spec.office.spreadsheet import Spreadsheet as _SpecSpreadsheet


class FodsSpreadsheet(_SpecSpreadsheet):
    """ARCHITECTURE MARKER — spec_qname attribution for office:spreadsheet (Gate 11 P-ARCH-001).

    Use fods production code for behavioral implementation.
    This class exists to satisfy Gate 11 P-ARCH-001 spec_qname traceability only.
    It inherits the canonical spec class but adds no behavioral implementation.
    TC-SP-002 disposition: PATH B (architecture marker, 2026-06-25).
    """

    spec_qname: ClassVar[str] = "office:spreadsheet"
    spec_fact_ref: ClassVar[str] = "FACT-FODS-003"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
