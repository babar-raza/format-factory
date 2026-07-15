"""
ODF spec element: style:style

Spec ref: ODF 1.3 §14.1 — Style Element
Fact ref: FACT-FODS-009
QName: style:style
Namespace: urn:oasis:names:tc:opendocument:xmlns:style:1.0
Canonical class: Style.Style
"""

from typing import ClassVar


class Style:
    """Canonical spec-shaped class for style:style in FODS context.

    Named style definition element within office:automatic-styles or office:styles.
    Has style:name, style:family, and style:parent-style-name attributes.
    """

    spec_qname: ClassVar[str] = "style:style"
    spec_fact_ref: ClassVar[str] = "FACT-FODS-009"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    local_name: ClassVar[str] = "style"
    facade_names: ClassVar[list] = []
