"""
ODF spec element: table:table-header-rows

Spec ref: ODF 1.3 §9.4 — Table Header Rows
Fact ref: FACT-FODS-021
QName: table:table-header-rows
Namespace: urn:oasis:names:tc:opendocument:xmlns:table:1.0
Canonical class: Table.TableHeaderRows
"""


class TableHeaderRows:
    """Canonical spec-shaped class for table:table-header-rows in FODS context.

    Groups header rows within a table:table element. All rows within this
    element are treated as column headers that repeat on each page when
    printing. Contains one or more table:table-row children.

    This is NOT the production model. Facade: use Compat/ layer for production access.
    """

    spec_qname = "table:table-header-rows"
    spec_fact_ref = "FACT-FODS-021"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    local_name = "table-header-rows"
    spec_source = "ODF 1.3 Part 3"
    facade_names: list = []
