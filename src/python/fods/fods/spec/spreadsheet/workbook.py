"""
ODF spec element: office:document (FODS root element).

Spec ref: ODF 1.3 §3.1 — Document Root Element
Fact ref: FACT-FODS-001
"""


class Workbook:
    """Canonical spec-shaped class for office:document in FODS context.

    This is NOT the production model (FodsDocument). It represents the
    ODF specification element at its canonical QName.
    """

    spec_qname = "office:document"
    spec_fact_ref = "FACT-FODS-001"
