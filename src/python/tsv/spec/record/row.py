"""TSV spec Row — canonical authority class for tsv:row.

spec_qname: tsv:row
spec_fact_ref: FACT-TSV-001
Namespace: urn:format:tsv:1.0
"""
from __future__ import annotations


class Row:
    """Authority-only class for tsv:row."""

    spec_qname = "tsv:row"
    spec_fact_ref = "FACT-TSV-001"
    namespace_uri = "urn:format:tsv:1.0"
    local_name = "row"
    authority_only = True
