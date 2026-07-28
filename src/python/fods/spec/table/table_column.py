"""
ODF spec element: table:table-column

Spec ref: ODF 1.3 §9.3 — Table Columns
Fact ref: SAL-FODS-00020
QName: table:table-column
Namespace: urn:oasis:names:tc:opendocument:xmlns:table:1.0
Canonical class: Table.TableColumn
"""

from typing import ClassVar


class TableColumn:
    """Canonical spec-shaped class for table:table-column in FODS context.

    Defines column-level properties within a table:table element.
    Key attributes: table:style-name, table:default-cell-style-name,
    table:visibility, table:number-columns-repeated.

    This is NOT the production model. Facade: use Compat/ layer for production access.
    """

    spec_qname: ClassVar[str] = "table:table-column"
    spec_fact_ref: ClassVar[str] = "SAL-FODS-00020"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    local_name: ClassVar[str] = "table-column"
    spec_source: ClassVar[str] = "ODF 1.3 Part 3"
    facade_names: ClassVar[list] = []
