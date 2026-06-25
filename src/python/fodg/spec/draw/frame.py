"""FODG spec Frame — canonical authority class for draw:frame.

spec_qname: draw:frame
spec_fact_ref: FACT-FODG-003
Namespace: urn:oasis:names:tc:opendocument:xmlns:drawing:1.0
"""
from __future__ import annotations


class Frame:
    """Authority-only class for draw:frame in FODG documents."""

    spec_qname = "draw:frame"
    spec_fact_ref = "FACT-FODG-003"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    local_name = "frame"
    authority_only = True
