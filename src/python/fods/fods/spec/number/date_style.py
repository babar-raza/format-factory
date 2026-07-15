"""
ODF spec element: number:date-style

Spec ref: ODF 1.3 §16.29 — Date Style
Fact ref: FACT-FODS-010
QName: number:date-style
Namespace: urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0
Canonical class: Number.DateStyle
"""

from typing import ClassVar


class DateStyle:
    """Canonical spec-shaped class for number:date-style in FODS context.

    Date formatting style definition within office:automatic-styles.
    Has style:name attribute and contains number:* child elements.
    """

    spec_qname: ClassVar[str] = "number:date-style"
    spec_fact_ref: ClassVar[str] = "FACT-FODS-010"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
    local_name: ClassVar[str] = "date-style"
    facade_names: ClassVar[list] = []
