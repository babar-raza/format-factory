"""
ODF spec element: table:table-row (table row element).

Spec ref: ODF 1.3 §9.4 — Table Row Element
Fact ref: FACT-FODS-005
"""


class Row:
    """Canonical spec-shaped class for table:table-row in FODS context.

    This is NOT the production model (FodsRow). It represents the
    ODF specification element at its canonical QName.
    """

    spec_qname = "table:table-row"
    spec_fact_ref = "FACT-FODS-005"
