"""
ODF spec element: office:document

Spec ref: ODF 1.3 §3.1 — Document Element (flat format)
Fact ref: FACT-FODS-001
QName: office:document
Namespace: urn:oasis:names:tc:opendocument:xmlns:office:1.0
Canonical class: Office.Document
"""


class Document:
    """Canonical spec-shaped class for office:document in FODS context.

    Root element of a flat ODS document. Contains office:body, office:automatic-styles,
    and office:scripts. Attributes include office:version and xmlns declarations.

    This is NOT the production model (use models.FodsDocument for production).
    Facades in Compat/ should delegate to this class via spec_qname.
    """

    spec_qname = "office:document"
    spec_fact_ref = "FACT-FODS-001"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name = "document"
    facade_names = ["FodsDocument"]
