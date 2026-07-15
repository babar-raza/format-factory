"""
ODF spec element: text:p

Spec ref: ODF 1.3 §5.1 — Paragraphs
Fact ref: FACT-FODS-007
QName: text:p
Namespace: urn:oasis:names:tc:opendocument:xmlns:text:1.0
Canonical class: Text.Paragraph
"""

from typing import ClassVar


class Paragraph:
    """Canonical spec-shaped class for text:p in FODS context.

    Text paragraph element within table:table-cell for string and formula cells.
    """

    spec_qname: ClassVar[str] = "text:p"
    spec_fact_ref: ClassVar[str] = "FACT-FODS-007"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    local_name: ClassVar[str] = "p"
    facade_names: ClassVar[list] = []
