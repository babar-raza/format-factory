"""Notebook-specific resource-limit policy."""

from __future__ import annotations

from typing import Any

from format_factory.core import DEFAULT_LIMITS, ResourceLimits

IPYNB_DEFAULT_LIMITS = DEFAULT_LIMITS.with_overrides(
    max_input_bytes=64 * 1024 * 1024,
    max_nesting_depth=64,
)


def effective_limits(limits: ResourceLimits | None) -> ResourceLimits:
    return limits or IPYNB_DEFAULT_LIMITS


def _utf8_size(value: str, limits: ResourceLimits, current: int) -> int:
    total = current
    for offset in range(0, len(value), 64 * 1024):
        total += len(value[offset : offset + 64 * 1024].encode("utf-8"))
        limits.enforce("max_decompressed_bytes", total)
    return total


def enforce_structure(value: Any, limits: ResourceLimits | None = None) -> None:
    """Bound an already-decoded JSON-like tree before recursive processing."""

    selected = effective_limits(limits)
    stack: list[tuple[Any, int]] = [(value, 0)]
    entries = 0
    decoded_bytes = 0
    while stack:
        current, depth = stack.pop()
        selected.enforce("max_nesting_depth", depth)
        if isinstance(current, dict):
            entries += len(current)
            selected.enforce("max_entries", entries)
            for key, item in current.items():
                if isinstance(key, str):
                    decoded_bytes = _utf8_size(key, selected, decoded_bytes)
                stack.append((item, depth + 1))
        elif isinstance(current, list):
            entries += len(current)
            selected.enforce("max_entries", entries)
            stack.extend((item, depth + 1) for item in current)
        elif isinstance(current, str):
            decoded_bytes = _utf8_size(current, selected, decoded_bytes)


__all__ = ["IPYNB_DEFAULT_LIMITS", "effective_limits", "enforce_structure"]
