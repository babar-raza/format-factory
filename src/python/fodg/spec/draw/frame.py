"""FODG spec Frame — canonical authority class for draw:frame.

spec_qname: draw:frame
spec_fact_ref: SAL-FODG-00003
Namespace: urn:oasis:names:tc:opendocument:xmlns:drawing:1.0
"""
from __future__ import annotations

from typing import ClassVar


class Frame:
    """Authority-only class for draw:frame in FODG documents."""

    spec_qname: ClassVar[str] = "draw:frame"
    spec_fact_ref: ClassVar[str] = "SAL-FODG-00003"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    local_name: ClassVar[str] = "frame"
    authority_only: ClassVar[bool] = True
