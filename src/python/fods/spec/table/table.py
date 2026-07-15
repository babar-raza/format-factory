"""
ODF spec element: table:table

Spec ref: ODF 1.3 §9.1 — Table Element
Fact ref: FACT-FODS-004
QName: table:table
Namespace: urn:oasis:names:tc:opendocument:xmlns:table:1.0
Canonical class: Table.Table
"""

from typing import ClassVar


class Table:
    """Canonical spec-shaped class for table:table in FODS context.

    Represents a single sheet/table within office:spreadsheet.
    Has table:name attribute and contains table:table-row children.

    This is NOT the production model (use models.FodsSheet for production).
    Facade: FodsSheet delegates to this via spec_qname.
    """

    spec_qname: ClassVar[str] = "table:table"
    spec_fact_ref: ClassVar[str] = "FACT-FODS-004"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    local_name: ClassVar[str] = "table"
    facade_names: ClassVar[list] = ["FodsSheet"]
