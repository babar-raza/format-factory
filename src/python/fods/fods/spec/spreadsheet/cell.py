"""
ODF spec element: table:table-cell (table cell element).

Spec ref: ODF 1.3 §9.5 — Table Cell Elements
Fact ref: FACT-FODS-006
"""


class Cell:
    """Canonical spec-shaped class for table:table-cell in FODS context.

    This is NOT the production model (FodsCell). It represents the
    ODF specification element at its canonical QName.
    """

    spec_qname = "table:table-cell"
    spec_fact_ref = "FACT-FODS-006"
