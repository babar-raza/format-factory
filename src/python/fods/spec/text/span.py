"""
ODF spec element: text:span

Spec ref: ODF 1.3 §5.4 — Spans
Fact ref: SAL-FODS-00007
QName: text:span
Namespace: urn:oasis:names:tc:opendocument:xmlns:text:1.0
Canonical class: Text.Span
"""

from typing import ClassVar


class Span:
    """Canonical spec-shaped class for text:span in FODS context.

    Inline text span with optional style reference (text:style-name attribute).
    """

    spec_qname: ClassVar[str] = "text:span"
    spec_fact_ref: ClassVar[str] = "SAL-FODS-00007"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    local_name: ClassVar[str] = "span"
    facade_names: ClassVar[list] = []
