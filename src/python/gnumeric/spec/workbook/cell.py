"""Gnumeric structural element: gnumeric:cell

Spec ref: Gnumeric XML format — Cell element
Fact ref: FACT-GNUMERIC-003
QName: gnumeric:cell
Namespace: http://www.gnumeric.org/v10.dtd
Canonical class: Cell
"""
from __future__ import annotations
from typing import ClassVar


class Cell:
    """Authority-only class for gnumeric:cell."""

    spec_qname: ClassVar[str] = "gnumeric:cell"
    spec_fact_ref: ClassVar[str] = "FACT-GNUMERIC-003"
    namespace_uri: ClassVar[str] = "http://www.gnumeric.org/v10.dtd"
    local_name: ClassVar[str] = "cell"
    authority_only: ClassVar[bool] = True
