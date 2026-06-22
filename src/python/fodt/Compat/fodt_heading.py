"""FodtHeading — production facade for text:h (FODT).

Spec authority: text:h
Spec ref: ODF 1.3 §5.1.2
Fact ref: FACT-FODT-004
Canonical spec class: src/python/fodt/spec/text/heading.py::Heading
"""
from __future__ import annotations

from ..spec.text.heading import Heading as _SpecHeading


class FodtHeading(_SpecHeading):
    """Production facade for text:h (FODT heading element).

    Inherits all behavioral properties from the canonical spec class.
    """

    spec_qname = "text:h"
    spec_fact_ref = "FACT-FODT-004"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
