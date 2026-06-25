"""TOML spec Value — canonical authority class for toml:value.

spec_qname: toml:value
spec_fact_ref: FACT-TOML-003
Namespace: urn:format:toml:1.0
"""
from __future__ import annotations


class Value:
    """Authority-only class for toml:value."""

    spec_qname = "toml:value"
    spec_fact_ref = "FACT-TOML-003"
    namespace_uri = "urn:format:toml:1.0"
    local_name = "value"
    authority_only = True
