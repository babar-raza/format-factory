"""
ODF spec element: table:table-cell

Spec ref: ODF 1.3 §9.5 — Table Cell Elements
Fact ref: FACT-FODS-006
QName: table:table-cell
Namespace: urn:oasis:names:tc:opendocument:xmlns:table:1.0
Canonical class: Table.TableCell
"""


class TableCell:
    """Canonical spec-shaped class for table:table-cell in FODS context.

    A cell within table:table-row. Has office:value-type, office:value,
    and table:style-name attributes. Contains text:p children for string/formula cells.

    This is NOT the production model (use models.FodsCell for production).
    Facade: FodsCell delegates to this via spec_qname.
    """

    spec_qname = "table:table-cell"
    spec_fact_ref = "FACT-FODS-006"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    local_name = "table-cell"
    facade_names = ["FodsCell"]
