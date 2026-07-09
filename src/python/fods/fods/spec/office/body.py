"""
ODF spec element: office:body

Spec ref: ODF 1.3 §3.3 — Document Body
Fact ref: FACT-FODS-003
QName: office:body
Namespace: urn:oasis:names:tc:opendocument:xmlns:office:1.0
Canonical class: Office.Body
"""


class Body:
    """Canonical spec-shaped class for office:body in FODS context.

    Contains the document content root (office:spreadsheet for FODS).
    """

    spec_qname = "office:body"
    spec_fact_ref = "FACT-FODS-003"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name = "body"
    facade_names = []
