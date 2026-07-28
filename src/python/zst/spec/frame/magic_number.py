"""ZST spec MagicNumber — canonical authority class for zst:magic-number.

spec_qname: zst:magic-number
spec_fact_ref: SAL-ZST-00003
Namespace: urn:ietf:rfc:8878:zstandard

The Zstandard magic number is 0xFD2FB528 (little-endian) per RFC 8878 §3.1.1.
"""
from __future__ import annotations
from typing import ClassVar


class MagicNumber:
    """Authority-only class for zst:magic-number."""

    spec_qname: ClassVar[str] = "zst:magic-number"
    spec_fact_ref: ClassVar[str] = "SAL-ZST-00003"
    namespace_uri: ClassVar[str] = "urn:ietf:rfc:8878:zstandard"
    local_name: ClassVar[str] = "magic-number"
    authority_only: ClassVar[bool] = True

    #: RFC 8878 §3.1.1: Magic_Number = 0xFD2FB528
    MAGIC_BYTES = b"\x28\xb5\x2f\xfd"
