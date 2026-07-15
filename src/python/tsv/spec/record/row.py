"""TSV spec Row — canonical authority class for tsv:row.

spec_qname: tsv:row
spec_fact_ref: FACT-TSV-001
Namespace: urn:format:tsv:1.0
"""
from __future__ import annotations
from typing import ClassVar


class Row:
    """Authority-only class for tsv:row."""

    spec_qname: ClassVar[str] = "tsv:row"
    spec_fact_ref: ClassVar[str] = "FACT-TSV-001"
    namespace_uri: ClassVar[str] = "urn:format:tsv:1.0"
    local_name: ClassVar[str] = "row"
    authority_only: ClassVar[bool] = True
