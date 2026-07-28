"""
ODF spec element: table:table-row

Spec ref: ODF 1.3 §9.4 — Table Row Element
Fact ref: SAL-FODS-00005
QName: table:table-row
Namespace: urn:oasis:names:tc:opendocument:xmlns:table:1.0
Canonical class: Table.TableRow
"""

from typing import ClassVar


class TableRow:
    """Canonical spec-shaped class for table:table-row in FODS context.

    A row within table:table. Contains table:table-cell and
    table:covered-table-cell children.
    """

    spec_qname: ClassVar[str] = "table:table-row"
    spec_fact_ref: ClassVar[str] = "SAL-FODS-00005"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    local_name: ClassVar[str] = "table-row"
    facade_names: ClassVar[list] = []
