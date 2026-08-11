"""Read-mode enum, factored out of `lifecycle.py` so the codec layer
(`codec/container.py`, `codec/stack_xml.py`) can depend on it without a
circular import back through `lifecycle.py`, which itself depends on the
codec layer.
"""

from __future__ import annotations

from enum import Enum


class ReadMode(Enum):
    """STRICT rejects anything the specification requires; TOLERANT recovers
    where the format permits and reports what it did."""

    STRICT = "strict"
    TOLERANT = "tolerant"


__all__ = ["ReadMode"]
