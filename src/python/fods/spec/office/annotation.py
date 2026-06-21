"""
ODF spec element: office:annotation

Spec ref: ODF 1.3 §14.1 — Annotations
Fact ref: FACT-FODS-022
QName: office:annotation
Namespace: urn:oasis:names:tc:opendocument:xmlns:office:1.0
Canonical class: Office.Annotation
"""


class Annotation:
    """Canonical spec-shaped class for office:annotation in FODS context.

    Represents a cell comment/annotation in an OpenDocument spreadsheet.
    Key attributes: office:display (bool), svg:x, svg:y, svg:width, svg:height,
    draw:caption-point-x, draw:caption-point-y.
    Contains text:p children with the annotation text.

    This is NOT the production model. Facade: use Compat/ layer for production access.
    """

    spec_qname = "office:annotation"
    spec_fact_ref = "FACT-FODS-022"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name = "annotation"
    spec_source = "ODF 1.3 Part 3"
    facade_names: list = []
