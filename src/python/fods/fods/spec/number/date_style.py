"""
ODF spec element: number:date-style

Spec ref: ODF 1.3 §16.29 — Date Style
Fact ref: FACT-FODS-010
QName: number:date-style
Namespace: urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0
Canonical class: Number.DateStyle
"""


class DateStyle:
    """Canonical spec-shaped class for number:date-style in FODS context.

    Date formatting style definition within office:automatic-styles.
    Has style:name attribute and contains number:* child elements.
    """

    spec_qname = "number:date-style"
    spec_fact_ref = "FACT-FODS-010"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
    local_name = "date-style"
    facade_names = []
