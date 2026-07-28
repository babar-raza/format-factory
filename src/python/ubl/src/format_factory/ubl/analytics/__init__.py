"""Optional structural analytics kept outside the codec."""

from __future__ import annotations

from collections import Counter

from ..model import UblDocument


def element_count(document: UblDocument) -> int:
    return sum(1 for _ in document.root.iter())


def qname_histogram(document: UblDocument) -> dict[str, int]:
    return dict(sorted(Counter(node.qname for node in document.root.iter()).items()))


__all__ = ["element_count", "qname_histogram"]
