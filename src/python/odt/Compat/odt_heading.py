"""OdtHeading — production facade for text:h (ODT).

Spec authority: text:h
Fact ref: SAL-ODT-00091
Canonical spec class: src/python/odt/spec/text/heading.py::Heading
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.text.heading import Heading as _SpecHeading


class OdtHeading(_SpecHeading):
    """Production facade for text:h (ODF Text Document heading element)."""

    spec_qname: ClassVar[str] = "text:h"
    spec_fact_ref: ClassVar[str] = "SAL-ODT-00091"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
