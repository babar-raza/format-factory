"""
ODF spec element: text:span

Spec ref: ODF 1.3 §5.4 — Spans
Fact ref: FACT-FODS-007
QName: text:span
Namespace: urn:oasis:names:tc:opendocument:xmlns:text:1.0
Canonical class: Text.Span
"""


class Span:
    """Canonical spec-shaped class for text:span in FODS context.

    Inline text span with optional style reference (text:style-name attribute).
    """

    spec_qname = "text:span"
    spec_fact_ref = "FACT-FODS-007"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    local_name = "span"
    facade_names = []
