"""FodtSpan — production facade for text:span (FODT).

Spec authority: text:span
Spec ref: ODF 1.3 §6.1.7
Fact ref: FACT-FODT-006
Canonical spec class: src/python/fodt/spec/text/span.py::Span
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.text.span import Span as _SpecSpan


class FodtSpan(_SpecSpan):
    """Production facade for text:span (FODT inline span element).

    Inherits all behavioral properties from the canonical spec class.
    """

    spec_qname: ClassVar[str] = "text:span"
    spec_fact_ref: ClassVar[str] = "FACT-FODT-006"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
