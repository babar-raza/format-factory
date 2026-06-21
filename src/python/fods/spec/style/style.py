"""
ODF spec element: style:style

Spec ref: ODF 1.3 §14.1 — Style Element
Fact ref: FACT-FODS-009
QName: style:style
Namespace: urn:oasis:names:tc:opendocument:xmlns:style:1.0
Canonical class: Style.Style
"""


class Style:
    """Canonical spec-shaped class for style:style in FODS context.

    Named style definition element within office:automatic-styles or office:styles.
    Has style:name, style:family, and style:parent-style-name attributes.
    """

    spec_qname = "style:style"
    spec_fact_ref = "FACT-FODS-009"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    local_name = "style"
    facade_names = []
