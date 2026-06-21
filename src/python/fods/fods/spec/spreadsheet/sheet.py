"""
ODF spec element: table:table (spreadsheet sheet/table element).

Spec ref: ODF 1.3 §9.1 — Table Element
Fact ref: FACT-FODS-004
"""


class Sheet:
    """Canonical spec-shaped class for table:table in FODS context.

    This is NOT the production model (FodsSheet). It represents the
    ODF specification element at its canonical QName.
    """

    spec_qname = "table:table"
    spec_fact_ref = "FACT-FODS-004"
