"""TOML spec Value — canonical authority class for toml:value.

spec_qname: toml:value
spec_fact_ref: FACT-TOML-003
Namespace: urn:format:toml:1.0
"""
from __future__ import annotations
from typing import ClassVar


class Value:
    """Authority-only class for toml:value."""

    spec_qname: ClassVar[str] = "toml:value"
    spec_fact_ref: ClassVar[str] = "FACT-TOML-003"
    namespace_uri: ClassVar[str] = "urn:format:toml:1.0"
    local_name: ClassVar[str] = "value"
    authority_only: ClassVar[bool] = True
