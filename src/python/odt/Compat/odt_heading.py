"""OdtHeading — production facade for text:h (ODT).

Spec authority: text:h
Fact ref: FACT-ODT-EX-0094
Canonical spec class: src/python/odt/spec/text/heading.py::Heading
"""
from __future__ import annotations

from ..spec.text.heading import Heading as _SpecHeading


class OdtHeading(_SpecHeading):
    """Production facade for text:h (ODF Text Document heading element)."""

    spec_qname = "text:h"
    spec_fact_ref = "FACT-ODT-EX-0094"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
