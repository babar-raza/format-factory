"""
ODF spec element: office:automatic-styles

Spec ref: ODF 1.3 §3.15 — Automatic Styles
Fact ref: FACT-FODS-008
QName: office:automatic-styles
Namespace: urn:oasis:names:tc:opendocument:xmlns:office:1.0
Canonical class: Office.AutomaticStyles
"""


class AutomaticStyles:
    """Canonical spec-shaped class for office:automatic-styles in FODS context.

    Container for automatically generated style definitions (style:style elements).
    Appears inside office:document at the same level as office:body.
    """

    spec_qname = "office:automatic-styles"
    spec_fact_ref = "FACT-FODS-008"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name = "automatic-styles"
    facade_names = []
