"""Gnumeric structural element: gnumeric:cell

Spec ref: Gnumeric XML format — Cell element
Fact ref: FACT-GNUMERIC-003
QName: gnumeric:cell
Namespace: http://www.gnumeric.org/v10.dtd
Canonical class: Cell
"""
from __future__ import annotations


class Cell:
    """Authority-only class for gnumeric:cell."""

    spec_qname = "gnumeric:cell"
    spec_fact_ref = "FACT-GNUMERIC-003"
    namespace_uri = "http://www.gnumeric.org/v10.dtd"
    local_name = "cell"
    authority_only = True
