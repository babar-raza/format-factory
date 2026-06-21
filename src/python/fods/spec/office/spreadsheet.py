"""
ODF spec element: office:spreadsheet

Spec ref: ODF 1.3 §9 — Spreadsheet Document Content
Fact ref: FACT-FODS-003
QName: office:spreadsheet
Namespace: urn:oasis:names:tc:opendocument:xmlns:office:1.0
Canonical class: Office.Spreadsheet
"""


class Spreadsheet:
    """Canonical spec-shaped class for office:spreadsheet in FODS context.

    Container element inside office:body for spreadsheet content.
    Contains one or more table:table elements (sheets).
    """

    spec_qname = "office:spreadsheet"
    spec_fact_ref = "FACT-FODS-003"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name = "spreadsheet"
    facade_names = []
