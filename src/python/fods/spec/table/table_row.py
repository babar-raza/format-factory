"""
ODF spec element: table:table-row

Spec ref: ODF 1.3 §9.4 — Table Row Element
Fact ref: FACT-FODS-005
QName: table:table-row
Namespace: urn:oasis:names:tc:opendocument:xmlns:table:1.0
Canonical class: Table.TableRow
"""


class TableRow:
    """Canonical spec-shaped class for table:table-row in FODS context.

    A row within table:table. Contains table:table-cell and
    table:covered-table-cell children.
    """

    spec_qname = "table:table-row"
    spec_fact_ref = "FACT-FODS-005"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    local_name = "table-row"
    facade_names = []
