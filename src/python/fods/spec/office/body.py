"""
ODF spec element: office:body

Spec ref: ODF 1.3 §3.3 — Document Body
Fact ref: SAL-FODS-00003
QName: office:body
Namespace: urn:oasis:names:tc:opendocument:xmlns:office:1.0
Canonical class: Office.Body
"""

from typing import ClassVar


class Body:
    """Canonical spec-shaped class for office:body in FODS context.

    Contains the document content root (office:spreadsheet for FODS).
    """

    spec_qname: ClassVar[str] = "office:body"
    spec_fact_ref: ClassVar[str] = "SAL-FODS-00003"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name: ClassVar[str] = "body"
    facade_names: ClassVar[list] = []
