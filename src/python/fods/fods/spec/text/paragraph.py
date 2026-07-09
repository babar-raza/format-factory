"""
ODF spec element: text:p

Spec ref: ODF 1.3 §5.1 — Paragraphs
Fact ref: FACT-FODS-007
QName: text:p
Namespace: urn:oasis:names:tc:opendocument:xmlns:text:1.0
Canonical class: Text.Paragraph
"""


class Paragraph:
    """Canonical spec-shaped class for text:p in FODS context.

    Text paragraph element within table:table-cell for string and formula cells.
    """

    spec_qname = "text:p"
    spec_fact_ref = "FACT-FODS-007"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    local_name = "p"
    facade_names = []
