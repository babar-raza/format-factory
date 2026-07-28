"""
ODF spec element: office:annotation

Spec ref: ODF 1.3 §14.1 — Annotations
Fact ref: SAL-FODS-00022
QName: office:annotation
Namespace: urn:oasis:names:tc:opendocument:xmlns:office:1.0
Canonical class: Office.Annotation
"""

from typing import ClassVar


class Annotation:
    """Canonical spec-shaped class for office:annotation in FODS context.

    Represents a cell comment/annotation in an OpenDocument spreadsheet.
    Key attributes: office:display (bool), svg:x, svg:y, svg:width, svg:height,
    draw:caption-point-x, draw:caption-point-y.
    Contains text:p children with the annotation text.

    This is NOT the production model. Facade: use Compat/ layer for production access.
    """

    spec_qname: ClassVar[str] = "office:annotation"
    spec_fact_ref: ClassVar[str] = "SAL-FODS-00022"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name: ClassVar[str] = "annotation"
    spec_source: ClassVar[str] = "ODF 1.3 Part 3"
    facade_names: ClassVar[list] = []
