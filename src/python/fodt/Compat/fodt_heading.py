"""FodtHeading — production facade for text:h (FODT).

Spec authority: text:h
Spec ref: ODF 1.3 §5.1.2
Fact ref: SAL-FODT-00004
Canonical spec class: src/python/fodt/spec/text/heading.py::Heading
"""
from __future__ import annotations
from typing import ClassVar

from ..spec.text.heading import Heading as _SpecHeading


class FodtHeading(_SpecHeading):
    """Production facade for text:h (FODT heading element).

    Inherits all behavioral properties from the canonical spec class.
    """

    spec_qname: ClassVar[str] = "text:h"
    spec_fact_ref: ClassVar[str] = "SAL-FODT-00004"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
