"""FodsDocument — Production facade for the FODS document root element.

Spec authority: office:document (FACT-FODS-001, ODF 1.3 §3.1)
Canonical spec class: src/python/fods/spec/office/document.py::Document
Qname registry: shared/qname-registry/fods.yaml (facade_names: [FodsDocument])

TC-MACH-ARCH-004 (2026-06-21): facade created to satisfy Gate 11 P-ARCH-001.
"""
from __future__ import annotations

from src.python.fods.spec.office.document import Document as _SpecDocument


class FodsDocument(_SpecDocument):
    """Production facade for office:document (FODS root element).

    Inherits all behavior from the canonical spec authority class. Adds production
    convenience methods for interacting with FODS data structures.
    """

    spec_qname = "office:document"
    spec_fact_ref = "FACT-FODS-001"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
