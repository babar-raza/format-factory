"""
ODF spec element: table:covered-table-cell

Spec ref: ODF 1.3 §9.5.2 — Covered Table Cell
Fact ref: FACT-FODS-023
QName: table:covered-table-cell
Namespace: urn:oasis:names:tc:opendocument:xmlns:table:1.0
Canonical class: Table.CoveredTableCell
"""


class CoveredTableCell:
    """Canonical spec-shaped class for table:covered-table-cell in FODS context.

    A placeholder element for cells that are covered by a spanning table cell
    (table:table-cell with table:number-columns-spanned or table:number-rows-spanned).
    Has the same attributes as table:table-cell but no content is rendered.

    This is NOT the production model. Facade: use Compat/ layer for production access.
    """

    spec_qname = "table:covered-table-cell"
    spec_fact_ref = "FACT-FODS-023"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    local_name = "covered-table-cell"
    spec_source = "ODF 1.3 Part 3"
    facade_names: list = []
